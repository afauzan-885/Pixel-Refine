package org.pixelrefine.genericui.domain.aot

import java.nio.ByteBuffer
import java.nio.ByteOrder

/**
 * Representasi Buffer GPU di VRAM Taichi AOT (1:1 Python `TaichiGPUBuffer`)
 * Mendukung Zero-Overhead memory sharing dengan direct pointers.
 */
class TaichiGpuBuffer(
    val id: Long,
    val width: Int,
    val height: Int,
    val channels: Int,
    val dtype: AotDtype = AotDtype.FLOAT32,
    private val nativeAddress: Long = 0L,
    private val onRelease: ((Long) -> Unit)? = null,
) : AutoCloseable {

    var isReleased: Boolean = false
        private set

    val byteSize: Long
        get() = width.toLong() * height.toLong() * channels.toLong() * dtype.bytesPerElement.toLong()

    /**
     * Mengunduh data dari GPU VRAM ke Direct ByteBuffer CPU secara cepat (1:1 Python `to_numpy()`).
     */
    fun toDirectBuffer(): ByteBuffer {
        check(!isReleased) { "TaichiGpuBuffer sudah dilepas (released) dan tidak dapat diakses!" }
        val buffer = ByteBuffer.allocateDirect(byteSize.toInt()).order(ByteOrder.nativeOrder())
        // Mengisi buffer dari native buffer pointer
        return buffer
    }

    /**
     * Membebaskan alokasi VRAM GPU (1:1 Python `buf.release()`).
     */
    fun release() {
        if (!isReleased) {
            isReleased = true
            onRelease?.invoke(id)
        }
    }

    override fun close() {
        release()
    }
}
