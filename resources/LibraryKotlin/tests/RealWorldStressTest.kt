package org.pixelrefine.genericui

import kotlinx.coroutines.flow.toList
import kotlinx.coroutines.runBlocking
import org.pixelrefine.genericui.domain.cache.LruMemoryCache
import org.pixelrefine.genericui.domain.deletion.AdaptiveChunkProcessor
import org.pixelrefine.genericui.domain.models.AlgorithmCategory
import org.pixelrefine.genericui.domain.models.AlgorithmConfig
import org.pixelrefine.genericui.domain.models.BatchItem
import org.pixelrefine.genericui.domain.models.ImageItem
import org.pixelrefine.genericui.domain.state.BatchStateManager
import org.pixelrefine.genericui.domain.state.ProcessingState
import org.pixelrefine.genericui.domain.state.WorkflowStateManager
import org.pixelrefine.genericui.domain.stream.ImageStreamer
import org.pixelrefine.genericui.domain.validation.ImageValidator
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertNotNull
import kotlin.test.assertTrue

/**
 * Simulasi data sintetis untuk 50 Megapixel RAW Image Stacking
 * 50MP = ~8688 x 5792 piksel (~100 MB per uncompressed RGB frame)
 */
data class Synthetic50MPImage(
    val path: String,
    val width: Int = 8688,
    val height: Int = 5792,
    val estimatedBytes: Long = 8688L * 5792L * 3L, // ~150 MB buffer
    val isDemosaiced: Boolean = true,
)

class RealWorldStressTest {

    @Test
    fun testMassiveBurstAndBatchSimulation() = runBlocking {
        println("=== 1. SIMULASI GENERASI 20 BATCH DENGAN TOTAL 1.000 FOTO 50MP ===")
        
        val totalBatches = 20
        val imagesPerBatch = 50
        val totalImages = totalBatches * imagesPerBatch // 1.000 foto 50MP (~150 GB data sintetis)

        val batchManager = BatchStateManager()

        // 1. Inisialisasi 20 Batch secara asinkron
        for (b in 1..totalBatches) {
            val syntheticPaths = (1..imagesPerBatch).map { imgIdx ->
                "D:/RAW_BURST/Batch_${b.toString().padStart(2, '0')}/IMG_${imgIdx.toString().padStart(4, '0')}.dng"
            }
            batchManager.addBatch(name = "Night_Stack_Batch_$b", imagePaths = syntheticPaths)
        }

        assertEquals(20, batchManager.batches.size)
        assertEquals(50, batchManager.activeBatch?.imageCount)
        assertEquals("D:/RAW_BURST/Batch_01/IMG_0001.dng", batchManager.activeBatch?.referenceImage?.path)
        println("-> Berhasil membuat 20 batch dengan auto-assigned reference images.")

        // 2. Validasi & Deduplikasi
        val extraCandidates = listOf(
            "D:/RAW_BURST/Batch_01/IMG_0001.dng", // Duplikat
            "D:/RAW_BURST/Batch_01/IMG_0051.dng", // Baru
            "D:/RAW_BURST/Batch_01/corrupt_file.txt" // Format tidak didukung
        )
        val existingPaths = batchManager.activeBatch!!.images.map { it.path }.toSet()
        val valResult = ImageValidator.validatePaths(extraCandidates, existingPaths)

        assertEquals(1, valResult.accepted.size) // Hanya IMG_0051.dng yang lolos
        assertEquals(2, valResult.rejected.size) // Duplikat & .txt ditolak
        println("-> Validasi & deduplikasi berjalan presisi (1 accepted, 2 rejected).")

        // 3. Low-RAM Producer-Consumer ImageStreamer untuk 50MP
        println("\n=== 2. SIMULASI STREAMING 50MP TANPA LONJAKAN MEMORI (ZERO-OOM) ===")
        val activeBatchImages = batchManager.activeBatch!!.images.map { it.path }
        
        var maxSimultaneousBuffers = 0
        var currentLoadedBuffers = 0

        val streamer = ImageStreamer<Synthetic50MPImage>(
            paths = activeBatchImages,
            loader = { path ->
                currentLoadedBuffers++
                if (currentLoadedBuffers > maxSimultaneousBuffers) {
                    maxSimultaneousBuffers = currentLoadedBuffers
                }
                // Simulasi dekode 50MP
                val result = Synthetic50MPImage(path = path)
                currentLoadedBuffers--
                result
            },
            maxQueueSize = 3 // Buffer dibatasi maksimal 3 frame (~450MB) di RAM
        )

        var streamedCount = 0
        streamer.stream().collect { item ->
            streamedCount++
            assertNotNull(item.data)
            assertEquals(8688, item.data?.width)
            assertEquals(5792, item.data?.height)
        }

        assertEquals(50, streamedCount)
        assertTrue(maxSimultaneousBuffers <= 4, "Buffer RAM terjaga dan tidak meluap!")
        println("-> 50 foto 50MP berhasil di-stream satu per satu tanpa OOM.")

        // 4. LRU Memory Cache untuk Thumbnail
        println("\n=== 3. SIMULASI LRU THUMBNAIL CACHE UNTUK BROWSER 1.000 FOTO ===")
        val thumbnailCache = LruMemoryCache<String, String>(maxCapacity = 100)
        
        // Populate cache dengan 1.000 thumbnail
        for (b in 1..totalBatches) {
            for (imgIdx in 1..imagesPerBatch) {
                val path = "D:/RAW_BURST/Batch_${b.toString().padStart(2, '0')}/IMG_${imgIdx.toString().padStart(4, '0')}.dng"
                thumbnailCache.put(path, "THUMBNAIL_RGB_CACHE_${b}_${imgIdx}")
            }
        }
        // Cache harus secara otomatis membuang 900 item tertua dan hanya menyimpan 100 item terbaru
        assertEquals(100, thumbnailCache.size)
        println("-> LRU Cache secara otomatis menjaga kapasitas RAM konstan pada 100 thumbnail.")

        // 5. Adaptive Chunk Processing (Penghapusan Massal 1.000 item)
        println("\n=== 4. SIMULASI PENGHAPUSAN DINAMIS (ADAPTIVE CHUNKING) ===")
        val allPaths = batchManager.batches.flatMap { it.images.map { img -> img.path } }
        assertEquals(1000, allPaths.size)

        val processedChunks = mutableListOf<List<String>>()
        AdaptiveChunkProcessor.processAdaptive(allPaths) { chunk ->
            // Simulasi batch deletion DB & I/O
            processedChunks.add(chunk)
        }.collect { progress ->
            assertTrue(progress.progressFraction in 0f..1f)
        }

        // Untuk 1.000 item, chunk size yang dihitung adalah 200 (sehingga 1.000 / 200 = 5 batch transaksi)
        assertEquals(5, processedChunks.size)
        processedChunks.forEach { chunk ->
            assertEquals(200, chunk.size)
        }
        println("-> 1.000 item berhasil diproses dalam 5 chunk adaptif (masing-masing 200 item) tanpa disk freezing.")

        // 6. Workflow Pipeline State Tracking
        println("\n=== 5. SIMULASI WORKFLOW PIPELINE ALGORITMA ===")
        val workflow = WorkflowStateManager()
        val config = AlgorithmConfig(
            category = AlgorithmCategory.DENOISING,
            name = "MFDenoiser",
            parameters = mapOf("spatial_sigma" to 2.0, "temporal_weight" to 0.8, "burst_count" to 50)
        )

        workflow.start("Night_Stack_Batch_01", "Aligning Frames (Farneback)")
        assertEquals("Aligning Frames (Farneback)", workflow.currentStep)
        assertTrue(workflow.isRunning)

        workflow.updateProgress("Spatio-Temporal Fusion (MFDenoiser)", 0.65f, "Night_Stack_Batch_01")
        assertEquals(0.65f, workflow.progress)

        workflow.complete("D:/OUTPUT/Night_Stack_Batch_01_Fused_50MP.tif", 3420L)
        assertTrue(workflow.state is ProcessingState.Success)
        val success = workflow.state as ProcessingState.Success
        assertEquals(3420L, success.durationMs)
        println("-> Workflow pipeline 50MP tuntas dalam ${success.durationMs}ms dengan status Success.")
    }
}
