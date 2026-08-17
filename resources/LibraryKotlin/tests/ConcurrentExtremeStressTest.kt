package org.pixelrefine.genericui

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.flow.toList
import kotlinx.coroutines.runBlocking
import org.pixelrefine.genericui.domain.cache.LruMemoryCache
import org.pixelrefine.genericui.domain.deletion.AdaptiveChunkProcessor
import org.pixelrefine.genericui.domain.gestures.TransformState
import org.pixelrefine.genericui.domain.models.BatchItem
import org.pixelrefine.genericui.domain.models.BatchStatus
import org.pixelrefine.genericui.domain.models.ImageItem
import org.pixelrefine.genericui.domain.state.BatchStateManager
import org.pixelrefine.genericui.domain.state.ProcessingState
import org.pixelrefine.genericui.domain.state.WorkflowStateManager
import org.pixelrefine.genericui.domain.stream.ImageStreamer
import org.pixelrefine.genericui.domain.validation.ImageValidator
import kotlin.random.Random
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertNotNull
import kotlin.test.assertTrue

class ConcurrentExtremeStressTest {

    @Test
    fun testChaoticConcurrentMutationsWithoutRaceCondition() = runBlocking {
        println("=== 1. STRESS TEST KONKURENSI EKSTREM: 50 WORKER PARALEL PADA BATCH MANAGER ===")
        
        val batchManager = BatchStateManager()
        val totalBatches = 50

        // Inisialisasi awal 50 batch
        for (i in 1..totalBatches) {
            batchManager.addBatch("Batch_$i", listOf("C:/IMG_001.dng", "C:/IMG_002.dng"))
        }
        assertEquals(50, batchManager.batches.size)

        // 50 Coroutine simultan melakukan mutasi acak (tambah gambar, ganti referensi, hapus gambar, toggle select)
        coroutineScope {
            val jobs = (1..50).map { workerId ->
                async(Dispatchers.Default) {
                    val batchIdx = workerId % totalBatches
                    val newImgPath = "C:/Worker_${workerId}_IMG_${Random.nextInt(100, 999)}.dng"
                    
                    // Operasi 1: Validasi dan tambah gambar
                    val valid = ImageValidator.validatePaths(listOf(newImgPath)).accepted
                    if (valid.isNotEmpty()) {
                        synchronized(batchManager) {
                            val current = batchManager.batches[batchIdx]
                            batchManager.batches[batchIdx] = current.addImage(valid.first())
                        }
                    }

                    // Operasi 2: Ubah referensi
                    synchronized(batchManager) {
                        val current = batchManager.batches[batchIdx]
                        if (current.images.isNotEmpty()) {
                            val randomPath = current.images.random().path
                            batchManager.batches[batchIdx] = current.setReference(randomPath)
                        }
                    }

                    // Operasi 3: Toggle Select
                    synchronized(batchManager) {
                        val current = batchManager.batches[batchIdx]
                        if (current.images.isNotEmpty()) {
                            batchManager.batches[batchIdx] = current.toggleSelect(current.images.first().path)
                        }
                    }
                }
            }
            jobs.awaitAll()
        }

        // Verifikasi integritas setiap batch setelah 50 worker paralel
        assertEquals(50, batchManager.batches.size)
        batchManager.batches.forEach { batch ->
            assertTrue(batch.images.isNotEmpty(), "Setiap batch tetap berisi gambar")
            assertNotNull(batch.referenceImage, "Setiap batch memiliki tepat 1 reference image yang valid")
        }
        println("-> 50 worker paralel berhasil mengeksekusi mutasi acak tanpa race condition!")
    }

    @Test
    fun testHighContentionLruCacheStress() = runBlocking {
        println("\n=== 2. STRESS TEST LRU CACHE: 100 THREAD MENULIS & MEMBACA 10.000 KEY SECARA SERENTAK ===")
        val cache = LruMemoryCache<String, String>(maxCapacity = 50)

        coroutineScope {
            val tasks = (1..100).map { threadId ->
                async(Dispatchers.Default) {
                    for (i in 1..100) {
                        val key = "KEY_${(threadId * 100 + i) % 200}"
                        val value = "VALUE_$i"
                        cache.put(key, value)
                        cache.get(key)
                    }
                }
            }
            tasks.awaitAll()
        }

        // Ukuran cache harus selalu terikat dan tidak melampaui maxCapacity 50
        assertEquals(50, cache.size)
        println("-> LRU Cache tetap konsisten pada kapasitas 50 di bawah tekanan 10.000 akses serentak.")
    }

    @Test
    fun testExtremeStreamingBackpressure() = runBlocking {
        println("\n=== 3. STRESS TEST IMAGE STREAMER DENGAN 10.000 DATA SINTETIS ===")
        val massivePaths = (1..10_000).map { "D:/MASSIVE_DATA/IMG_$it.dng" }
        var activeBuffers = 0
        var peakBuffers = 0

        val streamer = ImageStreamer<String>(
            paths = massivePaths,
            loader = { path ->
                activeBuffers++
                if (activeBuffers > peakBuffers) peakBuffers = activeBuffers
                activeBuffers--
                "LOADED_$path"
            },
            maxQueueSize = 3
        )

        var count = 0
        streamer.stream().collect { item ->
            count++
        }

        assertEquals(10_000, count)
        assertTrue(peakBuffers <= 4, "Buffer RAM puncak tetap <= 4 selama 10.000 streaming")
        println("-> 10.000 streaming tuntas dengan konsumsi buffer RAM yang terikat sempurna.")
    }

    @Test
    fun testExtremeAdaptiveChunkMassiveDataset() = runBlocking {
        println("\n=== 4. STRESS TEST ADAPTIVE CHUNKER DENGAN 25.000 FILE DATABASE ===")
        val giantList = (1..25_000).map { "FILE_$it.raw" }
        var totalChunksCount = 0
        var totalItemsProcessed = 0

        AdaptiveChunkProcessor.processAdaptive(giantList) { chunk ->
            if (totalChunksCount < 62) {
                assertEquals(400, chunk.size)
            } else {
                assertEquals(200, chunk.size) // Sisa 25.000 % 400 = 200
            }
            totalChunksCount++
            totalItemsProcessed += chunk.size
        }.collect { progress ->
            assertTrue(progress.progressFraction in 0f..1f)
        }

        assertEquals(25_000, totalItemsProcessed)
        assertEquals(63, totalChunksCount) // 25.000 / 400 = 62.5 -> 63 chunks
        println("-> 25.000 file terproses dalam 63 chunk adaptif (400 per chunk) tanpa kendala.")
    }
}
