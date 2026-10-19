"""Serial resident WeightNet patches for RGB analysis and CFA/RGB fusion."""
from __future__ import annotations
from dataclasses import dataclass
from functools import wraps
import numpy as np

from .onnx_resident_aot import ResidentONNXGraph


def _serialized(function):
    @wraps(function)
    def wrapped(self, *args, **kwargs):
        with self._lock:
            return function(self, *args, **kwargs)
    return wrapped


def view(buffer, shape, *, vector=False):
    from taichi_vision.taichi_aot.engine import TaichiGPUBuffer
    result = TaichiGPUBuffer(buffer.size_bytes, buffer.handle, tuple(shape), buffer.dtype,
                             is_vector=vector, vector_dim=2 if vector else 1,
                             engine=buffer.engine, is_owner=False,
                             host_accessible=buffer.host_accessible)
    result._parent_ref = buffer
    return result


@dataclass
class ResidentImage:
    owner: object
    buffer: object
    shape: tuple

    def __del__(self):
        self.buffer.destroy()


@dataclass
class ResidentRank:
    owner: object
    indices: object
    offsets: tuple
    rank: int
    shape: tuple

    def flow(self, *, full_shape, flow_shape, base_transform=None):
        return self.owner.compose_flow(self, full_shape, flow_shape, base_transform)


class ResidentConfidence:
    def __init__(self, owner, buffer):
        self.owner, self.buffer = owner, buffer
        self.shape = (1, *buffer.shape)

    def device(self, scale=1.0):
        if self.buffer is None:
            raise RuntimeError("Resident confidence ownership was already transferred")
        if scale != 1.0:
            self.owner.dispatch("scale", image=self.buffer, output=self.buffer, factor=float(scale))
        result, self.buffer = self.buffer, None
        return result

    def __del__(self):
        if self.buffer is not None:
            self.buffer.destroy()


class ResidentScalar:
    """Keep alpha reporting on device until explicit final float conversion."""
    def __init__(self, owner, buffer):
        self.owner, self.buffer, self.cached = owner, buffer, None

    def __add__(self, other):
        output = self.owner.allocate((1,))
        b = other.buffer if isinstance(other, ResidentScalar) else self.buffer
        self.owner.dispatch("scalar", a=self.buffer, b=b, output=output, ca=1.0,
                            cb=1.0 if isinstance(other, ResidentScalar) else 0.0,
                            bias=0.0 if isinstance(other, ResidentScalar) else float(other))
        return ResidentScalar(self.owner, output)

    __radd__ = __add__

    def __truediv__(self, divisor):
        output = self.owner.allocate((1,))
        self.owner.dispatch("scalar", a=self.buffer, b=self.buffer, output=output,
                            ca=1.0 / float(divisor), cb=0.0, bias=0.0)
        return ResidentScalar(self.owner, output)

    def __float__(self):
        if self.cached is None:
            self.cached = float(self.buffer.to_numpy()[0])
        return self.cached

    def __format__(self, spec):
        return "resident"

    def __del__(self):
        self.buffer.destroy()


class ResidentWeightNet(ResidentONNXGraph):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.metadata.get("patch_tools"):
            self.close()
            raise RuntimeError("Resident WeightNet requires an artifact compiled with --patch-tools")
        self.patch_size = int(self.get_inputs()[0].shape[-1])
        self._persistent = []
        self._offset_cache = {}
        self._work = None
        self.ref_tile = self.keep((self.patch_size ** 2,))
        self.support_tile = self.keep((self.patch_size ** 2,))
        window = np.hanning(self.patch_size).astype(np.float32)
        self.window = self.engine.upload(np.outer(window, window).astype(np.float32).reshape(-1), is_vector=False)
        self._persistent.append(self.window)
        self.dummy_indices = self.engine.upload(np.full((1, 1, 1), -1, np.int32), is_vector=False)
        self._persistent.append(self.dummy_indices)
        self.dummy_flow = self.engine.upload(np.zeros((1, 1, 2), np.float32), is_vector=True)
        self._persistent.append(self.dummy_flow)
        self.identity = self.engine.upload(np.eye(3, dtype=np.float32).reshape(-1), is_vector=False)
        self._persistent.append(self.identity)

    def allocate(self, shape, dtype=np.float32):
        return self.engine.allocate(tuple(shape), dtype=dtype, is_vector=False, host_accessible=False)

    def keep(self, shape, dtype=np.float32):
        buffer = self.allocate(shape, dtype)
        self._persistent.append(buffer)
        return buffer

    def dispatch(self, name, **args):
        self.module.run(f"deno_resident_{name}_v1", **args)

    def prepare_reference(self, source):
        return self.prepare(source), self

    def prepare(self, source):
        from taichi_vision import taichi_aot as aot
        gray = source if len(source.shape) == 2 else aot.cvtColor(source, aot.COLOR_RGB2GRAY, return_gpu=True)
        height, width = gray.shape
        output = self.allocate((height * width,))
        try:
            self.dispatch("proxy", gray=gray, output=output, width=width)
            return ResidentImage(self, output, (1, height, width))
        except Exception:
            output.destroy()
            raise
        finally:
            if gray is not source:
                gray.destroy()

    @_serialized
    def infer(self, reference, support, *, overlap, ghost_penalty, ghost_cutoff,
              stop_event=None, rank=None, **unused):
        if reference.owner is not self or support.owner is not self or reference.shape != support.shape:
            raise ValueError("Resident WeightNet requires same-owner matching analysis buffers")
        _, height, width = reference.shape
        if self._work is None or self._work[0].shape != (height, width):
            if self._work is not None:
                for buffer in self._work:
                    buffer.destroy()
            self._work = (self.allocate((height, width)), self.allocate((height, width)))
        numerator, denominator = self._work
        alpha_sum, output = self.allocate((1,)), self.allocate((height, width))
        try:
            self.dispatch("clear", numerator=numerator, denominator=denominator, alpha=alpha_sum)
            stride = max(1, self.patch_size - int(self.patch_size * float(overlap)))
            count = 0
            for y in range(0, height, stride):
                for x in range(0, width, stride):
                    cancelled = stop_event is not None and (
                        stop_event() if callable(stop_event) else stop_event.is_set())
                    if cancelled:
                        raise RuntimeError("Resident WeightNet cancelled")
                    y1, x1 = min(height, y + self.patch_size), min(width, x + self.patch_size)
                    y0, x0 = max(0, y1 - self.patch_size), max(0, x1 - self.patch_size)
                    self.dispatch("extract", reference=reference.buffer, support=support.buffer,
                                  ref_tile=self.ref_tile, support_tile=self.support_tile,
                                  height=height, width=width, size=self.patch_size, y0=y0, x0=x0)
                    values = self.run_device({"ref_img": self.ref_tile, "support_img": self.support_tile})
                    self.dispatch("stitch", weight=values["weight_map"], window=self.window,
                                  numerator=numerator, denominator=denominator, alpha=values["alpha"],
                                  alpha_sum=alpha_sum, size=self.patch_size, cur_h=y1-y0, cur_w=x1-x0,
                                  y0=y0, x0=x0)
                    count += 1
            self.dispatch("confidence", numerator=numerator, denominator=denominator, output=output,
                          indices=rank.indices if rank else self.dummy_indices,
                          rank=rank.rank if rank else -1, penalty=float(ghost_penalty), cutoff=float(ghost_cutoff))
            # Preserve the existing helper's alpha aggregation contract.
            self.dispatch("scalar", a=alpha_sum, b=alpha_sum, output=alpha_sum,
                          ca=1.0 / max(1, count ** 2), cb=0.0, bias=0.0)
            return ResidentConfidence(self, output), ResidentScalar(self, alpha_sum)
        except Exception:
            alpha_sum.destroy()
            output.destroy()
            raise

    def offset_buffers(self, offsets):
        key = tuple((v.dx_proxy, v.dy_proxy, v.dx_full, v.dy_full) for v in offsets)
        if key not in self._offset_cache:
            proxy = self.engine.upload(np.asarray([(v[0], v[1]) for v in key], np.int32), is_vector=False)
            full = self.engine.upload(np.asarray([(v[2], v[3]) for v in key], np.int32), is_vector=False)
            self._offset_cache[key] = proxy, full
            self._persistent.extend((proxy, full))
        return self._offset_cache[key]

    def candidates(self, reference, support, offsets, *, max_neighbors, telemetry, **options):
        import time
        _, height, width = support.shape
        started = time.perf_counter()
        cell_size = 10
        proxy_offsets, _ = self.offset_buffers(offsets)
        cell_shape = ((height + cell_size - 1) // cell_size,
                      (width + cell_size - 1) // cell_size)
        raw = self.allocate((min(max_neighbors, len(offsets)), *cell_shape), np.int32)
        indices = self.allocate((raw.shape[0], height, width), np.int32)
        try:
            self.dispatch("multi_patch_topk_kernel",
                          reference=view(reference.buffer, reference.shape),
                          candidate=view(support.buffer, support.shape),
                          offsets=proxy_offsets, indices=raw, height=height, width=width,
                          channels=reference.shape[0], candidate_count=len(offsets),
                          neighbor_count=raw.shape[0], cell_size=cell_size)
            self.dispatch("coherent_cells", indices=raw, output=indices,
                          height=height, width=width, cell_size=cell_size,
                          border_y=min(height, 2+max(abs(v.dy_proxy) for v in offsets)),
                          border_x=min(width, 2+max(abs(v.dx_proxy) for v in offsets)))
            telemetry.record("local_patch_search", started)
            telemetry.searched(len(offsets))
            for rank in range(indices.shape[0]):
                selected = ResidentRank(self, indices, tuple(offsets), rank, (height, width))
                candidate = ResidentImage(self, self.allocate((height*width,)), support.shape)
                self.dispatch("gather", source=support.buffer, indices=indices,
                              offsets=proxy_offsets, output=candidate.buffer,
                              height=height, width=width, rank=rank)
                started = time.perf_counter()
                confidence, alpha = self.infer(reference, candidate, rank=selected, **options)
                telemetry.record("weightnet", started)
                telemetry.candidate()
                yield selected, None, confidence, alpha
                del candidate
        finally:
            raw.destroy()
            indices.destroy()

    def compose_flow(self, rank, full_shape, flow_shape, base_transform=None):
        from taichi_vision.taichi_aot.engine import TaichiGPUBuffer
        mode, inverse, owned = 0, self.identity, None
        base = self.dummy_flow
        if isinstance(base_transform, TaichiGPUBuffer):
            base, flow_shape, mode = base_transform, base_transform.shape[:2], 1
        elif base_transform is not None:
            inverse = self.engine.upload(np.linalg.inv(np.asarray(base_transform, np.float32)).astype(np.float32).reshape(-1), is_vector=False)
            owned, mode = inverse, 2
        output = self.engine.allocate((*flow_shape, 2), dtype=np.float32, is_vector=True, vector_dim=2)
        try:
            self.dispatch("flow", indices=rank.indices, offsets=self.offset_buffers(rank.offsets)[1],
                          base=base.view_as_vector(False) if base.is_vector else base,
                          inverse=inverse, output=output.view_as_vector(False), rank=rank.rank, mode=mode,
                          height=rank.shape[0], width=rank.shape[1], full_h=full_shape[0], full_w=full_shape[1])
            return output
        except Exception:
            output.destroy()
            raise
        finally:
            if owned is not None:
                owned.destroy()

    def close(self):
        for buffer in getattr(self, "_persistent", ()):
            buffer.destroy()
        if getattr(self, "_work", None) is not None:
            for buffer in self._work:
                buffer.destroy()
        super().close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass
