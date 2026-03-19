
## 1. What We Are Building
 
A simplified but faithful Cookie Clicker simulation engine in Python.
 
---
 
## 2. Buildings
 
10 buildings, using real Cookie Clicker numbers. Cost scaling: each purchase of the same building type multiplies the cost by **1.15** (15% increase per unit owned).
 
**Price formula:** `base_cost * 1.15 ^ units_owned` (rounded up to nearest integer)
 
| # | Building | Base Cost | Base CpS |
|---|----------|-----------|----------|
| 0 | Cursor | 15 | 0.1 |
| 1 | Grandma | 100 | 1 |
| 2 | Farm | 1,100 | 8 |
| 3 | Mine | 12,000 | 47 |
| 4 | Factory | 130,000 | 260 |
| 5 | Bank | 1,400,000 | 1,400 |
| 6 | Temple | 20,000,000 | 7,800 |
| 7 | Wizard Tower | 330,000,000 | 44,000 |
| 8 | Shipment | 5,100,000,000 | 260,000 |
| 9 | Alchemy Lab | 75,000,000,000 | 1,600,000 |
 
**Starting state:** The game begins with 0 cookies, 0.1 CpS, and 1 Cursor already owned.
 
---
 
## 3. Upgrades
 
Each building has **tiered upgrades** that double that building's CpS output. These unlock when you own a certain number of that building type.
 
### Tiered Upgrade Schedule
 
Each building gets upgrades at these ownership thresholds. The upgrade cost is calculated as `building_base_cost * tier_multiplier`.
 
| Tier | Unlock At (# owned) | Cost Multiplier (× base cost) | Effect |
|------|---------------------|-------------------------------|--------|
| 1 | 1 | 10 | Doubles building CpS |
| 2 | 5 | 50 | Doubles building CpS |
| 3 | 25 | 500 | Doubles building CpS |
| 4 | 50 | 5,000 | Doubles building CpS |
| 5 | 100 | 50,000 | Doubles building CpS |
| 6 | 150 | 5,000,000 | Doubles building CpS |
| 7 | 200 | 500,000,000 | Doubles building CpS |
 
**Example:** Grandma (base cost 100)
- Own 1 Grandma → unlock Tier 1 upgrade for 1,000 cookies → Grandma CpS goes from 1 to 2
- Own 5 Grandmas → unlock Tier 2 upgrade for 5,000 cookies → Grandma CpS goes from 2 to 4
- Own 25 Grandmas → unlock Tier 3 upgrade for 50,000 cookies → Grandma CpS goes from 4 to 8
- And so on...
 
**Important:** Upgrades stack multiplicatively. If you've bought Tier 1 and Tier 2, each building of that type produces `base_CpS * 2 * 2 = base_CpS * 4`.
 
### Grandma Synergy Upgrades
 
Each building type from Farm onward has an associated **Grandma type** upgrade. When unlocked, it doubles Grandma CpS AND adds a small percentage boost to the associated building based on grandma count.
 
| Building | Unlock Condition | Grandma Type | Effect |
|----------|-----------------|--------------|--------|
| Farm | Own 1 Farm + 1 Grandma | Farmer Grandma | Grandmas are twice as efficient; Farms gain +1% CpS per Grandma |
| Mine | Own 1 Mine + 1 Grandma | Miner Grandma | Grandmas are twice as efficient; Mines gain +0.5% CpS per Grandma (1 per 2 grandmas) |
| Factory | Own 1 Factory + 1 Grandma | Worker Grandma | Grandmas are twice as efficient; Factories gain +0.33% CpS per Grandma (1 per 3 grandmas) |
| Bank | Own 1 Bank + 1 Grandma | Banker Grandma | Grandmas are twice as efficient; Banks gain +0.25% CpS per Grandma (1 per 4 grandmas) |
| Temple | Own 1 Temple + 1 Grandma | Priestess Grandma | Grandmas are twice as efficient; Temples gain +0.2% CpS per Grandma (1 per 5 grandmas) |
| Wizard Tower | Own 1 WT + 1 Grandma | Witch Grandma | Grandmas are twice as efficient; Wizard Towers gain +0.167% CpS per Grandma (1 per 6 grandmas) |
| Shipment | Own 1 Ship + 1 Grandma | Cosmic Grandma | Grandmas are twice as efficient; Shipments gain +0.143% CpS per Grandma (1 per 7 grandmas) |
| Alchemy Lab | Own 1 AL + 1 Grandma | Transmuted Grandma | Grandmas are twice as efficient; Alchemy Labs gain +0.125% CpS per Grandma (1 per 8 grandmas) |
 
**Cost:** Each grandma type upgrade costs the same as the associated building's base cost × 6.

---
 
## 4. CpS Calculation
 
For each building type:
 
```
effective_cps_per_unit = base_cps × tier_multiplier × grandma_bonus
 
where:
  tier_multiplier = 2 ^ (number of tier upgrades purchased for this building)
  grandma_bonus = 1 + (num_grandmas × grandma_percentage) if grandma type upgrade purchased, else 1
 
total_cps = sum over all building types of (units_owned × effective_cps_per_unit)
```
 
---
 
## 5. Game Loop
 
```
Each tick = 1 second of simulated time
 
1. Add (current_CpS) cookies to bank
2. Add (current_CpS) to total_cookies_baked_all_time
3. Check for newly available upgrades (both tier and grandma type)
4. Strategy decides: buy a building, buy an upgrade, or wait
5. If buying: deduct cost from bank, update game state
6. Record metrics for this tick
7. Advance to next tick
```
 
**The strategy can only make ONE purchase per tick.** This prevents any strategy from doing instant multi-buys that would be unrealistic.
 
**Simulation length:** Configurable. Default runs:
- Short: 36,000 ticks (10 simulated hours)
- Long: 86,400 ticks (24 simulated hours)
 
---
 
## 6. What the Strategies Need to Decide
 
At each tick, the strategy receives the full game state and must return one of:
- `("buy_building", building_index)` — buy one unit of a building
- `("buy_upgrade", upgrade_id)` — buy an available upgrade
- `("wait", None)` — do nothing, save cookies
 
**Available information for each decision:**
- Current cookies in bank
- Current CpS
- For each building: count owned, current price, base CpS, effective CpS per unit
- For each available upgrade: cost, what it affects, expected CpS increase
- Total cookies baked all time
- Current tick number

---

## 7. Metrics to Track

### Time Series (sampled every 100 ticks)

- CpS — the main comparison curve
- Cookies in bank — shows saving vs spending behavior
- Total cookies baked all time — cumulative production

### End-of-Run Summary

- Final CpS
- Total cookies baked
- Number of each building type owned
- Number of upgrades purchased
- Cookies produced per building type (as percentage of total)
- Total purchases made
- Average time between purchases