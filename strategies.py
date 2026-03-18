from abc import ABC, abstractmethod
from typing import Literal
from unittest import result
from dotenv import load_dotenv

from openai import OpenAI
from pydantic import BaseModel

from engine import Action, GameState, BUILDINGS, building_cost, available_upgrades, compute_building_cps


def _cps_delta(state: GameState, action: Action) -> float:
    """CpS increase from applying action without modifying state."""
    owned = state.owned[:]
    tier_upgrades = state.tier_upgrades[:]
    grandma_synergy = dict(state.grandma_synergy)

    if action.kind == "building":
        owned[action.idx] += 1
    elif action.kind == "tier":
        tier_upgrades[action.idx] += 1
    elif action.kind == "grandma_synergy":
        grandma_synergy[action.idx] = True

    _, new_cps = compute_building_cps(owned, tier_upgrades, grandma_synergy)
    return new_cps - state.cps


class Strategy(ABC):
    @abstractmethod
    def decide(self, state: GameState) -> Action | None:
        """Return an Action to buy, or None to wait and save cookies."""
        ...


class CheapestStrategy(Strategy):
    def decide(self, state: GameState) -> Action | None:
        options = [(building_cost(bc, state.owned[i]), "building", i, name) for i, (name, bc, _) in enumerate(BUILDINGS)]
        options += [(cost, utype, idx, uname)
            for cost, utype, idx, uname in available_upgrades(
                state.owned, state.tier_upgrades, state.grandma_synergy
            )
        ]
        options.sort(key=lambda x: x[0])

        for cost, otype, idx, name in options:
            if state.cookies >= cost:
                return Action(otype, idx, cost, name)
        return None


class GreedyROIStrategy(Strategy):
    def decide(self, state: GameState) -> Action | None:
        if state.cps == 0:
            return None

        candidates = []

        for i, (name, bc, _) in enumerate(BUILDINGS):
            cost = building_cost(bc, state.owned[i])
            action = Action("building", i, cost, name)
            delta = _cps_delta(state, action)
            if delta > 0:
                payback = max(0, (cost - state.cookies) / state.cps) + cost / delta #time to afford + time to ROI
                candidates.append((payback, action))

        for cost, utype, idx, uname in available_upgrades(state.owned, state.tier_upgrades, state.grandma_synergy):
            action = Action(utype, idx, cost, uname)
            delta = _cps_delta(state, action)
            if delta > 0:
                payback = max(0, (cost - state.cookies) / state.cps) + cost / delta
                candidates.append((payback, action))

        if not candidates:
            return None

        best = min(candidates, key=lambda x: x[0])[1]
        return best if state.cookies >= best.cost else None


class _LLMDecision(BaseModel):
    action: Literal["buy_building", "buy_upgrade", "wait"]
    target: str  # building/upgrade name, or ticks to wait (as string)
    reasoning: str


class LLMStrategy(Strategy):
    MODEL = "gpt-5-mini"
    
    def __init__(self, sim_length=1000):
        self._tick = 0
        self._pending_buy: Action | None = None  # LLM said buy this; execute when affordable
        self._wait_until: int = -1               # tick at which wait expires (-1 = no timer)
        self._wait_for: str | None = None        # item name to auto-buy when affordable
        self._wait_for_since: int = 0            # tick when _wait_for was set
        self._next_call_tick = self._tick
        self.llm_calls: int = 0
        self.sim_length = sim_length

        load_dotenv()
        self._client = OpenAI()

    def decide(self, state: GameState) -> Action | None:
        self._tick += 1

        all_options = self._all_options(state)
        affordable = {n: a for n, a in all_options.items() if state.cookies >= a.cost}

        #Cool off period after each LLM call to avoid excessive calls when multiple options are affordable
        if self._tick < self._next_call_tick:
            return None

        # Complete a wait_for direction once the item is affordable
        if self._wait_for and self._wait_for in affordable:
            action = affordable[self._wait_for]
            self._wait_for = None
            return action

        # Respect active wait_until — no interruption
        if self._wait_until >= 0:
            if self._tick < self._wait_until:
                return None
            self._wait_until = -1  # timer expired, fall through to consult LLM

        # Respect active wait_for — still saving up, unless timeout exceeded
        if self._wait_for:
            action = all_options.get(self._wait_for)
            if action and state.cps > 0:
                timeout = 3 * (action.cost / state.cps)
                if self._tick - self._wait_for_since <= timeout:
                    return None
            else:
                return None
            self._wait_for = None  # timeout exceeded, fall through to re-consult LLM

        # No direction from LLM; consult if something is affordable
        if not affordable:
            return None

        decision, options_list = self._call_llm(state, all_options)
        self._next_call_tick = self._tick + 100  # cool off period to avoid excessive calls
        self._apply(decision, affordable, options_list)

        # If the decision is immediately actionable, execute now
        if self._pending_buy and state.cookies >= self._pending_buy.cost:
            action = self._pending_buy
            self._pending_buy = None
            return action

        return None
    
    def _all_options(self, state: GameState) -> dict[str, Action]:
        result = {}
        for i, (name, bc, _) in enumerate(BUILDINGS):
            cost = building_cost(bc, state.owned[i])
            if cost <= state.cps * 500:
                result[name] = Action("building", i, cost, name)

        # add the cheapest unaffordable building as a stretch goal
        stretch = min(
            ((building_cost(bc, state.owned[i]), name, i)
             for i, (name, bc, _) in enumerate(BUILDINGS)
             if name not in result),
            key=lambda x: x[0],
            default=None,
        )

        if stretch:
            cost, name, i = stretch
            result[name] = Action("building", i, cost, name)

        upgrades = available_upgrades(state.owned, state.tier_upgrades, state.grandma_synergy)

        # add the cheapest unaffordable upgrade as a stretch goal
        ustretch = min(
            ((c, ut, idx, un) for c, ut, idx, un in upgrades if c > state.cps * 500),
            key=lambda x: x[0],
            default=None,
        )
        if ustretch:
            cost, utype, idx, uname = ustretch
            result[uname] = Action(utype, idx, cost, uname)

        return result

    def _call_llm(self, state: GameState, all_options: dict) -> tuple[_LLMDecision, list]:
        options_list = list(all_options.items())  # stable order for this call

        system_content = """You are optimizing a Cookie Clicker game. Maximize CpS efficiently.

                        Rules:
                        - Building cost increases 15% each purchase (compounds)
                        - Tier upgrades double ALL existing and future buildings of that type
                        - Grandma synergies: buying a grandma type doubles ALL grandma CpS AND gives the linked building +X% CpS per grandma owned
                        - You cannot buy another building for 100 ticks after a purchase (cool off period)

                        You will be shown current state and options to buy. 
                        You can choose: 
                            1.buy an item now (building, upgrade or synergy) OR
                            2.save up to buy an item OR
                            3.wait N ticks"""

        lines = [
            f"Simulation: tick {self._tick} of {self.sim_length}",
            f"Cookies: {state.cookies:.0f}",
            f"CpS: {state.cps:.2f}",
            f"Buildings owned:",
        ]
        for i, (name, _, _) in enumerate(BUILDINGS):
            lines.append(f"  {name}: {state.owned[i]}")

        lines += ["", "Purchase options:"]
        for i, (name, action) in enumerate(options_list):
            if action.kind in ("tier", "grandma_synergy"):
                context = f" [doubles CpS of ALL {BUILDINGS[action.idx][0]}s you own ({state.owned[action.idx]})]"
            else:
                context = ""
    
            affordable = state.cookies >= action.cost
            tag = " [AFFORDABLE]" if affordable else f" (need {action.cost - state.cookies:.0f} more)"
            lines.append(f"  {i}: {name}  cost={action.cost:.0f}{context}{tag}")

        lines += [
            "",
            "Goal: Maximize CpS as efficiently as possible.",
            "For buy_building/buy_upgrade: set target to the option index (e.g., '2'). Use this even if you cannot afford it yet — the engine will save up and buy it automatically.",
            "For wait: only use this if you genuinely want to do nothing (e.g., no good option exists). Set target to ticks to wait.",
        ]

        response = self._client.beta.chat.completions.parse(
            model=self.MODEL,
            messages=[
                {
                    "role": "system",
                    "content": system_content,
                },
                {"role": "user", "content": "\n".join(lines)},
            ],
            response_format=_LLMDecision,
        )
        self.llm_calls += 1
        dec = response.choices[0].message.parsed
        name = options_list[int(dec.target)][0] if dec.target.isdigit() and int(dec.target) < len(options_list) else dec.target
        print(f"  [LLM tick={self._tick} call={self.llm_calls}] {dec.action} -> {name} | {dec.reasoning}")
        return dec, options_list

    def _apply(self, decision: _LLMDecision, affordable: dict, options_list: list):
        if decision.action in ("buy_building", "buy_upgrade"):
            target = decision.target.strip()
            if target.isdigit():
                idx = int(target)
                if 0 <= idx < len(options_list):
                    name, action = options_list[idx]
                    if name in affordable:
                        self._pending_buy = action
                    else:
                        self._wait_for = name
                    self._wait_for_since = self._tick
        elif decision.action == "wait":
            target = decision.target.strip()
            if target.isdigit():
                self._wait_until = self._tick + int(target)
            else:
                self._wait_until = self._tick + 100  # fallback
