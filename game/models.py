from dataclasses import dataclass


@dataclass
class GameState:
    cookies: float
    owned: list
    tier_upgrades: list
    grandma_synergy: dict
    cps: float
    total_baked: float = 0.0


@dataclass
class Action:
    kind: str  # "building", "tier", "grandma_synergy"
    idx: int
    cost: int
    name: str = ""
