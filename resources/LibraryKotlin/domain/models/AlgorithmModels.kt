package org.pixelrefine.genericui.domain.models

/**
 * Kategori algoritma pemrosesan gambar
 */
enum class AlgorithmCategory(val key: String, val displayName: String) {
    ALIGNMENT("alignment", "Alignment"),
    DENOISING("denoising", "Denoising / Fusion"),
    SUPER_RESOLUTION("super_resolution", "Super Resolution");

    companion object {
        fun fromKey(key: String): AlgorithmCategory =
            entries.firstOrNull { it.key.equals(key.trim(), ignoreCase = true) } ?: ALIGNMENT
    }
}

/**
 * Opsi algoritma yang tersedia dalam registri
 */
data class AlgorithmOption(
    val name: String,
    val description: String,
    val defaultParams: Map<String, Any> = emptyMap(),
)

/**
 * Konfigurasi algoritma terpilih beserta parameternya (Type-Safe Parameter Access)
 */
data class AlgorithmConfig(
    val category: AlgorithmCategory,
    val name: String,
    val parameters: Map<String, Any> = emptyMap(),
) {
    fun getInt(key: String, default: Int = 0): Int {
        return (parameters[key] as? Number)?.toInt() ?: default
    }

    fun getFloat(key: String, default: Float = 0f): Float {
        return (parameters[key] as? Number)?.toFloat() ?: default
    }

    fun getDouble(key: String, default: Double = 0.0): Double {
        return (parameters[key] as? Number)?.toDouble() ?: default
    }

    fun getBoolean(key: String, default: Boolean = false): Boolean {
        return (parameters[key] as? Boolean) ?: default
    }

    fun getString(key: String, default: String = ""): String {
        return parameters[key]?.toString() ?: default
    }

    fun withParam(key: String, value: Any): AlgorithmConfig {
        return copy(parameters = parameters + (key to value))
    }
}

/**
 * Registri default algoritma bawaan Pixel Refine
 */
object AlgorithmRegistry {
    val AlignmentOptions = listOf(
        AlgorithmOption("Farneback", "Dense Optical Flow Farneback Algorithm"),
        AlgorithmOption("Lucas Kanade", "Sparse-to-Dense Feature Alignment"),
        AlgorithmOption("Block Matching GPU", "Hardware-accelerated block motion estimation"),
        AlgorithmOption("RAFT", "Recurrent All-Pairs Field Transforms Deep Alignment"),
    )

    val DenoisingOptions = listOf(
        AlgorithmOption("MFDenoiser", "Multi-frame robust spatio-temporal fusion filter"),
        AlgorithmOption("Bilateral Grid", "Edge-preserving fast bilateral filter"),
        AlgorithmOption("Gaussian Blur", "Fast isotropic gaussian smoothing"),
    )

    val SuperResolutionOptions = listOf(
        AlgorithmOption("No Super Resolution", "Process without resolution upscaling"),
        AlgorithmOption("WSR", "Weighted-Spatial Multi-Frame Super-Resolution 2x/4x"),
    )

    fun getOptions(category: AlgorithmCategory): List<AlgorithmOption> = when (category) {
        AlgorithmCategory.ALIGNMENT -> AlignmentOptions
        AlgorithmCategory.DENOISING -> DenoisingOptions
        AlgorithmCategory.SUPER_RESOLUTION -> SuperResolutionOptions
    }
}
