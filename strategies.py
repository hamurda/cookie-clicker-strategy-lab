from abc import ABC, abstractmethod
from typing import Literal
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
        options = [(building_cost(bc, state.owned[i]), "building", i) for i, (_, bc, _) in enumerate(BUILDINGS)]
        options += [(cost, utype, idx) 
            for cost, utype, idx, _ in available_upgrades(
                state.owned, state.tier_upgrades, state.grandma_synergy
            )
        ]
        options.sort(key=lambda x: x[0])

        for cost, otype, idx in options:
            if state.cookies >= cost:
                return Action(otype, idx, cost)
        return None


class GreedyROIStrategy(Strategy):
    def decide(self, state: GameState) -> Action | None:
        if state.cps == 0:
            return None

        candidates = []

        for i, (_, bc, _) in enumerate(BUILDINGS):
            cost = building_cost(bc, state.owned[i])
            action = Action("building", i, cost)
            delta = _cps_delta(state, action)
            if delta > 0:
                payback = max(0, (cost - state.cookies) / state.cps) + cost / delta #time to afford + time to ROI
                candidates.append((payback, action))

        for cost, utype, idx, _ in available_upgrades(state.owned, state.tier_upgrades, state.grandma_synergy):
            action = Action(utype, idx, cost)
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
    load_dotenv()

    def __init__(self):
        self._client = OpenAI()
        self._tick = 0
        self._pending_buy: Action | None = None  # LLM said buy this; execute when affordable
        self._wait_until: int = -1               # tick at which wait expires (-1 = no timer)
        self._wait_for: str | None = None        # item name to auto-buy when affordable
        self.llm_calls: int = 0

    def _has_direction(self) -> bool:
        return self._pending_buy is not None or self._wait_for is not None or self._wait_until >= 0

    def decide(self, state: GameState) -> Action | None:
        self._tick += 1

        all_options = self._all_options(state)
        affordable = {n: a for n, a in all_options.items() if state.cookies >= a.cost}

        # Complete a wait_for direction once the item is affordable
        if self._wait_for and self._wait_for in affordable:
            action = affordable[self._wait_for]
            self._wait_for = None
            return action

        # Complete a pending buy direction once affordable
        if self._pending_buy and state.cookies >= self._pending_buy.cost:
            action = self._pending_buy
            self._pending_buy = None
            return action

        # Respect active wait_until — no interruption
        if self._wait_until >= 0:
            if self._tick < self._wait_until:
                return None
            self._wait_until = -1  # timer expired, fall through to consult LLM

        # Respect active wait_for — still saving up, no interruption
        if self._wait_for:
            return None

        # No direction from LLM; consult if something is affordable
        if not affordable:
            return None

        decision = self._call_llm(state, all_options)
        self._apply(decision, affordable, all_options)

        # If the decision is immediately actionable, execute now
        if self._pending_buy and state.cookies >= self._pending_buy.cost:
            action = self._pending_buy
            self._pending_buy = None
            return action

        return None

    def _all_options(self, state: GameState) -> dict[str, Action]:
        result = {}
        for i, (name, bc, _) in enumerate(BUILDINGS):
            result[name] = Action("building", i, building_cost(bc, state.owned[i]))
        for cost, utype, idx, uname in available_upgrades(state.owned, state.tier_upgrades, state.grandma_synergy):
            result[uname] = Action(utype, idx, cost)
        return result

    def _call_llm(self, state: GameState, all_options: dict) -> _LLMDecision:
        lines = [
            f"Cookies: {state.cookies:.0f}",
            f"CpS: {state.cps:.2f}",
            "",
            "Buildings owned:",
        ]
        for i, (name, _, _) in enumerate(BUILDINGS):
            if state.owned[i] > 0:
                lines.append(f"  {name}: {state.owned[i]}")

        lines += ["", "Purchase options (AFFORDABLE marked):"]
        for name, action in all_options.items():
            delta = _cps_delta(state, action)
            affordable = state.cookies >= action.cost
            tag = " [AFFORDABLE]" if affordable else f" (need {action.cost - state.cookies:.0f} more)"
            lines.append(f"  {name}: cost={action.cost:.0f}, CpS gain={delta:.2f}{tag}")

        lines += [
            "",
            "Goal: Maximize CpS as efficiently as possible.",
            "Choose: buy an affordable item, or wait (specify item name or number of ticks).",
        ]

        response = self._client.beta.chat.completions.parse(
            model=self.MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are optimizing a Cookie Clicker game. Make purchase decisions to maximize cookies per second efficiently.",
                },
                {"role": "user", "content": "\n".join(lines)},
            ],
            response_format=_LLMDecision,
        )
        self.llm_calls += 1
        dec = response.choices[0].message.parsed
        print(f"  [LLM tick={self._tick} call={self.llm_calls}] {dec.action} -> {dec.target} | {dec.reasoning}")
        return dec

    def _apply(self, decision: _LLMDecision, affordable: dict, all_options: dict):
        if decision.action in ("buy_building", "buy_upgrade"):
            target = decision.target
            if target in affordable:
                self._pending_buy = affordable[target]
            elif target in all_options:
                self._wait_for = target  # not affordable yet; auto-buy when ready
        elif decision.action == "wait":
            target = decision.target
            if target.isdigit():
                self._wait_until = self._tick + int(target)
            elif target in all_options:
                self._wait_for = target
            else:
                self._wait_until = self._tick + 100  # fallback
