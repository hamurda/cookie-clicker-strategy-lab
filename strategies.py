from abc import ABC, abstractmethod

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
