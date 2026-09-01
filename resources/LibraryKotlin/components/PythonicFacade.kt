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
 * 1-line Pythonic alias für `SmallDropdown`
 */
@Composable
fun small_dropdown(
    selected: String,
    options: List<String>,
    on_select: (String) -> Unit,
    modifier: Modifier = Modifier,
) = SmallDropdown(
    selected = selected,
    options = options,
    onSelect = on_select,
    modifier = modifier,
)

/**
 * 1-line Pythonic alias für `BottomActionBar`
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

// ============================================================================
// 3. PYTHONIC ALIASES FOR NEW COMPONENTS (BATCH 1-11)
// ============================================================================

// Typography
@Composable
fun h1(text: String, modifier: Modifier = Modifier) = H1(text = text, modifier = modifier)
@Composable
fun h2(text: String, modifier: Modifier = Modifier) = H2(text = text, modifier = modifier)
@Composable
fun h3(text: String, modifier: Modifier = Modifier) = H3(text = text, modifier = modifier)
@Composable
fun h4(text: String, modifier: Modifier = Modifier) = H4(text = text, modifier = modifier)
@Composable
fun h5(text: String, modifier: Modifier = Modifier) = H5(text = text, modifier = modifier)
@Composable
fun h6(text: String, modifier: Modifier = Modifier) = H6(text = text, modifier = modifier)
@Composable
fun body_text(text: String, modifier: Modifier = Modifier) = BodyText(text = text, modifier = modifier)
@Composable
fun caption_text(text: String, modifier: Modifier = Modifier) = CaptionText(text = text, modifier = modifier)
@Composable
fun overline_text(text: String, modifier: Modifier = Modifier) = OverlineText(text = text, modifier = modifier)
@Composable
fun code_text(text: String, modifier: Modifier = Modifier) = CodeText(text = text, modifier = modifier)
@Composable
fun link_text(text: String, on_click: () -> Unit, modifier: Modifier = Modifier) =
    LinkText(text = text, onClick = on_click, modifier = modifier)

// Single Slider
@Composable
fun slider(
    value: Float,
    on_change: (Float) -> Unit,
    min_val: Float = 0f,
    max_val: Float = 1f,
    step: Float = 0f,
    enabled: Boolean = true,
    title: String? = null,
    modifier: Modifier = Modifier,
) = Slider(
    value = value,
    onValueChange = on_change,
    minVal = min_val,
    maxVal = max_val,
    step = step,
    enabled = enabled,
    title = title,
    modifier = modifier,
)

// Tooltip
@Composable
fun tooltip(
    text: String,
    position: TooltipPosition = TooltipPosition.TOP,
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit,
) = Tooltip(text = text, position = position, modifier = modifier, content = content)

// Divider
@Composable
fun divider(modifier: Modifier = Modifier) = HorizontalDivider(modifier = modifier)
@Composable
fun divider_with_label(text: String, modifier: Modifier = Modifier) = DividerWithLabel(text = text, modifier = modifier)

// Avatar
@Composable
fun avatar(
    initials: String? = null,
    size: AvatarSize = AvatarSize.MD,
    modifier: Modifier = Modifier,
) = Avatar(initials = initials, size = size, modifier = modifier)
@Composable
fun avatar_group(
    avatars: List<AvatarData>,
    max_visible: Int = 5,
    size: AvatarSize = AvatarSize.MD,
    modifier: Modifier = Modifier,
) = AvatarGroup(avatars = avatars, maxVisible = max_visible, size = size, modifier = modifier)

// Chips
@Composable
fun chip(
    text: String,
    variant: Variant = Variant.Primary,
    selected: Boolean = false,
    on_click: (() -> Unit)? = null,
    on_close: (() -> Unit)? = null,
    modifier: Modifier = Modifier,
) = Chip(text = text, variant = variant, selected = selected, onClick = on_click, onClose = on_close, modifier = modifier)
@Composable
fun tag(text: String, variant: Variant = Variant.Primary, modifier: Modifier = Modifier) =
    Tag(text = text, variant = variant, modifier = modifier)

// NumberInput
@Composable
fun number_input(
    value: Double,
    on_change: (Double) -> Unit,
    min_val: Double = 0.0,
    max_val: Double = 100.0,
    step: Double = 1.0,
    label: String? = null,
    modifier: Modifier = Modifier,
) = NumberInput(value = value, onValueChange = on_change, minVal = min_val, maxVal = max_val, step = step, label = label, modifier = modifier)

// TextArea
@Composable
fun text_area(
    value: String,
    on_change: (String) -> Unit,
    placeholder: String = "",
    min_lines: Int = 3,
    modifier: Modifier = Modifier,
) = TextArea(value = value, onValueChange = on_change, placeholder = placeholder, minLines = min_lines, modifier = modifier)

// SearchInput
@Composable
fun search_input(
    value: String,
    on_change: (String) -> Unit,
    placeholder: String = "Search...",
    modifier: Modifier = Modifier,
) = SearchInput(value = value, onValueChange = on_change, placeholder = placeholder, modifier = modifier)

// CheckboxGroup
@Composable
fun checkbox_group(
    options: List<String>,
    selected: Set<String>,
    on_change: (Set<String>) -> Unit,
    modifier: Modifier = Modifier,
) = CheckboxGroup(options = options, selectedOptions = selected, onSelectionChange = on_change, modifier = modifier)

// DatePicker
@Composable
fun date_picker(
    selected_date: SimpleDate?,
    on_date_selected: (SimpleDate) -> Unit,
    modifier: Modifier = Modifier,
) = DatePicker(selectedDate = selected_date, onDateSelected = on_date_selected, modifier = modifier)

// Alert
@Composable
fun success_alert(title: String, description: String? = null, modifier: Modifier = Modifier) =
    SuccessAlert(title = title, description = description, modifier = modifier)
@Composable
fun warning_alert(title: String, description: String? = null, modifier: Modifier = Modifier) =
    WarningAlert(title = title, description = description, modifier = modifier)
@Composable
fun error_alert(title: String, description: String? = null, modifier: Modifier = Modifier) =
    ErrorAlert(title = title, description = description, modifier = modifier)
@Composable
fun info_alert(title: String, description: String? = null, modifier: Modifier = Modifier) =
    InfoAlert(title = title, description = description, modifier = modifier)

// Snackbar
fun show_snackbar(
    message: String,
    variant: Variant = Variant.Info,
    duration_ms: Long = 4000L,
) = SnackbarManager.show(message = message, variant = variant, duration = duration_ms)

// Notification
fun add_notification(
    title: String,
    description: String? = null,
    variant: Variant = Variant.Info,
) = NotificationManager.add(NotificationData(title = title, description = description, variant = variant))

// Popover
@Composable
fun popover(
    content: @Composable () -> Unit,
    trigger_content: @Composable () -> Unit,
    modifier: Modifier = Modifier,
) = Popover(modifier = modifier, content = content, triggerContent = trigger_content)

// Breadcrumbs
@Composable
fun breadcrumbs(
    items: List<BreadcrumbItem>,
    separator: BreadcrumbSeparator = BreadcrumbSeparator.Slash,
    modifier: Modifier = Modifier,
) = Breadcrumbs(items = items, separator = separator, modifier = modifier)

// Pagination
@Composable
fun pagination(
    current_page: Int,
    total_pages: Int,
    on_page_change: (Int) -> Unit,
    modifier: Modifier = Modifier,
) = Pagination(currentPage = current_page, totalPages = total_pages, onPageChange = on_page_change, modifier = modifier)

// Steps
@Composable
fun steps(
    steps: List<StepItem>,
    current_step: Int = 0,
    modifier: Modifier = Modifier,
) = Steps(steps = steps, currentStep = current_step, modifier = modifier)

// Drawer
@Composable
fun drawer(
    visible: Boolean,
    on_dismiss: () -> Unit,
    position: DrawerPosition = DrawerPosition.Left,
    content: @Composable () -> Unit,
    modifier: Modifier = Modifier,
) = Drawer(visible = visible, onDismissRequest = on_dismiss, position = position, content = content, modifier = modifier)

// BottomSheet
@Composable
fun bottom_sheet(
    visible: Boolean,
    on_dismiss: () -> Unit,
    content: @Composable () -> Unit,
    modifier: Modifier = Modifier,
) = BottomSheet(visible = visible, onDismissRequest = on_dismiss, content = content, modifier = modifier)

// Resizable
@Composable
fun resizable(
    first: @Composable () -> Unit,
    second: @Composable () -> Unit,
    direction: ResizableDirection = ResizableDirection.Horizontal,
    modifier: Modifier = Modifier,
) = Resizable(firstContent = first, secondContent = second, direction = direction, modifier = modifier)

// Statistic
@Composable
fun statistic(
    value: String,
    label: String,
    trend: StatTrend = StatTrend.Neutral,
    trend_value: String? = null,
    modifier: Modifier = Modifier,
) = Statistic(data = StatData(value = value, label = label, trend = trend, trendValue = trend_value), modifier = modifier)

// Descriptions
@Composable
fun descriptions(
    items: List<DescriptionItem>,
    columns: Int = 2,
    modifier: Modifier = Modifier,
) = Descriptions(items = items, columns = columns, modifier = modifier)

// Timeline
@Composable
fun timeline(
    items: List<TimelineItemData>,
    modifier: Modifier = Modifier,
) = Timeline(items = items, modifier = modifier)

// Comment
@Composable
fun comment(
    comment: CommentData,
    modifier: Modifier = Modifier,
) = Comment(comment = comment, modifier = modifier)

// Autocomplete
@Composable
fun autocomplete(
    value: String,
    on_change: (String) -> Unit,
    options: List<String>,
    modifier: Modifier = Modifier,
) = Autocomplete(value = value, onValueChange = on_change, options = options, modifier = modifier)

// Transfer
@Composable
fun transfer(
    source_items: List<TransferItem>,
    target_items: List<TransferItem>,
    on_source_change: (List<TransferItem>) -> Unit,
    on_target_change: (List<TransferItem>) -> Unit,
    modifier: Modifier = Modifier,
) = Transfer(
    sourceItems = source_items,
    targetItems = target_items,
    onSourceChange = on_source_change,
    onTargetChange = on_target_change,
    modifier = modifier,
)

// TreeView
@Composable
fun tree_view(
    nodes: List<TreeNode>,
    on_select: ((String) -> Unit)? = null,
    modifier: Modifier = Modifier,
) = SimpleTreeView(nodes = nodes, onSelect = on_select, modifier = modifier)

// ColorPicker
@Composable
fun color_picker(
    selected_color: androidx.compose.ui.graphics.Color,
    on_color_change: (androidx.compose.ui.graphics.Color) -> Unit,
    modifier: Modifier = Modifier,
) = ColorPicker(selectedColor = selected_color, onColorChange = on_color_change, modifier = modifier)

// Image
@Composable
fun image(
    image_url: String? = null,
    modifier: Modifier = Modifier,
    width: androidx.compose.ui.unit.Dp? = null,
    height: androidx.compose.ui.unit.Dp? = null,
) = ImageComponent(imageUrl = image_url, modifier = modifier, width = width, height = height)

// FileUpload
@Composable
fun file_upload(
    on_file_selected: ((List<String>) -> Unit)? = null,
    label: String = "Drop files here or click to upload",
    modifier: Modifier = Modifier,
) = FileUpload(onFileSelected = on_file_selected, label = label, modifier = modifier)

// QRCode
@Composable
fun qr_code(
    data: String,
    size: androidx.compose.ui.unit.Dp = 200.dp,
    modifier: Modifier = Modifier,
) = QRCode(data = data, size = size, modifier = modifier)

// Rating
@Composable
fun rating(
    value: Float,
    on_change: ((Float) -> Unit)? = null,
    max_rating: Int = 5,
    read_only: Boolean = false,
    modifier: Modifier = Modifier,
) = Rating(value = value, onValueChange = on_change, maxRating = max_rating, readOnly = read_only, modifier = modifier)

// FloatButton
@Composable
fun float_button(
    icon: String,
    on_click: () -> Unit,
    label: String? = null,
    modifier: Modifier = Modifier,
) = FloatButton(icon = icon, onClick = on_click, label = label, modifier = modifier)

// SpeedDial
@Composable
fun speed_dial(
    actions: List<SpeedDialAction>,
    modifier: Modifier = Modifier,
) = SpeedDial(actions = actions, modifier = modifier)

// BackToTop
@Composable
fun back_to_top(
    visible: Boolean = true,
    on_click: () -> Unit,
    modifier: Modifier = Modifier,
) = BackToTop(visible = visible, onClick = on_click, modifier = modifier)

// CopyButton
@Composable
fun copy_button(
    text_to_copy: String,
    label: String = "Copy",
    modifier: Modifier = Modifier,
) = CopyButton(textToCopy = text_to_copy, label = label, modifier = modifier)

// Watermark
@Composable
fun watermark(
    text: String,
    rotation: Float = -22f,
    opacity: Float = 0.1f,
    modifier: Modifier = Modifier,
) = Watermark(text = text, rotation = rotation, opacity = opacity, modifier = modifier)

// VirtualList
@Composable
fun virtual_list(
    item_count: Int,
    modifier: Modifier = Modifier,
    content: @Composable (Int) -> Unit,
) = VirtualList(itemCount = item_count, modifier = modifier, content = content)

// ConfigProvider
@Composable
fun config_provider(
    config: Config,
    content: @Composable () -> Unit,
) = ConfigProvider(config = config, content = content)
@Composable
fun dark_mode_config(content: @Composable () -> Unit) = DarkModeConfig(content = content)

// Responsive
@Composable
fun responsive(
    modifier: Modifier = Modifier,
    mobile: @Composable () -> Unit = {},
    desktop: @Composable () -> Unit = mobile,
) = Responsive(modifier = modifier, mobile = mobile, desktop = desktop)

// CodeBlock
@Composable
fun code_block(
    code: String,
    language: String = "kotlin",
    title: String? = null,
    modifier: Modifier = Modifier,
) = CodeBlock(code = code, language = language, title = title, modifier = modifier)

// Markdown
@Composable
fun markdown(
    markdown: String,
    modifier: Modifier = Modifier,
) = Markdown(markdown = markdown, modifier = modifier)

// FormValidation
@Composable
fun validated_input(
    value: String,
    on_change: (String) -> Unit,
    config: ValidationConfig,
    label: String? = null,
    modifier: Modifier = Modifier,
) = ValidatedInput(value = value, onValueChange = on_change, config = config, label = label, modifier = modifier)

// Skeleton
@Composable
fun skeleton_text(lines: Int = 1, modifier: Modifier = Modifier) = SkeletonText(lines = lines, modifier = modifier)
@Composable
fun skeleton_circle(size: androidx.compose.ui.unit.Dp = 40.dp, modifier: Modifier = Modifier) = SkeletonCircle(size = size, modifier = modifier)
@Composable
fun skeleton_card(modifier: Modifier = Modifier) = SkeletonCard(modifier = modifier)
@Composable
fun skeleton_list(count: Int = 5, modifier: Modifier = Modifier) = SkeletonList(count = count, modifier = modifier)
