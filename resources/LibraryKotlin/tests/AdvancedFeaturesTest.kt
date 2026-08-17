package org.pixelrefine.genericui

import kotlinx.coroutines.flow.toList
import kotlinx.coroutines.runBlocking
import org.pixelrefine.genericui.domain.cache.LruMemoryCache
import org.pixelrefine.genericui.domain.deletion.AdaptiveChunkProcessor
import org.pixelrefine.genericui.domain.state.ThumbnailPolicyState
import org.pixelrefine.genericui.domain.stream.ImageStreamer
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertNull
import kotlin.test.assertTrue

class AdvancedFeaturesTest {

    @Test
    fun testLruMemoryCache() {
        val cache = LruMemoryCache<String, String>(maxCapacity = 3)
        cache.put("img1", "data1")
        cache.put("img2", "data2")
        cache.put("img3", "data3")

        assertEquals(3, cache.size)
        assertEquals("data1", cache.get("img1"))

        // Menambahkan item ke-4 harus memicu eviksi item paling lama digunakan (img2)
        cache.put("img4", "data4")
        assertEquals(3, cache.size)
        assertTrue(cache.containsKey("img1")) // Karena baru di-get
        assertTrue(cache.containsKey("img3"))
        assertTrue(cache.containsKey("img4"))
        assertFalse(cache.containsKey("img2")) // img2 ter-evict
    }

    @Test
    fun testAdaptiveChunkCalculation() {
        assertEquals(50, AdaptiveChunkProcessor.calculateAdaptiveChunkSize(100))
        assertEquals(100, AdaptiveChunkProcessor.calculateAdaptiveChunkSize(600))
        assertEquals(200, AdaptiveChunkProcessor.calculateAdaptiveChunkSize(1200))
        assertEquals(400, AdaptiveChunkProcessor.calculateAdaptiveChunkSize(2000))
    }

    @Test
    fun testAdaptiveChunkProcessingFlow() = runBlocking {
        val items = (1..250).toList()
        val processedChunks = mutableListOf<List<Int>>()

        val progressList = AdaptiveChunkProcessor.processAdaptive(items) { chunk ->
            processedChunks.add(chunk)
        }.toList()

        assertEquals(5, progressList.size) // 250 / 50 = 5 chunks
        assertEquals(5, processedChunks.size)
        assertEquals(250, progressList.last().totalProcessedCount)
        assertEquals(1.0f, progressList.last().progressFraction)
    }

    @Test
    fun testImageStreamerFlow() = runBlocking {
        val paths = listOf("C:/img1.jpg", "C:/img2.jpg", "C:/img3.jpg")
        val streamer = ImageStreamer(paths, loader = { path -> "Decoded: $path" })

        val results = streamer.stream().toList()
        assertEquals(3, results.size)
        assertEquals("Decoded: C:/img1.jpg", results[0].data)
        assertEquals("Decoded: C:/img3.jpg", results[2].data)
        assertEquals(1.0f, results[2].progressFraction)
    }

    @Test
    fun testThumbnailPolicy() {
        val policy = ThumbnailPolicyState(initialEnabled = true)
        assertTrue(policy.isEnabled)

        policy.toggle()
        assertFalse(policy.isEnabled)

        policy.set(true)
        assertTrue(policy.isEnabled)
    }
}
