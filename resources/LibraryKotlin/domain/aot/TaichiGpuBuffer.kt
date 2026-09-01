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
     *
     * Mengalokasikan Direct ByteBuffer dan menyalin data dari native pointer.
     * Untuk implementasi production, gunakan JNI/FFI untuk memcpy dari nativeAddress.
     */
    fun toDirectBuffer(): ByteBuffer {
        check(!isReleased) { "TaichiGpuBuffer sudah dilepas (released) dan tidak dapat diakses!" }
        val size = byteSize.toInt()
        require(size > 0) { "Buffer size must be positive, got $size" }
        require(size <= 1024 * 1024 * 1024) { "Buffer size exceeds 1GB limit: $size bytes" }

        val buffer = ByteBuffer.allocateDirect(size).order(ByteOrder.nativeOrder())
        // TODO: Implementasi native memcpy dari nativeAddress ke buffer
        // Saat ini buffer dialokasikan kosong; untuk production, gunakan:
        // JNI: memcpy(buffer.address(), nativeAddress, byteSize)
        // Atau gunakan sun.misc.Unsafe.copyMemory() untuk zero-copy
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
