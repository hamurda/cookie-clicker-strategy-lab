# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

---

## Project Overview

This is a Cookie Clicker simulation engine in Python. All the details and mechanics for the simulation are provided in @COOKIE_CLICKER.md.

---

## Phase 1:
**Goal:** A single Python file that runs a Cookie Clicker simulation with a dumb "buy cheapest" strategy. Do not create folder structures, separate modules, or anything beyond what's needed to run the simulation with a basic buy-cheapest strategy. At the end of Phase 1, the simulation should print CpS and total cookies every 1000 ticks so we can verify the game logic is working.

### Strategy : "Buy Cheapest" (Baseline)
 
Always buys the cheapest available thing (building or upgrade) that you can currently afford. If nothing is affordable, wait. This is your sanity-check baseline — any smart strategy should beat this.

---

## Phase 2: Strategy Interface + Greedy Algorithm
**Goal:** Extract the decision-making into a clean interface. Implement the time-to-ROI strategy. Run both strategies and compare.

### Strategy: Greedy Time-to-ROI (Algorithmic)
 
For each available purchase (building or upgrade), calculate:
 
```
time_to_roi = cost / additional_cps_gained_per_second
```
 
Where `additional_cps_gained_per_second` is:
- For a building: the effective CpS per unit of that building type (with current upgrades)
- For an upgrade: the total CpS increase across all buildings of that type (since it doubles their output)
 
**Adjustment for saving time:** If you can't afford the purchase yet, add the wait time:
 
```
payback_time = max(0, (cost - current_cookies) / current_cps) + (cost / additional_cps)
```
 
Pick the purchase with the **lowest payback_time**. If payback_time for the best option means waiting, return `("wait", None)`.

---

## Phase 3: LLM Strategy
 
**Goal:** Add an LLM-based strategy that makes purchase decisions. Run all three strategies and comp

### Strategy 3: LLM Decision Maker
 
Sends the game state as a structured prompt to an LLM API. The prompt includes:
- Current game state (cookies, CpS, buildings owned, available purchases)
- The goal: "Maximize CpS as efficiently as possible"
- A request for the decision and brief reasoning
 
**Does NOT tell the LLM the time-to-ROI formula.** The LLM must figure out its own approach. This is the whole point of the comparison.
 
The LLM returns a structured decision (building/upgrade/wait). The game engine parses and executes it.
 
**Important:** The LLM won't be called every single tick — that would be thousands of API calls. Instead, call the LLM:
- When the strategy can afford at least one purchase, OR
- Every N ticks if nothing has been bought (to check if it wants to keep saving)
- Between LLM calls, the strategy defaults to "wait"

---

## Phase 4: Analysis & Cleanup (Session 4)
 
**Goal:** Generate comparison charts, clean up the codebase, write the README, organize for GitHub.

---

## Coding standards

1. Use latest versions of libraries and idiomatic approaches as of today
2. Keep it simple - NEVER over-engineer, ALWAYS simplify, NO unnecessary defensive programming. No extra features - focus on simplicity.
3. Be concise. Keep README minimal. IMPORTANT: no emojis ever
4. Use short, minimal comments only where needed.
5. Prefer uv over pip
6. We will build this incrementally.
7. If a design decision isn't covered in COOKIE-CLICKER.md, always ask before implementing.
