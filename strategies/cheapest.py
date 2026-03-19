from game.config import BUILDINGS
from game.engine import building_cost, available_upgrades
from game.models import GameState, Action
from strategies.base import Strategy


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
