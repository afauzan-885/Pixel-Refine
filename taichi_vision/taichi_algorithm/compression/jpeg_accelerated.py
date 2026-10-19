"""Optional JPEG codec routing for vendor hardware and the Taichi fallback.

The existing ``jpeg_aot`` API remains unchanged. This module is an opt-in
facade: Intel's native adapter is preferred when installed, followed by
NVIDIA nvImageCodec, then the established Taichi encoder (or Pillow CPU
decoder, because this package has no general lossy-JPEG Taichi decoder).
"""

from __future__ import annotations

import importlib
import os
from pathlib import Path
import threading
from typing import Any


class JpegBackendUnavailableError(RuntimeError):
    """Raised when an explicitly requested JPEG backend cannot be used."""


_TLS = threading.local()
_DLL_DIRECTORY_HANDLES: list[Any] = []


def _load_nvimgcodec():
    """Load nvImageCodec after registering its Windows DLL directories."""
    if os.name == "nt" and not _DLL_DIRECTORY_HANDLES:
        site_packages = Path(__file__).resolve().parents[2] / ".." / "venv" / "Lib" / "site-packages"
        # The normal installed-package layout is not necessarily this source
        # tree's sibling venv. Use the active interpreter's site-packages too.
        try:
            import site

            roots = [Path(p) for p in site.getsitepackages()]
        except Exception:
            roots = []
        roots.insert(0, site_packages.resolve())
        for root in roots:
            for relative in (
                "nvidia/nvjpeg/bin",
                "nvidia/nvimgcodec",
                "nvidia/nvimgcodec/extensions",
                "torch/lib",
            ):
                directory = root / relative
                if directory.is_dir():
                    try:
                        _DLL_DIRECTORY_HANDLES.append(os.add_dll_directory(str(directory)))
                    except OSError:
                        pass
    try:
        from nvidia import nvimgcodec
    except Exception as exc:
        raise JpegBackendUnavailableError(f"NVIDIA nvImageCodec tidak tersedia: {exc}") from exc
    return nvimgcodec


def _load_intel_adapter(operation: str):
    """Load an optional native Intel JPEG provider, if one is packaged.

    The Intel Media SDK runtime alone is not enough: its codec ABI must be
    wrapped and qualified before it can be selected as an encoder/decoder.
    The adapter module contract is deliberately small and vendor-local.
    """
    try:
        adapter = importlib.import_module("taichi_vision._intel_jpeg")
    except ModuleNotFoundError as exc:
        if exc.name == "taichi_vision._intel_jpeg":
            raise JpegBackendUnavailableError(
                "Adapter JPEG Intel belum terpasang; sesi Media SDK saja belum membuktikan codec aktif."
            ) from exc
        raise JpegBackendUnavailableError(f"Dependensi adapter Intel tidak tersedia: {exc}") from exc
    method_name = f"{operation}_jpeg"
    if not callable(getattr(adapter, method_name, None)):
        raise JpegBackendUnavailableError(f"Adapter Intel tidak menyediakan {method_name}.")
    return adapter


def _normalize_subsampling(value: str):
    # Keep accepted public spellings explicit instead of silently changing
    # unsupported JPEG sampling modes.
    aliases = {"420": "420", "422": "422", "444": "444", "gray": "gray", "400": "gray"}
    normalized = str(value).strip().lower().replace(":", "").replace("-", "")
    if normalized not in aliases:
        raise ValueError("subsampling harus salah satu dari '420', '422', '444', atau 'gray'")
    return aliases[normalized]


def _as_nv_image(image, nv):
    """Wrap HxW or HxWx3 uint8 input without copying GPU-resident tensors."""
    import numpy as np

    is_cuda = hasattr(image, "__cuda_array_interface__")
    if not is_cuda and callable(getattr(image, "__dlpack_device__", None)):
        try:
            is_cuda = int(image.__dlpack_device__()[0]) == 2
        except Exception:
            is_cuda = False
    if is_cuda:
        shape = tuple(int(v) for v in image.shape)
        color = nv.ColorSpec.GRAY if len(shape) == 2 or (len(shape) == 3 and shape[-1] == 1) else nv.ColorSpec.SRGB
        return nv.as_image(image, color_spec=color)
    array = np.asarray(image)
    if array.dtype != np.uint8:
        raise TypeError(f"JPEG input harus uint8; dtype diterima: {array.dtype}")
    if array.ndim == 3 and array.shape[2] == 1:
        array = array[:, :, 0]
    if array.ndim not in (2, 3) or (array.ndim == 3 and array.shape[2] != 3):
        raise ValueError("JPEG input harus berbentuk HxW, HxWx1, atau HxWx3")
    if not array.flags.c_contiguous:
        array = np.ascontiguousarray(array)
    color = nv.ColorSpec.GRAY if array.ndim == 2 else nv.ColorSpec.SRGB
    return nv.as_image(array, color_spec=color)


def _nvidia_codec(nv, device_id: int, operation: str, backend_kind):
    key = (int(device_id), operation, backend_kind)
    cache = getattr(_TLS, "nv_codecs", None)
    if cache is None:
        cache = _TLS.nv_codecs = {}
    if key not in cache:
        codec_type = nv.Encoder if operation == "encoder" else nv.Decoder
        cache[key] = codec_type(device_id=int(device_id), backends=[nv.Backend(backend_kind)])
    return cache[key]


def _failed_nvidia_hardware_routes() -> set[tuple[int, str]]:
    failed = getattr(_TLS, "nv_hardware_unavailable", None)
    if failed is None:
        failed = _TLS.nv_hardware_unavailable = set()
    return failed


def _encode_nvidia(image, *, quality: int, subsampling: str, device_id: int) -> tuple[bytes, str]:
    nv = _load_nvimgcodec()
    nv_image = _as_nv_image(image, nv)
    sampling = _normalize_subsampling(subsampling)
    if sampling == "gray" and nv_image.num_channels != 1:
        raise ValueError("subsampling='gray' memerlukan input satu kanal")
    if sampling != "gray" and nv_image.num_channels == 1:
        raise ValueError("input grayscale memerlukan subsampling='gray'")
    chroma = {
        "420": nv.ChromaSubsampling.CSS_420,
        "422": nv.ChromaSubsampling.CSS_422,
        "444": nv.ChromaSubsampling.CSS_444,
        "gray": nv.ChromaSubsampling.CSS_GRAY,
    }[sampling]
    color = nv.ColorSpec.GRAY if sampling == "gray" else nv.ColorSpec.SRGB
    params = nv.EncodeParams(
        nv.QualityType.QUALITY,
        float(quality),
        color,
        chroma,
    )
    route_key = (int(device_id), "encoder")
    failed_routes = _failed_nvidia_hardware_routes()
    if route_key not in failed_routes:
        try:
            stream = _nvidia_codec(
                nv, device_id, "encoder", nv.BackendKind.HW_GPU_ONLY
            ).encode(nv_image, ".jpg", params=params)
            return memoryview(stream).tobytes(), "nvidia-hardware"
        except Exception:
            # Some GPU generations have no fixed-function JPEG engine. Cache
            # the unsupported route for this thread/device to avoid retrying
            # a known-impossible codec on every frame.
            failed_routes.add(route_key)
    stream = _nvidia_codec(
        nv, device_id, "encoder", nv.BackendKind.HYBRID_CPU_GPU
    ).encode(nv_image, ".jpg", params=params)
    return memoryview(stream).tobytes(), "nvidia-hybrid"


def encode_jpeg_accelerated(
    image,
    *,
    quality: int = 85,
    subsampling: str = "420",
    backend: str = "auto",
    device_id: int = 0,
    return_backend: bool = False,
):
    """Encode JPEG using Intel, NVIDIA, then Taichi according to availability.

    ``image`` is uint8 HxW/HxWx3 data or a GPU array/tensor. The returned JPEG
    payload remains ``bytes``. Set ``return_backend=True`` to also receive the
    backend actually used (``intel``, ``nvidia-hardware``, ``nvidia-hybrid``,
    or ``taichi``).
    ``backend`` may force ``auto``, ``intel``, ``nvidia``, or ``taichi``.
    """
    if not 1 <= int(quality) <= 100:
        raise ValueError("quality harus berada pada rentang 1..100")
    selected = str(backend).lower()
    if selected not in {"auto", "intel", "nvidia", "taichi"}:
        raise ValueError("backend harus 'auto', 'intel', 'nvidia', atau 'taichi'")
    errors: list[str] = []
    candidates = ("intel", "nvidia", "taichi") if selected == "auto" else (selected,)
    for candidate in candidates:
        try:
            if candidate == "intel":
                adapter = _load_intel_adapter("encode")
                payload = adapter.encode_jpeg(
                    image, quality=int(quality), subsampling=_normalize_subsampling(subsampling)
                )
                payload = bytes(payload)
            elif candidate == "nvidia":
                payload, nvidia_mode = _encode_nvidia(
                    image,
                    quality=int(quality),
                    subsampling=subsampling,
                    device_id=int(device_id),
                )
                candidate = nvidia_mode
            else:
                from .jpeg_aot import jpeg_encode_aot

                payload = jpeg_encode_aot(image, quality=int(quality), subsampling=subsampling)
                candidate = "taichi"
            return (payload, candidate) if return_backend else payload
        except Exception as exc:
            errors.append(f"{candidate}: {exc}")
            if selected != "auto":
                raise JpegBackendUnavailableError(errors[-1]) from exc
    raise JpegBackendUnavailableError("Semua backend JPEG gagal: " + " | ".join(errors))


def decode_jpeg_accelerated(
    jpeg_data: bytes | bytearray | memoryview,
    *,
    backend: str = "auto",
    device_id: int = 0,
    output: str = "device",
    return_backend: bool = False,
):
    """Decode JPEG with Intel, NVIDIA, then Pillow CPU fallback.

    ``output='device'`` returns the nvImageCodec device image where supported;
    CPU fallback returns a uint8 NumPy array. ``output='cpu'`` returns a uint8
    NumPy array for either accelerated backend or CPU fallback. This package
    currently has no general baseline-JPEG decoder implemented in Taichi.
    """
    selected = str(backend).lower()
    if selected not in {"auto", "intel", "nvidia", "cpu"}:
        raise ValueError("backend harus 'auto', 'intel', 'nvidia', atau 'cpu'")
    if output not in {"device", "cpu"}:
        raise ValueError("output harus 'device' atau 'cpu'")
    payload = bytes(jpeg_data)
    candidates = ("intel", "nvidia", "cpu") if selected == "auto" else (selected,)
    errors: list[str] = []
    for candidate in candidates:
        try:
            if candidate == "intel":
                adapter = _load_intel_adapter("decode")
                decoded = adapter.decode_jpeg(payload, output=output, device_id=int(device_id))
            elif candidate == "nvidia":
                nv = _load_nvimgcodec()
                route_key = (int(device_id), "decoder")
                failed_routes = _failed_nvidia_hardware_routes()
                if route_key not in failed_routes:
                    try:
                        decoded = _nvidia_codec(
                            nv, device_id, "decoder", nv.BackendKind.HW_GPU_ONLY
                        ).read(nv.CodeStream(payload))
                        candidate = "nvidia-hardware"
                    except Exception:
                        failed_routes.add(route_key)
                if route_key in failed_routes:
                    decoded = _nvidia_codec(
                        nv, device_id, "decoder", nv.BackendKind.HYBRID_CPU_GPU
                    ).read(nv.CodeStream(payload))
                    candidate = "nvidia-hybrid"
                if output == "device":
                    decoded = decoded.cuda(device_id=int(device_id))
                else:
                    import numpy as np

                    host_image = decoded.cpu()
                    try:
                        decoded = np.asarray(host_image).copy()
                    except Exception:
                        # Image exports DLPack but does not promise NumPy's
                        # array protocol. PyTorch is optional and used only as
                        # a bridge when the array protocol is unavailable.
                        try:
                            import torch
                        except Exception as exc:
                            raise JpegBackendUnavailableError(
                                "Konversi output nvImageCodec ke NumPy memerlukan array protocol atau PyTorch."
                            ) from exc
                        decoded = torch.from_dlpack(host_image.to_dlpack()).numpy().copy()
            else:
                from PIL import Image
                import io
                import numpy as np

                with Image.open(io.BytesIO(payload)) as decoded_image:
                    decoded = np.asarray(decoded_image.convert("RGB")).copy()
            return (decoded, candidate) if return_backend else decoded
        except Exception as exc:
            errors.append(f"{candidate}: {exc}")
            if selected != "auto":
                raise JpegBackendUnavailableError(errors[-1]) from exc
    raise JpegBackendUnavailableError("Semua backend JPEG gagal: " + " | ".join(errors))


def jpeg_acceleration_status() -> dict[str, Any]:
    """Return installation-level availability without initializing a codec."""
    try:
        import importlib.util

        nvidia_available = importlib.util.find_spec("nvidia.nvimgcodec") is not None
    except (ImportError, ModuleNotFoundError, ValueError):
        nvidia_available = False
    try:
        import importlib.util

        intel_adapter_available = importlib.util.find_spec("taichi_vision._intel_jpeg") is not None
    except (ImportError, ModuleNotFoundError, ValueError):
        intel_adapter_available = False
    return {
        "priority": ["intel", "nvidia", "taichi_or_cpu"],
        "intel": {
            "adapter_installed": intel_adapter_available,
            "qualified_here": False,
            "note": "Runtime MFX tersedia, tetapi codec adapter belum lolos validasi end-to-end.",
        },
        "nvidia": {
            "nvimgcodec_installed": nvidia_available,
            "mode": "mencoba HW_GPU_ONLY; fallback nvJPEG HYBRID_CPU_GPU",
        },
        "fallback": {
            "encode": "Taichi AOT dengan backend yang sedang dikonfigurasi",
            "decode": "Pillow CPU; belum ada general JPEG decoder di Taichi",
        },
    }


__all__ = [
    "JpegBackendUnavailableError",
    "decode_jpeg_accelerated",
    "encode_jpeg_accelerated",
    "jpeg_acceleration_status",
]
