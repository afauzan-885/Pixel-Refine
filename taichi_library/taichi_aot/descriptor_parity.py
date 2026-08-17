"""Bounded, semantic CPU contracts for binary descriptor matching.

This module intentionally does not call an AOT graph and does not register an
automatic block adapter.  It provides a deterministic reference for the small
fixed-cardinality part of a feature pipeline: pairwise Hamming distance and
nearest-neighbour selection.  AKAZE/OFB descriptor extraction and
variable-cardinality output remain full-frame/fail-closed.  Ratio and
cross-check helpers below are fixed-capacity semantic references: every query
row produces one slot and a rejected match is represented by ``-1``.
"""

from __future__ import annotations

from typing import Any

import numpy as np


def _descriptor_matrix(value: Any, name: str) -> np.ndarray:
    """Validate and normalize a descriptor matrix without changing bits."""

    array = np.asarray(value)
    if array.ndim != 2 or array.shape[1] <= 0:
        raise ValueError(f"{name} must be a non-empty 2D descriptor matrix")
    if array.shape[0] <= 0:
        raise ValueError(f"{name} must contain at least one descriptor")
    if array.dtype.kind not in "ui":
        raise TypeError(f"{name} must use an unsigned or signed integer dtype")
    # A descriptor is an opaque bit string.  Convert only to uint8 after
    # checking that the source range is representable; no float round-trip is
    # allowed.  This accepts u8/i8 and wider packed-word descriptors.
    if array.dtype.itemsize == 1:
        return np.ascontiguousarray(array.view(np.uint8))
    return np.ascontiguousarray(array).view(np.uint8).reshape(array.shape[0], -1)


def match_binary_descriptors_reference(
    query: Any,
    train: Any,
    *,
    block_rows: int | None = None,
) -> np.ndarray:
    """Return the deterministic nearest train index for each query row.

    Ties choose the first train descriptor (row-major ``argmin`` semantics).
    ``block_rows`` partitions only the query rows; train descriptors remain a
    shared read-only global domain.  Thus this helper is a semantic proof for
    fixed-capacity matching, not qualification of AKAZE/OFB ratio matching.
    """

    queries = _descriptor_matrix(query, "query")
    trains = _descriptor_matrix(train, "train")
    if queries.shape[1] != trains.shape[1]:
        raise ValueError("query and train descriptor widths must match")
    if block_rows is None:
        block_rows = queries.shape[0]
    block_rows = int(block_rows)
    if block_rows <= 0:
        raise ValueError("block_rows must be positive")

    output = np.empty((queries.shape[0],), dtype=np.int32)
    for start in range(0, queries.shape[0], block_rows):
        stop = min(start + block_rows, queries.shape[0])
        # XOR in uint8 prevents signed overflow.  The lookup table gives a
        # stable popcount for every byte and is independent of host word size.
        xor = np.bitwise_xor(queries[start:stop, None, :], trains[None, :, :])
        distances = _POPCOUNT[xor].sum(axis=2, dtype=np.uint32)
        output[start:stop] = np.argmin(distances, axis=1).astype(np.int32)
    return output


def verify_binary_descriptor_partition_parity(
    query: Any,
    train: Any,
    *,
    block_rows: int = 32,
) -> dict[str, Any]:
    """Compare full and query-row-partitioned fixed-cardinality matching."""

    full = match_binary_descriptors_reference(query, train)
    tiled = match_binary_descriptors_reference(query, train, block_rows=block_rows)
    return {
        "operation": "binary_descriptor_nearest_match",
        "scope": "semantic_numpy_fixed_cardinality",
        "backend": "cpu",
        "query_shape": list(_descriptor_matrix(query, "query").shape),
        "train_shape": list(_descriptor_matrix(train, "train").shape),
        "block_rows": int(block_rows),
        "passed": bool(np.array_equal(full, tiled)),
        "max_abs_error": int(np.max(np.abs(full.astype(np.int64) - tiled.astype(np.int64))))
        if full.size
        else 0,
        "deterministic_merge": True,
        "native_runtime": False,
        "automatic_safe": False,
        "qualification": "candidate_only",
    }


def _nearest_two_binary_descriptors(
    query: np.ndarray,
    train: np.ndarray,
    *,
    block_rows: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return best index, best distance, and second distance per query row."""

    if int(block_rows) <= 0:
        raise ValueError("block_rows must be positive")
    if train.shape[0] < 2:
        raise ValueError("ratio matching requires at least two train descriptors")
    best_index = np.empty((query.shape[0],), dtype=np.int32)
    best_distance = np.empty((query.shape[0],), dtype=np.uint32)
    second_distance = np.empty((query.shape[0],), dtype=np.uint32)
    for start in range(0, query.shape[0], int(block_rows)):
        stop = min(start + int(block_rows), query.shape[0])
        xor = np.bitwise_xor(query[start:stop, None, :], train[None, :, :])
        distances = _POPCOUNT[xor].sum(axis=2, dtype=np.uint32)
        order = np.argsort(distances, axis=1, kind="stable")
        rows = np.arange(stop - start)
        best_index[start:stop] = order[:, 0].astype(np.int32)
        best_distance[start:stop] = distances[rows, order[:, 0]]
        second_distance[start:stop] = distances[rows, order[:, 1]]
    return best_index, best_distance, second_distance


def ratio_test_binary_descriptors_reference(
    query: Any,
    train: Any,
    *,
    ratio_threshold: float = 0.8,
    block_rows: int | None = None,
) -> dict[str, np.ndarray]:
    """Apply a deterministic Lowe ratio test with fixed-capacity output.

    ``indices`` has exactly one slot per query row and contains ``-1`` when
    the strict test ``best < ratio_threshold * second`` rejects the match.
    A strict comparison rejects a zero-distance tie instead of inventing
    confidence.  This is a CPU semantic reference only.
    """

    queries = _descriptor_matrix(query, "query")
    trains = _descriptor_matrix(train, "train")
    if queries.shape[1] != trains.shape[1]:
        raise ValueError("query and train descriptor widths must match")
    ratio = float(ratio_threshold)
    if not np.isfinite(ratio) or not 0.0 < ratio < 1.0:
        raise ValueError("ratio_threshold must be finite and strictly between 0 and 1")
    rows = queries.shape[0] if block_rows is None else int(block_rows)
    best, first, second = _nearest_two_binary_descriptors(
        queries, trains, block_rows=rows
    )
    accepted = first.astype(np.float64) < ratio * second.astype(np.float64)
    indices = np.where(accepted, best, np.int32(-1)).astype(np.int32)
    return {
        "indices": indices,
        "best_distance": first,
        "second_distance": second,
        "accepted": accepted.astype(bool),
    }


def cross_check_binary_descriptors_reference(
    query: Any,
    train: Any,
    *,
    block_rows: int | None = None,
) -> np.ndarray:
    """Return mutual-nearest matches, one fixed slot per query row."""

    queries = _descriptor_matrix(query, "query")
    trains = _descriptor_matrix(train, "train")
    if queries.shape[1] != trains.shape[1]:
        raise ValueError("query and train descriptor widths must match")
    rows = queries.shape[0] if block_rows is None else int(block_rows)
    forward = match_binary_descriptors_reference(queries, trains, block_rows=rows)
    reverse = match_binary_descriptors_reference(trains, queries, block_rows=rows)
    query_indices = np.arange(queries.shape[0], dtype=np.int32)
    mutual = (forward >= 0) & (reverse[forward] == query_indices)
    return np.where(mutual, forward, np.int32(-1)).astype(np.int32)


def ratio_cross_check_binary_descriptors_reference(
    query: Any,
    train: Any,
    *,
    ratio_threshold: float = 0.8,
    block_rows: int | None = None,
) -> np.ndarray:
    """Apply ratio filtering followed by deterministic mutual-nearest check."""

    queries = _descriptor_matrix(query, "query")
    trains = _descriptor_matrix(train, "train")
    if queries.shape[1] != trains.shape[1]:
        raise ValueError("query and train descriptor widths must match")
    rows = queries.shape[0] if block_rows is None else int(block_rows)
    ratio = ratio_test_binary_descriptors_reference(
        queries, trains, ratio_threshold=ratio_threshold, block_rows=rows
    )["indices"]
    reverse = match_binary_descriptors_reference(trains, queries, block_rows=rows)
    valid = ratio >= 0
    valid_indices = np.flatnonzero(valid)
    valid[valid_indices] = (
        reverse[ratio[valid_indices]] == valid_indices.astype(np.int32)
    )
    return np.where(valid, ratio, np.int32(-1)).astype(np.int32)


def verify_binary_descriptor_matching_partition_parity(
    query: Any,
    train: Any,
    *,
    ratio_threshold: float = 0.8,
    block_rows: int = 32,
) -> dict[str, Any]:
    """Verify full versus query-partitioned ratio/cross-check semantics."""

    if int(block_rows) <= 0:
        raise ValueError("block_rows must be positive")
    full_ratio = ratio_test_binary_descriptors_reference(
        query, train, ratio_threshold=ratio_threshold
    )
    tiled_ratio = ratio_test_binary_descriptors_reference(
        query, train, ratio_threshold=ratio_threshold, block_rows=block_rows
    )
    full_cross = cross_check_binary_descriptors_reference(query, train)
    tiled_cross = cross_check_binary_descriptors_reference(
        query, train, block_rows=block_rows
    )
    full_combined = ratio_cross_check_binary_descriptors_reference(
        query, train, ratio_threshold=ratio_threshold
    )
    tiled_combined = ratio_cross_check_binary_descriptors_reference(
        query, train, ratio_threshold=ratio_threshold, block_rows=block_rows
    )
    passed = all(
        np.array_equal(full_ratio[key], tiled_ratio[key])
        for key in ("indices", "best_distance", "second_distance", "accepted")
    ) and np.array_equal(full_cross, tiled_cross) and np.array_equal(
        full_combined, tiled_combined
    )
    errors = []
    for left, right in (
        (full_ratio["indices"], tiled_ratio["indices"]),
        (full_cross, tiled_cross),
        (full_combined, tiled_combined),
    ):
        errors.append(
            int(np.max(np.abs(left.astype(np.int64) - right.astype(np.int64))))
            if left.size
            else 0
        )
    return {
        "operation": "binary_descriptor_ratio_cross_check",
        "scope": "semantic_numpy_fixed_cardinality",
        "backend": "cpu",
        "query_shape": list(_descriptor_matrix(query, "query").shape),
        "train_shape": list(_descriptor_matrix(train, "train").shape),
        "block_rows": int(block_rows),
        "ratio_threshold": float(ratio_threshold),
        "passed": bool(passed),
        "max_abs_error": max(errors, default=0),
        "deterministic_merge": True,
        "native_runtime": False,
        "automatic_safe": False,
        "qualification": "candidate_only",
    }


_POPCOUNT = np.array([int(value).bit_count() for value in range(256)], dtype=np.uint8)


__all__ = [
    "match_binary_descriptors_reference",
    "verify_binary_descriptor_partition_parity",
    "ratio_test_binary_descriptors_reference",
    "cross_check_binary_descriptors_reference",
    "ratio_cross_check_binary_descriptors_reference",
    "verify_binary_descriptor_matching_partition_parity",
]
