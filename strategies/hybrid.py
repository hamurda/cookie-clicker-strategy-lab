from game.config import BUILDINGS
from game.engine import building_cost, available_upgrades
from game.models import GameState, Action
from strategies.base import Strategy, _cps_delta
from strategies.llm_planner import LLMPlannerStrategy


class HybridStrategy(Strategy):
    """LLM planner with greedy ROI fallback while saving for planned purchases."""

    def __init__(self, sim_length=1000, plan_save_path=None):
        self._llm = LLMPlannerStrategy(sim_length=sim_length, plan_save_path=plan_save_path)

    @property
    def llm_calls(self):
        return self._llm.llm_calls

    def decide(self, state: GameState) -> Action | None:
        action = self._llm.decide(state)
        if action is not None:
            return action

        # LLM is waiting — run greedy ROI, but protect cookies reserved for next planned item.
        next_cost = self._next_planned_cost(state)
        return self._greedy_decide(state, next_cost)

    def _next_planned_cost(self, state: GameState) -> float | None:
        if not self._llm._plan:
            return None
        resolved = self._llm._resolve(self._llm._plan[0], state)
        return resolved.cost if resolved is not None else None

    def _greedy_decide(self, state: GameState, reserved: float | None) -> Action | None:
        if state.cps == 0:
            return None

        candidates = []

        for i, (name, bc, _) in enumerate(BUILDINGS):
            cost = building_cost(bc, state.owned[i])
            action = Action("building", i, cost, name)
            delta = _cps_delta(state, action)
            if delta > 0:
                payback = max(0, (cost - state.cookies) / state.cps) + cost / delta
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

        if state.cookies < best.cost:
            return None

        # Skip if buying now would leave us unable to afford the next planned item.
        ticks_to_afford = max(0, (reserved - state.cookies) / state.cps) if state.cps > 0 else float('inf')
        if reserved is not None  and ticks_to_afford < 50 and  state.cookies - best.cost < reserved:
            return None

        return best
