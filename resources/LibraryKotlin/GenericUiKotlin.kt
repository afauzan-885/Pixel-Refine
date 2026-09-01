package org.pixelrefine.genericui

/**
 * ============================================================================
 * GENERIC UI LIBRARY — FACADE EXPORTS
 * ============================================================================
 * File ini adalah entry point utama untuk seluruh Generic UI Library.
 * Import file ini untuk mengakses semua komponen, tema, animasi, dan domain logic.
 */

// ============================================================================
// THEME
// ============================================================================
import org.pixelrefine.genericui.theme.GenericTheme
import org.pixelrefine.genericui.theme.GenericThemeProvider
import org.pixelrefine.genericui.theme.LocalGenericTheme
import org.pixelrefine.genericui.theme.LocalTheme
import org.pixelrefine.genericui.theme.LightTheme
import org.pixelrefine.genericui.theme.DarkTheme
import org.pixelrefine.genericui.theme.Theme
import org.pixelrefine.genericui.theme.ThemeShadow

// ============================================================================
// COMPONENTS — UI PRIMITIVES (ORIGINAL 31)
// ============================================================================
import org.pixelrefine.genericui.components.Variant
import org.pixelrefine.genericui.components.variantColor
import org.pixelrefine.genericui.components.variantHoverColor
import org.pixelrefine.genericui.components.toVariant
import org.pixelrefine.genericui.components.Button
import org.pixelrefine.genericui.components.IconButton
import org.pixelrefine.genericui.components.ToggleButton
import org.pixelrefine.genericui.components.BackButton
import org.pixelrefine.genericui.components.ButtonGroup
import org.pixelrefine.genericui.components.ToggleSwitch
import org.pixelrefine.genericui.components.Switch
import org.pixelrefine.genericui.components.Container
import org.pixelrefine.genericui.components.Row
import org.pixelrefine.genericui.components.Col
import org.pixelrefine.genericui.components.Stack
import org.pixelrefine.genericui.components.ScrollContainer
import org.pixelrefine.genericui.components.Spacer
import org.pixelrefine.genericui.components.HorizontalScrollRow
import org.pixelrefine.genericui.components.ScrollableColumn
import org.pixelrefine.genericui.components.Card
import org.pixelrefine.genericui.components.CardHeader
import org.pixelrefine.genericui.components.CardBody
import org.pixelrefine.genericui.components.CardFooter
import org.pixelrefine.genericui.components.CardGroup
import org.pixelrefine.genericui.components.FeatureCard
import org.pixelrefine.genericui.components.Input
import org.pixelrefine.genericui.components.Select
import org.pixelrefine.genericui.components.Checkbox
import org.pixelrefine.genericui.components.Radio
import org.pixelrefine.genericui.components.RadioGroup
import org.pixelrefine.genericui.components.FormGroup
import org.pixelrefine.genericui.components.FormRow
import org.pixelrefine.genericui.components.ListGroup
import org.pixelrefine.genericui.components.ListItem
import org.pixelrefine.genericui.components.GridContainer
import org.pixelrefine.genericui.components.GridItem
import org.pixelrefine.genericui.components.Gallery
import org.pixelrefine.genericui.components.ThumbnailGrid
import org.pixelrefine.genericui.components.DataTable
import org.pixelrefine.genericui.components.Badge
import org.pixelrefine.genericui.components.EmptyState
import org.pixelrefine.genericui.components.SkeletonLoader
import org.pixelrefine.genericui.components.Navbar
import org.pixelrefine.genericui.components.NavItem
import org.pixelrefine.genericui.components.Sidebar
import org.pixelrefine.genericui.components.SidebarItem
import org.pixelrefine.genericui.components.TabContainer
import org.pixelrefine.genericui.components.TabPane
import org.pixelrefine.genericui.components.SimpleTabs
import org.pixelrefine.genericui.components.Collapse
import org.pixelrefine.genericui.components.Accordion
import org.pixelrefine.genericui.components.AccordionItem
import org.pixelrefine.genericui.components.ProgressBar
import org.pixelrefine.genericui.components.CustomProgressBar
import org.pixelrefine.genericui.components.CircularProgressFallback
import org.pixelrefine.genericui.components.IndeterminateProgress
import org.pixelrefine.genericui.components.ProgressGroup
import org.pixelrefine.genericui.components.Overlay
import org.pixelrefine.genericui.components.LoadingSpinner
import org.pixelrefine.genericui.components.LoadingOverlay
import org.pixelrefine.genericui.components.Toast
import org.pixelrefine.genericui.components.Modal
import org.pixelrefine.genericui.components.ModalHeader
import org.pixelrefine.genericui.components.ModalBody
import org.pixelrefine.genericui.components.ModalFooter
import org.pixelrefine.genericui.components.ModalDialog
import org.pixelrefine.genericui.components.ModalConfirm
import org.pixelrefine.genericui.components.modal_confirm
import org.pixelrefine.genericui.components.AlertModal
import org.pixelrefine.genericui.components.ProgressModal
import org.pixelrefine.genericui.components.OverlayContainer
import org.pixelrefine.genericui.components.OverlayPosition
import org.pixelrefine.genericui.components.ImageCard
import org.pixelrefine.genericui.components.GridItemWidget
import org.pixelrefine.genericui.components.ImageCompareWidget
import org.pixelrefine.genericui.components.ImageCompareItem
import org.pixelrefine.genericui.components.ToneCurveEditor
import org.pixelrefine.genericui.components.ControlPoint
import org.pixelrefine.genericui.components.HistogramViewer
import org.pixelrefine.genericui.components.Filmstrip
import org.pixelrefine.genericui.components.PresetSelector
import org.pixelrefine.genericui.components.SegmentedControl
import org.pixelrefine.genericui.components.SmallDropdown
import org.pixelrefine.genericui.components.RangeSlider
import org.pixelrefine.genericui.components.Magnifier
import org.pixelrefine.genericui.components.SplitPane
import org.pixelrefine.genericui.components.SplitOrientation
import org.pixelrefine.genericui.components.BottomActionBar
import org.pixelrefine.genericui.components.BottomNavItem
import org.pixelrefine.genericui.components.DotIndicator
import org.pixelrefine.genericui.components.BatchCard
import org.pixelrefine.genericui.components.NewBatchCard

// ============================================================================
// NEW COMPONENTS — BATCH 1-11 (50+ components)
// ============================================================================

// Typography
import org.pixelrefine.genericui.components.TypographyVariant
import org.pixelrefine.genericui.components.Heading
import org.pixelrefine.genericui.components.H1
import org.pixelrefine.genericui.components.H2
import org.pixelrefine.genericui.components.H3
import org.pixelrefine.genericui.components.H4
import org.pixelrefine.genericui.components.H5
import org.pixelrefine.genericui.components.H6
import org.pixelrefine.genericui.components.BodyText
import org.pixelrefine.genericui.components.CaptionText
import org.pixelrefine.genericui.components.OverlineText
import org.pixelrefine.genericui.components.CodeText
import org.pixelrefine.genericui.components.TruncatedText
import org.pixelrefine.genericui.components.TextWithIcon
import org.pixelrefine.genericui.components.IconPosition
import org.pixelrefine.genericui.components.LinkText
import org.pixelrefine.genericui.components.EllipsisText

// Single Slider
import org.pixelrefine.genericui.components.Slider
import org.pixelrefine.genericui.components.IntSlider
import org.pixelrefine.genericui.components.PercentageSlider

// Tooltip
import org.pixelrefine.genericui.components.Tooltip
import org.pixelrefine.genericui.components.TooltipPosition
import org.pixelrefine.genericui.components.TooltipBox
import org.pixelrefine.genericui.components.RichTooltip

// Divider
import org.pixelrefine.genericui.components.Divider
import org.pixelrefine.genericui.components.HorizontalDivider
import org.pixelrefine.genericui.components.VerticalDivider
import org.pixelrefine.genericui.components.DividerWithLabel
import org.pixelrefine.genericui.components.DashedDivider
import org.pixelrefine.genericui.components.DividerStyle
import org.pixelrefine.genericui.components.DividerOrientation

// Avatar
import org.pixelrefine.genericui.components.Avatar
import org.pixelrefine.genericui.components.AvatarSize
import org.pixelrefine.genericui.components.AvatarGroup
import org.pixelrefine.genericui.components.AvatarData
import org.pixelrefine.genericui.components.AvatarWithStatus
import org.pixelrefine.genericui.components.AvatarStatus

// Chips
import org.pixelrefine.genericui.components.Chip
import org.pixelrefine.genericui.components.ChipGroup
import org.pixelrefine.genericui.components.ChipData
import org.pixelrefine.genericui.components.FilterChip
import org.pixelrefine.genericui.components.InputChip
import org.pixelrefine.genericui.components.ActionChip
import org.pixelrefine.genericui.components.Tag

// Number Input
import org.pixelrefine.genericui.components.NumberInput
import org.pixelrefine.genericui.components.IntNumberInput

// TextArea
import org.pixelrefine.genericui.components.TextArea
import org.pixelrefine.genericui.components.AutoResizingTextArea

// SearchInput
import org.pixelrefine.genericui.components.SearchInput
import org.pixelrefine.genericui.components.SearchInputWithResults

// CheckboxGroup
import org.pixelrefine.genericui.components.CheckboxGroup
import org.pixelrefine.genericui.components.Orientation

// DatePicker
import org.pixelrefine.genericui.components.DatePicker
import org.pixelrefine.genericui.components.SimpleDate
import org.pixelrefine.genericui.components.DatePickerInput

// Alert
import org.pixelrefine.genericui.components.Alert
import org.pixelrefine.genericui.components.SuccessAlert
import org.pixelrefine.genericui.components.WarningAlert
import org.pixelrefine.genericui.components.ErrorAlert
import org.pixelrefine.genericui.components.InfoAlert

// Snackbar
import org.pixelrefine.genericui.components.Snackbar
import org.pixelrefine.genericui.components.SnackbarManager
import org.pixelrefine.genericui.components.SnackbarData
import org.pixelrefine.genericui.components.SnackbarPosition
import org.pixelrefine.genericui.components.SnackbarHost

// Notification
import org.pixelrefine.genericui.components.Notification
import org.pixelrefine.genericui.components.NotificationData
import org.pixelrefine.genericui.components.NotificationManager
import org.pixelrefine.genericui.components.NotificationList
import org.pixelrefine.genericui.components.NotificationBadge

// Popover
import org.pixelrefine.genericui.components.Popover
import org.pixelrefine.genericui.components.PopoverContent
import org.pixelrefine.genericui.components.PopoverTrigger

// Breadcrumbs
import org.pixelrefine.genericui.components.Breadcrumbs
import org.pixelrefine.genericui.components.BreadcrumbItem
import org.pixelrefine.genericui.components.SimpleBreadcrumbs
import org.pixelrefine.genericui.components.BreadcrumbSeparator

// Pagination
import org.pixelrefine.genericui.components.Pagination
import org.pixelrefine.genericui.components.SimplePagination

// Steps
import org.pixelrefine.genericui.components.Steps
import org.pixelrefine.genericui.components.StepItem
import org.pixelrefine.genericui.components.StepStatus
import org.pixelrefine.genericui.components.StepsDirection

// Drawer
import org.pixelrefine.genericui.components.Drawer
import org.pixelrefine.genericui.components.DrawerHeader
import org.pixelrefine.genericui.components.DrawerBody
import org.pixelrefine.genericui.components.DrawerFooter
import org.pixelrefine.genericui.components.DrawerPosition

// BottomSheet
import org.pixelrefine.genericui.components.BottomSheet
import org.pixelrefine.genericui.components.BottomSheetHeader
import org.pixelrefine.genericui.components.BottomSheetContent
import org.pixelrefine.genericui.components.BottomSheetActions

// Resizable
import org.pixelrefine.genericui.components.Resizable
import org.pixelrefine.genericui.components.ResizableDirection

// Statistic
import org.pixelrefine.genericui.components.Statistic
import org.pixelrefine.genericui.components.StatisticGroup
import org.pixelrefine.genericui.components.StatData
import org.pixelrefine.genericui.components.StatTrend

// Descriptions
import org.pixelrefine.genericui.components.Descriptions
import org.pixelrefine.genericui.components.DescriptionItem
import org.pixelrefine.genericui.components.DescriptionSize

// Timeline
import org.pixelrefine.genericui.components.Timeline
import org.pixelrefine.genericui.components.TimelineItem
import org.pixelrefine.genericui.components.TimelineItemData
import org.pixelrefine.genericui.components.TimelineItemStatus

// Comment
import org.pixelrefine.genericui.components.Comment
import org.pixelrefine.genericui.components.CommentData

// Autocomplete
import org.pixelrefine.genericui.components.Autocomplete
import org.pixelrefine.genericui.components.AutocompleteWithFilter

// Transfer
import org.pixelrefine.genericui.components.Transfer
import org.pixelrefine.genericui.components.TransferItem

// TreeView
import org.pixelrefine.genericui.components.TreeView
import org.pixelrefine.genericui.components.TreeNode
import org.pixelrefine.genericui.components.SimpleTreeView

// ColorPicker
import org.pixelrefine.genericui.components.ColorPicker
import org.pixelrefine.genericui.components.QRErrorCorrection

// ImageComponent
import org.pixelrefine.genericui.components.ImageComponent
import org.pixelrefine.genericui.components.ImageFit
import org.pixelrefine.genericui.components.AvatarImage

// FileUpload
import org.pixelrefine.genericui.components.FileUpload
import org.pixelrefine.genericui.components.FileUploadList
import org.pixelrefine.genericui.components.FileUploadData

// QRCode
import org.pixelrefine.genericui.components.QRCode
import org.pixelrefine.genericui.components.QRCodeWithLabel

// Rating
import org.pixelrefine.genericui.components.Rating
import org.pixelrefine.genericui.components.StarRating
import org.pixelrefine.genericui.components.RatingDisplay

// Tour
import org.pixelrefine.genericui.components.Tour
import org.pixelrefine.genericui.components.TourStep
import org.pixelrefine.genericui.components.TourHost

// FloatButton
import org.pixelrefine.genericui.components.FloatButton
import org.pixelrefine.genericui.components.FloatButtonPosition
import org.pixelrefine.genericui.components.MiniFloatButton

// SpeedDial
import org.pixelrefine.genericui.components.SpeedDial
import org.pixelrefine.genericui.components.SpeedDialAction
import org.pixelrefine.genericui.components.SpeedDialDirection

// Anchor
import org.pixelrefine.genericui.components.Anchor
import org.pixelrefine.genericui.components.AnchorItem
import org.pixelrefine.genericui.components.SimpleAnchor

// Affix
import org.pixelrefine.genericui.components.Affix
import org.pixelrefine.genericui.components.AffixPosition
import org.pixelrefine.genericui.components.StickyHeader

// BackToTop
import org.pixelrefine.genericui.components.BackToTop
import org.pixelrefine.genericui.components.ScrollToTopButton

// Watermark
import org.pixelrefine.genericui.components.Watermark
import org.pixelrefine.genericui.components.TextWatermark

// ConfigProvider
import org.pixelrefine.genericui.components.ConfigProvider
import org.pixelrefine.genericui.components.Config
import org.pixelrefine.genericui.components.LocalConfig
import org.pixelrefine.genericui.components.useConfig
import org.pixelrefine.genericui.components.withConfig
import org.pixelrefine.genericui.components.ThemedConfig
import org.pixelrefine.genericui.components.DarkModeConfig
import org.pixelrefine.genericui.components.LayoutDirection
import org.pixelrefine.genericui.components.ComponentSize

// CopyButton
import org.pixelrefine.genericui.components.CopyButton
import org.pixelrefine.genericui.components.CopyText

// VirtualList
import org.pixelrefine.genericui.components.VirtualList

// InfiniteScroll
import org.pixelrefine.genericui.components.InfiniteScroll

// Responsive
import org.pixelrefine.genericui.components.Responsive
import org.pixelrefine.genericui.components.DeviceType
import org.pixelrefine.genericui.components.Breakpoint
import org.pixelrefine.genericui.components.rememberDeviceType
import org.pixelrefine.genericui.components.rememberBreakpoint
import org.pixelrefine.genericui.components.ShowOn
import org.pixelrefine.genericui.components.HideOn

// Accessibility
import org.pixelrefine.genericui.components.AccessibleBox
import org.pixelrefine.genericui.components.SemanticRole
import org.pixelrefine.genericui.components.accessibilityLabel
import org.pixelrefine.genericui.components.accessibilityRole
import org.pixelrefine.genericui.components.combineAccessibility

// KeyboardShortcuts
import org.pixelrefine.genericui.components.keyboardShortcuts
import org.pixelrefine.genericui.components.KeyboardShortcut
import org.pixelrefine.genericui.components.ShortcutKeys
import org.pixelrefine.genericui.components.ShortcutDisplay

// DragDrop
import org.pixelrefine.genericui.components.DragDropList
import org.pixelrefine.genericui.components.DropZone
import org.pixelrefine.genericui.components.DraggableItem

// ContextMenu
import org.pixelrefine.genericui.components.ContextMenu
import org.pixelrefine.genericui.components.ContextMenuItem

// Menu
import org.pixelrefine.genericui.components.Menu
import org.pixelrefine.genericui.components.MenuEntry
import org.pixelrefine.genericui.components.DropdownMenu

// SkeletonVariants
import org.pixelrefine.genericui.components.SkeletonText
import org.pixelrefine.genericui.components.SkeletonCircle
import org.pixelrefine.genericui.components.SkeletonRect
import org.pixelrefine.genericui.components.SkeletonCard
import org.pixelrefine.genericui.components.SkeletonAvatar
import org.pixelrefine.genericui.components.SkeletonButton
import org.pixelrefine.genericui.components.SkeletonList

// CodeBlock
import org.pixelrefine.genericui.components.CodeBlock

// Markdown
import org.pixelrefine.genericui.components.Markdown

// FormValidation
import org.pixelrefine.genericui.components.ValidatedInput
import org.pixelrefine.genericui.components.rememberFormField
import org.pixelrefine.genericui.components.FieldState
import org.pixelrefine.genericui.components.ValidationConfig
import org.pixelrefine.genericui.components.ValidationError
import org.pixelrefine.genericui.components.ValidationRule
import org.pixelrefine.genericui.components.FormFieldLabel

// ============================================================================
// ANIMATIONS
// ============================================================================
import org.pixelrefine.genericui.animations.AnimationType
import org.pixelrefine.genericui.animations.SlideDirection
import org.pixelrefine.genericui.animations.AnimationCurves
import org.pixelrefine.genericui.animations.StackedWidgetAnimator
import org.pixelrefine.genericui.animations.WidgetLifecycleAnimator
import org.pixelrefine.genericui.animations.combinedAnimation
import org.pixelrefine.genericui.animations.pulseAnimation
import org.pixelrefine.genericui.animations.shakeAnimation
import org.pixelrefine.genericui.animations.shimmerBrush
import org.pixelrefine.genericui.animations.fadeInTransition
import org.pixelrefine.genericui.animations.fadeOutTransition
import org.pixelrefine.genericui.animations.FadeTransition
import org.pixelrefine.genericui.animations.SlideTransition
import org.pixelrefine.genericui.animations.ZoomTransition
import org.pixelrefine.genericui.animations.DeleteTransition
import org.pixelrefine.genericui.animations.ToastManager
import org.pixelrefine.genericui.animations.GlobalToastManager
import org.pixelrefine.genericui.animations.ToastHost
import org.pixelrefine.genericui.animations.ToastItem

// ============================================================================
// DOMAIN — MODELS
// ============================================================================
import org.pixelrefine.genericui.domain.models.ImageItem
import org.pixelrefine.genericui.domain.models.BatchItem
import org.pixelrefine.genericui.domain.models.BatchStatus
import org.pixelrefine.genericui.domain.models.AlgorithmCategory
import org.pixelrefine.genericui.domain.models.AlgorithmOption
import org.pixelrefine.genericui.domain.models.AlgorithmConfig
import org.pixelrefine.genericui.domain.models.AlgorithmRegistry

// ============================================================================
// DOMAIN — STATE MANAGEMENT
// ============================================================================
import org.pixelrefine.genericui.domain.state.BatchStateManager
import org.pixelrefine.genericui.domain.state.rememberBatchStateManager
import org.pixelrefine.genericui.domain.state.WorkflowStateManager
import org.pixelrefine.genericui.domain.state.rememberWorkflowStateManager
import org.pixelrefine.genericui.domain.state.ProcessingState
import org.pixelrefine.genericui.domain.state.SessionCheckpoint
import org.pixelrefine.genericui.domain.state.SessionCheckpointManager
import org.pixelrefine.genericui.domain.state.ThumbnailPolicyState
import org.pixelrefine.genericui.domain.state.GlobalThumbnailPolicy
import org.pixelrefine.genericui.domain.state.rememberThumbnailPolicy

// ============================================================================
// DOMAIN — VALIDATION & METRICS
// ============================================================================
import org.pixelrefine.genericui.domain.validation.ImageValidator
import org.pixelrefine.genericui.domain.validation.ValidationResult
import org.pixelrefine.genericui.domain.validation.RejectedPathInfo
import org.pixelrefine.genericui.domain.validation.SharpnessMetric

// ============================================================================
// DOMAIN — PRESETS
// ============================================================================
import org.pixelrefine.genericui.domain.presets.AlgorithmPreset
import org.pixelrefine.genericui.domain.presets.PresetStore

// ============================================================================
// DOMAIN — STREAMING & PROCESSING
// ============================================================================
import org.pixelrefine.genericui.domain.stream.ImageStreamer
import org.pixelrefine.genericui.domain.stream.StreamedImage
import org.pixelrefine.genericui.domain.deletion.AdaptiveChunkProcessor
import org.pixelrefine.genericui.domain.deletion.ChunkProgress

// ============================================================================
// DOMAIN — CACHE
// ============================================================================
import org.pixelrefine.genericui.domain.cache.LruMemoryCache

// ============================================================================
// DOMAIN — GESTURES
// ============================================================================
import org.pixelrefine.genericui.domain.gestures.TransformState
import org.pixelrefine.genericui.domain.gestures.rememberTransformState
import org.pixelrefine.genericui.domain.gestures.zoomable

// ============================================================================
// DOMAIN — PROJECT
// ============================================================================
import org.pixelrefine.genericui.domain.project.ProjectArchiveManager
import org.pixelrefine.genericui.domain.project.ProjectManifest

// ============================================================================
// DOMAIN — AOT NATIVE
// ============================================================================
import org.pixelrefine.genericui.domain.aot.TaichiAot
import org.pixelrefine.genericui.domain.aot.TaichiGpuBuffer
import org.pixelrefine.genericui.domain.aot.AotArch
import org.pixelrefine.genericui.domain.aot.AotDtype
import org.pixelrefine.genericui.domain.aot.InterpolationMode
import org.pixelrefine.genericui.domain.aot.ColorConversionCode
import org.pixelrefine.genericui.domain.aot.ThresholdType
import org.pixelrefine.genericui.domain.aot.BorderType
import org.pixelrefine.genericui.domain.aot.DemosaicAlgorithm

// ============================================================================
// PYTHONIC FACADE (1-line convenience functions)
// ============================================================================
import org.pixelrefine.genericui.tone_curve_editor
import org.pixelrefine.genericui.histogram_viewer
import org.pixelrefine.genericui.filmstrip
import org.pixelrefine.genericui.preset_selector
import org.pixelrefine.genericui.segmented_control
import org.pixelrefine.genericui.range_slider
import org.pixelrefine.genericui.magnifier
import org.pixelrefine.genericui.button
import org.pixelrefine.genericui.badge
import org.pixelrefine.genericui.batch_card
import org.pixelrefine.genericui.new_batch_card
import org.pixelrefine.genericui.dot_indicator
import org.pixelrefine.genericui.progress_bar
import org.pixelrefine.genericui.small_dropdown
import org.pixelrefine.genericui.bottom_action_bar
import org.pixelrefine.genericui.toast
import org.pixelrefine.genericui.auto_cull
import org.pixelrefine.genericui.compute_sharpness
import org.pixelrefine.genericui.validate_paths
import org.pixelrefine.genericui.get_preset
import org.pixelrefine.genericui.list_presets
import org.pixelrefine.genericui.save_preset
import org.pixelrefine.genericui.save_checkpoint
import org.pixelrefine.genericui.has_recovery
import org.pixelrefine.genericui.get_checkpoint
import org.pixelrefine.genericui.clear_checkpoint
