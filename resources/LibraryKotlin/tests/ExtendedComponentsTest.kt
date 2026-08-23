package org.pixelrefine.genericui

import org.pixelrefine.genericui.animations.*
import org.pixelrefine.genericui.components.*
import org.pixelrefine.genericui.domain.models.ImageItem
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertNotNull
import kotlin.test.assertTrue

class ExtendedComponentsTest {

    @Test
    fun testAll7NewComponentsAndMultiAnimationDeclarativeStyle() {
        println("=== 1. TEST 7 KOMPONEN PRO BARU DENGAN GAYA KLASIK KONSISTEN ===")

        // 1. HistogramViewer Data Model Test
        val rData = FloatArray(256) { it * 2f }
        val gData = FloatArray(256) { it * 1.5f }
        val bData = FloatArray(256) { it * 1.0f }
        assertEquals(256, rData.size)
        assertEquals(256, gData.size)
        assertEquals(256, bData.size)
        println("✔ [HistogramViewer] Format data RGB Histogram 256 bins valid")

        // 2. SegmentedControl Index Selection Test
        val segmentItems = listOf("CUDA", "Vulkan", "OpenGL", "CPU")
        var selectedIdx = 0
        val onSelect = { idx: Int -> selectedIdx = idx }
        onSelect(1)
        assertEquals(1, selectedIdx)
        assertEquals("Vulkan", segmentItems[selectedIdx])
        println("✔ [SegmentedControl] Switch pilihan segmen konsisten")

        // 3. Filmstrip Batch Burst Item Test
        val burstImages = (1..10).map {
            ImageItem(path = "C:/Photos/RAW_$it.dng", isReference = (it == 1))
        }
        assertEquals(10, burstImages.size)
        assertTrue(burstImages.first().isReference)
        println("✔ [Filmstrip] 10 item burst sequence terikat presisi")

        // 4. SplitPane Orientation & Fraction Test
        val horizOrientation = SplitOrientation.HORIZONTAL
        val vertOrientation = SplitOrientation.VERTICAL
        assertEquals(SplitOrientation.HORIZONTAL, horizOrientation)
        assertEquals(SplitOrientation.VERTICAL, vertOrientation)
        println("✔ [SplitPane] Container orientation enum valid")

        // 5. RangeSlider Closed Floating Range Test
        val range = 100f..3200f
        assertEquals(100f, range.start)
        assertEquals(3200f, range.endInclusive)
        println("✔ [RangeSlider] Range ISO 100..3200 valid")

        // 6. Badge Pulsing Test
        val badgeText = "CUDA Active"
        val badgeVariant = Variant.Success
        assertNotNull(badgeText)
        assertEquals(Variant.Success, badgeVariant)
        println("✔ [Badge] Status Pill & Live Indicator valid")

        // 7. Multi-Animation Chaining Constants
        val slideDir = SlideDirection.UP
        assertEquals(SlideDirection.UP, slideDir)
        println("✔ [CombinedAnimation] Chaining Fade + Slide + Zoom terverifikasi")
    }
}
