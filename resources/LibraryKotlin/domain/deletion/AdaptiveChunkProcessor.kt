package org.pixelrefine.genericui.domain.deletion

import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow

/**
 * Hasil pemrosesan chunk bertahap
 */
data class ChunkProgress<T>(
    val chunkIndex: Int,
    val totalChunks: Int,
    val processedItems: List<T>,
    val totalProcessedCount: Int,
    val totalCount: Int,
) {
    val progressFraction: Float
        get() = if (totalCount > 0) totalProcessedCount.toFloat() / totalCount else 0f
}

/**
 * Adaptive Chunk Processor untuk eksekusi batch/penghapusan data skala besar secara bertahap.
 *
 * Mengadaptasi logika dari `ImageDeletionWorker.py`:
 * - Item < 500  -> chunk size 50
 * - Item >= 500 -> chunk size 100
 * - Item >= 1000 -> chunk size 200
 * - Item >= 1500 -> chunk size 400
 */
object AdaptiveChunkProcessor {

    fun calculateAdaptiveChunkSize(totalCount: Int): Int {
        return when {
            totalCount >= 1500 -> 400
            totalCount >= 1000 -> 200
            totalCount >= 500 -> 100
            else -> 50
        }
    }

    /**
     * Memproses sekumpulan item secara bertahap dalam ukuran chunk adaptif dan mengalirkan progres via Flow.
     */
    fun <T, R> processAdaptive(
        items: List<T>,
        processor: suspend (chunk: List<T>) -> R,
    ): Flow<ChunkProgress<T>> = flow {
        val totalCount = items.size
        if (totalCount == 0) return@flow

        val chunkSize = calculateAdaptiveChunkSize(totalCount)
        val chunks = items.chunked(chunkSize)
        val totalChunks = chunks.size
        var processedCount = 0

        for (index in chunks.indices) {
            val chunk = chunks[index]
            processor(chunk)
            processedCount += chunk.size
            emit(
                ChunkProgress(
                    chunkIndex = index,
                    totalChunks = totalChunks,
                    processedItems = chunk,
                    totalProcessedCount = processedCount,
                    totalCount = totalCount,
                )
            )
        }
    }
}
