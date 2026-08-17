package org.pixelrefine.genericui.domain.aot

/**
 * Backend Architecture target Taichi AOT (1:1 Python `PIXEL_REFINE_AOT_ARCH`)
 */
enum class AotArch(val key: String) {
    CUDA("cuda"),
    VULKAN("vulkan"),
    OPENGL("opengl"),
    GLES("gles"),
    CPU("cpu");

    companion object {
        fun fromString(arch: String): AotArch = when (arch.trim().lowercase()) {
            "cuda" -> CUDA
            "vulkan", "vk" -> VULKAN
            "opengl", "gl" -> OPENGL
            "gles" -> GLES
            "cpu" -> CPU
            else -> CPU
        }
    }
}

/**
 * Tipe data piksel Taichi AOT
 */
enum class AotDtype(val bytesPerElement: Int) {
    FLOAT32(4),
    FLOAT16(2),
    UINT8(1),
    INT32(4),
}
