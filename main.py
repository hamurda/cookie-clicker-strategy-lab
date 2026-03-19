import argparse

from analysis.runner import run_simulation
from strategies.cheapest import CheapestStrategy
from strategies.greedy_roi import GreedyROIStrategy
from strategies.llm_planner import LLMPlannerStrategy

STRATEGIES = {
    "cheapest": lambda ticks: CheapestStrategy(),
    "greedy":   lambda ticks: GreedyROIStrategy(),
    "llm":      lambda ticks: LLMPlannerStrategy(sim_length=ticks, plan_save_path="results/plan.json"),
}

parser = argparse.ArgumentParser(description="Cookie Clicker simulation")
subparsers = parser.add_subparsers(dest="command", required=True)

sim = subparsers.add_parser("run", help="Run a simulation")
sim.add_argument("strategy", choices=STRATEGIES.keys(), help="Strategy to use")
sim.add_argument("--ticks", type=int, default=5_000, help="Number of ticks (default: 5000)")
sim.add_argument("--resume", default="results/starting_state.json", help="Starting state JSON")
sim.add_argument("--save", default=None, help="Path to save final state JSON")

subparsers.add_parser("visualize", help="Generate comparison charts into results/")

args = parser.parse_args()

if args.command == "run":
    strategy = STRATEGIES[args.strategy](args.ticks)
    run_simulation(strategy, args.ticks, resume_from=args.resume, save_to=args.save)

elif args.command == "visualize":
    import analysis.visualize  # runs on import
