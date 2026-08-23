"""Canonical graph names for the demosaic AOT families.

The per-family compiler modules own kernel construction.  This module only
describes the graph names that those builders register and provides a small,
dependency-free selector API for callers.  Keeping the manifest separate
prevents wrapper code from re-creating (and eventually diverging from) the
builder's graph naming scheme.

``resolve_graph_name`` deliberately returns the *registered graph name*, not
an implementation function or a TCM path.  Backend selection and graph
execution remain responsibilities of the AOT runtime.
"""

from __future__ import annotations

from types import MappingProxyType
from typing import Mapping
from .demosaic_runtime import DemosaicGraphSpec


# The keys are the canonical selector names accepted by this module.  The
# values are the exact names passed to ``module.add_graph`` in the builder.
# Keep variants descriptive and stable; aliases are handled separately below.
_MANIFEST: dict[str, dict[str, str]] = {
    "bilinear": {
        "default": "bilinear_demosaice",
        "pure": "pure_bilinear_demosaice",
        "1channel": "bilinear_demosaice_1channel",
        "half_res": "bilinear_demosaice_half_res",
        "rgb_half_res": "bilinear_demosaice_rgb_half_res",
        "rgb_to_bgr_i32": "rgb_to_bgr_i32",
    },
    "hamilton": {
        "default": "hamilton_demosaic",
        "tonemapped": "hamilton_demosaic_tonemapped",
        "1channel": "hamilton_demosaic_1channel",
        "half_res": "hamilton_demosaic_half_res",
        "rgb_half_res": "hamilton_demosaic_rgb_half_res",
        "3channel": "hamilton_demosaic_3channel",
        "rgb_to_bgr_i32": "rgb_to_bgr_i32",
    },
    "dcb": {
        "default": "dcb_demosaic",
        "headroom": "dcb_demosaic_headroom",
        "tonemapped": "dcb_demosaic_tonemapped",
        "highlight_ratio_seed": "dcb_highlight_ratio_seed",
        "highlight_ratio_propagate": "dcb_highlight_ratio_propagate",
        "highlight_apply": "dcb_highlight_apply",
        "copy_rgb": "dcb_copy_rgb",
        "1channel": "dcb_demosaic_1channel",
        "rgb_half_res": "dcb_demosaic_rgb_half_res",
        "half_res": "dcb_demosaic_half_res",
        "rgb_to_luma": "dcb_rgb_to_luma",
    },
    "arm": {
        "default": "arm_demosaic",
        "tonemapped": "arm_demosaic_tonemapped",
        "pure": "pure_arm_demosaic",
        "1channel": "arm_demosaic_1channel",
        "half_res": "arm_demosaic_half_res",
        "rgb_half_res": "arm_demosaic_rgb_half_res",
        "rgb_to_bgr_i32": "rgb_to_bgr_i32",
    },
    "mlri": {
        "default": "mlri_admm_demosaic",
        "tonemapped": "mlri_admm_demosaic_tonemapped",
        "1channel": "mlri_admm_demosaic_1channel",
        "half_res": "mlri_admm_demosaic_half_res",
        "rgb_half_res": "mlri_admm_demosaic_rgb_half_res",
        "3channel": "mlri_admm_demosaic_3channel",
    },
}


# A read-only public view prevents accidental mutation by callers while still
# making the canonical mapping easy to inspect in diagnostics and tests.
GRAPH_MANIFEST: Mapping[str, Mapping[str, str]] = MappingProxyType(
    {family: MappingProxyType(variants) for family, variants in _MANIFEST.items()}
)


_FAMILY_METADATA = {
    "bilinear": {
        "required_inputs": ("bayer", "cmatrix", "dst"),
        "scratch_buffers": (),
        "stages": ("bayer_normalize", "bilinear_interpolate", "white_balance", "color_matrix"),
    },
    "hamilton": {
        "required_inputs": ("bayer", "green", "dst"),
        "scratch_buffers": ("green",),
        "stages": ("green_edge_directed", "red_blue_reconstruct"),
    },
    "dcb": {
        "required_inputs": ("bayer", "mosaic", "green", "rgb_a", "rgb_b", "dst"),
        "scratch_buffers": ("mosaic", "green", "rgb_a", "rgb_b"),
        "stages": ("preprocess", "green", "initial_rgb", "chroma_refine", "copy_rgb"),
    },
    "arm": {
        "required_inputs": ("bayer", "wb_bayer", "green", "r_diff", "b_diff", "r_diff_filtered", "b_diff_filtered", "cmatrix", "dst"),
        "scratch_buffers": ("wb_bayer", "green", "r_diff", "b_diff", "r_diff_filtered", "b_diff_filtered"),
        "stages": ("preprocess", "green", "residual", "median", "reconstruct"),
    },
    "mlri": {
        "required_inputs": ("bayer", "wb_bayer", "green", "r_diff", "b_diff", "temp_a", "temp_b", "dst"),
        "scratch_buffers": ("wb_bayer", "green", "r_diff", "b_diff", "temp_a", "temp_b"),
        "stages": ("preprocess", "denoise", "green_diff", "guided_filter", "admm", "reconstruct"),
    },
}


FAMILY_ALIASES: Mapping[str, str] = MappingProxyType(
    {
        "bilinear_demosaice": "bilinear",
        "hamilton_adams": "hamilton",
        "hamilton_demosaice": "hamilton",
        "arm_demosaice": "arm",
        "dcb_demosaice": "dcb",
        "mlri_admm": "mlri",
        "mlri_admm_demosaice": "mlri",
    }
)


VARIANT_ALIASES: Mapping[str, str] = MappingProxyType(
    {
        "": "default",
        "linear": "default",
        "fused": "default",
        "tone_map": "tonemapped",
        "tone_mapped": "tonemapped",
        "tone-mapped": "tonemapped",
        "rgb-half-res": "rgb_half_res",
        "half-resolution": "half_res",
    }
)


def _normalize_token(value: str, *, label: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{label} must be a string, got {type(value).__name__}")
    token = value.strip().lower().replace(" ", "_")
    if not token:
        raise ValueError(f"{label} must not be empty")
    return token


def _canonical_family(family: str) -> str:
    token = _normalize_token(family, label="family")
    token = FAMILY_ALIASES.get(token, token)
    if token not in GRAPH_MANIFEST:
        available = ", ".join(sorted(GRAPH_MANIFEST))
        raise ValueError(f"Unknown demosaic family {family!r}; available families: {available}")
    return token


def _canonical_variant(variant: str | None) -> str:
    if variant is None:
        return "default"
    token = _normalize_token(variant, label="variant")
    return VARIANT_ALIASES.get(token, token)


def resolve_graph_name(family: str, variant: str | None = None) -> str:
    """Resolve a family/variant selector to a registered graph name.

    ``variant=None`` selects the family's canonical default graph.  Errors
    include the available variants, which makes stale wrapper selectors easy
    to diagnose without inspecting a compiled TCM.
    """

    canonical_family = _canonical_family(family)
    canonical_variant = _canonical_variant(variant)
    variants = GRAPH_MANIFEST[canonical_family]
    try:
        return variants[canonical_variant]
    except KeyError as exc:
        available = ", ".join(sorted(variants))
        raise ValueError(
            f"Unknown variant {variant!r} for demosaic family {canonical_family!r}; "
            f"available variants: {available}"
        ) from exc


def validate_graph_selector(family: str, variant: str | None = None) -> bool:
    """Return ``True`` when a family/variant selector is registered.

    The function intentionally preserves the detailed ``ValueError`` and
    ``TypeError`` raised by :func:`resolve_graph_name`; callers that need a
    boolean-only probe can catch those exceptions explicitly.
    """

    resolve_graph_name(family, variant)
    return True


def registered_graph_names(family: str | None = None) -> tuple[str, ...]:
    """Return canonical registered graph names, optionally for one family."""

    if family is None:
        names = {name for variants in GRAPH_MANIFEST.values() for name in variants.values()}
    else:
        names = set(GRAPH_MANIFEST[_canonical_family(family)].values())
    return tuple(sorted(names))


def graph_specs(family: str | None = None) -> tuple[DemosaicGraphSpec, ...]:
    """Return immutable graph descriptors for diagnostics and tests."""

    families = GRAPH_MANIFEST if family is None else {_canonical_family(family): GRAPH_MANIFEST[_canonical_family(family)]}
    return tuple(
        DemosaicGraphSpec(
            family=family_name,
            graph_name=graph_name,
            variant=variant,
            required_inputs=tuple(_FAMILY_METADATA[family_name]["required_inputs"]),
            scratch_buffers=tuple(_FAMILY_METADATA[family_name]["scratch_buffers"]),
            stages=tuple(_FAMILY_METADATA[family_name]["stages"]),
        )
        for family_name, variants in families.items()
        for variant, graph_name in variants.items()
    )


__all__ = [
    "DemosaicGraphSpec",
    "GRAPH_MANIFEST",
    "FAMILY_ALIASES",
    "VARIANT_ALIASES",
    "resolve_graph_name",
    "validate_graph_selector",
    "registered_graph_names",
    "graph_specs",
]
