"""ONNX Runtime execution provider and hardware backend resolver.

Ensures ONNX sessions prioritize the appropriate GPU backend (Intel DirectML,
NVIDIA CUDA / DirectML, or CPU fallback) based on the user's active GPU
Acceleration setting.
"""

from __future__ import annotations

import ctypes
from ctypes import wintypes
import os
import sys
from typing import Any, Dict, List, Optional, Tuple

_CACHED_DML_ADAPTERS: Optional[List[Dict[str, Any]]] = None


class DXGI_ADAPTER_DESC1(ctypes.Structure):
    _fields_ = [
        ("Description", wintypes.WCHAR * 128),
        ("VendorId", wintypes.UINT),
        ("DeviceId", wintypes.UINT),
        ("SubSysId", wintypes.UINT),
        ("Revision", wintypes.UINT),
        ("DedicatedVideoMemory", ctypes.c_size_t),
        ("DedicatedSystemMemory", ctypes.c_size_t),
        ("SharedSystemMemory", ctypes.c_size_t),
        ("AdapterLuid_LowPart", wintypes.DWORD),
        ("AdapterLuid_HighPart", wintypes.LONG),
        ("Flags", wintypes.UINT),
    ]


def scan_directml_adapters() -> List[Dict[str, Any]]:
    """Enumerate hardware DirectX adapters for DirectML provider targeting."""
    global _CACHED_DML_ADAPTERS
    if _CACHED_DML_ADAPTERS is not None:
        return _CACHED_DML_ADAPTERS

    adapters: List[Dict[str, Any]] = []
    if sys.platform != "win32":
        _CACHED_DML_ADAPTERS = adapters
        return adapters

    try:
        dxgi = ctypes.windll.dxgi
        pFactory = ctypes.c_void_p()
        # IID_IDXGIFactory1: 770aae78-f26f-4dba-a829-253c83d1b387
        IID_IDXGIFactory1 = (ctypes.c_byte * 16)(
            0x78, 0xAE, 0x0A, 0x77, 0x6F, 0xF2, 0xBA, 0x4D,
            0xA8, 0x29, 0x25, 0x3C, 0x83, 0xD1, 0xB3, 0x87,
        )
        if dxgi.CreateDXGIFactory1(IID_IDXGIFactory1, ctypes.byref(pFactory)) == 0:
            vtable = ctypes.cast(
                pFactory, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))
            ).contents
            EnumAdapters1 = ctypes.WINFUNCTYPE(
                ctypes.c_long, ctypes.c_void_p, wintypes.UINT, ctypes.POINTER(ctypes.c_void_p)
            )(vtable[12])

            for i in range(16):
                pAdapter = ctypes.c_void_p()
                if EnumAdapters1(pFactory, i, ctypes.byref(pAdapter)) != 0:
                    break
                avtable = ctypes.cast(
                    pAdapter, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))
                ).contents
                GetDesc1 = ctypes.WINFUNCTYPE(
                    ctypes.c_long, ctypes.c_void_p, ctypes.POINTER(DXGI_ADAPTER_DESC1)
                )(avtable[10])
                desc = DXGI_ADAPTER_DESC1()
                GetDesc1(pAdapter, ctypes.byref(desc))
                Release = ctypes.WINFUNCTYPE(wintypes.ULONG, ctypes.c_void_p)(avtable[2])
                Release(pAdapter)

                # Skip software rendering adapters (e.g. Basic Render Driver)
                if desc.Flags & 2:
                    continue

                v_id = desc.VendorId
                name_lower = desc.Description.lower()
                if v_id == 0x8086 or "intel" in name_lower:
                    vendor = "intel"
                elif (
                    v_id == 0x10DE
                    or "nvidia" in name_lower
                    or "geforce" in name_lower
                    or "rtx" in name_lower
                ):
                    vendor = "nvidia"
                elif v_id == 0x1002 or "amd" in name_lower or "radeon" in name_lower:
                    vendor = "amd"
                else:
                    vendor = "unknown"

                adapters.append(
                    {
                        "device_id": i,
                        "name": str(desc.Description),
                        "vendor": vendor,
                        "vendor_id": hex(v_id),
                    }
                )

            ctypes.WINFUNCTYPE(wintypes.ULONG, ctypes.c_void_p)(vtable[2])(pFactory)
    except Exception as exc:
        print(f"[DirectML Probe] Warning: Failed to enumerate DXGI adapters: {exc}")

    _CACHED_DML_ADAPTERS = adapters
    return adapters


def get_selected_gpu_vendor(store=None) -> str:
    """Identify user-selected GPU Acceleration vendor ('intel', 'nvidia', 'amd', 'cpu')."""
    if store is None:
        try:
            from pixel_refine_desktop.ui.views.settings.General.general_store import (
                get_general_store,
            )

            store = get_general_store()
        except Exception:
            store = None

    vendor = ""
    backend_text = ""
    if store is not None and hasattr(store, "get"):
        vendor = str(store.get("device_vendor", "") or "").lower()
        if not vendor:
            selector = store.get("device_selector")
            if isinstance(selector, dict):
                vendor = str(selector.get("vendor", "") or "").lower()
        backend_text = str(store.get("device_backend", "") or "").lower()

    if not vendor:
        vendor = str(
            os.environ.get("TARGET_VENDOR", "")
            or os.environ.get("ONNX_TARGET_VENDOR", "")
        ).lower()

    if not vendor and backend_text:
        if "intel" in backend_text or "uhd" in backend_text or "iris" in backend_text:
            vendor = "intel"
        elif (
            "nvidia" in backend_text
            or "geforce" in backend_text
            or "rtx" in backend_text
            or "cuda" in backend_text
        ):
            vendor = "nvidia"
        elif "amd" in backend_text or "radeon" in backend_text:
            vendor = "amd"
        elif "cpu" in backend_text:
            vendor = "cpu"

    return vendor or "unknown"


def resolve_onnx_runtime_and_providers(
    runtime: str = "auto", store=None
) -> Tuple[str, List[Any]]:
    """Resolve ONNX execution providers prioritized by the active GPU Acceleration backend."""
    try:
        import onnxruntime as ort
    except ImportError as exc:
        raise RuntimeError("ONNX inference requires onnxruntime package.") from exc

    if store is None:
        try:
            from pixel_refine_desktop.ui.views.settings.General.general_store import (
                get_general_store,
            )

            store = get_general_store()
        except Exception:
            store = None

    if runtime is None and store is not None and hasattr(store, "get"):
        runtime = str(store.get("onnx_runtime", "auto")).strip().lower()
    else:
        runtime = str(runtime or "auto").strip().lower()

    if runtime not in ("auto", "dml", "cpu"):
        runtime = "auto"

    available = set(ort.get_available_providers())
    target_vendor = get_selected_gpu_vendor(store)

    # If CPU requested, or Auto with CPU explicitly selected as backend:
    if runtime == "cpu" or (runtime == "auto" and target_vendor == "cpu"):
        return "cpu", ["CPUExecutionProvider"]

    # For auto or dml: prioritize the GPU matching target_vendor
    dml_adapters = scan_directml_adapters()
    matching_adapter = next(
        (a for a in dml_adapters if a.get("vendor") == target_vendor), None
    )
    if matching_adapter is None and target_vendor not in ("intel", "cpu") and dml_adapters:
        # Default to discrete adapter if available
        matching_adapter = next(
            (a for a in dml_adapters if a.get("vendor") in ("nvidia", "amd")),
            dml_adapters[0],
        )

    providers: List[Any] = []
    has_gpu_ep = False

    if target_vendor == "nvidia":
        if "CUDAExecutionProvider" in available:
            providers.append("CUDAExecutionProvider")
            has_gpu_ep = True
        if "DmlExecutionProvider" in available:
            if matching_adapter is not None:
                providers.append(
                    ("DmlExecutionProvider", {"device_id": matching_adapter["device_id"]})
                )
            providers.append("DmlExecutionProvider")
            has_gpu_ep = True
    elif target_vendor == "intel":
        if "DmlExecutionProvider" in available:
            if matching_adapter is not None:
                providers.append(
                    ("DmlExecutionProvider", {"device_id": matching_adapter["device_id"]})
                )
            providers.append("DmlExecutionProvider")
            has_gpu_ep = True
    elif target_vendor == "amd":
        if "DmlExecutionProvider" in available:
            if matching_adapter is not None:
                providers.append(
                    ("DmlExecutionProvider", {"device_id": matching_adapter["device_id"]})
                )
            providers.append("DmlExecutionProvider")
            has_gpu_ep = True
    else:
        # Unknown vendor or generic auto: try CUDA then DirectML
        if "CUDAExecutionProvider" in available:
            providers.append("CUDAExecutionProvider")
            has_gpu_ep = True
        if "DmlExecutionProvider" in available:
            if matching_adapter is not None:
                providers.append(
                    ("DmlExecutionProvider", {"device_id": matching_adapter["device_id"]})
                )
            providers.append("DmlExecutionProvider")
            has_gpu_ep = True

    # Always provide CPU fallback
    providers.append("CPUExecutionProvider")

    # A configured DirectML adapter is already the DirectML provider.  Do not
    # append a second bare provider entry, otherwise ONNX Runtime warns about
    # a duplicate and the provider selection becomes less explicit.  Keep the
    # first entry so adapter-specific options such as device_id are preserved.
    unique_providers: List[Any] = []
    seen_provider_names: set[str] = set()
    for provider in providers:
        provider_name = provider[0] if isinstance(provider, tuple) else provider
        if provider_name in seen_provider_names:
            continue
        seen_provider_names.add(provider_name)
        unique_providers.append(provider)
    providers = unique_providers

    if not has_gpu_ep:
        return "cpu", ["CPUExecutionProvider"]

    primary = providers[0]
    ep_name = primary[0] if isinstance(primary, tuple) else primary
    resolved_runtime = (
        "dml"
        if ep_name == "DmlExecutionProvider"
        else ("cuda" if ep_name == "CUDAExecutionProvider" else "cpu")
    )
    return resolved_runtime, providers
