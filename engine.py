import math
from dataclasses import dataclass

BUILDINGS = [
    ("Cursor",       15,             0.1),
    ("Grandma",      100,            1.0),
    ("Farm",         1_100,          8.0),
    ("Mine",         12_000,         47.0),
    ("Factory",      130_000,        260.0),
    ("Bank",         1_400_000,      1_400.0),
    ("Temple",       20_000_000,     7_800.0),
    ("Wizard Tower", 330_000_000,    44_000.0),
    ("Shipment",     5_100_000_000,  260_000.0),
    ("Alchemy Lab",  75_000_000_000, 1_600_000.0),
]

# (unlock_at_owned, cost_multiplier)
TIER_SCHEDULE = [
    (1,   10),
    (5,   50),
    (25,  500),
    (50,  5_000),
    (100, 50_000),
    (150, 5_000_000),
    (200, 500_000_000),
]

# building_index -> grandma CpS bonus per grandma owned
GRANDMA_SYNERGY_PCT = {
    2: 0.01,
    3: 0.005,
    4: 1 / 300,
    5: 0.0025,
    6: 0.002,
    7: 1 / 600,
    8: 1 / 700,
    9: 0.00125,
}


@dataclass
class GameState:
    cookies: float
    owned: list
    tier_upgrades: list
    grandma_synergy: dict
    cps: float


@dataclass
class Action:
    kind: str  # "building", "tier", "grandma_synergy"
    idx: int
    cost: int


def building_cost(base_cost, owned):
    return math.ceil(base_cost * (1.15 ** owned))


def compute_building_cps(owned, tier_upgrades, grandma_synergy):
    num_grandmas = owned[1]
    synergy_count = len(grandma_synergy)
    contribs = [0.0] * len(BUILDINGS)
    total = 0.0

    for i, (_, _, base_cps) in enumerate(BUILDINGS):
        if owned[i] == 0:
            continue
        tier_mult = 2 ** tier_upgrades[i]
        if i == 1:  # Grandma: boosted by each synergy upgrade purchased
            eff = base_cps * tier_mult * (2 ** synergy_count)
        elif i in GRANDMA_SYNERGY_PCT and grandma_synergy.get(i, False):
            grandma_bonus = 1 + num_grandmas * GRANDMA_SYNERGY_PCT[i]
            eff = base_cps * tier_mult * grandma_bonus
        else:
            eff = base_cps * tier_mult
        contribs[i] = owned[i] * eff
        total += owned[i] * eff

    return contribs, total


def available_upgrades(owned, tier_upgrades, grandma_synergy):
    upgrades = []

    for i, (name, base_cost, _) in enumerate(BUILDINGS):
        purchased = tier_upgrades[i]
        if purchased < len(TIER_SCHEDULE):
            unlock_at, cost_mult = TIER_SCHEDULE[purchased]
            if owned[i] >= unlock_at:
                cost = math.ceil(base_cost * cost_mult)
                upgrades.append((cost, "tier", i, f"{name} tier {purchased + 1}"))

        if i in GRANDMA_SYNERGY_PCT and not grandma_synergy.get(i, False):
            if owned[i] >= 1 and owned[1] >= 1:
                cost = math.ceil(base_cost * 6)
                upgrades.append((cost, "grandma_synergy", i, f"{name} grandma synergy"))

    return upgrades
