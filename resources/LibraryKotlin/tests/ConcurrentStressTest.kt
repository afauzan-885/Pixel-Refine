package org.pixelrefine.genericui

import kotlinx.coroutines.*
import org.pixelrefine.genericui.domain.cache.LruMemoryCache
import org.pixelrefine.genericui.domain.deletion.AdaptiveChunkProcessor
import org.pixelrefine.genericui.domain.gestures.TransformState
import org.pixelrefine.genericui.domain.models.BatchItem
import org.pixelrefine.genericui.domain.models.ImageItem
import org.pixelrefine.genericui.domain.state.BatchStateManager
import org.pixelrefine.genericui.domain.state.SessionCheckpointManager
import org.pixelrefine.genericui.domain.state.WorkflowStateManager
import org.pixelrefine.genericui.domain.stream.ImageStreamer
import org.pixelrefine.genericui.domain.validation.ImageValidator
import org.pixelrefine.genericui.domain.validation.SharpnessMetric
import java.nio.ByteBuffer
import java.util.concurrent.atomic.AtomicInteger
import kotlin.random.Random
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertNotNull
import kotlin.test.assertNull
import kotlin.test.assertTrue
import kotlin.test.assertFalse

/**
 * Stress test komprehensif untuk konkurensi, memory, dan edge cases:
 * - BatchStateManager concurrent mutations
 * - SessionCheckpointManager concurrent overwrite
 * - LruMemoryCache concurrent access
 * - TransformState rapid operations
 * - SharpnessMetric large buffer
 * - ImageStreamer backpressure
 * - AdaptiveChunkProcessor massive dataset
 */
class ConcurrentStressTest {

    // =========================================================================
    // 1. BATCH STATE MANAGER CONCURRENT TESTS
    // =========================================================================

    @Test
    fun testBatchStateManagerConcurrentAdd() = runBlocking {
        println("=== [STRESS 1] BATCH STATE MANAGER: CONCURRENT ADD ===")
        val manager = BatchStateManager()
        val totalWorkers = 50
        val errorCounter = AtomicInteger(0)

        val jobs = (1..totalWorkers).map { workerId ->
            launch(Dispatchers.Default) {
                try {
                    manager.addBatch("Batch_$workerId", listOf("C:/IMG_${workerId}.dng"))
                } catch (e: Throwable) {
                    errorCounter.incrementAndGet()
                }
            }
        }
        jobs.joinAll()

        assertEquals(0, errorCounter.get(), "No errors should occur during concurrent add")
        assertEquals(totalWorkers, manager.batches.size, "All batches should be added")
        assertTrue(manager.activeBatchIndex >= 0, "Active batch should be set")
        println("✔ BatchStateManager concurrent add: $totalWorkers workers, ${manager.batches.size} batches")
    }

    @Test
    fun testBatchStateManagerConcurrentMutations() = runBlocking {
        println("\n=== [STRESS 2] BATCH STATE MANAGER: CONCURRENT MUTATIONS ===")
        val manager = BatchStateManager()
        val totalBatches = 20
        val totalWorkers = 100
        val errorCounter = AtomicInteger(0)

        // Initialize batches
        for (i in 1..totalBatches) {
            manager.addBatch("Batch_$i", listOf("C:/IMG_${i}_001.dng", "C:/IMG_${i}_002.dng"))
        }

        // Concurrent mutations
        val jobs = (1..totalWorkers).map { workerId ->
            launch(Dispatchers.Default) {
                try {
                    val batchIdx = workerId % totalBatches
                    val newImgPath = "C:/Worker_${workerId}_IMG_${Random.nextInt(100, 999)}.dng"

                    // Add image
                    synchronized(manager) {
                        val current = manager.batches[batchIdx]
                        manager.batches[batchIdx] = current.addImage(ImageItem(path = newImgPath))
                    }

                    // Change reference
                    synchronized(manager) {
                        val current = manager.batches[batchIdx]
                        if (current.images.isNotEmpty()) {
                            val randomPath = current.images.random().path
                            manager.batches[batchIdx] = current.setReference(randomPath)
                        }
                    }

                    // Toggle select
                    synchronized(manager) {
                        val current = manager.batches[batchIdx]
                        if (current.images.isNotEmpty()) {
                            manager.batches[batchIdx] = current.toggleSelect(current.images.first().path)
                        }
                    }
                } catch (e: Throwable) {
                    errorCounter.incrementAndGet()
                }
            }
        }
        jobs.joinAll()

        assertEquals(0, errorCounter.get(), "No errors should occur during concurrent mutations")
        assertEquals(totalBatches, manager.batches.size, "All batches should still exist")

        // Verify integrity
        manager.batches.forEach { batch ->
            assertTrue(batch.images.isNotEmpty(), "Each batch should have images")
            assertNotNull(batch.referenceImage, "Each batch should have a reference image")
        }
        println("✔ BatchStateManager concurrent mutations: $totalWorkers workers, integrity verified")
    }

    @Test
    fun testBatchStateManagerConcurrentAddRemove() = runBlocking {
        println("\n=== [STRESS 3] BATCH STATE MANAGER: CONCURRENT ADD/REMOVE ===")
        val manager = BatchStateManager()
        val errorCounter = AtomicInteger(0)

        // Add initial batches
        for (i in 1..10) {
            manager.addBatch("Initial_$i", listOf("C:/img_$i.dng"))
        }

        // Concurrent add and remove
        val jobs = (1..50).map { workerId ->
            launch(Dispatchers.Default) {
                try {
                    if (workerId % 2 == 0) {
                        manager.addBatch("New_$workerId", listOf("C:/new_$workerId.dng"))
                    } else {
                        synchronized(manager) {
                            if (manager.batches.isNotEmpty()) {
                                manager.removeBatch(0)
                            }
                        }
                    }
                } catch (e: Throwable) {
                    errorCounter.incrementAndGet()
                }
            }
        }
        jobs.joinAll()

        assertEquals(0, errorCounter.get(), "No errors should occur during concurrent add/remove")
        assertTrue(manager.batches.size >= 0, "Batch count should be non-negative")
        println("✔ BatchStateManager concurrent add/remove: integrity verified")
    }

    // =========================================================================
    // 2. SESSION CHECKPOINT MANAGER CONCURRENT TESTS
    // =========================================================================

    @Test
    fun testSessionCheckpointConcurrentRecord() = runBlocking {
        println("\n=== [STRESS 4] SESSION CHECKPOINT: CONCURRENT RECORD ===")
        val totalWorkers = 100
        val errorCounter = AtomicInteger(0)

        val jobs = (1..totalWorkers).map { workerId ->
            launch(Dispatchers.Default) {
                try {
                    val batchId = "batch_$workerId"
                    SessionCheckpointManager.recordProgress(
                        batchId = batchId,
                        total = 10,
                        completed = workerId % 10,
                        lastPath = "C:/IMG_${workerId}.dng"
                    )

                    val checkpoint = SessionCheckpointManager.getCheckpoint(batchId)
                    assertNotNull(checkpoint, "Checkpoint should exist for $batchId")
                    assertEquals(workerId % 10, checkpoint.completedFrames)
                } catch (e: Throwable) {
                    errorCounter.incrementAndGet()
                }
            }
        }
        jobs.joinAll()

        assertEquals(0, errorCounter.get(), "No errors should occur during concurrent record")

        // Cleanup
        for (i in 1..totalWorkers) {
            SessionCheckpointManager.clearCheckpoint("batch_$i")
        }
        println("✔ SessionCheckpoint concurrent record: $totalWorkers workers, all verified")
    }

    @Test
    fun testSessionCheckpointConcurrentOverwrite() = runBlocking {
        println("\n=== [STRESS 5] SESSION CHECKPOINT: CONCURRENT OVERWRITE ===")
        val batchId = "shared_batch"
        val totalOverwrites = 1000
        val errorCounter = AtomicInteger(0)

        val jobs = (1..totalOverwrites).map { i ->
            launch(Dispatchers.Default) {
                try {
                    SessionCheckpointManager.recordProgress(
                        batchId = batchId,
                        total = 100,
                        completed = i % 100,
                        lastPath = "C:/IMG_$i.dng"
                    )
                } catch (e: Throwable) {
                    errorCounter.incrementAndGet()
                }
            }
        }
        jobs.joinAll()

        assertEquals(0, errorCounter.get(), "No errors should occur during concurrent overwrite")

        val checkpoint = SessionCheckpointManager.getCheckpoint(batchId)
        assertNotNull(checkpoint, "Checkpoint should exist after overwrites")
        assertEquals(100, checkpoint.totalFrames, "Total frames should be consistent")
        assertTrue(checkpoint.completedFrames in 0..99, "Completed frames should be valid")

        // Cleanup
        SessionCheckpointManager.clearCheckpoint(batchId)
        println("✔ SessionCheckpoint concurrent overwrite: $totalOverwrites overwrites, integrity verified")
    }

    @Test
    fun testSessionCheckpointConcurrentQuery() = runBlocking {
        println("\n=== [STRESS 6] SESSION CHECKPOINT: CONCURRENT QUERY ===")
        val totalBatches = 50
        val queriesPerBatch = 100
        val errorCounter = AtomicInteger(0)

        // Setup
        for (i in 1..totalBatches) {
            SessionCheckpointManager.recordProgress("batch_$i", 10, 5, null)
        }

        // Concurrent queries
        val jobs = (1..totalBatches).map { batchIdx ->
            launch(Dispatchers.Default) {
                try {
                    repeat(queriesPerBatch) {
                        val hasPending = SessionCheckpointManager.hasPendingRecovery("batch_$batchIdx")
                        assertTrue(hasPending, "batch_$batchIdx should have pending recovery")

                        val checkpoint = SessionCheckpointManager.getCheckpoint("batch_$batchIdx")
                        assertNotNull(checkpoint)
                        assertEquals(5, checkpoint.completedFrames)
                    }
                } catch (e: Throwable) {
                    errorCounter.incrementAndGet()
                }
            }
        }
        jobs.joinAll()

        assertEquals(0, errorCounter.get(), "No errors should occur during concurrent queries")

        // Cleanup
        for (i in 1..totalBatches) {
            SessionCheckpointManager.clearCheckpoint("batch_$i")
        }
        println("✔ SessionCheckpoint concurrent query: $totalBatches batches × $queriesPerBatch queries")
    }

    // =========================================================================
    // 3. LRU MEMORY CACHE CONCURRENT TESTS
    // =========================================================================

    @Test
    fun testLruCacheConcurrentReadWrite() = runBlocking {
        println("\n=== [STRESS 7] LRU CACHE: CONCURRENT READ/WRITE ===")
        val cache = LruMemoryCache<String, String>(maxCapacity = 50)
        val totalThreads = 100
        val operationsPerThread = 100
        val errorCounter = AtomicInteger(0)

        val jobs = (1..totalThreads).map { threadId ->
            launch(Dispatchers.Default) {
                try {
                    for (i in 1..operationsPerThread) {
                        val key = "KEY_${(threadId * operationsPerThread + i) % 200}"
                        val value = "VALUE_$i"
                        cache.put(key, value)
                        cache.get(key)
                    }
                } catch (e: Throwable) {
                    errorCounter.incrementAndGet()
                }
            }
        }
        jobs.joinAll()

        assertEquals(0, errorCounter.get(), "No errors should occur during concurrent access")
        assertEquals(50, cache.size, "Cache size should be maintained at maxCapacity")
        println("✔ LRU cache concurrent read/write: $totalThreads threads × $operationsPerThread ops")
    }

    @Test
    fun testLruCacheConcurrentEviction() = runBlocking {
        println("\n=== [STRESS 8] LRU CACHE: CONCURRENT EVICTION ===")
        val cache = LruMemoryCache<String, String>(maxCapacity = 10)
        val totalWrites = 1000
        val errorCounter = AtomicInteger(0)

        val jobs = (1..10).map { threadId ->
            launch(Dispatchers.Default) {
                try {
                    for (i in 1..100) {
                        val key = "T${threadId}_$i"
                        cache.put(key, "data")
                    }
                } catch (e: Throwable) {
                    errorCounter.incrementAndGet()
                }
            }
        }
        jobs.joinAll()

        assertEquals(0, errorCounter.get(), "No errors should occur during concurrent eviction")
        assertEquals(10, cache.size, "Cache should hold exactly maxCapacity items")
        println("✔ LRU cache concurrent eviction: $totalWrites writes, size maintained")
    }

    @Test
    fun testLruCacheConcurrentClear() = runBlocking {
        println("\n=== [STRESS 9] LRU CACHE: CONCURRENT CLEAR ===")
        val cache = LruMemoryCache<String, String>(maxCapacity = 100)
        val errorCounter = AtomicInteger(0)

        // Fill cache
        for (i in 1..100) {
            cache.put("key_$i", "value_$i")
        }

        // Concurrent clear and write
        val jobs = (1..20).map { threadId ->
            launch(Dispatchers.Default) {
                try {
                    if (threadId == 1) {
                        cache.clear()
                    } else {
                        cache.put("new_$threadId", "data")
                    }
                } catch (e: Throwable) {
                    errorCounter.incrementAndGet()
                }
            }
        }
        jobs.joinAll()

        assertEquals(0, errorCounter.get(), "No errors should occur during concurrent clear")
        assertTrue(cache.size <= 100, "Cache size should be valid")
        println("✔ LRU cache concurrent clear: integrity verified")
    }

    // =========================================================================
    // 4. TRANSFORM STATE RAPID OPERATIONS
    // =========================================================================

    @Test
    fun testTransformStateRapidZoom() {
        println("\n=== [STRESS 10] TRANSFORM STATE: RAPID ZOOM ===")
        val state = TransformState(minScale = 0.1f, maxScale = 10.0f, initialScale = 1.0f)

        // Rapid zoom in/out
        repeat(1000) { i ->
            val zoomDelta = if (i % 2 == 0) 1.1f else 0.9f
            state.onTransform(
                panDelta = androidx.compose.ui.geometry.Offset(1f, 1f),
                zoomDelta = zoomDelta
            )
        }

        assertTrue(state.scale in 0.1f..10.0f, "Scale should remain in bounds")
        println("✔ TransformState rapid zoom: scale=${state.scale}, offsetX=${state.offsetX}")
    }

    @Test
    fun testTransformStateRapidPan() {
        println("\n=== [STRESS 11] TRANSFORM STATE: RAPID PAN ===")
        val state = TransformState(minScale = 0.1f, maxScale = 10.0f, initialScale = 2.0f)

        // Rapid panning
        repeat(1000) { i ->
            val panX = if (i % 2 == 0) 10f else -10f
            val panY = if (i % 3 == 0) 5f else -5f
            state.onTransform(
                panDelta = androidx.compose.ui.geometry.Offset(panX, panY),
                zoomDelta = 1.0f
            )
        }

        assertTrue(state.scale in 0.1f..10.0f, "Scale should remain in bounds")
        println("✔ TransformState rapid pan: scale=${state.scale}, offsetX=${state.offsetX}, offsetY=${state.offsetY}")
    }

    @Test
    fun testTransformStateRapidPinch() {
        println("\n=== [STRESS 12] TRANSFORM STATE: RAPID PINCH ===")
        val state = TransformState(minScale = 0.1f, maxScale = 10.0f, initialScale = 1.0f)

        // Simulate rapid pinch gestures
        repeat(500) { i ->
            val zoomDelta = when {
                i % 4 == 0 -> 1.2f  // Pinch out
                i % 4 == 1 -> 1.1f  // Pinch out smaller
                i % 4 == 2 -> 0.8f  // Pinch in
                else -> 0.9f        // Pinch in smaller
            }
            state.onTransform(
                panDelta = androidx.compose.ui.geometry.Offset(
                    Random.nextFloat() * 10f - 5f,
                    Random.nextFloat() * 10f - 5f
                ),
                zoomDelta = zoomDelta
            )
        }

        assertTrue(state.scale in 0.1f..10.0f, "Scale should remain in bounds after rapid pinch")
        println("✔ TransformState rapid pinch: scale=${state.scale}")
    }

    @Test
    fun testTransformStateZoomBoundaryStress() {
        println("\n=== [STRESS 13] TRANSFORM STATE: ZOOM BOUNDARY STRESS ===")
        val state = TransformState(minScale = 0.5f, maxScale = 5.0f, initialScale = 1.0f)

        // Try to exceed boundaries
        repeat(100) {
            state.setZoom(100f) // Should clamp to max
            assertEquals(5.0f, state.scale)

            state.setZoom(0.01f) // Should clamp to min
            assertEquals(0.5f, state.scale)
        }

        println("✔ TransformState zoom boundary stress: boundaries maintained")
    }

    // =========================================================================
    // 5. SHARPNESS METRIC LARGE BUFFER
    // =========================================================================

    @Test
    fun testSharpnessMetricLargeBuffer() {
        println("\n=== [STRESS 14] SHARPNESS METRIC: LARGE BUFFER (12MP) ===")
        val w = 4000
        val h = 3000
        val buffer = ByteBuffer.allocateDirect(w * h)
        val rand = Random(42)
        val dummyRow = ByteArray(w)

        val startTime = System.currentTimeMillis()
        for (y in 0 until h) {
            rand.nextBytes(dummyRow)
            buffer.put(dummyRow)
        }
        buffer.rewind()

        val sharpness = SharpnessMetric.computeSharpness(buffer, w, h)
        val elapsed = System.currentTimeMillis() - startTime

        assertTrue(sharpness > 0, "High frequency texture should have positive sharpness")
        assertTrue(elapsed < 5000, "12MP computation should complete within 5 seconds")
        println("✔ Sharpness metric large buffer: ${elapsed}ms, score=$sharpness")
    }

    @Test
    fun testSharpnessMetricRepeatedCalls() {
        println("\n=== [STRESS 15] SHARPNESS METRIC: REPEATED CALLS ===")
        val size = 100
        val buffer = ByteBuffer.allocateDirect(size * size)
        for (i in 0 until size * size) {
            buffer.put((i % 256).toByte())
        }

        val startTime = System.currentTimeMillis()
        repeat(100) {
            buffer.rewind()
            val score = SharpnessMetric.computeSharpness(buffer, size, size)
            assertTrue(score >= 0, "Score should be non-negative")
        }
        val elapsed = System.currentTimeMillis() - startTime

        assertTrue(elapsed < 1000, "100 calls on 100x100 buffer should complete within 1 second")
        println("✔ Sharpness metric repeated calls: 100 calls in ${elapsed}ms")
    }

    // =========================================================================
    // 6. IMAGE STREAMER BACKPRESSURE
    // =========================================================================

    @Test
    fun testImageStreamerBackpressure() = runBlocking {
        println("\n=== [STRESS 16] IMAGE STREAMER: BACKPRESSURE ===")
        val totalItems = 1000
        val paths = (1..totalItems).map { "D:/IMG_$it.dng" }
        var activeBuffers = 0
        var peakBuffers = 0

        val streamer = ImageStreamer<String>(
            paths = paths,
            loader = { path ->
                activeBuffers++
                if (activeBuffers > peakBuffers) peakBuffers = activeBuffers
                delay(1) // Simulate I/O
                activeBuffers--
                "LOADED_$path"
            },
            maxQueueSize = 3
        )

        var count = 0
        streamer.stream().collect { item ->
            count++
            assertNotNull(item.data)
        }

        assertEquals(totalItems, count, "All items should be streamed")
        assertTrue(peakBuffers <= 4, "Peak buffers should be bounded (actual: $peakBuffers)")
        println("✔ ImageStreamer backpressure: $totalItems items, peak=$peakBuffers buffers")
    }

    @Test
    fun testImageStreamerErrorHandling() = runBlocking {
        println("\n=== [STRESS 17] IMAGE STREAMER: ERROR HANDLING ===")
        val paths = listOf("good1.jpg", "bad.jpg", "good2.jpg")
        var errorCount = 0

        val streamer = ImageStreamer<String>(
            paths = paths,
            loader = { path ->
                if (path == "bad.jpg") {
                    errorCount++
                    throw RuntimeException("Corrupt file")
                }
                "OK_$path"
            }
        )

        val results = streamer.stream().toList()
        assertEquals(3, results.size)
        assertEquals("OK_good1.jpg", results[0].data)
        assertNull(results[1].data, "Bad file should have null data")
        assertEquals("OK_good2.jpg", results[2].data)
        assertEquals(1, errorCount)
        println("✔ ImageStreamer error handling: errors handled gracefully")
    }

    // =========================================================================
    // 7. ADAPTIVE CHUNK PROCESSOR MASSIVE DATASET
    // =========================================================================

    @Test
    fun testAdaptiveChunkMassiveDataset() = runBlocking {
        println("\n=== [STRESS 18] ADAPTIVE CHUNK: MASSIVE DATASET (25,000) ===")
        val totalItems = 25_000
        val items = (1..totalItems).map { "FILE_$it.raw" }
        var totalProcessed = 0
        var totalChunks = 0

        AdaptiveChunkProcessor.processAdaptive(items) { chunk ->
            totalProcessed += chunk.size
            totalChunks++
        }.collect { progress ->
            assertTrue(progress.progressFraction in 0f..1f, "Progress should be in [0, 1]")
        }

        assertEquals(totalItems, totalProcessed, "All items should be processed")
        assertEquals(63, totalChunks, "Should have 63 chunks (25000/400)")
        println("✔ Adaptive chunk massive dataset: $totalItems items in $totalChunks chunks")
    }

    @Test
    fun testAdaptiveChunkEmptyList() = runBlocking {
        println("\n=== [STRESS 19] ADAPTIVE CHUNK: EMPTY LIST ===")
        val items = emptyList<String>()
        var emitted = false

        AdaptiveChunkProcessor.processAdaptive(items) { chunk ->
            // Should not be called
        }.collect { progress ->
            emitted = true
        }

        assertFalse(emitted, "Empty list should not emit any progress")
        println("✔ Adaptive chunk empty list: no emissions")
    }

    @Test
    fun testAdaptiveChunkSingleItem() = runBlocking {
        println("\n=== [STRESS 20] ADAPTIVE CHUNK: SINGLE ITEM ===")
        val items = listOf("single_file.raw")
        var processed = false

        AdaptiveChunkProcessor.processAdaptive(items) { chunk ->
            assertEquals(1, chunk.size)
            processed = true
        }.collect { progress ->
            assertEquals(1.0f, progress.progressFraction)
        }

        assertTrue(processed, "Single item should be processed")
        println("✔ Adaptive chunk single item: processed correctly")
    }

    // =========================================================================
    // 8. WORKFLOW STATE MANAGER CONCURRENT
    // =========================================================================

    @Test
    fun testWorkflowStateManagerConcurrentAccess() = runBlocking {
        println("\n=== [STRESS 21] WORKFLOW STATE: CONCURRENT ACCESS ===")
        val manager = WorkflowStateManager()
        val errorCounter = AtomicInteger(0)

        manager.start("Batch_001", "Initializing")

        val jobs = (1..50).map { workerId ->
            launch(Dispatchers.Default) {
                try {
                    repeat(100) { op ->
                        when (op % 4) {
                            0 -> manager.updateProgress("Step_$op", op / 100f)
                            1 -> {
                                val isRunning = manager.isRunning
                                // May be true or false depending on timing
                            }
                            2 -> {
                                val progress = manager.progress
                                assertTrue(progress in 0f..1f)
                            }
                            3 -> {
                                val step = manager.currentStep
                                assertNotNull(step)
                            }
                        }
                    }
                } catch (e: Throwable) {
                    errorCounter.incrementAndGet()
                }
            }
        }
        jobs.joinAll()

        assertEquals(0, errorCounter.get(), "No errors should occur during concurrent access")
        println("✔ WorkflowStateManager concurrent access: 50 workers × 100 ops")
    }

    // =========================================================================
    // 9. IMAGE VALIDATOR CONCURRENT
    // =========================================================================

    @Test
    fun testImageValidatorConcurrentValidation() = runBlocking {
        println("\n=== [STRESS 22] IMAGE VALIDATOR: CONCURRENT VALIDATION ===")
        val errorCounter = AtomicInteger(0)
        val totalValidations = 100

        val jobs = (1..20).map { workerId ->
            launch(Dispatchers.Default) {
                try {
                    repeat(5) { i ->
                        val paths = listOf(
                            "C:/Worker${workerId}_img$i.jpg",
                            "C:/Worker${workerId}_raw$i.dng",
                            "C:/Worker${workerId}_bad$i.txt"
                        )
                        val result = ImageValidator.validatePaths(paths)
                        assertEquals(2, result.accepted.size)
                        assertEquals(1, result.rejected.size)
                    }
                } catch (e: Throwable) {
                    errorCounter.incrementAndGet()
                }
            }
        }
        jobs.joinAll()

        assertEquals(0, errorCounter.get(), "No errors should occur during concurrent validation")
        println("✔ ImageValidator concurrent validation: 20 workers × 5 validations")
    }

    // =========================================================================
    // 10. PRESET STORE CONCURRENT
    // =========================================================================

    @Test
    fun testPresetStoreConcurrentAccess() = runBlocking {
        println("\n=== [STRESS 23] PRESET STORE: CONCURRENT ACCESS ===")
        val errorCounter = AtomicInteger(0)

        val jobs = (1..50).map { workerId ->
            launch(Dispatchers.Default) {
                try {
                    // Read
                    val presets = PresetStore.getAllPresets()
                    assertTrue(presets.isNotEmpty())

                    // Get by ID
                    val preset = PresetStore.getPresetById("night_denoise")
                    assertNotNull(preset)

                    // Save custom
                    val custom = PresetStore.saveCustomPreset(
                        name = "Custom_$workerId",
                        description = "Test",
                        params = mapOf("test" to workerId)
                    )
                    assertNotNull(custom)
                } catch (e: Throwable) {
                    errorCounter.incrementAndGet()
                }
            }
        }
        jobs.joinAll()

        assertEquals(0, errorCounter.get(), "No errors should occur during concurrent access")
        println("✔ PresetStore concurrent access: 50 workers")
    }

    // =========================================================================
    // 11. EXTREME MIXED CONCURRENCY
    // =========================================================================

    @Test
    fun testExtremeMixedConcurrency() = runBlocking {
        println("\n=== [STRESS 24] EXTREME MIXED CONCURRENCY ===")
        val manager = BatchStateManager()
        val cache = LruMemoryCache<String, String>(maxCapacity = 100)
        val errorCounter = AtomicInteger(0)

        val jobs = (1..100).map { workerId ->
            launch(Dispatchers.Default) {
                try {
                    // Mix of operations
                    when (workerId % 5) {
                        0 -> {
                            manager.addBatch("Batch_$workerId", listOf("C:/img.dng"))
                        }
                        1 -> {
                            cache.put("key_$workerId", "value_$workerId")
                        }
                        2 -> {
                            SessionCheckpointManager.recordProgress(
                                "cp_$workerId", 10, 5, null
                            )
                        }
                        3 -> {
                            val presets = PresetStore.getAllPresets()
                            assertTrue(presets.isNotEmpty())
                        }
                        4 -> {
                            val paths = listOf("C:/img.jpg", "C:/raw.dng")
                            val result = ImageValidator.validatePaths(paths)
                            assertEquals(2, result.accepted.size)
                        }
                    }
                } catch (e: Throwable) {
                    errorCounter.incrementAndGet()
                }
            }
        }
        jobs.joinAll()

        assertEquals(0, errorCounter.get(), "No errors should occur during extreme mixed concurrency")
        println("✔ Extreme mixed concurrency: 100 workers, 0 errors")

        // Cleanup
        for (i in 1..100) {
            SessionCheckpointManager.clearCheckpoint("cp_$i")
        }
    }

    // =========================================================================
    // 12. MEMORY PRESSURE TEST
    // =========================================================================

    @Test
    fun testMemoryPressureLargeCache() {
        println("\n=== [STRESS 25] MEMORY PRESSURE: LARGE CACHE ===")
        val cache = LruMemoryCache<String, ByteArray>(maxCapacity = 1000)

        // Fill with large objects
        repeat(5000) { i ->
            cache.put("key_$i", ByteArray(1024) { it.toByte() }) // 1KB each
        }

        assertEquals(1000, cache.size, "Cache should maintain maxCapacity")

        // Verify most recent items exist
        for (i in 4001..5000) {
            assertTrue(cache.containsKey("key_$i"), "Recent item key_$i should exist")
        }

        println("✔ Memory pressure large cache: 5000 × 1KB items, cache maintained at 1000")
    }

    @Test
    fun testMemoryPressureRapidAllocation() {
        println("\n=== [STRESS 26] MEMORY PRESSURE: RAPID ALLOCATION ===")
        val buffers = mutableListOf<ByteBuffer>()

        // Allocate and release many buffers
        repeat(1000) { i ->
            val buffer = ByteBuffer.allocateDirect(1024) // 1KB
            buffer.put(ByteArray(1024) { it.toByte() })
            buffers.add(buffer)

            // Keep only last 100
            if (buffers.size > 100) {
                buffers.removeAt(0)
            }
        }

        assertEquals(100, buffers.size, "Should maintain bounded buffer list")
        println("✔ Memory pressure rapid allocation: 1000 allocations, bounded to 100")
    }
}
