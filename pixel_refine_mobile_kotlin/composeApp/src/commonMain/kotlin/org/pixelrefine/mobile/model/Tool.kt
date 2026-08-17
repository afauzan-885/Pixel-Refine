package org.pixelrefine.mobile.model

import org.pixelrefine.genericui.components.Variant

/** Layar aplikasi (mirror AppState page routing di main_mobile.py). */
enum class Screen { Home, Workspace, Settings }

/** Tool pemrosesan — mirror kartu tool di Home (main_mobile.py). */
data class Tool(
    val name: String,
    val variant: Variant,
    val icon: String,
    val description: String,
)

val TOOLS = listOf(
    Tool("MFDenoiser", Variant.Primary, "🖼️", "Multi-frame denoising"),
    Tool("MFResolution", Variant.Success, "🌟", "Multi-frame super resolution"),
    Tool("HDR", Variant.Info, "🌅", "High dynamic range fusion"),
    Tool("Panorama", Variant.Secondary, "🌄", "Panorama stitching"),
)

/** Data batch contoh (placeholder, mirror mock workspace). */
val SAMPLE_BATCHES = listOf(
    "Batch 1" to 13,
    "Batch 2" to 8,
    "Batch 3" to 5,
    "Batch 4" to 12,
)

/** Opsi bahasa (Settings). */
val LANGUAGES = listOf("English", "Bahasa Indonesia", "中文", "Melayu")
