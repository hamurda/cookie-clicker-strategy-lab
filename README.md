# cookie-clicker-strategy-lab

A Cookie Clicker simulation engine in Python that compares three purchase strategies: Buy Cheapest (baseline), Greedy ROI (algorithmic), and LLM Planner (GPT-5-mini). All running from the same mid-game starting state for 5,000 ticks.

## How to run

```bash
uv sync
cp .env.example .env                  # add your OPENAI_API_KEY
uv run main.py run greedy             # or: cheapest, llm
uv run main.py visualize              # regenerate charts
```

## Results

5,000-tick run from the same mid-game checkpoint (tick 35,000):

| Strategy     | Final CpS  | Purchases | Upgrades | LLM Calls |
|--------------|------------|-----------|----------|-----------|
| Greedy ROI   | 8,771,218  | 27        | 0        | 0         |
| LLM Planner  | 8,314,442  | 42        | 1        | 5         |
| Buy Cheapest | 7,573,220  | 177       | 2        | 0         |

![CpS over time](results/chart_cps_over_time.png)

## What I learned

The time-to-ROI formula beats the LLM not because it's smarter, but because it's perfectly consistent. It makes the same calculation every tick with no overhead or variance. The LLM Planner reaches 95% of optimal performance on just 5 API calls, but with no mechanism to course-correct between plans, small misjudgments compound.
