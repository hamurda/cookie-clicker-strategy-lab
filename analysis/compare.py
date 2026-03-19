"""Print a side-by-side comparison of the three strategy runs."""


def print_comparison():
    results = [
        ("Greedy ROI",   8_771_218, 27,  0, 0),
        ("LLM Planner",  8_314_442, 42,  1, 5),
        ("Buy Cheapest", 7_573_220, 177, 2, 0),
    ]
    print(f"{'Strategy':<14} {'Final CpS':>12} {'Purchases':>10} {'Upgrades':>9} {'LLM Calls':>10}")
    print("-" * 60)
    for name, cps, purchases, upgrades, llm in results:
        print(f"{name:<14} {cps:>12,} {purchases:>10} {upgrades:>9} {llm:>10}")


if __name__ == "__main__":
    print_comparison()
