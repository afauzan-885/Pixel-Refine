"""Input contracts shared by the streaming HDR algorithms."""

from dataclasses import dataclass
from typing import Literal, Optional


@dataclass(frozen=True)
class HDRExposureMetadata:
    """EXIF values used for relative exposure normalization when available."""

    exposure_time_seconds: Optional[float] = None
    analog_gain: Optional[float] = None
    iso: Optional[float] = None
    black_level: Optional[float] = None
    white_level: Optional[float] = None
    transfer_function: Literal["linear", "unknown"] = "unknown"


@dataclass(frozen=True)
class HDRWeightPolicy:
    """AOT weighting policy used by the Weighted HDR and SPDE-MR runners."""

    exposure_model: str = "well_exposed_midrange"
    snr_model: str = "signal_over_estimated_noise"
    saturation_policy: str = "reject_clipped_samples"
    normalization: str = "stream_per_frame_then_normalize_per_output_pixel"


@dataclass(frozen=True)
class SPDEMRPolicy:
    """Initial patch settings accepted from the SPDE-MR report review."""

    patch_size: int = 8
    stride: int = 4
    structure_correlation_min: float = 0.8
    local_quality: str = "exposure_times_contrast_times_structure"
