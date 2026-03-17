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
**Goal:** Extract the decision-making into a clean interface. Implement the time-to-ROI strategy. At the end of Phase 2. the project should have the strategy, game-state and action abstracted. And the second strategy - greedy time-to-ROI should be implemented. 

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
 
**Goal:** Implement an LLM-based strategy that makes purchase decisions. After Phase 3, we should be able to compare all 3 strategies reliably with no issues. 

### Strategy 3: LLM Decision Maker

Uses OpenAI `gpt-5-mini`, uses structured output
Sends the game state as a structured prompt to an LLM API. The prompt includes:

- Current game state (cookies, CpS, buildings owned, available purchases)
- For each building type: how many owned, what the next one costs, what CpS it would add. 
- For each available upgrade: what it costs, what building it affects, what CpS increase it would produce. 
- The goal: "Maximize CpS as efficiently as possible"
- A request structured_output for the decision and brief reasoning. You can create a schema. Here I share an example:
    e.g. : Buy Decision: {"action": "buy_building", "target": "Factory", "reasoning": "..."} -> buy a factory now, then call LLM again if we can afford anything. 
           Wait Decision: {"action": "wait", "target": "200", "reasoning": "..."} -> 200 ticks to wait, call LLM after 200 ticks
           Wait Decision: {"action": "wait", "target": "Factory", "reasoning": "..."} -> wait until Factory is affordable, then buy Factory, then call LLM
 
**Does NOT tell the LLM the time-to-ROI formula.** The LLM must figure out its own approach. This is the whole point of the comparison.
 
The LLM returns a structured decision (building/upgrade/wait). The game engine parses and executes it.
 
**Important:** The LLM won't be called every single tick — that would be thousands of API calls. Instead, call the LLM:
1. Something becomes affordable → call LLM
2. LLM says buy → execute purchase → call LLM again immediately
3. LLM says wait N ticks → wait up to N ticks
4. Repeat
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
