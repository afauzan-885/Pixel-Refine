"""Reusable FusionNet patch candidate processing."""

from .multi_patch import (
    CandidateOffset,
    CandidateSelection,
    CandidateTelemetry,
    candidate_offsets,
    candidate_flow_from_indices,
    gather_rank_candidate,
    iter_candidate_offsets,
    normalize_weighted_accumulator,
    patch_distance_map,
    search_candidate_offsets,
    select_topk_candidates,
    shifted_candidate_view,
    validity_mask,
)

__all__ = [
    "CandidateOffset",
    "CandidateSelection",
    "CandidateTelemetry",
    "candidate_offsets",
    "candidate_flow_from_indices",
    "gather_rank_candidate",
    "iter_candidate_offsets",
    "normalize_weighted_accumulator",
    "patch_distance_map",
    "search_candidate_offsets",
    "select_topk_candidates",
    "shifted_candidate_view",
    "validity_mask",
]
