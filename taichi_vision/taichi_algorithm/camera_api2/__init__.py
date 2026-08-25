"""
Camera2 Pipeline - Taichi GPU Backend
======================================
Modul ini menyediakan pipeline capture gambar dari Camera2 API (Android)
dengan Taichi sebagai backend processing GPU.

Arsitektur:
  Camera2 YUV/RAW → [yuv_converter] → RGB float32
                  → [pipeline stages: denoise, color, enhance]
                  → output (numpy/display)

Modul yang tersedia:
  - yuv_converter: YUV_420_888/NV21/NV12 → RGB float32
  - camera_pipeline: Pipeline orchestrator dengan stage-based processing
  - frame_manager: Buffer pool, frame queue, adaptive frame controller

Modul taichi_algorithm yang dipanggil (reuse):
  - ta.non_local_means(): denoising per-frame
  - ta.hfcd_denoise(): heavy denoise
  - ta.gaussian(): blur/sharpen base
  - ta.guided_filter(): edge-preserving smooth
  - ta.bilateral(): bilateral filter
  - ta.clahe(): adaptive histogram equalization
  - ta.canny(): edge detection
  - ta.cvtColor() / ta.cvtColor_extended(): color conversion
  - ta.farneback_flow(): optical flow alignment
  - ta.phase_correlation(): global motion estimation
  - ta.build_image_pyramid(): multi-scale processing
  - ta.resize(): scaling (bilinear, bicubic, area, nearest)
  - ta.absdiff(): frame difference
  - ta.ssim(): quality metric
  - ta.gpu_histogram(): histogram analysis
  - ta.hamilton_demosaic() / ta.arm_demosaic(): RAW Bayer demosaic

Usage:
  from taichi_vision.taichi_algorithm.camera_api2 import (
      yuv420_to_rgb, nv21_to_rgb, yuv_to_gray,
      CameraPipeline, create_preview_pipeline,
      LatestFrameQueue, AdaptiveFrameController, FrameBufferPool,
  )
"""

# === YUV Conversion ===
from .yuv_converter import (
    yuv420_to_rgb,
    nv21_to_rgb,
    nv12_to_rgb,
    yuv_to_gray,
)

# === Pipeline Orchestrator ===
from .camera_pipeline import (
    CameraPipeline,
    AOTCameraPipeline,
    PipelineStage,
    create_preview_pipeline,
    create_capture_pipeline,
    create_low_light_pipeline,
)

# === Frame Management ===
from .frame_manager import (
    LatestFrameQueue,
    TripleBuffer,
    AdaptiveFrameController,
    FrameBufferPool,
    AOTFrameBufferPool,
    FrameSlot,
)


__all__ = [
    # YUV Conversion
    "yuv420_to_rgb",
    "nv21_to_rgb",
    "nv12_to_rgb",
    "yuv_to_gray",
    # Pipeline
    "CameraPipeline",
    "AOTCameraPipeline",
    "PipelineStage",
    "create_preview_pipeline",
    "create_capture_pipeline",
    "create_low_light_pipeline",
    # Frame Management
    "LatestFrameQueue",
    "TripleBuffer",
    "AdaptiveFrameController",
    "FrameBufferPool",
    "AOTFrameBufferPool",
    "FrameSlot",
]
