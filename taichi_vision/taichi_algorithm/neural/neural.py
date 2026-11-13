"""High-level, ergonomic ONNX InferenceSession powered by Taichi AOT native runtime.

Provides drop-in compatibility with onnxruntime.InferenceSession, backed by
zero-intermediate host upload, static VRAM reuse, and Ahead-of-Time compiled TCM modules.
Pre-baked models reside in pixel_refine_desktop/ui/data/aot_assets/neural/.
"""

from __future__ import annotations

import hashlib
import io
import math
import os
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional, Sequence, Union
import zipfile

import numpy as np

def _resolve_output(source, dst=None):
    """True when the result should stay resident (device-owned)."""
    from taichi.aot_engine import is_resident

    if dst is not None and is_resident(dst):
        return True
    if isinstance(source, dict):
        return any(is_resident(value) for value in source.values())
    if isinstance(source, (list, tuple)):
        return any(is_resident(value) for value in source)
    return is_resident(source)




DEFAULT_AOT_NEURAL_DIR = Path("pixel_refine_desktop/ui/data/aot_assets/neural")


def _resolve_backend_from_providers(providers: Optional[Sequence[str]], fallback: str = "auto") -> str:
    """Map standard ONNX Runtime execution provider names to Taichi backends."""
    if not providers:
        return fallback
    for p in providers:
        p_str = str(p).lower()
        if "cuda" in p_str:
            return "cuda"
        if "vulkan" in p_str:
            return "vulkan"
        if "opengl" in p_str:
            return "opengl"
        if "cpu" in p_str:
            return "cpu"
    return fallback


def find_prebaked_tcm(
    stem: str,
    backend: str,
    search_dir: Path = DEFAULT_AOT_NEURAL_DIR,
) -> Optional[Path]:
    """Search for a matching pre-baked .tcm model in the neural assets directory."""
    if not search_dir.is_dir():
        return None

    # Candidate file patterns in descending order of specificity
    candidates = [
        f"{stem}_{backend}.tcm",
        f"{stem}_resident_{backend}.tcm",
    ]
    for name in candidates:
        candidate_path = search_dir / name
        if candidate_path.is_file():
            return candidate_path

    # Check for prefix match in directory (e.g. stem_targetid_hash.tcm)
    for f in search_dir.glob(f"{stem}*.tcm"):
        if backend in f.name.lower():
            return f

    return None


def resolve_or_compile_tcm(
    model_path_or_bytes: Union[str, Path, bytes],
    backend: str = "auto",
    model_name: Optional[str] = None,
    output_dir: Optional[Union[str, Path]] = DEFAULT_AOT_NEURAL_DIR,
    patch_tools: bool = True,
) -> Path:
    """Resolve an existing pre-baked TCM in aot_assets/neural or compile into it.

    Returns the absolute Path to the .tcm file ready to be loaded by AOTEngine.
    """
    from taichi.aot_engine import get_backend_name
    from taichi.artifact_targets import detect_target

    if isinstance(model_path_or_bytes, (str, Path)):
        p = Path(model_path_or_bytes)
        if p.is_file() and p.suffix.lower() == ".tcm":
            return p.resolve()

    resolved_backend = backend.strip().lower()
    if resolved_backend in ("auto", "default", ""):
        resolved_backend = get_backend_name()

    target_dir = Path(output_dir).resolve() if output_dir else DEFAULT_AOT_NEURAL_DIR.resolve()

    if isinstance(model_path_or_bytes, (str, Path)):
        model_path = Path(model_path_or_bytes).resolve()
        if not model_path.is_file():
            raise FileNotFoundError(f"ONNX model not found: {model_path}")
        stem = model_name or model_path.stem
        model_bytes = model_path.read_bytes()
    elif isinstance(model_path_or_bytes, (bytes, bytearray, memoryview)):
        stem = model_name or "neural_model"
        model_bytes = bytes(model_path_or_bytes)
    else:
        raise TypeError(f"Expected model path or bytes, got {type(model_path_or_bytes)}")

    # 1. Check if already pre-baked in aot_assets/neural
    prebaked = find_prebaked_tcm(stem, resolved_backend, search_dir=target_dir)
    if prebaked is not None and prebaked.is_file():
        return prebaked

    # 2. Check canonical target name: {stem}_{backend}.tcm
    canonical_path = target_dir / f"{stem}_{resolved_backend}.tcm"
    if canonical_path.is_file():
        return canonical_path

    raise RuntimeError(
        f"Pre-baked TCM model not found at {canonical_path}. "
        "taichi_vision is load-only; compile the artifact with the Taichi venv "
        "toolchain before starting the application."
    )


class InferenceSession:
    """Drop-in high-performance ONNX InferenceSession powered by Taichi AOT.

    Usage:
        >>> import taichi_vision.taichi_algorithm.neural.neural as neural
        >>> session = neural.InferenceSession("model.onnx", backend="cuda")
        >>> outputs = session.run(None, {"input": x})
    """

    def __init__(
        self,
        model_path_or_bytes: Union[str, Path, bytes],
        backend: str = "auto",
        providers: Optional[Sequence[str]] = None,
        model_name: Optional[str] = None,
        output_dir: Optional[Union[str, Path]] = DEFAULT_AOT_NEURAL_DIR,
        enable_fusion: bool = True,
        patch_tools: bool = True,
    ):
        from taichi.aot_engine import get_backend_name, engine
        from taichi.artifact_targets import detect_target
        from taichi_vision.taichi_algorithm.denoising.onnx_resident_aot import ResidentONNXGraph

        if providers is not None:
            backend = _resolve_backend_from_providers(providers, fallback=backend)

        resolved_backend = backend.strip().lower()
        if resolved_backend in ("auto", "default", ""):
            resolved_backend = get_backend_name()

        self.backend = resolved_backend
        if str(engine.arch).lower() != self.backend:
            os.environ["AOT_ARCH"] = self.backend
        self.engine = engine._live() if hasattr(engine, "_live") else engine

        self.target_spec = detect_target(backend=self.backend)

        # 1. Direct TCM archive path
        if isinstance(model_path_or_bytes, (str, Path)):
            p = Path(model_path_or_bytes)
            if p.is_file() and p.suffix.lower() == ".tcm":
                self.tcm_path = p.resolve()
                self._graph = ResidentONNXGraph(
                    self.tcm_path, engine=self.engine, artifact_only=True
                )
                return

        # 2. Extract ONNX model bytes
        if isinstance(model_path_or_bytes, (str, Path)):
            model_path = Path(model_path_or_bytes).resolve()
            if not model_path.is_file():
                raise FileNotFoundError(f"ONNX model not found: {model_path}")
            model_bytes = model_path.read_bytes()
            stem = model_name or model_path.stem
        elif isinstance(model_path_or_bytes, (bytes, bytearray, memoryview)):
            model_bytes = bytes(model_path_or_bytes)
            stem = model_name or "neural_model"
        else:
            raise TypeError(f"Expected model path or bytes, got {type(model_path_or_bytes)}")

        model_sha256 = hashlib.sha256(model_bytes).hexdigest()

        # 3. Resolve from pre-baked aot_assets/neural or compile
        self.tcm_path = resolve_or_compile_tcm(
            model_bytes,
            backend=self.backend,
            model_name=stem,
            output_dir=output_dir,
            patch_tools=patch_tools,
        )
        self._graph = ResidentONNXGraph(
            self.tcm_path, engine=self.engine, model_sha256=model_sha256
        )

    def get_inputs(self) -> List[Any]:
        """Returns input tensor metadata with .name and .shape."""
        return self._graph.get_inputs()

    def get_outputs(self) -> List[Any]:
        """Returns output tensor metadata with .name and .shape."""
        return self._graph.get_outputs()

    def get_providers(self) -> List[str]:
        """Returns active execution provider info."""
        return self._graph.get_providers()

    def run(
        self,
        output_names: Optional[Sequence[str]] = None,
        input_feed: Optional[Dict[str, Any]] = None,
        
        borrowed_outputs: bool = False,
        **kwargs: Any,
    ) -> List[Any]:
        """Executes model with drop-in signature compatible with onnxruntime."""
        _resident_output = _resolve_output(input_feed)
        return self._graph.run(
            output_names=output_names,
            input_feed=input_feed,
            borrowed_outputs=borrowed_outputs,
        )

    def close(self):
        """Release device buffers and native graph resources."""
        if hasattr(self, "_graph") and self._graph is not None:
            self._graph.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __repr__(self) -> str:
        return f"<TaichiAOT.InferenceSession backend={self.backend} target={self.target_spec.target_id}>"
