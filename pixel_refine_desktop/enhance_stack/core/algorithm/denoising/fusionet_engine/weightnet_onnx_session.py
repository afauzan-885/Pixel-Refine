"""ONNX Runtime backend for WeightNet V3.1 (1024x1024 patch).

Drop-in replacement for ``ResidentWeightNet`` on the WeightNet inference path:
exposes ``runtime`` (``onnx_dml``/``onnx_cpu``) and ``infer(reference, support,
*, overlap, ghost_penalty, ghost_cutoff, stop_event, max_safety, ...)`` returning
``(weight_map[1,H,W] float32, alpha float)``.

The V3.1 bundle ships one GPU member (DirectML fused, requires DmlExecutionProvider)
and one CPU member (native ops). The provider selects the matching member; the GPU
member cannot run on CPU EP.
"""
from __future__ import annotations

import json
import os
import threading
import zipfile
from pathlib import Path
from types import SimpleNamespace

import numpy as np

DEFAULT_V31_BUNDLE = Path("database/Learning_Model/weightnet_v3.1/weightnet_v3.1.bundle")
DEFAULT_V3_BUNDLE = Path("database/Learning_Model/weightNet/weightnet_master.bundle")
V31_PATCH_SIZE = 1024
V3_PATCH_SIZES = (512, 1024)

_RUNTIME_BY_PROVIDER = {"dml": "onnx_dml", "cpu": "onnx_cpu"}


def _to_luma_chw(array) -> np.ndarray:
    """Return a contiguous float32 [1,H,W] luminance plane from 1/3-channel CHW."""
    arr = np.asarray(array, dtype=np.float32)
    if arr.ndim == 2:
        return np.ascontiguousarray(arr[None, ...])
    if arr.ndim != 3:
        raise ValueError(f"WeightNet input must be CHW, got shape {arr.shape}")
    if arr.shape[0] == 1:
        return np.ascontiguousarray(arr)
    if arr.shape[0] == 3:
        gray = (
            arr[0] * np.float32(0.299)
            + arr[1] * np.float32(0.587)
            + arr[2] * np.float32(0.114)
        )
        return np.ascontiguousarray(gray[None, ...])
    raise ValueError(f"WeightNet requires 1 or 3 channels, got {arr.shape[0]}")


def _select_provider(requested=None):
    """Resolve ORT providers from the application device settings.

    Honors ``onnx_runtime`` (auto/dml/cpu) and the selected GPU vendor from
    app.json / the worker environment via ``onnx_utils`` so DirectML uses the
    chosen adapter's ``device_id`` instead of the default adapter (Intel iGPU).

    Returns ``(provider, providers, device_id, vendor)`` where provider is
    ``"dml"`` or ``"cpu"``.
    """
    import onnxruntime as ort

    from pixel_refine_desktop.enhance_stack.core.algorithm.onnx_utils import (
        get_selected_gpu_vendor,
        scan_directml_adapters,
    )

    if requested not in ("dml", "cpu"):
        requested = os.environ.get("PIXEL_REFINE_WEIGHTNET_EP")
        if requested not in ("dml", "cpu"):
            requested = None

    if requested in ("dml", "cpu"):
        runtime = requested
    elif os.environ.get("ONNX_RUNTIME") in ("auto", "dml", "cpu"):
        runtime = os.environ["ONNX_RUNTIME"]
    else:
        runtime = "auto"
        try:
            from pixel_refine_desktop.ui.views.settings.General.general_store import (
                get_general_store,
            )

            runtime = str(get_general_store().get("onnx_runtime", "auto")).strip().lower()
        except Exception:
            runtime = "auto"
        if runtime not in ("auto", "dml", "cpu"):
            runtime = "auto"

    available = set(ort.get_available_providers())
    vendor = get_selected_gpu_vendor(None)
    dml_available = "DmlExecutionProvider" in available

    if runtime == "cpu" or (runtime == "auto" and vendor == "cpu"):
        return "cpu", ["CPUExecutionProvider"], None, vendor or "cpu"

    if not dml_available:
        if requested == "dml":
            raise RuntimeError(
                "WeightNet V3.1 requested DirectML but DmlExecutionProvider is "
                f"unavailable in onnxruntime (providers={sorted(available)})."
            )
        print(
            f"[WeightNet V3.1] DirectML unavailable in onnxruntime "
            f"(providers={sorted(available)}); running the CPU member."
        )
        return "cpu", ["CPUExecutionProvider"], None, vendor

    # Map the selected GPU vendor to its DirectML adapter index so ORT uses the
    # chosen device instead of the default adapter (often the Intel iGPU).
    adapters = scan_directml_adapters()
    matching = next((a for a in adapters if a.get("vendor") == vendor), None)
    if matching is None and vendor not in ("intel", "cpu") and adapters:
        matching = next(
            (a for a in adapters if a.get("vendor") in ("nvidia", "amd")),
            adapters[0],
        )
    if matching is not None:
        device_id = int(matching.get("device_id", 0))
        providers = [("DmlExecutionProvider", {"device_id": device_id})]
    else:
        device_id = None
        providers = ["DmlExecutionProvider"]
    return "dml", providers, device_id, vendor


class OrtWeightNetSession:
    """Tiled WeightNet V3.1 inference on ONNX Runtime."""

    def __init__(self, model_bytes: bytes, *, patch_size=None,
                 provider: str, providers):
        import onnxruntime as ort

        self.provider = provider
        self.runtime = _RUNTIME_BY_PROVIDER[provider]
        self.max_safety = 0.30
        self._lock = threading.RLock()

        options = ort.SessionOptions()
        options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
        options.log_severity_level = 3
        options.enable_mem_pattern = provider == "cpu"
        self.session = ort.InferenceSession(
            model_bytes, sess_options=options, providers=list(providers)
        )
        active = self.session.get_providers()
        if self.provider == "dml" and "DmlExecutionProvider" not in active:
            raise RuntimeError(
                f"WeightNet fell back off DirectML unexpectedly: {active}. "
                "Refusing silent GPU->CPU fallback."
            )
        self.providers = active
        inputs = self.session.get_inputs()
        self._input_names = {i.name for i in inputs}
        self._has_motion_input = "motion_sensitivity" in self._input_names
        self._has_ghost_input = "ghost_sensitivity" in self._input_names

        if patch_size is None:
            ref = next((i for i in inputs if i.name == "ref_img"), inputs[0])
            shape = tuple(ref.shape)
            patch_size = int(shape[-1]) if shape and isinstance(shape[-1], int) else V31_PATCH_SIZE
        self.patch_size = int(patch_size)
        self.motion_sensitivity = 1.0
        self.ghost_sensitivity = 0.30

        window = np.hanning(self.patch_size).astype(np.float32)
        self._window = np.clip(np.outer(window, window), 1e-4, None)

    @staticmethod
    def _select_member(models, resolved, patch_size):
        prov = "gpu" if resolved == "dml" else "cpu"
        if f"{prov}_p3_balance" in models:
            return models[f"{prov}_p3_balance"]["file_name"], None
        sizes = sorted({
            int(key.split("_")[1])
            for key in models
            if key.startswith(prov) and "_1c_fp32" in key and key.split("_")[1].isdigit()
        })
        if not sizes:
            raise FileNotFoundError(
                f"No {prov} ONNX member found in bundle models={list(models)}"
            )
        chosen = sizes[-1] if patch_size is None else min(
            sizes, key=lambda candidate: abs(candidate - int(patch_size))
        )
        key = f"{prov}_{chosen}_1c_fp32"
        if key not in models:
            raise FileNotFoundError(
                f"Bundle member {key} not found (available={list(models)})"
            )
        return models[key]["file_name"], chosen

    @classmethod
    def from_bundle(cls, bundle_path=DEFAULT_V31_BUNDLE, *,
                    patch_size=None, provider: str = "auto") -> "OrtWeightNetSession":
        bundle_path = Path(bundle_path)
        if not bundle_path.is_file():
            raise FileNotFoundError(f"WeightNet bundle not found: {bundle_path}")
        requested = provider if provider in ("dml", "cpu") else None
        resolved, providers, device_id, vendor = _select_provider(requested)
        with zipfile.ZipFile(bundle_path) as archive:
            manifest = json.loads(archive.read("manifest.json").decode("utf-8"))
            member, chosen_patch = cls._select_member(
                manifest.get("models", {}), resolved, patch_size
            )
            model_bytes = archive.read(member)
        session = cls(model_bytes, patch_size=chosen_patch, provider=resolved,
                      providers=providers)
        session.bundle_path = bundle_path
        session.member_name = member
        session.vendor = vendor
        session.dml_device_id = device_id
        return session

    def get_inputs(self):
        return [SimpleNamespace(name=i.name, shape=tuple(i.shape), type=i.type)
                for i in self.session.get_inputs()]

    def get_outputs(self):
        return [SimpleNamespace(name=o.name, shape=tuple(o.shape), type=o.type)
                for o in self.session.get_outputs()]

    def get_providers(self):
        return list(self.providers)

    @staticmethod
    def _stopped(stop_event) -> bool:
        if stop_event is None:
            return False
        if callable(stop_event):
            return bool(stop_event())
        if hasattr(stop_event, "is_set"):
            return bool(stop_event.is_set())
        return bool(stop_event)

    def _tiled_weight(self, ref: np.ndarray, supp: np.ndarray,
                      overlap: float, stop_event, motion_sensitivity: float,
                      ghost_sensitivity: float) -> np.ndarray:
        tile = self.patch_size
        height, width = ref.shape[-2:]
        pad_h = max(0, tile - height)
        pad_w = max(0, tile - width)
        if pad_h or pad_w:
            ref = np.pad(ref, ((0, 0), (0, pad_h), (0, pad_w)), mode="reflect")
            supp = np.pad(supp, ((0, 0), (0, pad_h), (0, pad_w)), mode="reflect")
        ph, pw = ref.shape[-2:]

        stride = max(1, tile - int(tile * float(overlap)))
        xs = list(range(0, max(1, pw - tile + 1), stride))
        ys = list(range(0, max(1, ph - tile + 1), stride))
        if xs[-1] != pw - tile:
            xs.append(pw - tile)
        if ys[-1] != ph - tile:
            ys.append(ph - tile)

        acc = np.zeros((ph, pw), np.float32)
        wsum = np.zeros((ph, pw), np.float32)
        win = self._window
        for y in ys:
            for x in xs:
                if self._stopped(stop_event):
                    raise RuntimeError("WeightNet V3.1 inference cancelled")
                rp = np.ascontiguousarray(ref[0, y:y + tile, x:x + tile])[None, None]
                sp = np.ascontiguousarray(supp[0, y:y + tile, x:x + tile])[None, None]
                feed = {"ref_img": rp, "support_img": sp}
                if self._has_motion_input:
                    feed["motion_sensitivity"] = np.array(
                        [float(motion_sensitivity)], np.float32
                    )
                if self._has_ghost_input:
                    feed["ghost_sensitivity"] = np.array(
                        [float(ghost_sensitivity)], np.float32
                    )
                w = self.session.run(None, feed)[0][0, 0]
                acc[y:y + tile, x:x + tile] += w * win
                wsum[y:y + tile, x:x + tile] += win
        weight = acc / np.maximum(wsum, 1e-8)
        weight = np.clip(weight, 0.0, 1.0)
        return weight[:height, :width]

    def infer(self, reference, support, *, overlap=0.20, ghost_penalty=1.0,
              ghost_cutoff=0.0, stop_event=None, max_safety=None,
              motion_sensitivity=None, ghost_sensitivity=None,
              return_scalar=True, **unused):
        """Return (weight_map [1,H,W] float32, alpha) for one reference/support pair.

        ``motion_sensitivity`` (V3.1) and ``ghost_sensitivity`` (V3) are fed to
        their respective model inputs when present; otherwise ignored.
        """
        ref = _to_luma_chw(reference)
        supp = _to_luma_chw(support)
        if ref.shape[-2:] != supp.shape[-2:]:
            raise ValueError(
                f"reference/support shape mismatch: {ref.shape[-2:]} vs {supp.shape[-2:]}"
            )
        ms_val = float(self.motion_sensitivity if motion_sensitivity is None
                       else motion_sensitivity)
        gs_val = float(self.ghost_sensitivity if ghost_sensitivity is None
                       else ghost_sensitivity)
        with self._lock:
            weight = self._tiled_weight(ref, supp, overlap, stop_event, ms_val, gs_val)
        plane = np.ascontiguousarray(weight[None, ...], dtype=np.float32)
        return plane, float(weight.mean())

    def close(self):
        self.session = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
