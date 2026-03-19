import json
from typing import Literal

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

from game.config import BUILDINGS, TIER_SCHEDULE
from game.engine import building_cost, available_upgrades
from game.models import GameState, Action
from strategies.base import Strategy, _cps_delta

_BUILDING_INDEX = {name: i for i, (name, _, _) in enumerate(BUILDINGS)}


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

        if new_upgrades and not new_upgrades.issubset({p.target for p in self._plan}):
            self._plan = []

        while self._plan:
            if self._resolve(self._plan[0], state) is not None:
                break
            if self._is_already_purchased(self._plan[0], state):
                self._plan.pop(0)
            else:
                self._plan = []
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

        return None

    def _resolve(self, purchase: PlannedPurchase, state: GameState) -> Action | None:
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
                    "- Plan purchases in execution order — prerequisites must appear before what they unlock\n"
                    "- Plan purchases that may require saving — the engine will wait and buy them in order.\n"
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
