package org.pixelrefine.genericui

import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import org.pixelrefine.genericui.animations.GlobalToastManager
import org.pixelrefine.genericui.components.*
import org.pixelrefine.genericui.domain.aot.TaichiAot
import org.pixelrefine.genericui.domain.models.BatchItem
import org.pixelrefine.genericui.domain.models.ImageItem
import org.pixelrefine.genericui.domain.presets.AlgorithmPreset
import org.pixelrefine.genericui.domain.presets.PresetStore
import org.pixelrefine.genericui.domain.state.BatchStateManager
import org.pixelrefine.genericui.domain.state.SessionCheckpoint
import org.pixelrefine.genericui.domain.state.SessionCheckpointManager
import org.pixelrefine.genericui.domain.validation.ImageValidator
import org.pixelrefine.genericui.domain.validation.SharpnessMetric
import org.pixelrefine.genericui.domain.validation.ValidationResult
import java.nio.ByteBuffer

/**
 * ============================================================================
 * PIXEL REFINE PYTHONIC 1-LINE CONVENIENCE FACADE & COMPOSABLE ALIASES
 * ============================================================================
 * Menyediakan pemanggilan 1-baris gaya Python (`snake_case`) untuk seluruh
 * komponen UI, domain logic, state management, dan AOT computing di Kotlin,
 * tanpa menghilangkan fungsi Kotlin standar yang sudah ada.
 */

// ============================================================================
// 1. PYTHONIC UI COMPOSABLES (1-LINE COMPOSABLE ALIASES)
// ============================================================================

/**
 * 1-line Pythonic alias untuk `ToneCurveEditor`
 */
@Composable
fun tone_curve_editor(
    on_change: (List<ControlPoint>) -> Unit = {},
    initial_points: List<ControlPoint> = listOf(
        ControlPoint(0.0f, 0.0f),
        ControlPoint(0.25f, 0.25f),
        ControlPoint(0.75f, 0.75f),
        ControlPoint(1.0f, 1.0f),
    ),
    variant: Variant = Variant.Primary,
    height: Dp = 150.dp,
    modifier: Modifier = Modifier,
) = ToneCurveEditor(
    onCurveChanged = on_change,
    initialPoints = initial_points,
    variant = variant,
    height = height,
    modifier = modifier,
)

/**
 * 1-line Pythonic alias untuk `HistogramViewer`
 */
@Composable
fun histogram_viewer(
    red_data: FloatArray = FloatArray(256) { 0f },
    green_data: FloatArray = FloatArray(256) { 0f },
    blue_data: FloatArray = FloatArray(256) { 0f },
    luminance_data: FloatArray? = null,
    show_channels: Boolean = true,
    variant: Variant = Variant.Dark,
    height: Dp = 110.dp,
    modifier: Modifier = Modifier,
) = HistogramViewer(
    redData = red_data,
    greenData = green_data,
    blueData = blue_data,
    luminanceData = luminance_data,
    showChannels = show_channels,
    variant = variant,
    height = height,
    modifier = modifier,
)

/**
 * 1-line Pythonic alias untuk `Filmstrip`
 */
@Composable
fun filmstrip(
    images: List<ImageItem>,
    selected_index: Int = -1,
    on_select: (Int) -> Unit = {},
    modifier: Modifier = Modifier,
) = Filmstrip(
    images = images,
    selectedIndex = selected_index,
    onSelectImage = on_select,
    modifier = modifier,
)

/**
 * 1-line Pythonic alias untuk `PresetSelector`
 */
@Composable
fun preset_selector(
    selected_id: String? = "night_denoise",
    on_select: (AlgorithmPreset) -> Unit = {},
    variant: Variant = Variant.Primary,
    modifier: Modifier = Modifier,
) = PresetSelector(
    selectedPresetId = selected_id,
    onSelectPreset = on_select,
    variant = variant,
    modifier = modifier,
)

/**
 * 1-line Pythonic alias untuk `SegmentedControl`
 */
@Composable
fun segmented_control(
    items: List<String>,
    selected_index: Int = 0,
    on_select: (Int) -> Unit = {},
    variant: Variant = Variant.Primary,
    modifier: Modifier = Modifier,
) = SegmentedControl(
    items = items,
    selectedIndex = selected_index,
    onItemSelected = on_select,
    variant = variant,
    modifier = modifier,
)

/**
 * 1-line Pythonic alias untuk `RangeSlider`
 */
@Composable
fun range_slider(
    min_val: Float = 0f,
    max_val: Float = 100f,
    current_range: ClosedFloatingPointRange<Float> = 20f..80f,
    on_change: (ClosedFloatingPointRange<Float>) -> Unit = {},
    title: String = "",
    variant: Variant = Variant.Primary,
    modifier: Modifier = Modifier,
) = RangeSlider(
    minVal = min_val,
    maxVal = max_val,
    currentRange = current_range,
    onRangeChange = on_change,
    title = title,
    variant = variant,
    modifier = modifier,
)

/**
 * 1-line Pythonic alias untuk `Magnifier` (Pixel Loupe)
 */
@Composable
fun magnifier(
    zoom_factor: Float = 4.0f,
    loupe_size: Dp = 100.dp,
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit,
) = Magnifier(
    zoomFactor = zoom_factor,
    loupeSize = loupe_size,
    modifier = modifier,
    content = content,
)

/**
 * 1-line Pythonic alias untuk `Button`
 */
@Composable
fun button(
    text: String,
    on_click: () -> Unit = {},
    variant: Variant = Variant.Primary,
    is_loading: Boolean = false,
    loading_text: String = "Wait...",
    is_disabled: Boolean = false,
    modifier: Modifier = Modifier,
) = Button(
    text = text,
    onClick = on_click,
    variant = variant,
    isLoading = is_loading,
    loadingText = loading_text,
    enabled = !is_disabled,
    modifier = modifier,
)

/**
 * 1-line Pythonic alias untuk `Badge`
 */
@Composable
fun badge(
    text: String,
    variant: Variant = Variant.Primary,
    show_pulse: Boolean = false,
    show_dot: Boolean = true,
    modifier: Modifier = Modifier,
) = Badge(
    text = text,
    variant = variant,
    pulsing = show_pulse,
    showDot = show_dot,
    modifier = modifier,
)

/**
 * 1-line Pythonic alias untuk `BatchCard`
 */
@Composable
fun batch_card(
    name: String,
    image_count: Int,
    on_click: () -> Unit = {},
    status: org.pixelrefine.genericui.domain.models.BatchStatus = org.pixelrefine.genericui.domain.models.BatchStatus.IDLE,
    modifier: Modifier = Modifier,
) = BatchCard(
    name = name,
    imageCount = image_count,
    onClick = on_click,
    status = status,
    modifier = modifier,
)

/**
 * 1-line Pythonic alias untuk `NewBatchCard`
 */
@Composable
fun new_batch_card(
    on_click: () -> Unit = {},
    modifier: Modifier = Modifier,
) = NewBatchCard(
    onClick = on_click,
    modifier = modifier,
)

/**
 * 1-line Pythonic alias untuk `DotIndicator`
 */
@Composable
fun dot_indicator(
    count: Int,
    active_index: Int = 0,
    on_index_changed: ((Int) -> Unit)? = null,
    modifier: Modifier = Modifier,
) = DotIndicator(
    count = count,
    activeIndex = active_index,
    onIndexChanged = on_index_changed,
    modifier = modifier,
)

/**
 * 1-line Pythonic alias untuk `ProgressBar`
 */
@Composable
fun progress_bar(
    value: Int = 0,
    max_value: Int = 100,
    variant: Variant = Variant.Primary,
    show_label: Boolean = true,
    height: Dp = 12.dp,
    modifier: Modifier = Modifier,
) = ProgressBar(
    value = value,
    maxValue = max_value,
    variant = variant,
    showLabel = show_label,
    height = height,
    modifier = modifier,
)

/**
 * 1-line Pythonic alias untuk `BottomActionBar`
 */
@Composable
fun bottom_action_bar(
    items: List<BottomNavItem>,
    active_item: String,
    primary_label: String = "Start",
    primary_running: Boolean = false,
    on_nav_click: (String) -> Unit = {},
    on_primary_click: () -> Unit = {},
    modifier: Modifier = Modifier,
) = BottomActionBar(
    items = items,
    activeItem = active_item,
    primaryLabel = primary_label,
    primaryRunning = primary_running,
    onNavClick = on_nav_click,
    onPrimaryClick = on_primary_click,
    modifier = modifier,
)

// ============================================================================
// 2. PYTHONIC PROCEDURAL FUNCTIONS (LOGIC & COMPUTE)
// ============================================================================

/**
 * 1-line Toast procedural gaya Python: `toast("Selesai!", Variant.Success)`
 */
fun toast(
    message: String,
    variant: Variant = Variant.Info,
    position: OverlayPosition = OverlayPosition.BottomCenter,
    duration_ms: Long = 3000L,
) {
    GlobalToastManager.show(
        message = message,
        variant = variant,
        position = position,
        durationMs = duration_ms,
    )
}

/**
 * 1-line AI Culling gaya Python: `auto_cull(images, buffers, 4000, 3000)`
 */
fun auto_cull(images: List<ImageItem>, buffers: List<ByteBuffer>, width: Int, height: Int): List<ImageItem> {
    val scores = buffers.map { SharpnessMetric.computeSharpness(it, width, height) }
    return SharpnessMetric.autoAssignBestReference(images, scores)
}

/**
 * 1-line Laplacian Sharpness Score: `compute_sharpness(buffer, 4000, 3000)`
 */
fun compute_sharpness(buffer: ByteBuffer, width: Int, height: Int): Double {
    return SharpnessMetric.computeSharpness(buffer, width, height)
}

/**
 * 1-line Path Validation: `validate_paths(listOf("path/to/raw.dng"))`
 */
fun validate_paths(paths: List<String>, existing_paths: Set<String> = emptySet()): ValidationResult {
    return ImageValidator.validatePaths(paths, existing_paths)
}

/**
 * 1-line Preset Manager gaya Python: `get_preset("night_denoise")`
 */
fun get_preset(preset_id: String): AlgorithmPreset? = PresetStore.getPresetById(preset_id)
fun list_presets(): List<AlgorithmPreset> = PresetStore.getAllPresets()
fun save_preset(name: String, description: String, params: Map<String, Any>): AlgorithmPreset =
    PresetStore.saveCustomPreset(name, description, params)

/**
 * 1-line Session Checkpoint gaya Python: `save_checkpoint("batch_1", 50, 25)`
 */
fun save_checkpoint(batch_id: String, total: Int, completed: Int, last_path: String? = null) =
    SessionCheckpointManager.recordProgress(batch_id, total, completed, last_path)

fun has_recovery(batch_id: String): Boolean = SessionCheckpointManager.hasPendingRecovery(batch_id)
fun get_checkpoint(batch_id: String): SessionCheckpoint? = SessionCheckpointManager.getCheckpoint(batch_id)
fun clear_checkpoint(batch_id: String) = SessionCheckpointManager.clearCheckpoint(batch_id)

/**
 * Objek facade tunggal namespace `pixel_refine`
 */
object pixel_refine {
    fun toast(message: String, variant: Variant = Variant.Info, position: OverlayPosition = OverlayPosition.BottomCenter, duration_ms: Long = 3000L) =
        org.pixelrefine.genericui.toast(message, variant, position, duration_ms)

    fun auto_cull(images: List<ImageItem>, buffers: List<ByteBuffer>, width: Int, height: Int) =
        org.pixelrefine.genericui.auto_cull(images, buffers, width, height)

    fun compute_sharpness(buffer: ByteBuffer, width: Int, height: Int) =
        org.pixelrefine.genericui.compute_sharpness(buffer, width, height)

    fun validate_paths(paths: List<String>, existing: Set<String> = emptySet()) =
        org.pixelrefine.genericui.validate_paths(paths, existing)

    fun get_preset(id: String) = org.pixelrefine.genericui.get_preset(id)
    fun list_presets() = org.pixelrefine.genericui.list_presets()
    fun save_preset(name: String, desc: String, params: Map<String, Any>) =
        org.pixelrefine.genericui.save_preset(name, desc, params)

    fun save_checkpoint(id: String, total: Int, completed: Int, last: String? = null) =
        org.pixelrefine.genericui.save_checkpoint(id, total, completed, last)

    fun has_recovery(id: String) = org.pixelrefine.genericui.has_recovery(id)
    fun get_checkpoint(id: String) = org.pixelrefine.genericui.get_checkpoint(id)
    fun clear_checkpoint(id: String) = org.pixelrefine.genericui.clear_checkpoint(id)
}
