import math

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


def building_cost(base_cost, owned):
    return math.ceil(base_cost * (1.15 ** owned))


def compute_cps(owned, tier_upgrades, grandma_synergy):
    num_grandmas = owned[1]
    synergy_count = len(grandma_synergy)
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
        total += owned[i] * eff

    return total


def available_upgrades(owned, tier_upgrades, grandma_synergy):
    upgrades = []

    for i, (name, base_cost, _) in enumerate(BUILDINGS):
        # Next tier upgrade for this building
        purchased = tier_upgrades[i]
        if purchased < len(TIER_SCHEDULE):
            unlock_at, cost_mult = TIER_SCHEDULE[purchased]
            if owned[i] >= unlock_at:
                cost = math.ceil(base_cost * cost_mult)
                upgrades.append((cost, "tier", i, f"{name} tier {purchased + 1}"))

        # Grandma synergy upgrade
        if i in GRANDMA_SYNERGY_PCT and not grandma_synergy.get(i, False):
            if owned[i] >= 1 and owned[1] >= 1:
                cost = math.ceil(base_cost * 6)
                upgrades.append((cost, "grandma_synergy", i, f"{name} grandma synergy"))

    return upgrades


def greedy_cheapest(cookies, owned, tier_upgrades, grandma_synergy):
    options = [(building_cost(bc, owned[i]), "building", i) for i, (_, bc, _) in enumerate(BUILDINGS)]
    options += [(cost, utype, idx) for cost, utype, idx, _ in available_upgrades(owned, tier_upgrades, grandma_synergy)]
    options.sort(key=lambda x: x[0])

    for cost, otype, idx in options:
        if cookies >= cost:
            return (otype, idx, cost)
    return None


def run_simulation(ticks=1000):
    owned = [0] * 10
    owned[0] = 1  # start with 1 cursor
    tier_upgrades = [0] * 10
    grandma_synergy = {}

    cookies = 0.0
    total_baked = 0.0

    for tick in range(1, ticks + 1):
        cps = compute_cps(owned, tier_upgrades, grandma_synergy)
        cookies += cps
        total_baked += cps

        decision = greedy_cheapest(cookies, owned, tier_upgrades, grandma_synergy)
        if decision:
            otype, idx, cost = decision
            cookies -= cost
            if otype == "building":
                owned[idx] += 1
            elif otype == "tier":
                tier_upgrades[idx] += 1
            elif otype == "grandma_synergy":
                grandma_synergy[idx] = True

        if tick % 100 == 0:
            cps = compute_cps(owned, tier_upgrades, grandma_synergy)
            print(f"Tick {tick:5d} | CpS: {cps:>12.2f} | Total baked: {total_baked:>16.0f}")

if __name__ == "__main__":
    run_simulation(1000)
