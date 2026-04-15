#!/usr/bin/env python3
"""
ARC-AGI vs Elpida's Parliament
================================

Tests Elpida's actual LLM fleet (the same providers Parliament uses)
against the ARC-AGI abstract reasoning benchmark.

Each LLM node receives the same ARC task (train examples + test input)
and must predict the test output grid. We then compare:
  - Individual provider accuracy (who reasons best?)
  - Majority-vote ensemble (Parliament-style collective intelligence)
  - Heuristic baseline vs LLM reasoning

This is READ-ONLY on Elpida — imports LLMClient but writes nothing
to evolution memory, S3, or any Elpida state.
"""

import json
import os
import sys
import time
import re
import random
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from collections import Counter

# Add parent dir so we can import Elpida's LLMClient (read-only)
sys.path.insert(0, str(Path(__file__).parent.parent))
from llm_client import LLMClient

# Also import our heuristic baseline for comparison
sys.path.insert(0, str(Path(__file__).parent))
from solver import solve_task, grids_equal, Grid

DATA_DIR = Path(__file__).parent / "data" / "data"

# The Parliament nodes — same providers as Elpida's governance
PARLIAMENT_NODES = {
    "D0_VOID":       "claude",      # Domain 0 — the frozen origin
    "D1_OPENAI":     "openai",      # Domain 1 — transparency
    "D4_GEMINI":     "gemini",      # Domain 4 — process
    "D7_GROK":       "grok",        # Domain 7 — adaptive learning
    "D3_MISTRAL":    "mistral",     # Domain 3 — dialectical truth
    "D6_COHERE":     "cohere",      # Domain 6 — collective emergence
}

# Lighter/free providers for larger runs
LIGHT_NODES = {
    "OPENROUTER":    "openrouter",
    "GROQ":          "groq",
    "CEREBRAS":      "cerebras",
}


def grid_to_str(grid: Grid) -> str:
    """Compact string representation of a grid."""
    return "\n".join(" ".join(str(c) for c in row) for row in grid)


def build_arc_prompt(task: Dict, test_idx: int = 0) -> str:
    """
    Build a prompt that presents an ARC task to an LLM.
    Shows all training input/output pairs, then asks for the test output.
    """
    lines = [
        "You are solving an abstract visual reasoning puzzle.",
        "Each example shows an input grid and its corresponding output grid.",
        "Grids contain integers 0-9 representing colors (0 = black/background).",
        "Study the pattern in the examples, then predict the output for the test input.",
        "",
        "IMPORTANT: Reply with ONLY the output grid — one row per line,",
        "space-separated integers. No explanation, no markdown, no extra text.",
        "",
    ]

    for i, ex in enumerate(task["train"]):
        lines.append(f"--- Example {i+1} ---")
        lines.append(f"Input ({len(ex['input'])}x{len(ex['input'][0])}):")
        lines.append(grid_to_str(ex["input"]))
        lines.append(f"Output ({len(ex['output'])}x{len(ex['output'][0])}):")
        lines.append(grid_to_str(ex["output"]))
        lines.append("")

    test_input = task["test"][test_idx]["input"]
    lines.append("--- Test ---")
    lines.append(f"Input ({len(test_input)}x{len(test_input[0])}):")
    lines.append(grid_to_str(test_input))
    lines.append("")
    lines.append("Output:")

    return "\n".join(lines)


def parse_grid_response(text: str) -> Optional[Grid]:
    """
    Parse an LLM response into a grid. Handles messy outputs.
    """
    if not text:
        return None

    # Strip markdown code blocks if present
    text = re.sub(r"```[\w]*\n?", "", text)
    text = text.strip()

    # Try to find grid-like content: lines of space/comma-separated integers
    grid = []
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        # Extract numbers from the line
        nums = re.findall(r"\d+", line)
        if nums:
            row = [int(n) for n in nums]
            # Sanity: skip lines that are just a single number (might be commentary)
            if len(row) >= 1:
                grid.append(row)

    if not grid:
        return None

    # Verify all rows have the same length
    widths = set(len(r) for r in grid)
    if len(widths) != 1:
        # Try to salvage by taking the most common width
        target_w = Counter(len(r) for r in grid).most_common(1)[0][0]
        grid = [r for r in grid if len(r) == target_w]
        if not grid:
            return None

    return grid


def load_tasks(split: str) -> Dict[str, Dict]:
    folder = DATA_DIR / split
    tasks = {}
    for fname in sorted(os.listdir(folder)):
        if fname.endswith(".json"):
            with open(folder / fname) as f:
                tasks[fname.replace(".json", "")] = json.load(f)
    return tasks


def run_parliament_on_task(
    client: LLMClient,
    task: Dict,
    nodes: Dict[str, str],
    test_idx: int = 0,
    max_tokens: int = 1200,
) -> Dict[str, Any]:
    """
    Send one ARC task to all Parliament nodes and collect predictions.
    """
    prompt = build_arc_prompt(task, test_idx)
    results = {}

    for node_name, provider in nodes.items():
        t0 = time.time()
        try:
            raw = client.call(
                provider,
                prompt,
                max_tokens=max_tokens,
                system_prompt="You are an expert at abstract pattern recognition and grid transformations. Output ONLY the grid, nothing else.",
            )
            elapsed = time.time() - t0
            predicted = parse_grid_response(raw) if raw else None
            results[node_name] = {
                "provider": provider,
                "prediction": predicted,
                "raw": (raw or "")[:500],
                "time_s": round(elapsed, 2),
                "success": predicted is not None,
            }
        except Exception as e:
            results[node_name] = {
                "provider": provider,
                "prediction": None,
                "raw": str(e)[:200],
                "time_s": round(time.time() - t0, 2),
                "success": False,
            }

    return results


def majority_vote(predictions: List[Optional[Grid]]) -> Optional[Grid]:
    """
    Parliament-style majority vote: pick the most common prediction.
    """
    valid = [json.dumps(p) for p in predictions if p is not None]
    if not valid:
        return None
    most_common = Counter(valid).most_common(1)[0][0]
    return json.loads(most_common)


def run_benchmark(
    n_tasks: int = 10,
    split: str = "training",
    use_parliament: bool = True,
    use_light: bool = False,
    seed: int = 42,
):
    """
    Run the ARC benchmark against Elpida's LLM fleet.

    Args:
        n_tasks: How many tasks to test (random sample)
        split: "training" or "evaluation"
        use_parliament: Use the 6 main Parliament nodes
        use_light: Also include lighter/free providers
        seed: Random seed for task selection
    """
    print(f"\n{'='*65}")
    print(f"  ARC-AGI  vs  ELPIDA'S PARLIAMENT")
    print(f"  Split: {split} | Tasks: {n_tasks} | Seed: {seed}")
    print(f"{'='*65}\n")

    tasks = load_tasks(split)
    task_ids = sorted(tasks.keys())

    random.seed(seed)
    sample_ids = random.sample(task_ids, min(n_tasks, len(task_ids)))

    client = LLMClient(rate_limit_seconds=1.0, default_max_tokens=1200)

    nodes = {}
    if use_parliament:
        nodes.update(PARLIAMENT_NODES)
    if use_light:
        nodes.update(LIGHT_NODES)

    print(f"Nodes: {', '.join(f'{k}({v})' for k, v in nodes.items())}")
    print(f"Heuristic baseline also running for comparison.\n")

    # Score tracking
    provider_correct = {name: 0 for name in nodes}
    provider_total = {name: 0 for name in nodes}
    heuristic_correct = 0
    ensemble_correct = 0
    total_tests = 0

    all_results = []

    for i, task_id in enumerate(sample_ids):
        task = tasks[task_id]
        n_tests = len(task["test"])

        for test_idx in range(n_tests):
            total_tests += 1
            test_ex = task["test"][test_idx]
            has_gt = "output" in test_ex
            gt = test_ex.get("output")

            print(f"[{i+1}/{len(sample_ids)}] Task {task_id} test {test_idx}", end="")

            # Heuristic baseline
            heur_preds = solve_task(task)
            heur_pred = heur_preds[test_idx] if test_idx < len(heur_preds) else None
            heur_ok = has_gt and heur_pred is not None and grids_equal(heur_pred, gt)
            if heur_ok:
                heuristic_correct += 1

            # Parliament LLMs
            node_results = run_parliament_on_task(client, task, nodes, test_idx)

            predictions = []
            for node_name, res in node_results.items():
                provider_total[node_name] += 1
                pred = res["prediction"]
                predictions.append(pred)
                if has_gt and pred is not None and grids_equal(pred, gt):
                    provider_correct[node_name] += 1
                    res["correct"] = True
                else:
                    res["correct"] = False

            # Ensemble (majority vote)
            ensemble_pred = majority_vote(predictions)
            ensemble_ok = has_gt and ensemble_pred is not None and grids_equal(ensemble_pred, gt)
            if ensemble_ok:
                ensemble_correct += 1

            # Status line
            node_marks = "".join(
                "✓" if node_results[n]["correct"] else ("✗" if node_results[n]["success"] else "—")
                for n in nodes
            )
            h_mark = "✓" if heur_ok else "✗"
            e_mark = "✓" if ensemble_ok else "✗"
            print(f"  H:{h_mark} LLMs:[{node_marks}] Vote:{e_mark}")

            all_results.append({
                "task_id": task_id,
                "test_idx": test_idx,
                "heuristic_correct": heur_ok,
                "ensemble_correct": ensemble_ok,
                "nodes": node_results,
            })

    # ---- Summary ----
    print(f"\n{'='*65}")
    print(f"  RESULTS — {total_tests} test grids across {len(sample_ids)} tasks")
    print(f"{'='*65}")
    print(f"\n  {'Method':<25} {'Correct':>8} {'Accuracy':>10}")
    print(f"  {'-'*45}")
    print(f"  {'Heuristic baseline':<25} {heuristic_correct:>5}/{total_tests:<3} {100*heuristic_correct/max(total_tests,1):>8.1f}%")
    for node_name in nodes:
        c = provider_correct[node_name]
        t = provider_total[node_name]
        prov = nodes[node_name]
        print(f"  {node_name:<25} {c:>5}/{t:<3} {100*c/max(t,1):>8.1f}%")
    print(f"  {'Ensemble (majority)':<25} {ensemble_correct:>5}/{total_tests:<3} {100*ensemble_correct/max(total_tests,1):>8.1f}%")
    print(f"{'='*65}")

    # Cost report
    print(f"\n  LLM cost report:")
    total_cost = 0
    for prov_name, stats in client.stats.items():
        if stats.requests > 0:
            print(f"    {prov_name:<15} {stats.requests} calls, {stats.tokens} tokens, ${stats.cost:.4f}")
            total_cost += stats.cost
    print(f"    {'TOTAL':<15} ${total_cost:.4f}")

    # Save results
    out_path = Path(__file__).parent / "parliament_vs_arc_results.json"
    with open(out_path, "w") as f:
        json.dump({
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "split": split,
            "n_tasks": len(sample_ids),
            "total_tests": total_tests,
            "heuristic_correct": heuristic_correct,
            "ensemble_correct": ensemble_correct,
            "provider_correct": provider_correct,
            "provider_total": provider_total,
            "details": all_results,
        }, f, indent=2)
    print(f"\n  Full results saved to {out_path}")

    return all_results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="ARC-AGI vs Elpida Parliament")
    parser.add_argument("-n", "--tasks", type=int, default=5, help="Number of tasks to test")
    parser.add_argument("--split", default="training", choices=["training", "evaluation"])
    parser.add_argument("--light", action="store_true", help="Include light/free providers")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    run_benchmark(
        n_tasks=args.tasks,
        split=args.split,
        use_parliament=True,
        use_light=args.light,
        seed=args.seed,
    )
