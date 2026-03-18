from abc import ABC, abstractmethod
from typing import Literal
from unittest import result
from dotenv import load_dotenv

from openai import OpenAI
from pydantic import BaseModel

from engine import Action, GameState, BUILDINGS, TIER_SCHEDULE, building_cost, available_upgrades, compute_building_cps

_BUILDING_INDEX = {name: i for i, (name, _, _) in enumerate(BUILDINGS)}


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


class PlannedPurchase(BaseModel):
    action: Literal["buy_building", "buy_upgrade"]
    target: str  # exact name as shown in prompt, e.g. "Grandma", "Farm tier 3", "Farm grandma synergy"
    reasoning: str


class _LLMPlan(BaseModel):
    purchases: list[PlannedPurchase]


class LLMPlannerStrategy(Strategy):
    MODEL = "gpt-5-mini"

    def __init__(self, sim_length=1000, plan_save_path: str | None = None):
        self._tick = 0
        self._plan: list[PlannedPurchase] = []
        self._known_upgrades: set[str] = set()
        self.llm_calls = 0
        self.sim_length = sim_length
        self._plan_save_path = plan_save_path
        load_dotenv()
        self._client = OpenAI()

    def decide(self, state: GameState) -> Action | None:
        self._tick += 1

        current_upgrades = {uname for _, _, _, uname in available_upgrades(state.owned, state.tier_upgrades, state.grandma_synergy)}
        new_upgrades = current_upgrades - self._known_upgrades
        self._known_upgrades = current_upgrades

        # Re-plan if a new upgrade appeared that isn't already covered by remaining plan
        if new_upgrades and not new_upgrades.issubset({p.target for p in self._plan}):
            self._plan = []

        # Advance past already-purchased front items; re-plan if stuck on unavailable upgrade
        while self._plan:
            if self._resolve(self._plan[0], state) is not None:
                break
            if self._is_already_purchased(self._plan[0], state):
                self._plan.pop(0)
            else:
                self._plan = []  # not yet unlocked — re-plan
                break

        if not self._plan:
            self._plan = self._call_llm(state)

        if not self._plan:
            return None

        action = self._resolve(self._plan[0], state)
        if action is None:
            return None

        if state.cookies >= action.cost:
            purchase = self._plan.pop(0)
            print(f"  [Planner tick={self._tick} call={self.llm_calls}] {purchase.action} -> {purchase.target} | {purchase.reasoning}")
            return action

        return None  # saving up for plan[0]

    def _resolve(self, purchase: PlannedPurchase, state: GameState) -> Action | None:
        """Map a PlannedPurchase to an Action using current state, or None if invalid/unavailable."""
        if purchase.action == "buy_building":
            idx = _BUILDING_INDEX.get(purchase.target)
            if idx is None:
                return None
            cost = building_cost(BUILDINGS[idx][1], state.owned[idx])
            return Action("building", idx, cost, purchase.target)

        for cost, utype, idx, uname in available_upgrades(state.owned, state.tier_upgrades, state.grandma_synergy):
            if uname == purchase.target:
                return Action(utype, idx, cost, uname)
        return None

    def _is_already_purchased(self, purchase: PlannedPurchase, state: GameState) -> bool:
        """True if a planned upgrade has already been bought (so we can skip it)."""
        if purchase.action == "buy_building":
            return False
        name = purchase.target
        for i, (bname, _, _) in enumerate(BUILDINGS):
            if name == f"{bname} grandma synergy":
                return state.grandma_synergy.get(i, False)
            tier_prefix = f"{bname} tier "
            if name.startswith(tier_prefix):
                tier_num = int(name[len(tier_prefix):])
                return state.tier_upgrades[i] >= tier_num
        return False

    def _call_llm(self, state: GameState) -> list[PlannedPurchase]:
        response = self._client.beta.chat.completions.parse(
            model=self.MODEL,
            messages=[
                {"role": "system", "content": (
                    "You are optimizing a Cookie Clicker game. Maximize CpS as efficiently as possible.\n\n"
                    "Rules:\n"
                    "- Building cost scales 15% per purchase (compounding)\n"
                    "- Tier upgrades DOUBLE ALL existing and future buildings of that type\n"
                    "- Grandma synergies double ALL grandma CpS AND give the linked building +% CpS per grandma owned\n"
                    "- Plan purchases in execution order — prerequisites must appear before what they unlock"
                    "- Plan purchases that may require saving — the engine will wait and buy them in order. "
                    "- Don't fill the plan with cheap items just because they're immediately affordable."
                )},
                {"role": "user", "content": self._build_prompt(state)},
            ],
            response_format=_LLMPlan,
        )
        self.llm_calls += 1
        plan = response.choices[0].message.parsed
        print(f"  [Planner tick={self._tick} call={self.llm_calls}] new plan ({len(plan.purchases)} purchases):")
        for i, p in enumerate(plan.purchases):
            print(f"    [{i}] {p.action} -> {p.target}")
        if self._plan_save_path:
            import json
            with open(self._plan_save_path, "w") as f:
                json.dump({
                    "tick": self._tick,
                    "call": self.llm_calls,
                    "purchases": [p.model_dump() for p in plan.purchases],
                }, f, indent=2)
        return plan.purchases

    def _build_prompt(self, state: GameState) -> str:
        lines = [
            f"Simulation: tick {self._tick} of {self.sim_length}",
            f"Cookies: {state.cookies:.0f}  |  CpS: {state.cps:.2f}",
            "",
            "Buildings owned (count | next cost):",
        ]
        for i, (name, bc, _) in enumerate(BUILDINGS):
            cost = building_cost(bc, state.owned[i])
            lines.append(f"  {name}: {state.owned[i]} owned, next costs {cost:.0f}")

        # Hint: buildings 1–5 away from unlocking the next tier
        hints = []
        for i, (name, _, _) in enumerate(BUILDINGS):
            purchased = state.tier_upgrades[i]
            if purchased < len(TIER_SCHEDULE):
                unlock_at = TIER_SCHEDULE[purchased][0]
                remaining = unlock_at - state.owned[i]
                if 0 < remaining <= 5:
                    hints.append(f"  {remaining} more {name} unlocks {name} tier {purchased + 1} (doubles all {name}s)")
        if hints:
            lines += ["", "Near tier unlock thresholds:"] + hints

        # Available upgrades and synergies with CpS delta
        upgrades = available_upgrades(state.owned, state.tier_upgrades, state.grandma_synergy)
        if upgrades:
            lines += ["", "Available upgrades and synergies (with CpS impact):"]
            for cost, utype, idx, uname in upgrades:
                action = Action(utype, idx, cost, uname)
                delta = _cps_delta(state, action)
                tag = "[AFFORDABLE]" if state.cookies >= cost else f"(need {cost - state.cookies:.0f} more)"
                lines.append(f"  {uname}  cost={cost:.0f}  +{delta:.1f} CpS  {tag}")

        lines += [
            "",
            "Plan the next 10 purchases in execution order to maximize CpS.",
            "Consider: tier upgrade doubling effect, synergy stacking, buildings near unlock thresholds.",
            'Use exact names as shown above (e.g. "Grandma", "Farm tier 3", "Farm grandma synergy").',
            "Prerequisites must appear before what they unlock.",
        ]
        return "\n".join(lines)
