import time

from engine import BUILDINGS, GameState, compute_building_cps, load_state, save_state
from strategies import CheapestStrategy, GreedyROIStrategy, LLMStrategy, Strategy, LLMPlannerStrategy


def print_report(time_series, owned, tier_upgrades, grandma_synergy, total_baked, purchase_ticks, purchased_upgrades, llm_calls=None, elapsed=None):
    print("\n--- Time Series (every 100 ticks) ---")
    print(f"{'Tick':>6} | {'CpS':>12} | {'Bank':>14} | {'Total Baked':>16}")
    print("-" * 58)
    for entry in time_series:
        print(f"{entry['tick']:>6} | {entry['cps']:>12.2f} | {entry['bank']:>14.2f} | {entry['total_baked']:>16.0f}")

    contribs, final_cps = compute_building_cps(owned, tier_upgrades, grandma_synergy)
    total_purchases = len(purchase_ticks)
    avg_gap = (purchase_ticks[-1] - purchase_ticks[0]) / (total_purchases - 1) if total_purchases > 1 else 0.0

    print("\n--- End-of-Run Summary ---")
    print(f"Final CpS:          {final_cps:>16.2f}")
    print(f"Total cookies baked:{total_baked:>16.0f}")
    print(f"Total purchases:    {total_purchases:>16}")
    print(f"Upgrades purchased: {len(purchased_upgrades):>16}")
    print(f"Avg ticks between purchases: {avg_gap:>8.1f}")
    if llm_calls is not None:
        print(f"LLM calls:          {llm_calls:>16}")
    if elapsed is not None:
        print(f"Real time:          {elapsed:>13.1f}s")
    if purchased_upgrades:
        print("\nUpgrades purchased:")
        for u in purchased_upgrades:
            print(f"  {u}")
    print("\nBuildings owned & CpS share:")
    for i, (name, _, _) in enumerate(BUILDINGS):
        pct = (contribs[i] / final_cps * 100) if final_cps > 0 else 0.0
        print(f"  {name:<14} owned: {owned[i]:>4}   CpS share: {pct:>5.1f}%")


def run_simulation(strategy: Strategy, ticks=1000, resume_from: str | None = None, save_to: str | None = None):
    if resume_from:
        s = load_state(resume_from)
        owned = s.owned
        tier_upgrades = s.tier_upgrades
        grandma_synergy = s.grandma_synergy
        cookies = s.cookies
        total_baked = s.total_baked
    else:
        owned = [0] * 10
        owned[0] = 1  # start with 1 cursor
        tier_upgrades = [0] * 10
        grandma_synergy = {}
        cookies = 0.0
        total_baked = 0.0

    start = time.time()
    time_series = []
    purchase_ticks = []
    purchased_upgrades = []

    for tick in range(1, ticks + 1):
        _, cps = compute_building_cps(owned, tier_upgrades, grandma_synergy)
        cookies += cps
        total_baked += cps

        state = GameState(cookies, owned, tier_upgrades, grandma_synergy, cps, total_baked)
        action = strategy.decide(state)
        if action:
            cookies -= action.cost
            if action.kind == "building":
                owned[action.idx] += 1
            elif action.kind == "tier":
                tier_upgrades[action.idx] += 1
                purchased_upgrades.append(action.name)
            elif action.kind == "grandma_synergy":
                grandma_synergy[action.idx] = True
                purchased_upgrades.append(action.name)
            purchase_ticks.append(tick)

        if tick % 100 == 0:
            time_series.append({
                "tick": tick,
                "cps": compute_building_cps(owned, tier_upgrades, grandma_synergy)[1],
                "bank": cookies,
                "total_baked": total_baked,
            })

    elapsed = time.time() - start
    llm_calls = getattr(strategy, "llm_calls", None)
    print_report(time_series, owned, tier_upgrades, grandma_synergy, total_baked, purchase_ticks, purchased_upgrades, llm_calls, elapsed)
    if save_to:
        _, cps = compute_building_cps(owned, tier_upgrades, grandma_synergy)
        save_state(GameState(cookies, owned, tier_upgrades, grandma_synergy, cps, total_baked), save_to)
        print(f"State saved to {save_to}")


if __name__ == "__main__":
    # run_simulation(CheapestStrategy(), 5_000, "35k_greedy_roi.json", "40k_cheapest.json")
    # run_simulation(GreedyROIStrategy(), 5_000, "35k_greedy_roi.json", "36k_greedy_roi.json")
    run_simulation(LLMPlannerStrategy(sim_length=5000,plan_save_path="plan.json"), 5_000, "35k_greedy_roi.json", "40k_llm_planner_v2.json")
