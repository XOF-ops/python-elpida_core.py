"""
ARC-AGI-3 Evaluation Harness

Runs the solver against training/evaluation tasks and reports accuracy.
Completely isolated from Elpida — only touches files inside arc_agi_3/.
"""

import json
import os
import sys
import time
from pathlib import Path

# Ensure we import from our directory
sys.path.insert(0, str(Path(__file__).parent))
from solver import solve_task, grids_equal

DATA_DIR = Path(__file__).parent / "data" / "data"


def load_tasks(split: str) -> dict:
    """Load all tasks from a split (training / evaluation)."""
    folder = DATA_DIR / split
    tasks = {}
    for fname in sorted(os.listdir(folder)):
        if fname.endswith(".json"):
            with open(folder / fname) as f:
                tasks[fname.replace(".json", "")] = json.load(f)
    return tasks


def evaluate(split: str = "training", verbose: bool = True):
    tasks = load_tasks(split)
    total_tests = 0
    correct = 0
    solved_tasks = 0
    total_tasks = len(tasks)
    heuristic_hits = {}
    unsolved = []

    t0 = time.time()
    for task_id, task in tasks.items():
        predictions = solve_task(task)
        task_correct = True
        for i, pred in enumerate(predictions):
            total_tests += 1
            test_ex = task["test"][i]
            if "output" in test_ex and pred is not None:
                if grids_equal(pred, test_ex["output"]):
                    correct += 1
                else:
                    task_correct = False
            elif pred is None:
                task_correct = False
            else:
                # No ground truth available — can't score
                task_correct = False

        if task_correct and all(p is not None for p in predictions):
            solved_tasks += 1
        else:
            unsolved.append(task_id)

    elapsed = time.time() - t0

    print(f"\n{'='*60}")
    print(f"ARC-AGI Baseline Evaluation — {split}")
    print(f"{'='*60}")
    print(f"Tasks:      {total_tasks}")
    print(f"Tests:      {total_tests}")
    print(f"Correct:    {correct}/{total_tests} ({100*correct/max(total_tests,1):.1f}%)")
    print(f"Tasks fully solved: {solved_tasks}/{total_tasks} ({100*solved_tasks/max(total_tasks,1):.1f}%)")
    print(f"Time:       {elapsed:.2f}s")
    print(f"{'='*60}")

    if verbose and solved_tasks > 0:
        solved_ids = [tid for tid in tasks if tid not in unsolved]
        print(f"\nSolved tasks ({solved_tasks}):")
        for tid in solved_ids[:50]:
            print(f"  {tid}")
        if solved_tasks > 50:
            print(f"  ... and {solved_tasks - 50} more")

    return {
        "split": split,
        "total_tasks": total_tasks,
        "total_tests": total_tests,
        "correct": correct,
        "solved_tasks": solved_tasks,
        "accuracy_pct": 100 * correct / max(total_tests, 1),
        "elapsed_s": elapsed,
    }


def generate_submission(output_path: str = "submission.json"):
    """Generate a Kaggle submission file from evaluation set predictions."""
    tasks = load_tasks("evaluation")
    submission = {}
    for task_id, task in tasks.items():
        predictions = solve_task(task)
        task_preds = {}
        for i, pred in enumerate(predictions):
            if pred is None:
                # Fallback: return the input unchanged
                pred = task["test"][i]["input"]
            task_preds[str(i)] = pred
        submission[task_id] = task_preds

    out_path = Path(__file__).parent / output_path
    with open(out_path, "w") as f:
        json.dump(submission, f)
    print(f"Submission written to {out_path} ({len(submission)} tasks)")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "submit":
        generate_submission()
    else:
        split = sys.argv[1] if len(sys.argv) > 1 else "training"
        evaluate(split=split)
