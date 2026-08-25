"""AOT image-compression kernels.

This package contains device-side transform and quantization stages. Container
and entropy bitstream work is intentionally kept explicit in the public API so
the AOT contract remains inspectable.
"""
import os


def __getattr__(name):
    """Load heavy Taichi/JPEG helpers only when they are actually requested.

    DNG/RAW container parsing must remain usable in tooling and tests without
    constructing a Taichi context.  The historical package-level names are
    retained through this lazy compatibility hook.
    """
    if name in {"JPEG_QUALITY_TABLE", "JPEG_CHROMA_TABLE", "JPEG_ZIGZAG"}:
        from . import jpeg_tables as _tables

        return getattr(_tables, name)
    if name == "JPEG_PRESETS":
        from .jpeg_aot import JPEG_PRESETS as _presets

        return _presets
    if name == "jpeg_prepare_blocks":
        from . import kernels as _kernels

        return _kernels.jpeg_prepare_blocks
    if name == "RawMosaicFrame":
        from .raw_frame import RawMosaicFrame as _frame

        return _frame
    if name == "RawFlowTileContract":
        from .raw_pipeline import RawFlowTileContract as _contract

        return _contract
    if name in {"DNGCapabilityError", "DNGCapabilityReport"}:
        from . import dng_aot as _dng

        return getattr(_dng, name)
    if name in {"NativeTensor", "NativeAOTEngine", "build_native_request"}:
        from . import native_dispatch as _native

        return getattr(_native, name)
    if name in {
        "AV1RangeEncoder",
        "AV1RangeDecoder",
        "AV1EntropyError",
        "AV1EntropyMalformedError",
        "AV1EntropyStateError",
    }:
        from . import av1_entropy_aot as _entropy

        return getattr(_entropy, name)
    raise AttributeError(name)


def jpeg_prepare_blocks(*args, **kwargs):
    from .kernels import jpeg_prepare_blocks as _impl

    return _impl(*args, **kwargs)


def encode_grayscale_taichi(*args, **kwargs):
    from .jpeg_grayscale_pipeline import encode_grayscale_taichi as _impl

    return _impl(*args, **kwargs)


def encode_rgb_taichi(*args, **kwargs):
    from .jpeg_rgb_pipeline import encode_rgb_taichi as _impl

    return _impl(*args, **kwargs)
# Import these lazily: the canonical JPEG API reuses compression.kernels, and
# eager package-level imports would create a circular import during startup.
def encode_grayscale_aot(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.jpeg_aot import encode_grayscale_aot as _impl
    return _impl(*args, **kwargs)


def encode_rgb_aot(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.jpeg_aot import encode_rgb_aot as _impl
    return _impl(*args, **kwargs)


def jpeg_encode_aot(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.jpeg_aot import jpeg_encode_aot as _impl
    return _impl(*args, **kwargs)


def encode_png_aot(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.png_aot import encode_png_aot as _impl
    return _impl(*args, **kwargs)


def save_png_aot(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.png_aot import save_png_aot as _impl
    return _impl(*args, **kwargs)


def parse_png_aot(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.png_aot import parse_png_aot as _impl
    return _impl(*args, **kwargs)


def encode_lossless_jpeg(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.jpeg_lossless import encode_lossless_jpeg as _impl
    return _impl(*args, **kwargs)


def decode_lossless_jpeg(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.jpeg_lossless import decode_lossless_jpeg as _impl
    return _impl(*args, **kwargs)


def encode_dng_aot(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.dng_aot import encode_dng_aot as _impl
    return _impl(*args, **kwargs)


def encode_dng_bytes(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.dng_aot import encode_dng_bytes as _impl
    return _impl(*args, **kwargs)


def decode_dng_bytes(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.dng_aot import decode_dng_bytes as _impl
    return _impl(*args, **kwargs)


def read_dng_aot(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.dng_aot import read_dng_aot as _impl
    return _impl(*args, **kwargs)


def dng_capability_report(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.dng_aot import dng_capability_report as _impl
    return _impl(*args, **kwargs)


def save_dng_aot(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.dng_aot import save_dng_aot as _impl
    return _impl(*args, **kwargs)


def raw_frame_from_dng(*args, **kwargs):
    """Create a semantic pre-demosaic RAW frame from a parsed DNG frame."""
    from taichi_vision.taichi_algorithm.compression.raw_frame import raw_frame_from_dng as _impl
    return _impl(*args, **kwargs)


def fuse_dng_frames_blockwise(*args, **kwargs):
    """Fuse parsed DNG frames directly without a demosaic intermediate."""
    from taichi_vision.taichi_algorithm.compression.raw_pipeline import fuse_dng_frames_blockwise as _impl
    return _impl(*args, **kwargs)


def raw_mosaic_frame(*args, **kwargs):
    """Compatibility constructor for :class:`RawMosaicFrame`."""
    from taichi_vision.taichi_algorithm.compression.raw_frame import RawMosaicFrame
    return RawMosaicFrame(*args, **kwargs)


def fuse_raw_frames_blockwise(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.raw_pipeline import fuse_raw_frames_blockwise as _impl
    return _impl(*args, **kwargs)


def raw_alignment_guide(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.raw_pipeline import raw_alignment_guide as _impl
    return _impl(*args, **kwargs)


def raw_alignment_guide_dng(*args, **kwargs):
    """Build a streamed pre-demosaic guide directly from a DNG frame."""
    from taichi_vision.taichi_algorithm.compression.raw_pipeline import raw_alignment_guide_dng as _impl
    return _impl(*args, **kwargs)


def raw_alignment_guide_native(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.raw_pipeline import raw_alignment_guide_native as _impl
    return _impl(*args, **kwargs)


def raw_normalize_headroom_native(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.raw_pipeline import raw_normalize_headroom_native as _impl
    return _impl(*args, **kwargs)


def raw_weight_map(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.raw_pipeline import raw_weight_map as _impl
    return _impl(*args, **kwargs)


def raw_weight_map_native(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.raw_pipeline import raw_weight_map_native as _impl
    return _impl(*args, **kwargs)


def fuse_raw_pair_native(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.raw_pipeline import fuse_raw_pair_native as _impl
    return _impl(*args, **kwargs)


def fuse_raw_accumulate_native(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.raw_pipeline import fuse_raw_accumulate_native as _impl
    return _impl(*args, **kwargs)


def phase_safe_integer_warp(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.raw_pipeline import phase_safe_integer_warp as _impl
    return _impl(*args, **kwargs)


def raw_optical_flow(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.raw_pipeline import raw_optical_flow as _impl
    return _impl(*args, **kwargs)


def raw_optical_flow_dng(*args, **kwargs):
    """Run optical flow on streamed pre-demosaic DNG guides."""
    from taichi_vision.taichi_algorithm.compression.raw_pipeline import raw_optical_flow_dng as _impl
    return _impl(*args, **kwargs)


def raw_flow_tile_contract(*args, **kwargs):
    """Declare an explicit, phase-safe RAW green-guide tile contract."""
    from taichi_vision.taichi_algorithm.compression.raw_pipeline import raw_flow_tile_contract as _impl
    return _impl(*args, **kwargs)


def raw_flow_tile_parity_report(*args, **kwargs):
    """Run a read-only full-vs-tiled RAW-flow candidate diagnostic."""
    from taichi_vision.taichi_algorithm.compression.raw_pipeline import raw_flow_tile_parity_report as _impl
    return _impl(*args, **kwargs)


def package_heic_aot(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.heif_aot import package_heic_aot as _impl
    return _impl(*args, **kwargs)


def package_heic_image_aot(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.heif_aot import package_heic_image_aot as _impl
    return _impl(*args, **kwargs)


def build_heif_payload(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.heif_aot import build_heif_payload as _impl
    return _impl(*args, **kwargs)


def save_heic_aot(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.heif_aot import save_heic_aot as _impl
    return _impl(*args, **kwargs)


def parse_heif_aot(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.heif_aot import parse_heif_aot as _impl
    return _impl(*args, **kwargs)


def package_heic_vcl_aot(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.heif_aot import package_heic_vcl_aot as _impl
    return _impl(*args, **kwargs)


def package_heic_ipcm_aot(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.heif_aot import package_heic_ipcm_aot as _impl
    return _impl(*args, **kwargs)


def package_heic_neutral_aot(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.heif_aot import package_heic_neutral_aot as _impl
    return _impl(*args, **kwargs)


def package_heic_flat_aot(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.heif_aot import package_heic_flat_aot as _impl
    return _impl(*args, **kwargs)


def package_heic_ctu_stripes_aot(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.heif_aot import package_heic_ctu_stripes_aot as _impl
    return _impl(*args, **kwargs)


def package_heic_ipcm10_aot(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.heif_aot import package_heic_ipcm10_aot as _impl
    return _impl(*args, **kwargs)


def heic_vcl_capability_report(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.heif_aot import heic_vcl_capability_report as _impl
    return _impl(*args, **kwargs)


def heic_ipcm_capability_report(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.heif_aot import heic_ipcm_capability_report as _impl
    return _impl(*args, **kwargs)


def heic_neutral_capability_report(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.heif_aot import heic_neutral_capability_report as _impl
    return _impl(*args, **kwargs)


def heic_flat_capability_report(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.heif_aot import heic_flat_capability_report as _impl
    return _impl(*args, **kwargs)


def heic_flat10_capability_report(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.heif_aot import heic_flat10_capability_report as _impl
    return _impl(*args, **kwargs)


def heic_ctu_stripes_capability_report(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.heif_aot import heic_ctu_stripes_capability_report as _impl
    return _impl(*args, **kwargs)


def heic_ipcm10_capability_report(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.heif_aot import heic_ipcm10_capability_report as _impl
    return _impl(*args, **kwargs)


def build_hevc_parameter_sets(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.hevc_aot import build_hevc_parameter_sets as _impl
    return _impl(*args, **kwargs)


def build_hvcc(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.hevc_aot import build_hvcc as _impl
    return _impl(*args, **kwargs)


def parse_hvcc(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.hevc_aot import parse_hvcc as _impl
    return _impl(*args, **kwargs)


def encode_hevc_intra_aot(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.hevc_aot import encode_hevc_intra_aot as _impl
    return _impl(*args, **kwargs)


def hevc_capability_report(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.hevc_aot import hevc_capability_report as _impl
    return _impl(*args, **kwargs)


def encode_hevc_vcl_aot(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.hevc_vcl_aot import encode_hevc_vcl_aot as _impl
    return _impl(*args, **kwargs)


def build_hevc_vcl_picture(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.hevc_vcl_aot import build_hevc_vcl_picture as _impl
    return _impl(*args, **kwargs)


def parse_hevc_vcl_annex_b(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.hevc_vcl_aot import parse_hevc_vcl_annex_b as _impl
    return _impl(*args, **kwargs)


def validate_hevc_vcl_annex_b(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.hevc_vcl_aot import validate_hevc_vcl_annex_b as _impl
    return _impl(*args, **kwargs)


def hevc_vcl_capability_report(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.hevc_vcl_aot import hevc_vcl_capability_report as _impl
    return _impl(*args, **kwargs)


def encode_hevc_ipcm_aot(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.hevc_ipcm_aot import encode_hevc_ipcm_aot as _impl
    return _impl(*args, **kwargs)


def build_hevc_ipcm_picture(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.hevc_ipcm_aot import build_hevc_ipcm_picture as _impl
    return _impl(*args, **kwargs)


def validate_hevc_ipcm_annex_b(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.hevc_ipcm_aot import validate_hevc_ipcm_annex_b as _impl
    return _impl(*args, **kwargs)


def hevc_ipcm_capability_report(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.hevc_ipcm_aot import hevc_ipcm_capability_report as _impl
    return _impl(*args, **kwargs)


def encode_hevc_general_aot(*args, **kwargs):
    """Encode the bounded compressed HEVC intra profile."""
    from taichi_vision.taichi_algorithm.compression.hevc_general_aot import encode_hevc_general_aot as _impl
    return _impl(*args, **kwargs)


def build_hevc_general_picture(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.hevc_general_aot import build_hevc_general_picture as _impl
    return _impl(*args, **kwargs)


def validate_hevc_general_annex_b(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.hevc_general_aot import validate_hevc_general_annex_b as _impl
    return _impl(*args, **kwargs)


def hevc_general_capability_report(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.hevc_general_aot import hevc_general_capability_report as _impl
    return _impl(*args, **kwargs)


def encode_hevc_general10_aot(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.hevc_general10_aot import encode_hevc_general10_aot as _impl
    return _impl(*args, **kwargs)


def build_hevc_general10_picture(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.hevc_general10_aot import build_hevc_general10_picture as _impl
    return _impl(*args, **kwargs)


def hevc_general10_capability_report(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.hevc_general10_aot import hevc_general10_capability_report as _impl
    return _impl(*args, **kwargs)


def package_avif_aot(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.avif_aot import package_avif_aot as _impl
    return _impl(*args, **kwargs)


def build_avif_payload(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.avif_aot import build_avif_payload as _impl
    return _impl(*args, **kwargs)


def save_avif_aot(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.avif_aot import save_avif_aot as _impl
    return _impl(*args, **kwargs)


def parse_avif_aot(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.avif_aot import parse_avif_aot as _impl
    return _impl(*args, **kwargs)


def compression_production_audit(*args, **kwargs):
    """Return the machine-readable release-readiness audit."""
    from taichi_vision.taichi_algorithm.compression.production_audit import run_production_audit as _impl
    return _impl(*args, **kwargs)


def make_av1_still_profile(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.av1_aot import make_av1_still_profile as _impl
    return _impl(*args, **kwargs)


def build_av1_sequence_header(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.av1_aot import build_sequence_header as _impl
    return _impl(*args, **kwargs)


def parse_av1_sequence_header(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.av1_aot import parse_sequence_header as _impl
    return _impl(*args, **kwargs)


def build_av1_sequence_header_obu(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.av1_aot import build_sequence_header_obu as _impl
    return _impl(*args, **kwargs)


def build_av1_obu(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.av1_aot import build_obu as _impl
    return _impl(*args, **kwargs)


def parse_av1_obus(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.av1_aot import parse_obus as _impl
    return _impl(*args, **kwargs)


def build_av1c(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.av1_aot import build_av1c as _impl
    return _impl(*args, **kwargs)


def parse_av1c(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.av1_aot import parse_av1c as _impl
    return _impl(*args, **kwargs)


def encode_av1_tiny_constant(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.av1_aot import encode_av1_tiny_constant as _impl
    return _impl(*args, **kwargs)


def validate_av1_image_payload(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.av1_aot import validate_av1_image_payload as _impl
    return _impl(*args, **kwargs)


def av1_image_payload_report(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.av1_aot import av1_image_payload_report as _impl
    return _impl(*args, **kwargs)


def encode_av1_intra_constant(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.av1_intra_aot import encode_av1_intra_constant as _impl
    return _impl(*args, **kwargs)


def encode_av1_intra_constant_16x16(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.av1_intra_aot import encode_av1_intra_constant_16x16 as _impl
    return _impl(*args, **kwargs)


def validate_av1_intra_payload(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.av1_intra_aot import validate_av1_intra_payload as _impl
    return _impl(*args, **kwargs)


def av1_intra_capability_report(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.av1_intra_aot import av1_intra_capability_report as _impl
    return _impl(*args, **kwargs)


def supported_av1_constant_colors(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.av1_intra_aot import supported_constant_colors as _impl
    return _impl(*args, **kwargs)


def av1_entropy_encode_symbols(*args, **kwargs):
    """Encode symbols with the native AV1 Q15 range primitive."""
    from taichi_vision.taichi_algorithm.compression.av1_entropy_aot import encode_symbols as _impl
    return _impl(*args, **kwargs)


def av1_entropy_decode_symbols(*args, **kwargs):
    """Decode symbols with the native AV1 Q15 range primitive."""
    from taichi_vision.taichi_algorithm.compression.av1_entropy_aot import decode_symbols as _impl
    return _impl(*args, **kwargs)


def av1_entropy_update_icdf(*args, **kwargs):
    """Apply AV1 CDF adaptation explicitly, without mutating caller state."""
    from taichi_vision.taichi_algorithm.compression.av1_entropy_aot import update_icdf as _impl
    return _impl(*args, **kwargs)


def av1_entropy_capability_report(*args, **kwargs):
    """Return the bounded native AV1 entropy-layer capability report."""
    from taichi_vision.taichi_algorithm.compression.av1_entropy_aot import av1_entropy_capability_report as _impl
    return _impl(*args, **kwargs)


def av1_cdf_capability_report(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.av1_cdf_aot import (
        av1_cdf_capability_report as _impl,
    )

    return _impl(*args, **kwargs)


def get_av1_cdf(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.av1_cdf_aot import (
        get_av1_cdf as _impl,
    )

    return _impl(*args, **kwargs)


def av1_dc_predict_residual_4x4(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.av1_predict_aot import (
        av1_dc_predict_residual_4x4 as _impl,
    )

    return _impl(*args, **kwargs)


def av1_dc_predict_capability_report(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.av1_predict_aot import (
        av1_dc_predict_capability_report as _impl,
    )

    return _impl(*args, **kwargs)


def prepare_yuv_aot(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.video_prep import prepare_yuv_aot as _impl
    return _impl(*args, **kwargs)


def prepare_yuv_native(*args, **kwargs):
    """Run the opt-in NumPy-free native-buffer YUV preparation path."""
    from taichi_vision.taichi_algorithm.compression.native_video_prep import prepare_yuv_native as _impl
    return _impl(*args, **kwargs)


def prepare_av1_dc_residual_native(*args, **kwargs):
    """Run the bounded AV1 DC residual graph through native buffers."""
    from taichi_vision.taichi_algorithm.compression.native_video_prep import (
        prepare_av1_dc_residual_native as _impl,
    )

    return _impl(*args, **kwargs)


def native_video_prep_capability_report(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.native_video_prep import native_video_prep_capability_report as _impl
    return _impl(*args, **kwargs)


def package_webp_aot(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.webp_aot import package_webp_aot as _impl
    return _impl(*args, **kwargs)


def build_webp_payload(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.webp_aot import build_webp_payload as _impl
    return _impl(*args, **kwargs)


def save_webp_aot(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.webp_aot import save_webp_aot as _impl
    return _impl(*args, **kwargs)


def encode_webp_lossless_aot(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.webp_aot import encode_webp_lossless_aot as _impl
    return _impl(*args, **kwargs)


def save_webp_lossless_aot(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.webp_aot import save_webp_lossless_aot as _impl
    return _impl(*args, **kwargs)


def parse_webp_aot(*args, **kwargs):
    from taichi_vision.taichi_algorithm.compression.webp_aot import parse_webp_aot as _impl
    return _impl(*args, **kwargs)


# Backend-neutral aliases for callers that want the maintained AOT pipeline.
encode_grayscale = encode_grayscale_aot
encode_rgb = encode_rgb_aot
jpeg_encode = jpeg_encode_aot

if os.environ.get("AOT_MODE", "1") == "1":
    # Preserve the historical names while ensuring AOT-mode callers do not
    # accidentally enter the old JIT-only orchestration.
    encode_grayscale_taichi = encode_grayscale_aot
    encode_rgb_taichi = encode_rgb_aot

__all__ = [
    "JPEG_QUALITY_TABLE",
    "JPEG_PRESETS",
    "jpeg_prepare_blocks",
    "encode_grayscale_taichi",
    "encode_rgb_taichi",
    "encode_grayscale_aot",
    "encode_rgb_aot",
    "jpeg_encode_aot",
    "encode_grayscale",
    "encode_rgb",
    "jpeg_encode",
    "encode_png_aot",
    "save_png_aot",
    "parse_png_aot",
    "encode_lossless_jpeg",
    "decode_lossless_jpeg",
    "encode_dng_aot",
    "encode_dng_bytes",
    "decode_dng_bytes",
    "read_dng_aot",
    "dng_capability_report",
    "DNGCapabilityError",
    "DNGCapabilityReport",
    "save_dng_aot",
    "RawMosaicFrame",
    "raw_frame_from_dng",
    "fuse_dng_frames_blockwise",
    "raw_mosaic_frame",
    "fuse_raw_frames_blockwise",
    "raw_alignment_guide",
    "raw_alignment_guide_dng",
    "raw_alignment_guide_native",
    "raw_normalize_headroom_native",
    "raw_weight_map",
    "raw_weight_map_native",
    "fuse_raw_pair_native",
    "fuse_raw_accumulate_native",
    "phase_safe_integer_warp",
    "raw_optical_flow",
    "raw_optical_flow_dng",
    "RawFlowTileContract",
    "raw_flow_tile_contract",
    "raw_flow_tile_parity_report",
    "package_heic_aot",
    "package_heic_image_aot",
    "build_heif_payload",
    "save_heic_aot",
    "parse_heif_aot",
    "package_heic_vcl_aot",
    "package_heic_ipcm_aot",
    "package_heic_neutral_aot",
    "package_heic_flat_aot",
    "package_heic_ctu_stripes_aot",
    "package_heic_ipcm10_aot",
    "heic_vcl_capability_report",
    "heic_ipcm_capability_report",
    "heic_neutral_capability_report",
    "heic_flat_capability_report",
    "heic_flat10_capability_report",
    "heic_ctu_stripes_capability_report",
    "heic_ipcm10_capability_report",
    "build_hevc_parameter_sets",
    "build_hvcc",
    "parse_hvcc",
    "encode_hevc_intra_aot",
    "hevc_capability_report",
    "encode_hevc_vcl_aot",
    "build_hevc_vcl_picture",
    "parse_hevc_vcl_annex_b",
    "validate_hevc_vcl_annex_b",
    "hevc_vcl_capability_report",
    "encode_hevc_ipcm_aot",
    "build_hevc_ipcm_picture",
    "validate_hevc_ipcm_annex_b",
    "hevc_ipcm_capability_report",
    "encode_hevc_general_aot",
    "build_hevc_general_picture",
    "validate_hevc_general_annex_b",
    "hevc_general_capability_report",
    "encode_hevc_general10_aot",
    "build_hevc_general10_picture",
    "hevc_general10_capability_report",
    "package_avif_aot",
    "build_avif_payload",
    "save_avif_aot",
    "parse_avif_aot",
    "make_av1_still_profile",
    "build_av1_sequence_header",
    "parse_av1_sequence_header",
    "build_av1_sequence_header_obu",
    "build_av1_obu",
    "parse_av1_obus",
    "build_av1c",
    "parse_av1c",
    "encode_av1_tiny_constant",
    "validate_av1_image_payload",
    "av1_image_payload_report",
    "encode_av1_intra_constant",
    "encode_av1_intra_constant_16x16",
    "validate_av1_intra_payload",
    "av1_intra_capability_report",
    "supported_av1_constant_colors",
    "AV1RangeEncoder",
    "AV1RangeDecoder",
    "AV1EntropyError",
    "AV1EntropyMalformedError",
    "AV1EntropyStateError",
    "av1_entropy_encode_symbols",
    "av1_entropy_decode_symbols",
    "av1_entropy_update_icdf",
    "av1_entropy_capability_report",
    "av1_cdf_capability_report",
    "get_av1_cdf",
    "av1_dc_predict_residual_4x4",
    "av1_dc_predict_capability_report",
    "prepare_yuv_aot",
    "prepare_yuv_native",
    "prepare_av1_dc_residual_native",
    "native_video_prep_capability_report",
    "NativeTensor",
    "NativeAOTEngine",
    "build_native_request",
    "package_webp_aot",
    "build_webp_payload",
    "save_webp_aot",
    "encode_webp_lossless_aot",
    "save_webp_lossless_aot",
    "parse_webp_aot",
]
