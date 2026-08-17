package org.pixelrefine.genericui

import org.pixelrefine.genericui.domain.models.AlgorithmCategory
import org.pixelrefine.genericui.domain.models.AlgorithmConfig
import org.pixelrefine.genericui.domain.models.AlgorithmRegistry
import org.pixelrefine.genericui.domain.models.BatchItem
import org.pixelrefine.genericui.domain.models.ImageItem
import org.pixelrefine.genericui.domain.state.BatchStateManager
import org.pixelrefine.genericui.domain.state.ProcessingState
import org.pixelrefine.genericui.domain.state.WorkflowStateManager
import org.pixelrefine.genericui.domain.gestures.TransformState
import org.pixelrefine.genericui.domain.validation.ImageValidator
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertNotNull
import kotlin.test.assertTrue

class LogicParityTest {

    @Test
    fun testImageAndBatchModelOperations() {
        val img1 = ImageItem(path = "C:/photos/image1.jpg")
        val img2 = ImageItem(path = "C:/photos/image2.dng")
        val img3 = ImageItem(path = "C:/photos/image3.png")

        assertEquals("image1.jpg", img1.filename)
        assertEquals("jpg", img1.extension)
        assertFalse(img1.isRaw)
        assertTrue(img2.isRaw)

        var batch = BatchItem(name = "Night_Stack")
        batch = batch.addImage(img1)
        batch = batch.addImage(img2)
        batch = batch.addImage(img3)

        assertEquals(3, batch.imageCount)
        assertEquals("C:/photos/image1.jpg", batch.referenceImage?.path)

        // Ubah reference image
        batch = batch.setReference("C:/photos/image2.dng")
        assertEquals("C:/photos/image2.dng", batch.referenceImage?.path)

        // Hapus image
        batch = batch.removeImage("C:/photos/image2.dng")
        assertEquals(2, batch.imageCount)
        assertTrue(batch.referenceImage != null)
    }

    @Test
    fun testImageValidator() {
        val candidates = listOf(
            "C:/test/photo.jpg",
            "C:/test/raw.dng",
            "C:/test/unsupported.txt",
            "C:/test/photo.jpg", // duplikat
            ""
        )

        val result = ImageValidator.validatePaths(candidates)
        assertEquals(2, result.accepted.size) // photo.jpg dan raw.dng
        assertEquals(3, result.rejected.size) // unsupported.txt, duplikat photo.jpg, path kosong
    }

    @Test
    fun testAlgorithmConfigTypeSafeAccess() {
        val config = AlgorithmConfig(
            category = AlgorithmCategory.DENOISING,
            name = "MFDenoiser",
            parameters = mapOf("spatial_sigma" to 1.5, "iterations" to 3, "use_gpu" to true)
        )

        assertEquals(1.5f, config.getFloat("spatial_sigma"))
        assertEquals(3, config.getInt("iterations"))
        assertTrue(config.getBoolean("use_gpu"))

        val alignmentOptions = AlgorithmRegistry.getOptions(AlgorithmCategory.ALIGNMENT)
        assertTrue(alignmentOptions.isNotEmpty())
        assertTrue(alignmentOptions.any { it.name == "Farneback" })
    }

    @Test
    fun testWorkflowStateManager() {
        val manager = WorkflowStateManager()
        assertTrue(manager.isIdle)

        manager.start("Batch_001", "Alignment")
        assertTrue(manager.isRunning)
        assertEquals("Alignment", manager.currentStep)

        manager.updateProgress("Denoising", 0.5f, "Batch_001")
        assertEquals(0.5f, manager.progress)

        manager.complete("C:/output/result.jpg", 1200L)
        assertTrue(manager.state is ProcessingState.Success)
    }

    @Test
    fun testTransformStateMath() {
        val state = TransformState(minScale = 0.5f, maxScale = 4.0f, initialScale = 1.0f)
        state.zoomIn(0.5f)
        assertEquals(1.5f, state.scale)

        state.setZoom(10.0f) // Melebihi maxScale
        assertEquals(4.0f, state.scale)

        state.setZoom(0.1f) // Kurang dari minScale
        assertEquals(0.5f, state.scale)

        state.reset()
        assertEquals(1.0f, state.scale)
        assertEquals(0f, state.offsetX)
        assertEquals(0f, state.offsetY)
    }
}
