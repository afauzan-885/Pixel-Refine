package org.pixelrefine.genericui

import org.pixelrefine.genericui.domain.models.ImageItem
import org.pixelrefine.genericui.domain.presets.PresetStore
import org.pixelrefine.genericui.domain.state.SessionCheckpointManager
import org.pixelrefine.genericui.domain.validation.SharpnessMetric
import java.nio.ByteBuffer
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertNotNull
import kotlin.test.assertTrue

class ProFeaturesTestSuite {

    @Test
    fun testSmartCullingLaplacianVariance() {
        println("=== 1. TEST SMART CULLING (LAPLACIAN SHARPNESS) ===")
        val size = 64
        val flatBuffer = ByteBuffer.allocateDirect(size * size)
        for (i in 0 until size * size) flatBuffer.put(128.toByte())
        flatBuffer.rewind()

        // Gambar flat/tanpa tepi memiliki variance ~0
        val flatScore = SharpnessMetric.computeSharpness(flatBuffer, size, size)
        assertEquals(0.0, flatScore, 0.001)

        // Uji penetapan frame terbaik (Smart Auto-Assign Reference ★)
        val images = listOf(
            ImageItem(path = "photo_01.dng"),
            ImageItem(path = "photo_02.dng"),
            ImageItem(path = "photo_03.dng"),
        )
        val sharpnessScores = listOf(120.5, 950.8, 340.2) // photo_02 adalah yang paling tajam
        val evaluated = SharpnessMetric.autoAssignBestReference(images, sharpnessScores)

        assertFalse(evaluated[0].isReference)
        assertTrue(evaluated[1].isReference) // photo_02 terpilih sebagai Best Reference Frame ★
        assertFalse(evaluated[2].isReference)
        println("✔ [Smart Culling] Hero frame berhasil dideteksi dan ditandai (★) secara presisi")
    }

    @Test
    fun testAlgorithmPresetsStore() {
        println("=== 2. TEST PRO ALGORITHM PRESETS ===")
        val presets = PresetStore.getAllPresets()
        assertTrue(presets.size >= 4)

        val nightDenoise = PresetStore.getPresetById("night_denoise")
        assertNotNull(nightDenoise)
        assertEquals("Night Low-Light Denoise", nightDenoise.name)
        assertEquals(0.85, nightDenoise.parameters["denoise_strength"])

        val custom = PresetStore.saveCustomPreset(
            name = "My Custom HDR",
            description = "Custom profile",
            params = mapOf("sharpness" to 2.0),
        )
        assertNotNull(PresetStore.getPresetById(custom.id))
        println("✔ [PresetStore] Preset bawaan & preset kustom tersimpan sempurna")
    }

    @Test
    fun testSessionCheckpointAndCrashRecovery() {
        println("=== 3. TEST FAULT-TOLERANT SESSION CHECKPOINT & RECOVERY ===")
        val batchId = "batch_hdr_99"

        // Catat progres: 5 dari 10 frame selesai
        SessionCheckpointManager.recordProgress(
            batchId = batchId,
            total = 10,
            completed = 5,
            lastPath = "C:/Photos/RAW_05.dng",
        )

        assertTrue(SessionCheckpointManager.hasPendingRecovery(batchId))
        val cp = SessionCheckpointManager.getCheckpoint(batchId)
        assertNotNull(cp)
        assertEquals(5, cp.completedFrames)
        assertEquals(10, cp.totalFrames)
        assertEquals("C:/Photos/RAW_05.dng", cp.lastProcessedPath)

        // Selesai seluruhnya
        SessionCheckpointManager.clearCheckpoint(batchId)
        assertFalse(SessionCheckpointManager.hasPendingRecovery(batchId))
        println("✔ [SessionCheckpoint] Auto-save & crash recovery tervalidasi 100%")
    }
}
