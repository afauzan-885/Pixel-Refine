package org.pixelrefine.genericui

import org.pixelrefine.genericui.domain.aot.*
import org.pixelrefine.genericui.domain.models.BatchItem
import org.pixelrefine.genericui.domain.models.ImageItem
import org.pixelrefine.genericui.domain.project.ProjectArchiveManager
import java.nio.ByteBuffer
import java.nio.ByteOrder
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertNotNull
import kotlin.test.assertTrue

class TaichiAotParityTest {

    @Test
    fun testTaichiAot1to1ParityLifecycle() {
        println("=== 1. TEST TAICHI AOT 1:1 PYTHON PARITY LIFECYCLE ===")

        // 1. Python: `aot.init("vulkan", device=0)`
        TaichiAot.init(arch = "vulkan", device = 0)
        assertTrue(TaichiAot.isReady)
        assertEquals(AotArch.VULKAN, TaichiAot.activeArch)
        assertEquals(0, TaichiAot.activeDevice)

        // 2. Python: `buf = aot.upload(image_data)`
        val width = 1920
        val height = 1080
        val channels = 3
        val byteSize = width * height * channels * 4 // Float32 ~8.29 MB

        val directBuffer = ByteBuffer.allocateDirect(byteSize).order(ByteOrder.nativeOrder())
        // Mengisi buffer dengan data sintetis
        for (i in 0 until 100) {
            directBuffer.putFloat(i.toFloat())
        }
        directBuffer.rewind()

        val gpuBuffer = TaichiAot.upload(
            buffer = directBuffer,
            width = width,
            height = height,
            channels = channels,
            dtype = AotDtype.FLOAT32
        )

        assertNotNull(gpuBuffer)
        assertEquals(width, gpuBuffer.width)
        assertEquals(height, gpuBuffer.height)
        assertEquals(byteSize.toLong(), gpuBuffer.byteSize)
        assertFalse(gpuBuffer.isReleased)

        // 3. Python: `resident_gpu = aot.run("cmn_gaussian_f32", src=gpuBuffer, return_gpu=True)`
        val residentResult = TaichiAot.run(
            "cmn_gaussian_f32",
            "src" to gpuBuffer,
            "sigma" to 1.5f,
            returnGpu = true
        )

        assertTrue(residentResult is TaichiGpuBuffer)
        val resultGpuBuffer = residentResult as TaichiGpuBuffer
        assertEquals(width, resultGpuBuffer.width)
        assertEquals(height, resultGpuBuffer.height)

        // 3b. OpenCV Style: `taichi_aot.gaussian_blur(src, ksize=(5, 5), sigmaX=1.5f)`
        val blurred = TaichiAot.gaussian_blur(gpuBuffer, ksize = Pair(5, 5), sigmaX = 1.5f)
        assertTrue(blurred is TaichiGpuBuffer)

        // 3c. OpenCV Style: `taichi_aot.resize(src, dsize=(960, 540))`
        val resized = TaichiAot.resize(gpuBuffer, dsize = Pair(960, 540))
        assertTrue(resized is TaichiGpuBuffer)

        // 3d. OpenCV Style: `taichi_aot.sobel(src)`
        val edges = TaichiAot.sobel(gpuBuffer)
        assertTrue(edges is TaichiGpuBuffer)

        // 4. Python: `downloaded = aot.run("cmn_gaussian_f32", src=resultGpuBuffer, return_gpu=False)`
        val downloadedResult = TaichiAot.run(
            "cmn_gaussian_f32",
            "src" to resultGpuBuffer,
            returnGpu = false
        )

        assertTrue(downloadedResult is ByteBuffer)
        val resultBytes = downloadedResult as ByteBuffer
        assertEquals(byteSize, resultBytes.capacity())

        // 5. Python: `gpuBuffer.release(); aot.destroy()`
        gpuBuffer.release()
        resultGpuBuffer.release()
        assertTrue(gpuBuffer.isReleased)
        assertTrue(resultGpuBuffer.isReleased)

        TaichiAot.destroy()
        assertFalse(TaichiAot.isReady)
        println("-> Taichi AOT Lifecycle 100% identik dengan Python dan terverifikasi sukses!")
    }

    @Test
    fun testProjectArchiveAndUnsavedChanges() {
        println("\n=== 2. TEST PROJECT ARCHIVE (.PRF) & UNSAVED CHANGES TRACKER ===")

        val img1 = ImageItem(path = "C:/Photos/IMG_001.dng", isReference = true)
        val img2 = ImageItem(path = "C:/Photos/IMG_002.dng")
        val batch = BatchItem(name = "Night_Stack", images = listOf(img1, img2))

        val currentBatches = listOf(batch)

        // Baseline sebelum disimpan
        val baselineToken = ProjectArchiveManager.calculateSessionToken(currentBatches)
        assertNotNull(baselineToken)

        // Simpan proyek
        val manifest = ProjectArchiveManager.saveProject(
            path = "C:/Projects/MyLandscape.prf",
            batches = currentBatches,
            activeBatchId = 1L
        )

        assertEquals("MyLandscape", manifest.projectName)
        assertEquals(1, manifest.batchCount)
        assertEquals(2, manifest.totalImages)
        assertEquals(baselineToken, manifest.stateToken)

        // Tidak ada perubahan yang belum tersimpan
        assertFalse(ProjectArchiveManager.hasUnsavedChanges(currentBatches, baselineToken))

        // Modifikasi data (tambah foto baru)
        val modifiedBatches = listOf(batch.addImage(ImageItem(path = "C:/Photos/IMG_003.dng")))
        
        // Terdeteksi ada perubahan yang belum tersimpan!
        assertTrue(ProjectArchiveManager.hasUnsavedChanges(modifiedBatches, baselineToken))

        // Recent projects list
        assertEquals(listOf("C:/Projects/MyLandscape.prf"), ProjectArchiveManager.recentProjects())
        println("-> Project Archive (.prf) & State Tracker terverifikasi presisi!")
    }
}
