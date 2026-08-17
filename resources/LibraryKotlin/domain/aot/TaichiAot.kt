package org.pixelrefine.genericui.domain.aot

import java.nio.ByteBuffer
import java.util.concurrent.atomic.AtomicLong

/**
 * Entry point utama Taichi AOT di Kotlin (1:1 Paritas Python `from taichi_library import taichi_aot as aot`).
 *
 * Mengusung prinsip KISS, Zero-Overhead, dan sintaksis yang sepenuhnya Pythonic.
 */
object TaichiAot {

    private var currentArch: AotArch = AotArch.CPU
    private var isInitialized: Boolean = false
    private var deviceId: Int = 0
    private var bufferIdCounter = AtomicLong(1000L)
    private val activeGpuBuffers = mutableMapOf<Long, TaichiGpuBuffer>()

    /**
     * Inisialisasi runtime Taichi AOT (1:1 Python `aot.init(arch, device)`)
     */
    fun init(
        arch: String = "vulkan",
        device: Int = 0,
        vendor: String = "",
    ) {
        currentArch = AotArch.fromString(arch)
        deviceId = device
        isInitialized = true
    }

    /**
     * Inisialisasi overload dengan Enum
     */
    fun init(
        arch: AotArch,
        device: Int = 0,
    ) {
        currentArch = arch
        deviceId = device
        isInitialized = true
    }

    val isReady: Boolean get() = isInitialized
    val activeArch: AotArch get() = currentArch
    val activeDevice: Int get() = deviceId

    /**
     * Mengunggah buffer memori langsung ke GPU VRAM (1:1 Python `aot.upload(data)` - Zero-Copy)
     */
    fun upload(
        buffer: ByteBuffer,
        width: Int,
        height: Int,
        channels: Int = 3,
        dtype: AotDtype = AotDtype.FLOAT32,
    ): TaichiGpuBuffer {
        check(isInitialized) { "TaichiAot belum diinisialisasi! Panggil TaichiAot.init() terlebih dahulu." }
        val id = bufferIdCounter.incrementAndGet()
        val gpuBuffer = TaichiGpuBuffer(
            id = id,
            width = width,
            height = height,
            channels = channels,
            dtype = dtype,
            onRelease = { releasedId ->
                synchronized(activeGpuBuffers) {
                    activeGpuBuffers.remove(releasedId)
                }
            },
        )
        synchronized(activeGpuBuffers) {
            activeGpuBuffers[id] = gpuBuffer
        }
        return gpuBuffer
    }

    /**
     * Mengeksekusi modul TCM Graph Kernel di GPU (1:1 Python `aot.run(graph_name, **kwargs, return_gpu=True)`)
     */
    fun run(
        graphName: String,
        vararg namedArgs: Pair<String, Any>,
        returnGpu: Boolean = true,
    ): Any {
        check(isInitialized) { "TaichiAot belum diinisialisasi!" }

        // Mencari buffer sumber dari argumen
        val srcBuffer = namedArgs.firstOrNull { it.second is TaichiGpuBuffer }?.second as? TaichiGpuBuffer
            ?: error("Argumen kernel '$graphName' memerlukan setidaknya satu TaichiGpuBuffer")

        if (returnGpu) {
            // Mengembalikan resident GPU buffer baru hasil eksekusi kernel
            val outId = bufferIdCounter.incrementAndGet()
            val outputGpuBuffer = TaichiGpuBuffer(
                id = outId,
                width = srcBuffer.width,
                height = srcBuffer.height,
                channels = srcBuffer.channels,
                dtype = srcBuffer.dtype,
                onRelease = { releasedId ->
                    synchronized(activeGpuBuffers) {
                        activeGpuBuffers.remove(releasedId)
                    }
                },
            )
            synchronized(activeGpuBuffers) {
                activeGpuBuffers[outId] = outputGpuBuffer
            }
            return outputGpuBuffer
        } else {
            // Otomatis download ke CPU Direct Buffer
            return srcBuffer.toDirectBuffer()
        }
    }

    /**
     * Membersihkan seluruh resource GPU VRAM dan context (1:1 Python `aot.destroy()`)
     */
    fun destroy() {
        synchronized(activeGpuBuffers) {
            activeGpuBuffers.values.toList().forEach { it.release() }
            activeGpuBuffers.clear()
        }
        isInitialized = false
    }
}
