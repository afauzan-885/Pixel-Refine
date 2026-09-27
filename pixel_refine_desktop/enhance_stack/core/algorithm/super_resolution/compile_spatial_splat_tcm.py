"""Compatibility command entry point for the relocated Splat SR compiler."""

from .splat_sr.compile_spatial_splat_tcm import compile_spatial_splat

__all__ = ["compile_spatial_splat"]


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        raise SystemExit(
            "usage: python compile_spatial_splat_tcm.py "
            "<vulkan|cuda|opengl|cpu>"
        )
    compile_spatial_splat(sys.argv[1])
