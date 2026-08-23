package org.pixelrefine.genericui

import org.pixelrefine.genericui.components.Variant
import org.pixelrefine.genericui.domain.models.ImageItem
import org.pixelrefine.genericui.domain.presets.AlgorithmPreset
import org.pixelrefine.genericui.domain.validation.SharpnessMetric
import java.nio.ByteBuffer
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertNotNull
import kotlin.test.assertTrue

/**
 * Uji paritas dan kemudahan 1-baris pemanggilan seluruh API bergaya Pythonic di Kotlin.
 */
class PythonicApiParityTest {

    @Test
    fun testPythonicOneLineProceduralCalls() {
        println("=== 1. TEST PYTHONIC 1-LINE LOGIC API ===")

        // 1. Toast gaya Python (1 baris murni):
        toast("Proses batch dimulai!", variant = Variant.Info)

        // 2. Preset Registry gaya Python (1 baris murni):
        val presets = list_presets()
        assertTrue(presets.isNotEmpty())
        val preset = get_preset("night_denoise")
        assertNotNull(preset)
        assertEquals("Night Low-Light Denoise", preset.name)

        val custom = save_preset("Astro Custom", "Deskripsi", mapOf("denoise" to 0.7))
        assertEquals("Astro Custom", custom.name)

        // 3. Session Checkpoint gaya Python (1 baris murni):
        save_checkpoint("batch_py_99", total = 10, completed = 5, last_path = "D:/img_05.dng")
        assertTrue(has_recovery("batch_py_99"))
        val cp = get_checkpoint("batch_py_99")
        assertEquals(5, cp?.completedFrames)
        clear_checkpoint("batch_py_99")

        // 4. Smart AI Culling gaya Python (1 baris murni):
        val imgList = listOf(ImageItem(path = "RAW_1.dng"), ImageItem(path = "RAW_2.dng"))
        val testBuf = ByteBuffer.allocateDirect(64 * 64)
        for (i in 0 until 64 * 64) testBuf.put(128.toByte())
        testBuf.rewind()

        val sharpness1 = compute_sharpness(testBuf, 64, 64)
        val sharpness2 = 850.0 // higher sharpness
        val culled = SharpnessMetric.autoAssignBestReference(imgList, listOf(sharpness1, sharpness2))
        assertTrue(culled[1].isReference, "Foto kedua harus terpilih sebagai reference")

        println("✔ Seluruh API Pythonic 1-baris procedural tervalidasi 100%!")
    }
}
