from abc import ABC, abstractmethod

from game.engine import compute_building_cps
from game.models import GameState, Action


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
