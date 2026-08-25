"""Compatibility wrapper; canonical compiler lives in taichi_algorithm."""
from taichi_vision.taichi_algorithm.compile_cast_tcm import *

if __name__ == "__main__":
    import runpy
    runpy.run_module("taichi_vision.taichi_algorithm.compile_cast_tcm", run_name="__main__")
