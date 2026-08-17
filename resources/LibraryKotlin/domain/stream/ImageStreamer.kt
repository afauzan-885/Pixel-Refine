package org.pixelrefine.genericui.domain.stream

import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.channels.ReceiveChannel
import kotlinx.coroutines.channels.produce
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.flow.flowOn

/**
 * Item yang dihasilkan oleh ImageStreamer
 */
data class StreamedImage<T>(
    val index: Int,
    val total: Int,
    val path: String,
    val data: T?,
) {
    val progressFraction: Float
        get() = if (total > 0) (index + 1).toFloat() / total else 0f
}

/**
 * ImageStreamer generik untuk Producer-Consumer Image Streaming.
 * Membaca data gambar satu per satu secara asinkron dengan buffer kecil
 * untuk menghemat penggunaan RAM dan mencegah OOM (Out Of Memory).
 *
 * Mirror: `resources/pixel_refine_desktop/enhance_stack/core/logic/image_streamer.py`
 */
class ImageStreamer<T>(
    private val paths: List<String>,
    private val loader: suspend (path: String) -> T?,
    private val maxQueueSize: Int = 3,
) {
    val totalCount: Int get() = paths.size

    /**
     * Menghasilkan Kotlin Flow yang dapat dikonsumsi oleh UI atau proses worker secara kontinyu.
     */
    fun stream(): Flow<StreamedImage<T>> = flow {
        val total = paths.size
        for (index in paths.indices) {
            val path = paths[index]
            val data = try {
                loader(path)
            } catch (e: Exception) {
                null
            }
            emit(StreamedImage(index = index, total = total, path = path, data = data))
        }
    }.flowOn(Dispatchers.Default)

    /**
     * Producer-Consumer Channel stream untuk konsumsi paralel dengan backpressure.
     */
    @OptIn(kotlinx.coroutines.ExperimentalCoroutinesApi::class)
    fun CoroutineScope.produceChannel(): ReceiveChannel<StreamedImage<T>> = produce(
        context = Dispatchers.Default,
        capacity = maxQueueSize,
    ) {
        val total = paths.size
        for (index in paths.indices) {
            val path = paths[index]
            val data = try {
                loader(path)
            } catch (e: Exception) {
                null
            }
            send(StreamedImage(index = index, total = total, path = path, data = data))
        }
    }
}
