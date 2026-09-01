package org.pixelrefine.genericui

import org.pixelrefine.genericui.domain.aot.*
import java.nio.ByteBuffer
import java.nio.ByteOrder
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertNotNull
import kotlin.test.assertNull
import kotlin.test.assertTrue
import kotlin.test.assertFalse
import kotlin.test.assertFailsWith

/**
 * Test komprehensif untuk Taichi AOT integration:
 * - Lifecycle (init, upload, run, destroy)
 * - Output dimensions (resize, demosaic)
 * - Buffer management (release, double-release)
 * - Error handling (not initialized, invalid args)
 * - Multi-backend support
 * - GPU buffer properties
 */
class TaichiAotIntegrationTest {

    // =========================================================================
    // 1. LIFECYCLE TESTS
    // =========================================================================

    @Test
    fun testTaichiAotInitAndDestroy() {
        println("=== [AOT 1] LIFECYCLE: INIT AND DESTROY ===")
        assertFalse(TaichiAot.isReady, "Should not be ready before init")

        TaichiAot.init(arch = "vulkan", device = 0)
        assertTrue(TaichiAot.isReady, "Should be ready after init")
        assertEquals(AotArch.VULKAN, TaichiAot.activeArch)
        assertEquals(0, TaichiAot.activeDevice)

        TaichiAot.destroy()
        assertFalse(TaichiAot.isReady, "Should not be ready after destroy")
        println("✔ TaichiAot init and destroy verified")
    }

    @Test
    fun testTaichiAotInitWithEnum() {
        println("\n=== [AOT 2] LIFECYCLE: INIT WITH ENUM ===")
        TaichiAot.init(arch = AotArch.CUDA, device = 1)
        assertTrue(TaichiAot.isReady)
        assertEquals(AotArch.CUDA, TaichiAot.activeArch)
        assertEquals(1, TaichiAot.activeDevice)

        TaichiAot.destroy()
        println("✔ TaichiAot init with enum verified")
    }

    @Test
    fun testTaichiAotInitMultipleBackends() {
        println("\n=== [AOT 3] LIFECYCLE: MULTIPLE BACKENDS ===")
        val backends = listOf("cpu", "vulkan", "cuda", "opengl", "gles")

        backends.forEach { arch ->
            TaichiAot.init(arch = arch)
            assertTrue(TaichiAot.isReady, "Should be ready for $arch")
            assertEquals(AotArch.fromString(arch), TaichiAot.activeArch)
            TaichiAot.destroy()
            assertFalse(TaichiAot.isReady, "Should not be ready after destroy for $arch")
        }
        println("✔ TaichiAot multiple backends verified")
    }

    // =========================================================================
    // 2. UPLOAD TESTS
    // =========================================================================

    @Test
    fun testTaichiAotUpload() {
        println("\n=== [AOT 4] UPLOAD: BASIC UPLOAD ===")
        TaichiAot.init(arch = "cpu")

        val width = 1920
        val height = 1080
        val channels = 3
        val byteSize = width * height * channels * 4 // Float32

        val buffer = ByteBuffer.allocateDirect(byteSize).order(ByteOrder.nativeOrder())
        for (i in 0 until 100) {
            buffer.putFloat(0.5f)
        }
        buffer.rewind()

        val gpuBuffer = TaichiAot.upload(
            buffer = buffer,
            width = width,
            height = height,
            channels = channels,
            dtype = AotDtype.FLOAT32
        )

        assertNotNull(gpuBuffer)
        assertEquals(width, gpuBuffer.width)
        assertEquals(height, gpuBuffer.height)
        assertEquals(channels, gpuBuffer.channels)
        assertEquals(byteSize.toLong(), gpuBuffer.byteSize)
        assertFalse(gpuBuffer.isReleased)

        gpuBuffer.release()
        TaichiAot.destroy()
        println("✔ TaichiAot upload verified")
    }

    @Test
    fun testTaichiAotUploadDifferentDtypes() {
        println("\n=== [AOT 5] UPLOAD: DIFFERENT DTYPES ===")
        TaichiAot.init(arch = "cpu")

        val width = 100
        val height = 100

        // Float32
        val float32Buffer = ByteBuffer.allocateDirect(width * height * 4)
        val float32Gpu = TaichiAot.upload(float32Buffer, width, height, 1, AotDtype.FLOAT32)
        assertEquals(4, float32Gpu.dtype.bytesPerElement)
        assertEquals((width * height * 4).toLong(), float32Gpu.byteSize)

        // Float16
        val float16Buffer = ByteBuffer.allocateDirect(width * height * 2)
        val float16Gpu = TaichiAot.upload(float16Buffer, width, height, 1, AotDtype.FLOAT16)
        assertEquals(2, float16Gpu.dtype.bytesPerElement)
        assertEquals((width * height * 2).toLong(), float16Gpu.byteSize)

        // UINT8
        val uint8Buffer = ByteBuffer.allocateDirect(width * height)
        val uint8Gpu = TaichiAot.upload(uint8Buffer, width, height, 1, AotDtype.UINT8)
        assertEquals(1, uint8Gpu.dtype.bytesPerElement)
        assertEquals((width * height).toLong(), uint8Gpu.byteSize)

        float32Gpu.release()
        float16Gpu.release()
        uint8Gpu.release()
        TaichiAot.destroy()
        println("✔ TaichiAot upload different dtypes verified")
    }

    // =========================================================================
    // 3. RUN TESTS
    // =========================================================================

    @Test
    fun testTaichiAotRunReturnGpu() {
        println("\n=== [AOT 6] RUN: RETURN GPU ===")
        TaichiAot.init(arch = "cpu")

        val buffer = ByteBuffer.allocateDirect(100 * 100 * 4)
        val srcGpu = TaichiAot.upload(buffer, 100, 100, 1)

        val result = TaichiAot.run(
            "test_graph",
            "src" to srcGpu,
            returnGpu = true
        )

        assertTrue(result is TaichiGpuBuffer)
        val resultGpu = result as TaichiGpuBuffer
        assertEquals(100, resultGpu.width)
        assertEquals(100, resultGpu.height)
        assertFalse(resultGpu.isReleased)

        srcGpu.release()
        resultGpu.release()
        TaichiAot.destroy()
        println("✔ TaichiAot run return GPU verified")
    }

    @Test
    fun testTaichiAotRunReturnCpu() {
        println("\n=== [AOT 7] RUN: RETURN CPU ===")
        TaichiAot.init(arch = "cpu")

        val buffer = ByteBuffer.allocateDirect(100 * 100 * 4)
        val srcGpu = TaichiAot.upload(buffer, 100, 100, 1)

        val result = TaichiAot.run(
            "test_graph",
            "src" to srcGpu,
            returnGpu = false
        )

        assertTrue(result is ByteBuffer)
        val cpuBuffer = result as ByteBuffer
        assertEquals(100 * 100 * 4, cpuBuffer.capacity())

        srcGpu.release()
        TaichiAot.destroy()
        println("✔ TaichiAot run return CPU verified")
    }

    @Test
    fun testTaichiAotRunNotInitialized() {
        println("\n=== [AOT 8] RUN: NOT INITIALIZED ===")
        TaichiAot.destroy() // Ensure not initialized

        assertFailsWith<IllegalStateException> {
            TaichiAot.run("test_graph", "src" to TaichiGpuBuffer(id = 1, width = 10, height = 10))
        }
        println("✔ TaichiAot run not initialized verified")
    }

    @Test
    fun testTaichiAotRunNoBufferArg() {
        println("\n=== [AOT 9] RUN: NO BUFFER ARG ===")
        TaichiAot.init(arch = "cpu")

        assertFailsWith<IllegalStateException> {
            TaichiAot.run("test_graph", "param" to 42)
        }

        TaichiAot.destroy()
        println("✔ TaichiAot run no buffer arg verified")
    }

    // =========================================================================
    // 4. OUTPUT DIMENSIONS TESTS
    // =========================================================================

    @Test
    fun testTaichiAotRunResizeDimensions() {
        println("\n=== [AOT 10] OUTPUT DIMENSIONS: RESIZE ===")
        TaichiAot.init(arch = "cpu")

        val srcBuffer = ByteBuffer.allocateDirect(1920 * 1080 * 3 * 4)
        val srcGpu = TaichiAot.upload(srcBuffer, 1920, 1080, 3)

        // Resize to 960x540
        val result = TaichiAot.run(
            "bilinear_resize",
            "src" to srcGpu,
            "target_w" to 960,
            "target_h" to 540,
            returnGpu = true
        )

        assertTrue(result is TaichiGpuBuffer)
        val resultGpu = result as TaichiGpuBuffer
        assertEquals(960, resultGpu.width, "Width should be target_w")
        assertEquals(540, resultGpu.height, "Height should be target_h")
        assertEquals(3, resultGpu.channels, "Channels should be preserved")

        srcGpu.release()
        resultGpu.release()
        TaichiAot.destroy()
        println("✔ TaichiAot resize dimensions verified")
    }

    @Test
    fun testTaichiAotRunDemosaicChannels() {
        println("\n=== [AOT 11] OUTPUT DIMENSIONS: DEMOSAIC ===")
        TaichiAot.init(arch = "cpu")

        val rawBuffer = ByteBuffer.allocateDirect(100 * 100 * 1 * 4)
        val rawGpu = TaichiAot.upload(rawBuffer, 100, 100, 1)

        // Demosaic (1 channel -> 3 channels)
        val result = TaichiAot.run(
            "hamilton_demosaic",
            "src" to rawGpu,
            returnGpu = true
        )

        assertTrue(result is TaichiGpuBuffer)
        val resultGpu = result as TaichiGpuBuffer
        assertEquals(100, resultGpu.width, "Width should be preserved")
        assertEquals(100, resultGpu.height, "Height should be preserved")
        assertEquals(3, resultGpu.channels, "Channels should be 3 after demosaic")

        rawGpu.release()
        resultGpu.release()
        TaichiAot.destroy()
        println("✔ TaichiAot demosaic channels verified")
    }

    @Test
    fun testTaichiAotRunPreserveDimensions() {
        println("\n=== [AOT 12] OUTPUT DIMENSIONS: PRESERVE ===")
        TaichiAot.init(arch = "cpu")

        val srcBuffer = ByteBuffer.allocateDirect(200 * 200 * 3 * 4)
        val srcGpu = TaichiAot.upload(srcBuffer, 200, 200, 3)

        // No resize - should preserve dimensions
        val result = TaichiAot.run(
            "gaussian_blur",
            "src" to srcGpu,
            returnGpu = true
        )

        assertTrue(result is TaichiGpuBuffer)
        val resultGpu = result as TaichiGpuBuffer
        assertEquals(200, resultGpu.width, "Width should be preserved")
        assertEquals(200, resultGpu.height, "Height should be preserved")
        assertEquals(3, resultGpu.channels, "Channels should be preserved")

        srcGpu.release()
        resultGpu.release()
        TaichiAot.destroy()
        println("✔ TaichiAot preserve dimensions verified")
    }

    // =========================================================================
    // 5. GPU BUFFER TESTS
    // =========================================================================

    @Test
    fun testGpuBufferProperties() {
        println("\n=== [AOT 13] GPU BUFFER: PROPERTIES ===")
        val buffer = TaichiGpuBuffer(
            id = 1001,
            width = 1920,
            height = 1080,
            channels = 3,
            dtype = AotDtype.FLOAT32
        )

        assertEquals(1001L, buffer.id)
        assertEquals(1920, buffer.width)
        assertEquals(1080, buffer.height)
        assertEquals(3, buffer.channels)
        assertEquals(AotDtype.FLOAT32, buffer.dtype)
        assertEquals(1920L * 1080 * 3 * 4, buffer.byteSize)
        assertFalse(buffer.isReleased)

        buffer.release()
        assertTrue(buffer.isReleased)
        println("✔ GPU buffer properties verified")
    }

    @Test
    fun testGpuBufferDoubleRelease() {
        println("\n=== [AOT 14] GPU BUFFER: DOUBLE RELEASE ===")
        var releaseCount = 0
        val buffer = TaichiGpuBuffer(
            id = 1002,
            width = 100,
            height = 100,
            channels = 1,
            onRelease = { releaseCount++ }
        )

        buffer.release()
        assertEquals(1, releaseCount, "Should release once")
        assertTrue(buffer.isReleased)

        // Double release should not call onRelease again
        buffer.release()
        assertEquals(1, releaseCount, "Should not release again")
        println("✔ GPU buffer double release verified")
    }

    @Test
    fun testGpuBufferToDirectBuffer() {
        println("\n=== [AOT 15] GPU BUFFER: TO DIRECT BUFFER ===")
        val buffer = TaichiGpuBuffer(
            id = 1003,
            width = 100,
            height = 100,
            channels = 1,
            dtype = AotDtype.FLOAT32
        )

        val directBuffer = buffer.toDirectBuffer()
        assertNotNull(directBuffer)
        assertTrue(directBuffer.isDirect, "Should be direct buffer")
        assertEquals(100 * 100 * 4, directBuffer.capacity())

        buffer.release()
        println("✔ GPU buffer to direct buffer verified")
    }

    @Test
    fun testGpuBufferReleasedAccess() {
        println("\n=== [AOT 16] GPU BUFFER: RELEASED ACCESS ===")
        val buffer = TaichiGpuBuffer(
            id = 1004,
            width = 100,
            height = 100,
            channels = 1
        )

        buffer.release()

        assertFailsWith<IllegalStateException> {
            buffer.toDirectBuffer()
        }
        println("✔ GPU buffer released access verified")
    }

    @Test
    fun testGpuBufferAutoCloseable() {
        println("\n=== [AOT 17] GPU BUFFER: AUTO CLOSEABLE ===")
        var releaseCount = 0

        TaichiGpuBuffer(
            id = 1005,
            width = 100,
            height = 100,
            channels = 1,
            onRelease = { releaseCount++ }
        ).use { buffer ->
            assertFalse(buffer.isReleased)
        }

        assertEquals(1, releaseCount, "Should be released after use block")
        println("✔ GPU buffer AutoCloseable verified")
    }

    // =========================================================================
    // 6. AOT ARCH TESTS
    // =========================================================================

    @Test
    fun testAotArchFromString() {
        println("\n=== [AOT 18] AOT ARCH: FROM STRING ===")
        assertEquals(AotArch.CUDA, AotArch.fromString("cuda"))
        assertEquals(AotArch.VULKAN, AotArch.fromString("vulkan"))
        assertEquals(AotArch.VULKAN, AotArch.fromString("vk"))
        assertEquals(AotArch.OPENGL, AotArch.fromString("opengl"))
        assertEquals(AotArch.OPENGL, AotArch.fromString("gl"))
        assertEquals(AotArch.GLES, AotArch.fromString("gles"))
        assertEquals(AotArch.CPU, AotArch.fromString("cpu"))
        assertEquals(AotArch.CPU, AotArch.fromString("unknown"))
        println("✔ AotArch from string verified")
    }

    @Test
    fun testAotArchCaseInsensitive() {
        println("\n=== [AOT 19] AOT ARCH: CASE INSENSITIVE ===")
        assertEquals(AotArch.CUDA, AotArch.fromString("CUDA"))
        assertEquals(AotArch.CUDA, AotArch.fromString("Cuda"))
        assertEquals(AotArch.VULKAN, AotArch.fromString("VULKAN"))
        assertEquals(AotArch.CPU, AotArch.fromString("CPU"))
        println("✔ AotArch case insensitive verified")
    }

    // =========================================================================
    // 7. AOT DTYPE TESTS
    // =========================================================================

    @Test
    fun testAotDtypeBytesPerElement() {
        println("\n=== [AOT 20] AOT DTYPE: BYTES PER ELEMENT ===")
        assertEquals(4, AotDtype.FLOAT32.bytesPerElement)
        assertEquals(2, AotDtype.FLOAT16.bytesPerElement)
        assertEquals(1, AotDtype.UINT8.bytesPerElement)
        assertEquals(4, AotDtype.INT32.bytesPerElement)
        println("✔ AotDtype bytes per element verified")
    }

    // =========================================================================
    // 8. PIPELINE TESTS
    // =========================================================================

    @Test
    fun testSequentialPipeline() {
        println("\n=== [AOT 21] PIPELINE: SEQUENTIAL 4 ALGORITHMS ===")
        TaichiAot.init(arch = "cpu")

        val width = 100
        val height = 100
        val rawBuffer = ByteBuffer.allocateDirect(width * height * 4).order(ByteOrder.nativeOrder())
        for (i in 0 until 100) rawBuffer.putFloat(0.5f)
        rawBuffer.rewind()

        // Step 1: Upload
        val rawGpu = TaichiAot.upload(rawBuffer, width, height, 1)
        assertNotNull(rawGpu)

        // Step 2: Demosaic
        val rgbGpu = TaichiAot.run(
            "hamilton_demosaic",
            "src" to rawGpu,
            returnGpu = true
        ) as TaichiGpuBuffer
        assertEquals(3, rgbGpu.channels)

        // Step 3: Gaussian Blur
        val blurredGpu = TaichiAot.run(
            "gaussian_blur",
            "src" to rgbGpu,
            returnGpu = true
        ) as TaichiGpuBuffer
        assertEquals(3, blurredGpu.channels)

        // Step 4: Resize
        val resizedGpu = TaichiAot.run(
            "bilinear_resize",
            "src" to blurredGpu,
            "target_w" to 50,
            "target_h" to 50,
            returnGpu = true
        ) as TaichiGpuBuffer
        assertEquals(50, resizedGpu.width)
        assertEquals(50, resizedGpu.height)

        // Step 5: Download
        val finalBuffer = TaichiAot.run(
            "download",
            "src" to resizedGpu,
            returnGpu = false
        ) as ByteBuffer
        assertTrue(finalBuffer.isDirect)

        // Cleanup
        rawGpu.release()
        rgbGpu.release()
        blurredGpu.release()
        resizedGpu.release()
        TaichiAot.destroy()

        println("✔ Sequential pipeline: Upload → Demosaic → Blur → Resize → Download")
    }

    // =========================================================================
    // 9. EXTENSION FUNCTIONS TESTS
    // =========================================================================

    @Test
    fun testExtensionFunctionsExist() {
        println("\n=== [AOT 22] EXTENSION FUNCTIONS: EXISTENCE ===")
        // Verify extension functions are defined (compile-time check)
        // These would fail to compile if not defined
        val gaussianBlur: TaichiAot.(TaichiGpuBuffer, Pair<Int, Int>, Float, Float, Boolean) -> Any = TaichiAot::gaussian_blur
        val resize: TaichiAot.(TaichiGpuBuffer, Pair<Int, Int>, InterpolationMode, Boolean) -> Any = TaichiAot::resize
        val sobel: TaichiAot.(TaichiGpuBuffer, Int, Int, Int, Boolean) -> Any = TaichiAot::sobel
        val cvtColor: TaichiAot.(TaichiGpuBuffer, ColorConversionCode, Boolean) -> Any = TaichiAot::cvtColor

        assertNotNull(gaussianBlur)
        assertNotNull(resize)
        assertNotNull(sobel)
        assertNotNull(cvtColor)
        println("✔ Extension functions existence verified")
    }

    // =========================================================================
    // 10. ERROR HANDLING TESTS
    // =========================================================================

    @Test
    fun testUploadNotInitialized() {
        println("\n=== [AOT 23] ERROR: UPLOAD NOT INITIALIZED ===")
        TaichiAot.destroy()

        assertFailsWith<IllegalStateException> {
            TaichiAot.upload(ByteBuffer.allocateDirect(100), 10, 10, 1)
        }
        println("✔ Upload not initialized error verified")
    }

    @Test
    fun testGpuBufferInvalidSize() {
        println("\n=== [AOT 24] ERROR: GPU BUFFER INVALID SIZE ===")
        val buffer = TaichiGpuBuffer(
            id = 1006,
            width = 0,
            height = 0,
            channels = 1
        )

        assertEquals(0L, buffer.byteSize)

        // toDirectBuffer with size 0 should throw
        assertFailsWith<IllegalArgumentException> {
            buffer.toDirectBuffer()
        }
        println("✔ GPU buffer invalid size error verified")
    }

    @Test
    fun testGpuBufferNegativeSize() {
        println("\n=== [AOT 25] ERROR: GPU BUFFER NEGATIVE SIZE ===")
        val buffer = TaichiGpuBuffer(
            id = 1007,
            width = -1,
            height = -1,
            channels = 1
        )

        // byteSize calculation with negative values
        val byteSize = buffer.byteSize
        assertTrue(byteSize <= 0, "Negative dimensions should produce non-positive byteSize")
        println("✔ GPU buffer negative size error verified")
    }
}
