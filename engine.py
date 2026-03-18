import json
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
    total_baked: float = 0.0


@dataclass
class Action:
    kind: str  # "building", "tier", "grandma_synergy"
    idx: int
    cost: int
    name: str = ""


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


_BUILDING_NAMES = [name for name, _, _ in BUILDINGS]
_BUILDING_INDEX = {name: i for i, (name, _, _) in enumerate(BUILDINGS)}


def save_state(state: "GameState", path: str):
    data = {
        "cookies": state.cookies,
        "total_baked": state.total_baked,
        "buildings": {_BUILDING_NAMES[i]: state.owned[i] for i in range(len(BUILDINGS))},
        "tier_upgrades": {_BUILDING_NAMES[i]: state.tier_upgrades[i] for i in range(len(BUILDINGS))},
        "grandma_synergy": [_BUILDING_NAMES[i] for i in state.grandma_synergy if state.grandma_synergy[i]],
    }
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def load_state(path: str) -> GameState:
    with open(path) as f:
        data = json.load(f)
    owned = [data["buildings"].get(name, 0) for name in _BUILDING_NAMES]
    tier_upgrades = [data["tier_upgrades"].get(name, 0) for name in _BUILDING_NAMES]
    grandma_synergy = {_BUILDING_INDEX[name]: True for name in data.get("grandma_synergy", [])}
    _, cps = compute_building_cps(owned, tier_upgrades, grandma_synergy)
    return GameState(
        cookies=data.get("cookies", 0.0),
        owned=owned,
        tier_upgrades=tier_upgrades,
        grandma_synergy=grandma_synergy,
        cps=cps,
        total_baked=data.get("total_baked", 0.0),
    )
