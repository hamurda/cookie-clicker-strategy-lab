from game.config import BUILDINGS
from game.engine import building_cost, available_upgrades
from game.models import GameState, Action
from strategies.base import Strategy, _cps_delta


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
        return best if state.cookies >= best.cost else None
