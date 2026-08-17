"""Small explicit Taichi-JIT focus leaves."""

import importlib

import numpy as np

try:
    _ti = importlib.import_module("taichi")
except ImportError:  # pragma: no cover - minimal installations
    _ti = None


if _ti is not None:

    @_ti.kernel
    def _gradient_kernel(
        image: _ti.types.ndarray(dtype=_ti.f32, ndim=2),
        laplacian: _ti.types.ndarray(dtype=_ti.f32, ndim=2),
        dx: _ti.types.ndarray(dtype=_ti.f32, ndim=2),
        dy: _ti.types.ndarray(dtype=_ti.f32, ndim=2),
    ):
        for y, x in _ti.ndrange(image.shape[0], image.shape[1]):
            ym = _ti.max(y - 1, 0)
            yp = _ti.min(y + 1, image.shape[0] - 1)
            xm = _ti.max(x - 1, 0)
            xp = _ti.min(x + 1, image.shape[1] - 1)
            tl = image[ym, xm]
            tm = image[ym, x]
            tr = image[ym, xp]
            ml = image[y, xm]
            mr = image[y, xp]
            bl = image[yp, xm]
            bm = image[yp, x]
            br = image[yp, xp]
            dx[y, x] = (tr + 2.0 * mr + br) - (tl + 2.0 * ml + bl)
            dy[y, x] = (bl + 2.0 * bm + br) - (tl + 2.0 * tm + tr)
            laplacian[y, x] = tm + bm + ml + mr - 4.0 * image[y, x]

    @_ti.kernel
    def _brenner_kernel(
        image: _ti.types.ndarray(dtype=_ti.f32, ndim=2),
        output: _ti.types.ndarray(dtype=_ti.f32, ndim=2),
    ):
        for y, x in _ti.ndrange(image.shape[0], image.shape[1]):
            if x + 2 < image.shape[1]:
                delta = image[y, x + 2] - image[y, x]
                output[y, x] = delta * delta
            else:
                output[y, x] = 0.0


def brenner_taichi(image: np.ndarray) -> np.ndarray:
    """Evaluate the two-pixel Brenner difference on an explicit CPU JIT."""

    if _ti is None:
        raise ImportError("backend='taichi' requires the taichi package")
    from taichi.lang import impl

    runtime = impl.get_runtime()
    if getattr(runtime, "prog", None) is None:
        _ti.init(arch=_ti.cpu, offline_cache=False)
    elif getattr(getattr(_ti, "cfg", None), "arch", None) != _ti.cpu:
        raise RuntimeError("backend='taichi' Brenner requires a CPU JIT runtime")
    source = np.ascontiguousarray(image, dtype=np.float32)
    output = np.empty_like(source, dtype=np.float32)
    _brenner_kernel(source, output)
    _ti.sync()
    return output


def gradients_taichi(image: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return ``(laplacian, dx, dy)`` from one explicit CPU-JIT kernel."""

    if _ti is None:
        raise ImportError("backend='taichi' requires the taichi package")
    from taichi.lang import impl

    runtime = impl.get_runtime()
    if getattr(runtime, "prog", None) is None:
        _ti.init(arch=_ti.cpu, offline_cache=False)
    elif getattr(getattr(_ti, "cfg", None), "arch", None) != _ti.cpu:
        raise RuntimeError("backend='taichi' gradients require a CPU JIT runtime")
    source = np.ascontiguousarray(image, dtype=np.float32)
    laplacian = np.empty_like(source, dtype=np.float32)
    dx = np.empty_like(source, dtype=np.float32)
    dy = np.empty_like(source, dtype=np.float32)
    _gradient_kernel(source, laplacian, dx, dy)
    _ti.sync()
    return laplacian, dx, dy


__all__ = ["brenner_taichi", "gradients_taichi"]
