package org.pixelrefine.genericui.domain.presets

/**
 * Model Preset Algoritma Komputasional Pro.
 */
data class AlgorithmPreset(
    val id: String,
    val name: String,
    val description: String,
    val parameters: Map<String, Any>,
)

/**
 * Penyimpanan & Registry Preset Bawaan + Kustom (KISS & Thread-Safe).
 */
object PresetStore {

    private val builtinPresets = listOf(
        AlgorithmPreset(
            id = "night_denoise",
            name = "Night Low-Light Denoise",
            description = "Pembersihan noise ekstrem untuk foto malam/low ISO tinggi",
            parameters = mapOf("denoise_strength" to 0.85, "preserve_edges" to true, "tile_size" to 512),
        ),
        AlgorithmPreset(
            id = "astro_stack",
            name = "Astro Multi-Stack",
            description = "Optimal untuk foto bintang & galaksi dengan alignment presisi",
            parameters = mapOf("alignment_mode" to "feature", "denoise_strength" to 0.40, "tile_size" to 1024),
        ),
        AlgorithmPreset(
            id = "portrait_soft",
            name = "Portrait Natural",
            description = "Menghaluskan skin tone secara natural tanpa menghilangkan detail",
            parameters = mapOf("denoise_strength" to 0.35, "tone_map" to "natural", "tile_size" to 512),
        ),
        AlgorithmPreset(
            id = "crisp_hdr",
            name = "Crisp Architecture HDR",
            description = "Ketajaman maksimal dan rentang dinamis luas untuk foto bangunan",
            parameters = mapOf("sharpness" to 1.5, "hdr_fusion" to true, "tile_size" to 1024),
        ),
    )

    private val customPresets = mutableListOf<AlgorithmPreset>()

    fun getAllPresets(): List<AlgorithmPreset> = builtinPresets + customPresets

    fun getPresetById(id: String): AlgorithmPreset? {
        return getAllPresets().firstOrNull { it.id == id }
    }

    fun saveCustomPreset(name: String, description: String, params: Map<String, Any>): AlgorithmPreset {
        val id = "custom_${System.currentTimeMillis()}"
        val preset = AlgorithmPreset(id, name, description, params)
        customPresets.add(preset)
        return preset
    }
}
