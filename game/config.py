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
