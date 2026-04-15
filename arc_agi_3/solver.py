"""
ARC-AGI-3 Baseline Solver

Implements a collection of hand-coded transformation heuristics for ARC tasks.
Each heuristic attempts to explain the input→output mapping for all training
examples, then applies the same rule to predict test outputs.

This is a pure-Python baseline — no ML, no LLM calls, fully isolated from Elpida.
"""

import json
import os
import copy
import numpy as np
from typing import List, Optional, Tuple, Dict, Any

Grid = List[List[int]]

# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def grid_to_np(grid: Grid) -> np.ndarray:
    return np.array(grid, dtype=int)

def np_to_grid(arr: np.ndarray) -> Grid:
    return arr.tolist()

def grids_equal(a: Grid, b: Grid) -> bool:
    if len(a) != len(b):
        return False
    return all(
        len(ra) == len(rb) and all(ca == cb for ca, cb in zip(ra, rb))
        for ra, rb in zip(a, b)
    )

def grid_shape(g: Grid) -> Tuple[int, int]:
    return (len(g), len(g[0]) if g else 0)

def color_counts(g: Grid) -> Dict[int, int]:
    counts: Dict[int, int] = {}
    for row in g:
        for c in row:
            counts[c] = counts.get(c, 0) + 1
    return counts

def most_common_color(g: Grid) -> int:
    counts = color_counts(g)
    return max(counts, key=counts.get)

def background_color(g: Grid) -> int:
    """Most frequent color is usually background."""
    return most_common_color(g)

# ---------------------------------------------------------------------------
# Heuristic solvers — each returns Optional[Grid] for a test input,
# or None if the heuristic doesn't fit the training examples.
# ---------------------------------------------------------------------------

def try_identity(train: list, test_input: Grid) -> Optional[Grid]:
    """Output == input."""
    if all(grids_equal(ex["input"], ex["output"]) for ex in train):
        return copy.deepcopy(test_input)
    return None


def try_color_swap(train: list, test_input: Grid) -> Optional[Grid]:
    """Global color mapping (permutation)."""
    mapping = {}
    for ex in train:
        inp, out = ex["input"], ex["output"]
        if grid_shape(inp) != grid_shape(out):
            return None
        for ri, ro in zip(inp, out):
            for ci, co in zip(ri, ro):
                if ci in mapping:
                    if mapping[ci] != co:
                        return None
                else:
                    mapping[ci] = co
    # Apply mapping
    result = []
    for row in test_input:
        result.append([mapping.get(c, c) for c in row])
    return result


def try_rotation(train: list, test_input: Grid) -> Optional[Grid]:
    """Check if output is a rotation (90, 180, 270) of input."""
    arr_in = grid_to_np(train[0]["input"])
    arr_out = grid_to_np(train[0]["output"])
    for k in [1, 2, 3]:
        if np.array_equal(np.rot90(arr_in, k), arr_out):
            # Verify on all training examples
            if all(
                np.array_equal(
                    np.rot90(grid_to_np(ex["input"]), k),
                    grid_to_np(ex["output"])
                )
                for ex in train
            ):
                return np_to_grid(np.rot90(grid_to_np(test_input), k))
    return None


def try_flip(train: list, test_input: Grid) -> Optional[Grid]:
    """Check horizontal/vertical/both flips."""
    for flip_fn in [
        lambda a: np.flipud(a),
        lambda a: np.fliplr(a),
        lambda a: np.flipud(np.fliplr(a)),
        lambda a: a.T,
    ]:
        if all(
            np.array_equal(
                flip_fn(grid_to_np(ex["input"])),
                grid_to_np(ex["output"])
            )
            for ex in train
        ):
            return np_to_grid(flip_fn(grid_to_np(test_input)))
    return None


def try_tile(train: list, test_input: Grid) -> Optional[Grid]:
    """Output is input tiled NxM times."""
    for ex in train:
        inp_h, inp_w = grid_shape(ex["input"])
        out_h, out_w = grid_shape(ex["output"])
        if inp_h == 0 or inp_w == 0:
            return None
        if out_h % inp_h != 0 or out_w % inp_w != 0:
            return None
    # Determine tile factors from first example
    inp_h, inp_w = grid_shape(train[0]["input"])
    out_h, out_w = grid_shape(train[0]["output"])
    tile_h, tile_w = out_h // inp_h, out_w // inp_w
    # Verify
    for ex in train:
        inp = grid_to_np(ex["input"])
        expected = np.tile(inp, (tile_h, tile_w))
        if not np.array_equal(expected, grid_to_np(ex["output"])):
            return None
    return np_to_grid(np.tile(grid_to_np(test_input), (tile_h, tile_w)))


def try_scale(train: list, test_input: Grid) -> Optional[Grid]:
    """Output is input scaled by integer factor (each pixel → NxN block)."""
    for ex in train:
        ih, iw = grid_shape(ex["input"])
        oh, ow = grid_shape(ex["output"])
        if ih == 0 or iw == 0:
            return None
        if oh % ih != 0 or ow % iw != 0:
            return None
        sh, sw = oh // ih, ow // iw
        if sh != sw:
            return None
    # Determine scale from first example
    ih, iw = grid_shape(train[0]["input"])
    oh, ow = grid_shape(train[0]["output"])
    scale = oh // ih
    # Verify
    for ex in train:
        inp = grid_to_np(ex["input"])
        expected = np.repeat(np.repeat(inp, scale, axis=0), scale, axis=1)
        if not np.array_equal(expected, grid_to_np(ex["output"])):
            return None
    inp = grid_to_np(test_input)
    return np_to_grid(np.repeat(np.repeat(inp, scale, axis=0), scale, axis=1))


def try_crop_to_nonzero(train: list, test_input: Grid) -> Optional[Grid]:
    """Output is the bounding box of non-background pixels."""
    for ex in train:
        bg = background_color(ex["input"])
        inp = grid_to_np(ex["input"])
        mask = inp != bg
        if not mask.any():
            return None
        rows = np.any(mask, axis=1)
        cols = np.any(mask, axis=0)
        r0, r1 = np.where(rows)[0][[0, -1]]
        c0, c1 = np.where(cols)[0][[0, -1]]
        cropped = inp[r0:r1+1, c0:c1+1]
        if not np.array_equal(cropped, grid_to_np(ex["output"])):
            return None
    bg = background_color(test_input)
    inp = grid_to_np(test_input)
    mask = inp != bg
    if not mask.any():
        return None
    rows = np.any(mask, axis=1)
    cols = np.any(mask, axis=0)
    r0, r1 = np.where(rows)[0][[0, -1]]
    c0, c1 = np.where(cols)[0][[0, -1]]
    return np_to_grid(inp[r0:r1+1, c0:c1+1])


def try_fill_color(train: list, test_input: Grid) -> Optional[Grid]:
    """Output is uniform grid of a single color, same shape as input."""
    for ex in train:
        out = grid_to_np(ex["output"])
        if grid_shape(ex["input"]) != grid_shape(ex["output"]):
            return None
        if len(np.unique(out)) != 1:
            return None
    # Try to figure out which color: maybe the minority color in input
    target_colors = [grid_to_np(ex["output"]).flat[0] for ex in train]
    if len(set(target_colors)) != 1:
        return None
    c = target_colors[0]
    h, w = grid_shape(test_input)
    return np_to_grid(np.full((h, w), c, dtype=int))


def try_gravity_down(train: list, test_input: Grid) -> Optional[Grid]:
    """Non-background cells fall down (gravity)."""
    def apply_gravity(g: Grid) -> Grid:
        arr = grid_to_np(g)
        bg = 0  # assume 0 is background
        h, w = arr.shape
        result = np.full_like(arr, bg)
        for col in range(w):
            non_bg = arr[:, col][arr[:, col] != bg]
            if len(non_bg) > 0:
                result[h - len(non_bg):h, col] = non_bg
        return np_to_grid(result)

    if all(grids_equal(apply_gravity(ex["input"]), ex["output"]) for ex in train):
        return apply_gravity(test_input)
    return None


def try_replace_color_with_pattern(train: list, test_input: Grid) -> Optional[Grid]:
    """One specific color in input gets replaced by another color in output, rest unchanged."""
    if not train:
        return None
    inp0, out0 = grid_to_np(train[0]["input"]), grid_to_np(train[0]["output"])
    if inp0.shape != out0.shape:
        return None
    diff_mask = inp0 != out0
    if not diff_mask.any():
        return None
    # Find source→dest color mapping at changed positions
    src_colors = set(inp0[diff_mask].tolist())
    dst_colors = set(out0[diff_mask].tolist())
    if len(src_colors) != 1 or len(dst_colors) != 1:
        return None
    src_c, dst_c = src_colors.pop(), dst_colors.pop()
    # Verify on all examples
    for ex in train:
        inp, out = grid_to_np(ex["input"]), grid_to_np(ex["output"])
        if inp.shape != out.shape:
            return None
        expected = inp.copy()
        expected[expected == src_c] = dst_c
        if not np.array_equal(expected, out):
            return None
    result = grid_to_np(test_input).copy()
    result[result == src_c] = dst_c
    return np_to_grid(result)


def try_border(train: list, test_input: Grid) -> Optional[Grid]:
    """Output adds a 1-cell border of a specific color."""
    for ex in train:
        ih, iw = grid_shape(ex["input"])
        oh, ow = grid_shape(ex["output"])
        if oh != ih + 2 or ow != iw + 2:
            return None
    # Determine border color from first example
    out0 = grid_to_np(train[0]["output"])
    border_color = out0[0, 0]
    for ex in train:
        inp = grid_to_np(ex["input"])
        out = grid_to_np(ex["output"])
        oh, ow = out.shape
        # Check border cells are all border_color
        if not (
            np.all(out[0, :] == border_color) and
            np.all(out[-1, :] == border_color) and
            np.all(out[:, 0] == border_color) and
            np.all(out[:, -1] == border_color)
        ):
            return None
        # Check interior matches input
        if not np.array_equal(out[1:-1, 1:-1], inp):
            return None
    # Apply
    inp = grid_to_np(test_input)
    h, w = inp.shape
    result = np.full((h + 2, w + 2), border_color, dtype=int)
    result[1:-1, 1:-1] = inp
    return np_to_grid(result)


def try_self_product(train: list, test_input: Grid) -> Optional[Grid]:
    """
    Output is formed by replacing each non-zero cell with a copy of the input,
    and each zero cell with a zero block. (outer product / Kronecker-like)
    """
    for ex in train:
        inp = grid_to_np(ex["input"])
        out = grid_to_np(ex["output"])
        h, w = inp.shape
        oh, ow = out.shape
        if oh != h * h or ow != w * w:
            return None
        expected = np.zeros((h * h, w * w), dtype=int)
        for r in range(h):
            for c in range(w):
                if inp[r, c] != 0:
                    expected[r*h:(r+1)*h, c*w:(c+1)*w] = inp
        if not np.array_equal(expected, out):
            return None
    inp = grid_to_np(test_input)
    h, w = inp.shape
    result = np.zeros((h * h, w * w), dtype=int)
    for r in range(h):
        for c in range(w):
            if inp[r, c] != 0:
                result[r*h:(r+1)*h, c*w:(c+1)*w] = inp
    return np_to_grid(result)


# ---------------------------------------------------------------------------
# Solver — tries all heuristics in order
# ---------------------------------------------------------------------------

ALL_HEURISTICS = [
    ("identity", try_identity),
    ("color_swap", try_color_swap),
    ("rotation", try_rotation),
    ("flip", try_flip),
    ("tile", try_tile),
    ("scale", try_scale),
    ("crop_nonzero", try_crop_to_nonzero),
    ("fill_color", try_fill_color),
    ("gravity_down", try_gravity_down),
    ("replace_color", try_replace_color_with_pattern),
    ("border", try_border),
    ("self_product", try_self_product),
]


def solve_task(task: Dict[str, Any]) -> List[Optional[Grid]]:
    """
    Attempt to solve all test inputs for a task.
    Returns a list of predicted grids (or None for unsolved tests).
    """
    train = task["train"]
    predictions = []
    for test_ex in task["test"]:
        test_input = test_ex["input"]
        predicted = None
        for name, heuristic in ALL_HEURISTICS:
            try:
                result = heuristic(train, test_input)
                if result is not None:
                    predicted = result
                    break
            except Exception:
                continue
        predictions.append(predicted)
    return predictions
