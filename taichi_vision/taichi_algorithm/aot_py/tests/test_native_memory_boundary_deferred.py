"""Deferred native S1 checks for a bridge rebuilt from the hardened source.

DO NOT RUN while the user's no-compilation/native-execution restriction applies.
This file has no Taichi import or import-time native initialization. After the
restriction is lifted and a matching bridge/C API is built, set both
PIXEL_REFINE_RUN_NATIVE_S1=1 and PIXEL_REFINE_S1_TEST_BRIDGE to that bridge path.
PIXEL_REFINE_S1_ARCH_ID selects the bridge backend (2 CPU, 0 Vulkan); run each
profile separately on an actual device, including non-coherent Vulkan memory.
Allocation through the CPU/CUDA profiles reaches LlvmRuntime::allocate_memory;
the Vulkan profile reaches Runtime::allocate_memory. The same integration source
therefore exercises both virtual allocation dispatch paths when run later.
The tests cannot safely be used against an old binary without boundary guards.
"""

import ctypes as c
import os
import threading
import unittest


@unittest.skipUnless(
    os.environ.get("PIXEL_REFINE_RUN_NATIVE_S1") == "1"
    and os.environ.get("PIXEL_REFINE_S1_TEST_BRIDGE"),
    "deferred: requires explicit native execution authorization and rebuilt bridge",
)
class NativeMemoryBoundary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib = c.CDLL(os.environ["PIXEL_REFINE_S1_TEST_BRIDGE"])
        specs = {
            "init_aot_engine": ([c.c_int, c.c_int], c.c_void_p),
            "destroy_aot_engine": ([c.c_void_p], None),
            "get_last_engine_error": ([c.c_void_p], c.c_char_p),
            "clear_last_engine_error": ([c.c_void_p], None),
            "allocate_gpu_buffer": ([c.c_void_p, c.c_uint64, c.c_int], c.c_void_p),
            "free_gpu_buffer": ([c.c_void_p, c.c_void_p], None),
            "map_gpu_buffer": ([c.c_void_p, c.c_void_p], c.c_void_p),
            "unmap_gpu_buffer": ([c.c_void_p, c.c_void_p], None),
            "copy_gpu_buffer": ([c.c_void_p, c.c_void_p, c.c_void_p, c.c_uint64], None),
            "write_to_gpu_buffer": ([c.c_void_p, c.c_void_p, c.c_void_p, c.c_uint64], None),
            "read_from_gpu_buffer": ([c.c_void_p, c.c_void_p, c.c_void_p, c.c_uint64], None),
        }
        for name, (args, result) in specs.items():
            fn = getattr(cls.lib, name)
            fn.argtypes, fn.restype = args, result

    def setUp(self):
        self.arch = int(os.environ.get("PIXEL_REFINE_S1_ARCH_ID", "2"))
        self.ctx = self.lib.init_aot_engine(self.arch, 0)
        self.assertTrue(self.ctx, f"backend {self.arch} context creation failed")
        self.addCleanup(self.lib.destroy_aot_engine, self.ctx)

    def alloc(self, size=16, host_accessible=1):
        result = self.lib.allocate_gpu_buffer(self.ctx, size, host_accessible)
        self.assertTrue(result, self.error())
        return result

    def error(self, ctx=None):
        return (self.lib.get_last_engine_error(ctx or self.ctx) or b"").decode()

    def test_oversize_transfer_rejected_without_changing_host_or_device_bytes(self):
        memory = self.alloc()
        initial = c.create_string_buffer(bytes(range(16)), 16)
        self.lib.write_to_gpu_buffer(self.ctx, memory, initial, 16)
        self.assertEqual(self.error(), "")
        oversized = c.create_string_buffer(b"X" * 32, 32)
        self.lib.write_to_gpu_buffer(self.ctx, memory, oversized, 17)
        self.assertIn("capacity", self.error())
        self.lib.read_from_gpu_buffer(self.ctx, memory, oversized, 17)
        self.assertIn("capacity", self.error())
        self.assertEqual(oversized.raw, b"X" * 32)
        actual = c.create_string_buffer(16)
        self.lib.read_from_gpu_buffer(self.ctx, memory, actual, 16)
        self.assertEqual(actual.raw, initial.raw)

    def test_copy_direction_and_both_capacities(self):
        source, target = self.alloc(), self.alloc()
        expected = c.create_string_buffer(bytes(range(16)), 16)
        self.lib.write_to_gpu_buffer(self.ctx, source, expected, 16)
        self.lib.copy_gpu_buffer(self.ctx, source, target, 16)
        self.assertEqual(self.error(), "")
        actual = c.create_string_buffer(16)
        self.lib.read_from_gpu_buffer(self.ctx, target, actual, 16)
        self.assertEqual(actual.raw, expected.raw)
        small = self.alloc(8)
        for src, dst in ((small, target), (source, small)):
            self.lib.copy_gpu_buffer(self.ctx, src, dst, 16)
            self.assertIn("capacity", self.error())

    def test_foreign_and_freed_handles_are_rejected(self):
        foreign_ctx = self.lib.init_aot_engine(self.arch, 0)
        self.assertTrue(foreign_ctx)
        self.addCleanup(self.lib.destroy_aot_engine, foreign_ctx)
        memory = self.alloc()
        self.assertFalse(self.lib.map_gpu_buffer(foreign_ctx, memory))
        self.assertIn("owned", self.error(foreign_ctx))
        self.lib.free_gpu_buffer(self.ctx, memory)
        self.assertFalse(self.lib.map_gpu_buffer(self.ctx, memory))
        self.assertIn("freed", self.error())
        self.lib.free_gpu_buffer(self.ctx, memory)
        self.assertIn("freed", self.error())

    def test_mapped_state_and_free_cleanup(self):
        memory, target = self.alloc(), self.alloc()
        self.assertTrue(self.lib.map_gpu_buffer(self.ctx, memory))
        self.assertFalse(self.lib.map_gpu_buffer(self.ctx, memory))
        self.assertIn("already mapped", self.error())
        self.lib.copy_gpu_buffer(self.ctx, memory, target, 16)
        self.assertIn("mapped", self.error())
        self.lib.free_gpu_buffer(self.ctx, memory)
        self.assertEqual(self.error(), "")
        self.lib.unmap_gpu_buffer(self.ctx, target)
        self.assertIn("not mapped", self.error())

    def test_concurrent_free_consumes_handle_once_without_native_crash(self):
        memory = self.alloc()
        barrier = threading.Barrier(3)

        def release():
            barrier.wait(timeout=10)
            self.lib.free_gpu_buffer(self.ctx, memory)

        workers = [threading.Thread(target=release) for _ in range(2)]
        for worker in workers:
            worker.start()
        barrier.wait(timeout=10)
        for worker in workers:
            worker.join(timeout=10)
            self.assertFalse(worker.is_alive(), "native free deadlocked")
        self.assertIn("freed", self.error())

    def test_zero_allocation_null_host_and_uint64_size_are_checked(self):
        self.assertFalse(self.lib.allocate_gpu_buffer(self.ctx, 0, 1))
        self.assertIn("positive", self.error())
        memory = self.alloc()
        self.lib.write_to_gpu_buffer(self.ctx, memory, None, 1)
        self.assertIn("null host", self.error())
        self.lib.read_from_gpu_buffer(self.ctx, memory, None, (1 << 64) - 1)
        self.assertIn("capacity", self.error())

    def test_readback_after_device_copy_uses_host_read_staging(self):
        upload = self.alloc(257)
        device_buffer = self.alloc(257, host_accessible=0)
        for generation in range(5):
            payload = bytes((index + generation * 37) % 256 for index in range(257))
            expected = c.create_string_buffer(payload, 257)
            self.lib.write_to_gpu_buffer(self.ctx, upload, expected, 257)
            self.assertEqual(self.error(), "")
            self.lib.copy_gpu_buffer(self.ctx, upload, device_buffer, 257)
            self.assertEqual(self.error(), "")
            for memory in (device_buffer, upload):
                actual = c.create_string_buffer(257)
                self.lib.read_from_gpu_buffer(self.ctx, memory, actual, 257)
                self.assertEqual(self.error(), "")
                self.assertEqual(actual.raw, payload)
        # Both public buffers must remain usable after temporary staging cleanup.
        self.lib.copy_gpu_buffer(self.ctx, device_buffer, upload, 257)
        self.assertEqual(self.error(), "")


if __name__ == "__main__":
    unittest.main()
