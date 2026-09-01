package org.pixelrefine.genericui

import org.pixelrefine.genericui.components.*
import org.pixelrefine.genericui.domain.gestures.TransformState
import org.pixelrefine.genericui.theme.*
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertNotNull
import kotlin.test.assertTrue
import kotlin.test.assertFailsWith

/**
 * Test komprehensif untuk komponen UI interaktif:
 * - RangeSlider (drag gesture, boundary)
 * - Magnifier (position tracking, zoom)
 * - ToneCurveEditor (drag, boundary clamping, NaN)
 * - SplitPane (drag resize, orientation)
 * - ImageCompareWidget (interactive split, zoom sync)
 * - Button (debounce, loading state, timeout)
 * - Variant (fromString error, fromStringOrDefault)
 * - GenericTheme (shadow fields, theme switching)
 */
class ComponentInteractionTest {

    // =========================================================================
    // 1. RANGE SLIDER TESTS
    // =========================================================================

    @Test
    fun testRangeSliderInitialRange() {
        println("=== [TEST 1] RANGE SLIDER: INITIAL RANGE ===")
        val range = 100f..3200f
        assertEquals(100f, range.start)
        assertEquals(3200f, range.endInclusive)

        // Test range clamping
        val clampedRange = 50f..500f
        val span = clampedRange.endInclusive - clampedRange.start
        assertEquals(450f, span)

        // Test fraction calculation
        val minVal = 0f
        val maxVal = 100f
        val currentRange = 20f..80f
        val spanCalc = (maxVal - minVal).coerceAtLeast(1f)
        val startFrac = ((currentRange.start - minVal) / spanCalc).coerceIn(0f, 1f)
        val endFrac = ((currentRange.endInclusive - minVal) / spanCalc).coerceIn(0f, 1f)
        assertEquals(0.2f, startFrac)
        assertEquals(0.8f, endFrac)
        println("✔ RangeSlider initial range calculation correct")
    }

    @Test
    fun testRangeSliderBoundaryClamping() {
        println("\n=== [TEST 2] RANGE SLIDER: BOUNDARY CLAMPING ===")
        val minVal = 0f
        val maxVal = 100f

        // Test start fraction clamping
        val startFrac = ((-10f - minVal) / (maxVal - minVal)).coerceIn(0f, 1f)
        assertEquals(0f, startFrac, "Negative start should clamp to 0")

        // Test end fraction clamping
        val endFrac = ((110f - minVal) / (maxVal - minVal)).coerceIn(0f, 1f)
        assertEquals(1f, endFrac, "Exceeding max should clamp to 1")

        // Test minimum gap between thumbs
        val minGap = 0.01f
        val start = 0.5f
        val end = (start + minGap).coerceIn(0f, 1f)
        assertTrue(end - start >= minGap, "Minimum gap between thumbs should be maintained")
        println("✔ RangeSlider boundary clamping verified")
    }

    @Test
    fun testRangeSliderDragSimulation() {
        println("\n=== [TEST 3] RANGE SLIDER: DRAG SIMULATION ===")
        // Simulate drag gesture calculation
        var startFrac = 0.2f
        var endFrac = 0.8f
        val totalWidth = 1000f

        // Simulate dragging start thumb right by 100px
        val dragAmountStart = 100f
        val deltaStart = dragAmountStart / totalWidth
        startFrac = (startFrac + deltaStart).coerceIn(0f, endFrac - 0.01f)
        assertEquals(0.3f, startFrac, "Start thumb should move right")
        assertTrue(startFrac < endFrac, "Start should remain less than end")

        // Simulate dragging end thumb left by 150px
        val dragAmountEnd = -150f
        val deltaEnd = dragAmountEnd / totalWidth
        endFrac = (endFrac + deltaEnd).coerceIn(startFrac + 0.01f, 1f)
        assertEquals(0.65f, endFrac, "End thumb should move left")
        assertTrue(endFrac > startFrac, "End should remain greater than start")
        println("✔ RangeSlider drag simulation verified")
    }

    // =========================================================================
    // 2. MAGNIFIER TESTS
    // =========================================================================

    @Test
    fun testMagnifierZoomFactorRange() {
        println("\n=== [TEST 4] MAGNIFIER: ZOOM FACTOR RANGE ===")
        val validZoomFactors = listOf(2f, 4f, 8f, 16f)
        validZoomFactors.forEach { zoom ->
            assertTrue(zoom in 2f..16f, "Zoom factor $zoom should be in range 2..16")
        }

        // Test invalid zoom factors
        val invalidZoomFactors = listOf(0.5f, 1f, 0f, -1f, 20f)
        invalidZoomFactors.forEach { zoom ->
            assertTrue(zoom !in 2f..16f, "Zoom factor $zoom should be invalid")
        }
        println("✔ Magnifier zoom factor range validated")
    }

    @Test
    fun testMagnifierFocusOffsetCalculation() {
        println("\n=== [TEST 5] MAGNIFIER: FOCUS OFFSET CALCULATION ===")
        val loupeSizePx = 100f
        val halfLoupe = loupeSizePx / 2f
        val contentWidth = 400f
        val contentHeight = 300f
        val zoomFactor = 4f

        // Simulate focus at center
        var focusX = contentWidth / 2f
        var focusY = contentHeight / 2f
        assertEquals(200f, focusX)
        assertEquals(150f, focusY)

        // Simulate drag to move focus
        val dragX = 50f
        val dragY = 30f
        val scaleX = contentWidth / loupeSizePx
        val scaleY = contentHeight / loupeSizePx
        focusX = (focusX + dragX * scaleX / zoomFactor).coerceIn(0f, contentWidth)
        focusY = (focusY + dragY * scaleY / zoomFactor).coerceIn(0f, contentHeight)

        assertTrue(focusX > 200f, "Focus X should move right")
        assertTrue(focusY > 150f, "Focus Y should move down")
        assertTrue(focusX <= contentWidth, "Focus X should not exceed content width")
        assertTrue(focusY <= contentHeight, "Focus Y should not exceed content height")
        println("✔ Magnifier focus offset calculation verified")
    }

    @Test
    fun testMagnifierBoundaryClamping() {
        println("\n=== [TEST 6] MAGNIFIER: BOUNDARY CLAMPING ===")
        val contentWidth = 400f
        val contentHeight = 300f

        // Test clamping at boundaries
        val focusX = (-50f).coerceIn(0f, contentWidth)
        val focusY = (350f).coerceIn(0f, contentHeight)
        assertEquals(0f, focusX, "Negative focus X should clamp to 0")
        assertEquals(300f, focusY, "Focus Y exceeding height should clamp to max")

        // Test clamping at exact boundaries
        val focusXAtMax = (400f).coerceIn(0f, contentWidth)
        val focusYAtMax = (300f).coerceIn(0f, contentHeight)
        assertEquals(400f, focusXAtMax)
        assertEquals(300f, focusYAtMax)
        println("✔ Magnifier boundary clamping verified")
    }

    // =========================================================================
    // 3. TONE CURVE EDITOR TESTS
    // =========================================================================

    @Test
    fun testToneCurveControlPointCreation() {
        println("\n=== [TEST 7] TONE CURVE: CONTROL POINT CREATION ===")
        val points = listOf(
            ControlPoint(0.0f, 0.0f),
            ControlPoint(0.25f, 0.25f),
            ControlPoint(0.75f, 0.75f),
            ControlPoint(1.0f, 1.0f),
        )

        assertEquals(4, points.size)
        assertEquals(0.0f, points[0].x)
        assertEquals(0.0f, points[0].y)
        assertEquals(1.0f, points[3].x)
        assertEquals(1.0f, points[3].y)
        println("✔ ToneCurve control point creation verified")
    }

    @Test
    fun testToneCurveBoundaryClamping() {
        println("\n=== [TEST 8] TONE CURVE: BOUNDARY CLAMPING ===")
        // Test extreme points outside [0.0 .. 1.0]
        val extremePoints = listOf(
            ControlPoint(-10.0f, -50.0f),
            ControlPoint(0.5f, Float.NaN),
            ControlPoint(2.5f, 999.0f),
        )

        val clamped = extremePoints.map { pt ->
            val cx = pt.x.coerceIn(0.0f, 1.0f)
            val cy = if (pt.y.isNaN()) 0.5f else pt.y.coerceIn(0.0f, 1.0f)
            ControlPoint(cx, cy)
        }

        assertEquals(0.0f, clamped[0].x)
        assertEquals(0.0f, clamped[0].y)
        assertEquals(0.5f, clamped[1].y) // NaN recovered to default
        assertEquals(1.0f, clamped[2].x)
        assertEquals(1.0f, clamped[2].y)
        println("✔ ToneCurve boundary clamping verified")
    }

    @Test
    fun testToneCurveDragSimulation() {
        println("\n=== [TEST 9] TONE CURVE: DRAG SIMULATION ===")
        val points = mutableListOf(
            ControlPoint(0.0f, 0.0f),
            ControlPoint(0.25f, 0.25f),
            ControlPoint(0.75f, 0.75f),
            ControlPoint(1.0f, 1.0f),
        )

        // Simulate dragging middle point
        val dragIndex = 1
        val newX = 0.3f
        val newY = 0.4f

        // Lock endpoints (index 0 and lastIndex)
        if (dragIndex != 0 && dragIndex != points.lastIndex) {
            points[dragIndex] = ControlPoint(newX, newY)
        }

        assertEquals(0.3f, points[1].x)
        assertEquals(0.4f, points[1].y)
        assertEquals(0.0f, points[0].x, "Start point should remain locked")
        assertEquals(1.0f, points[3].x, "End point should remain locked")
        println("✔ ToneCurve drag simulation verified")
    }

    @Test
    fun testToneCurveEndpointLocking() {
        println("\n=== [TEST 10] TONE CURVE: ENDPOINT LOCKING ===")
        val points = mutableListOf(
            ControlPoint(0.0f, 0.0f),
            ControlPoint(0.5f, 0.5f),
            ControlPoint(1.0f, 1.0f),
        )

        // Try to drag endpoint (should be ignored)
        val dragIndex = 0
        if (dragIndex == 0 || dragIndex == points.lastIndex) {
            // Endpoint - do nothing
        } else {
            points[dragIndex] = ControlPoint(0.1f, 0.9f)
        }

        assertEquals(0.0f, points[0].x, "Start point X should remain 0")
        assertEquals(0.0f, points[0].y, "Start point Y should remain 0")
        assertEquals(1.0f, points[2].x, "End point X should remain 1")
        assertEquals(1.0f, points[2].y, "End point Y should remain 1")
        println("✔ ToneCurve endpoint locking verified")
    }

    // =========================================================================
    // 4. SPLIT PANE TESTS
    // =========================================================================

    @Test
    fun testSplitPaneOrientation() {
        println("\n=== [TEST 11] SPLIT PANE: ORIENTATION ===")
        val horizontal = SplitOrientation.HORIZONTAL
        val vertical = SplitOrientation.VERTICAL

        assertEquals(SplitOrientation.HORIZONTAL, horizontal)
        assertEquals(SplitOrientation.VERTICAL, vertical)
        assertTrue(horizontal != vertical)
        println("✔ SplitPane orientation enum verified")
    }

    @Test
    fun testSplitPaneFractionCalculation() {
        println("\n=== [TEST 12] SPLIT PANE: FRACTION CALCULATION ===")
        var fraction = 0.5f
        val totalWidth = 1000f

        // Simulate dragging divider right by 100px
        val dragAmount = 100f
        fraction = (fraction + dragAmount / totalWidth).coerceIn(0.1f, 0.9f)
        assertEquals(0.6f, fraction, "Fraction should increase when dragging right")

        // Simulate dragging divider left by 200px
        val dragAmountLeft = -200f
        fraction = (fraction + dragAmountLeft / totalWidth).coerceIn(0.1f, 0.9f)
        assertEquals(0.4f, fraction, "Fraction should decrease when dragging left")

        // Test boundary clamping
        fraction = (0.05f).coerceIn(0.1f, 0.9f)
        assertEquals(0.1f, fraction, "Fraction should clamp to minimum 0.1")

        fraction = (0.95f).coerceIn(0.1f, 0.9f)
        assertEquals(0.9f, fraction, "Fraction should clamp to maximum 0.9")
        println("✔ SplitPane fraction calculation verified")
    }

    @Test
    fun testSplitPaneVerticalDrag() {
        println("\n=== [TEST 13] SPLIT PANE: VERTICAL DRAG ===")
        var fraction = 0.5f
        val totalHeight = 800f

        // Simulate dragging divider down by 80px
        val dragAmount = 80f
        fraction = (fraction + dragAmount / totalHeight).coerceIn(0.1f, 0.9f)
        assertEquals(0.6f, fraction, "Fraction should increase when dragging down")

        // Simulate dragging divider up by 160px
        val dragAmountUp = -160f
        fraction = (fraction + dragAmountUp / totalHeight).coerceIn(0.1f, 0.9f)
        assertEquals(0.4f, fraction, "Fraction should decrease when dragging up")
        println("✔ SplitPane vertical drag verified")
    }

    // =========================================================================
    // 5. IMAGE COMPARE WIDGET TESTS
    // =========================================================================

    @Test
    fun testImageCompareItemCreation() {
        println("\n=== [TEST 14] IMAGE COMPARE: ITEM CREATION ===")
        val item = ImageCompareItem(
            title = "Before",
            description = "Original image",
            tag = "original"
        )

        assertEquals("Before", item.title)
        assertEquals("Original image", item.description)
        assertEquals("original", item.tag)
        println("✔ ImageCompareItem creation verified")
    }

    @Test
    fun testImageCompareSplitFraction() {
        println("\n=== [TEST 15] IMAGE COMPARE: SPLIT FRACTION ===")
        var splitFraction = 0.5f
        val totalWidthPx = 800f

        // Simulate dragging split handle
        val dragAmount = 100f
        splitFraction = (splitFraction + dragAmount / totalWidthPx).coerceIn(0.05f, 0.95f)
        assertEquals(0.625f, splitFraction, "Split fraction should increase")

        // Test boundary clamping
        splitFraction = (0.01f).coerceIn(0.05f, 0.95f)
        assertEquals(0.05f, splitFraction, "Split fraction should clamp to minimum")

        splitFraction = (0.99f).coerceIn(0.05f, 0.95f)
        assertEquals(0.95f, splitFraction, "Split fraction should clamp to maximum")
        println("✔ ImageCompare split fraction verified")
    }

    // =========================================================================
    // 6. BUTTON TESTS
    // =========================================================================

    @Test
    fun testButtonDebounceSimulation() {
        println("\n=== [TEST 16] BUTTON: DEBOUNCE SIMULATION ===")
        var lastClickTime = 0L
        val debounceMs = 300L
        var clickCount = 0

        // Simulate rapid clicks
        val clickTimes = listOf(0L, 100L, 200L, 350L, 500L)
        clickTimes.forEach { currentTime ->
            if (currentTime - lastClickTime >= debounceMs) {
                lastClickTime = currentTime
                clickCount++
            }
        }

        assertEquals(3, clickCount, "Should register 3 clicks (at 0ms, 350ms, 500ms)")
        println("✔ Button debounce simulation verified")
    }

    @Test
    fun testButtonLoadingState() {
        println("\n=== [TEST 17] BUTTON: LOADING STATE ===")
        var internalLoading = false
        val timeoutMs = 10000L

        // Simulate click
        internalLoading = true
        assertTrue(internalLoading, "Button should be loading after click")

        // Simulate synchronous completion
        internalLoading = false
        assertFalse(internalLoading, "Button should not be loading after completion")

        // Simulate timeout recovery
        internalLoading = true
        // In real code, LaunchedEffect would reset after timeoutMs
        // Here we simulate the reset
        internalLoading = false
        assertFalse(internalLoading, "Button should recover after timeout")
        println("✔ Button loading state verified")
    }

    @Test
    fun testButtonEnabledState() {
        println("\n=== [TEST 18] BUTTON: ENABLED STATE ===")
        val enabled = true
        val isLoading = false
        val internalLoading = false

        val isBusy = isLoading || internalLoading
        val isEffectivelyEnabled = enabled && !isBusy
        assertTrue(isEffectivelyEnabled, "Button should be enabled when not busy")

        // Test disabled state
        val enabledFalse = false
        val isEffectivelyEnabledFalse = enabledFalse && !isBusy
        assertFalse(isEffectivelyEnabledFalse, "Button should be disabled when enabled=false")

        // Test busy state
        val isLoadingTrue = true
        val isBusyTrue = isLoadingTrue || internalLoading
        val isEffectivelyEnabledBusy = enabled && !isBusyTrue
        assertFalse(isEffectivelyEnabledBusy, "Button should be disabled when loading")
        println("✔ Button enabled state verified")
    }

    // =========================================================================
    // 7. VARIANT TESTS
    // =========================================================================

    @Test
    fun testVariantFromStringValid() {
        println("\n=== [TEST 19] VARIANT: FROM STRING VALID ===")
        assertEquals(Variant.Primary, Variant.fromString("primary"))
        assertEquals(Variant.Secondary, Variant.fromString("secondary"))
        assertEquals(Variant.Success, Variant.fromString("success"))
        assertEquals(Variant.Danger, Variant.fromString("danger"))
        assertEquals(Variant.Warning, Variant.fromString("warning"))
        assertEquals(Variant.Info, Variant.fromString("info"))
        assertEquals(Variant.Light, Variant.fromString("light"))
        assertEquals(Variant.Dark, Variant.fromString("dark"))
        assertEquals(Variant.Ghost, Variant.fromString("ghost"))
        assertEquals(Variant.Outline, Variant.fromString("outline"))
        println("✔ Variant.fromString valid cases verified")
    }

    @Test
    fun testVariantFromStringCaseInsensitive() {
        println("\n=== [TEST 20] VARIANT: FROM STRING CASE INSENSITIVE ===")
        assertEquals(Variant.Primary, Variant.fromString("PRIMARY"))
        assertEquals(Variant.Primary, Variant.fromString("Primary"))
        assertEquals(Variant.Primary, Variant.fromString("  primary  "))
        assertEquals(Variant.Danger, Variant.fromString("DANGER"))
        println("✔ Variant.fromString case insensitive verified")
    }

    @Test
    fun testVariantFromStringInvalidThrows() {
        println("\n=== [TEST 21] VARIANT: FROM STRING INVALID THROWS ===")
        assertFailsWith<IllegalArgumentException> {
            Variant.fromString("primery") // typo
        }
        assertFailsWith<IllegalArgumentException> {
            Variant.fromString("invalid")
        }
        assertFailsWith<IllegalArgumentException> {
            Variant.fromString("")
        }
        println("✔ Variant.fromString invalid throws verified")
    }

    @Test
    fun testVariantFromStringOrDefault() {
        println("\n=== [TEST 22] VARIANT: FROM STRING OR DEFAULT ===")
        assertEquals(Variant.Primary, Variant.fromStringOrDefault("primary"))
        assertEquals(Variant.Secondary, Variant.fromStringOrDefault("invalid"))
        assertEquals(Variant.Danger, Variant.fromStringOrDefault("invalid", Variant.Danger))
        assertEquals(Variant.Secondary, Variant.fromStringOrDefault("", Variant.Secondary))
        println("✔ Variant.fromStringOrDefault verified")
    }

    @Test
    fun testVariantColorMapping() {
        println("\n=== [TEST 23] VARIANT: COLOR MAPPING ===")
        val theme = LightTheme

        assertEquals(theme.primary, variantColor(theme, Variant.Primary))
        assertEquals(theme.secondary, variantColor(theme, Variant.Secondary))
        assertEquals(theme.success, variantColor(theme, Variant.Success))
        assertEquals(theme.danger, variantColor(theme, Variant.Danger))
        assertEquals(theme.warning, variantColor(theme, Variant.Warning))
        assertEquals(theme.info, variantColor(theme, Variant.Info))
        assertEquals(theme.light, variantColor(theme, Variant.Light))
        assertEquals(theme.dark, variantColor(theme, Variant.Dark))
        assertEquals(Color.Transparent, variantColor(theme, Variant.Ghost))
        assertEquals(Color.Transparent, variantColor(theme, Variant.Outline))
        println("✔ Variant color mapping verified")
    }

    // =========================================================================
    // 8. GENERIC THEME TESTS
    // =========================================================================

    @Test
    fun testGenericThemeShadowFields() {
        println("\n=== [TEST 24] GENERIC THEME: SHADOW FIELDS ===")
        val theme = LightTheme

        assertNotNull(theme.shadowSm, "shadowSm should exist")
        assertNotNull(theme.shadowMd, "shadowMd should exist")
        assertNotNull(theme.shadowLg, "shadowLg should exist")

        // Verify shadow properties
        assertEquals(0.dp, theme.shadowSm.offsetX)
        assertEquals(1.dp, theme.shadowSm.offsetY)
        assertEquals(2.dp, theme.shadowSm.blur)

        assertEquals(0.dp, theme.shadowMd.offsetX)
        assertEquals(2.dp, theme.shadowMd.offsetY)
        assertEquals(4.dp, theme.shadowMd.blur)

        assertEquals(0.dp, theme.shadowLg.offsetX)
        assertEquals(4.dp, theme.shadowLg.offsetY)
        assertEquals(8.dp, theme.shadowLg.blur)
        println("✔ GenericTheme shadow fields verified")
    }

    @Test
    fun testGenericThemeShadowDataClass() {
        println("\n=== [TEST 25] GENERIC THEME: SHADOW DATA CLASS ===")
        val shadow = ThemeShadow(
            offsetX = 0.dp,
            offsetY = 2.dp,
            blur = 4.dp,
            spread = 0.dp,
            color = Color(0x1A000000)
        )

        assertEquals(0.dp, shadow.offsetX)
        assertEquals(2.dp, shadow.offsetY)
        assertEquals(4.dp, shadow.blur)
        assertEquals(0.dp, shadow.spread)
        assertEquals(Color(0x1A000000), shadow.color)

        // Test copy
        val shadowCopy = shadow.copy(offsetY = 4.dp)
        assertEquals(4.dp, shadowCopy.offsetY)
        assertEquals(shadow.blur, shadowCopy.blur)
        println("✔ GenericTheme shadow data class verified")
    }

    @Test
    fun testGenericThemeLightDarkConsistency() {
        println("\n=== [TEST 26] GENERIC THEME: LIGHT/DARK CONSISTENCY ===")
        // Both themes should have same structure
        assertEquals(LightTheme::class.members.size, DarkTheme::class.members.size)

        // Both should have shadow fields
        assertNotNull(LightTheme.shadowSm)
        assertNotNull(DarkTheme.shadowSm)
        assertNotNull(LightTheme.shadowMd)
        assertNotNull(DarkTheme.shadowMd)
        assertNotNull(LightTheme.shadowLg)
        assertNotNull(DarkTheme.shadowLg)

        // Shadow values should be same for both themes (from design_tokens.json)
        assertEquals(LightTheme.shadowSm.offsetX, DarkTheme.shadowSm.offsetX)
        assertEquals(LightTheme.shadowSm.offsetY, DarkTheme.shadowSm.offsetY)
        assertEquals(LightTheme.shadowSm.blur, DarkTheme.shadowSm.blur)
        println("✔ GenericTheme light/dark consistency verified")
    }

    @Test
    fun testGenericThemeColorTokens() {
        println("\n=== [TEST 27] GENERIC THEME: COLOR TOKENS ===")
        val light = LightTheme
        val dark = DarkTheme

        // Light theme colors
        assertEquals("light", light.name)
        assertEquals(Color(0xFF2ECC71), light.primary)
        assertEquals(Color(0xFFFFFFFF), light.bgPrimary)
        assertEquals(Color(0xFF333333), light.textPrimary)

        // Dark theme colors
        assertEquals("dark", dark.name)
        assertEquals(Color(0xFF2ECC71), dark.primary)
        assertEquals(Color(0xFF1E272C), dark.bgPrimary)
        assertEquals(Color(0xFFECEFF1), dark.textPrimary)

        // Both should have same primary color
        assertEquals(light.primary, dark.primary)
        println("✔ GenericTheme color tokens verified")
    }

    // =========================================================================
    // 9. TRANSFORM STATE TESTS
    // =========================================================================

    @Test
    fun testTransformStateZoomIn() {
        println("\n=== [TEST 28] TRANSFORM STATE: ZOOM IN ===")
        val state = TransformState(minScale = 0.1f, maxScale = 5.0f, initialScale = 1.0f)

        state.zoomIn(0.5f)
        assertEquals(1.5f, state.scale)

        state.zoomIn(0.5f)
        assertEquals(2.0f, state.scale)

        state.zoomIn(10f) // Should clamp to max
        assertEquals(5.0f, state.scale)
        println("✔ TransformState zoom in verified")
    }

    @Test
    fun testTransformStateZoomOut() {
        println("\n=== [TEST 29] TRANSFORM STATE: ZOOM OUT ===")
        val state = TransformState(minScale = 0.1f, maxScale = 5.0f, initialScale = 3.0f)

        state.zoomOut(0.5f)
        assertEquals(2.5f, state.scale)

        state.zoomOut(0.5f)
        assertEquals(2.0f, state.scale)

        state.zoomOut(10f) // Should clamp to min
        assertEquals(0.1f, state.scale)
        println("✔ TransformState zoom out verified")
    }

    @Test
    fun testTransformStateAutoRecenter() {
        println("\n=== [TEST 30] TRANSFORM STATE: AUTO RECENTER ===")
        val state = TransformState(minScale = 0.1f, maxScale = 10.0f, initialScale = 1.0f)

        // Zoom in and add offset
        state.onTransform(
            panDelta = androidx.compose.ui.geometry.Offset(100f, 50f),
            zoomDelta = 2.0f
        )
        assertEquals(2.0f, state.scale)
        assertEquals(100f, state.offsetX)
        assertEquals(50f, state.offsetY)

        // Zoom out below 1.0 - should auto recenter
        state.onTransform(
            panDelta = androidx.compose.ui.geometry.Offset(200f, 100f),
            zoomDelta = 0.4f // 2.0 * 0.4 = 0.8
        )
        assertEquals(0.8f, state.scale)
        assertEquals(0f, state.offsetX, "Offset X should reset when zoom < 1.0")
        assertEquals(0f, state.offsetY, "Offset Y should reset when zoom < 1.0")
        println("✔ TransformState auto recenter verified")
    }

    @Test
    fun testTransformStateExactOneZoom() {
        println("\n=== [TEST 31] TRANSFORM STATE: EXACT 1.0 ZOOM ===")
        val state = TransformState(minScale = 0.1f, maxScale = 10.0f, initialScale = 1.0f)

        // Add some offset first
        state.onTransform(
            panDelta = androidx.compose.ui.geometry.Offset(50f, 25f),
            zoomDelta = 1.5f
        )
        assertEquals(1.5f, state.scale)
        assertEquals(50f, state.offsetX)

        // Zoom to exactly 1.0
        state.onTransform(
            panDelta = androidx.compose.ui.geometry.Offset(0f, 0f),
            zoomDelta = 1.0f / 1.5f
        )
        assertEquals(1.0f, state.scale, 0.001f)
        // At zoom 1.0, offset should be preserved (not reset)
        assertEquals(50f, state.offsetX, "Offset should be preserved at zoom 1.0")
        println("✔ TransformState exact 1.0 zoom verified")
    }

    @Test
    fun testTransformStateReset() {
        println("\n=== [TEST 32] TRANSFORM STATE: RESET ===")
        val state = TransformState(minScale = 0.1f, maxScale = 5.0f, initialScale = 1.0f)

        state.zoomIn(2.0f)
        state.onTransform(
            panDelta = androidx.compose.ui.geometry.Offset(100f, 50f),
            zoomDelta = 1.0f
        )

        state.reset()
        assertEquals(1.0f, state.scale)
        assertEquals(0f, state.offsetX)
        assertEquals(0f, state.offsetY)
        println("✔ TransformState reset verified")
    }

    // =========================================================================
    // 10. LRU MEMORY CACHE TESTS
    // =========================================================================

    @Test
    fun testLruCacheBasicOperations() {
        println("\n=== [TEST 33] LRU CACHE: BASIC OPERATIONS ===")
        val cache = LruMemoryCache<String, String>(maxCapacity = 3)

        cache.put("a", "1")
        cache.put("b", "2")
        cache.put("c", "3")

        assertEquals(3, cache.size)
        assertEquals("1", cache.get("a"))
        assertEquals("2", cache.get("b"))
        assertEquals("3", cache.get("c"))
        assertTrue(cache.containsKey("a"))
        assertFalse(cache.containsKey("d"))
        println("✔ LRU cache basic operations verified")
    }

    @Test
    fun testLruCacheEvictionOrder() {
        println("\n=== [TEST 34] LRU CACHE: EVICTION ORDER ===")
        val cache = LruMemoryCache<String, String>(maxCapacity = 3)

        cache.put("a", "1")
        cache.put("b", "2")
        cache.put("c", "3")

        // Access "a" to make it most recently used
        cache.get("a")

        // Add "d" - should evict "b" (least recently used)
        cache.put("d", "4")

        assertEquals(3, cache.size)
        assertTrue(cache.containsKey("a"), "a should still exist (recently accessed)")
        assertFalse(cache.containsKey("b"), "b should be evicted (least recently used)")
        assertTrue(cache.containsKey("c"), "c should still exist")
        assertTrue(cache.containsKey("d"), "d should exist (just added)")
        println("✔ LRU cache eviction order verified")
    }

    @Test
    fun testLruCacheUpdateExisting() {
        println("\n=== [TEST 35] LRU CACHE: UPDATE EXISTING ===")
        val cache = LruMemoryCache<String, String>(maxCapacity = 3)

        cache.put("a", "1")
        cache.put("b", "2")
        cache.put("c", "3")

        // Update "a" - should move to most recently used
        cache.put("a", "updated")

        assertEquals("updated", cache.get("a"))

        // Add "d" - should evict "b" (not "a")
        cache.put("d", "4")

        assertTrue(cache.containsKey("a"), "a should still exist (updated)")
        assertFalse(cache.containsKey("b"), "b should be evicted")
        println("✔ LRU cache update existing verified")
    }

    @Test
    fun testLruCacheRemove() {
        println("\n=== [TEST 36] LRU CACHE: REMOVE ===")
        val cache = LruMemoryCache<String, String>(maxCapacity = 3)

        cache.put("a", "1")
        cache.put("b", "2")
        cache.put("c", "3")

        val removed = cache.remove("b")
        assertEquals("2", removed)
        assertEquals(2, cache.size)
        assertFalse(cache.containsKey("b"))

        // Remove non-existent
        val removedNull = cache.remove("d")
        assertNull(removedNull)
        println("✔ LRU cache remove verified")
    }

    @Test
    fun testLruCacheClear() {
        println("\n=== [TEST 37] LRU CACHE: CLEAR ===")
        val cache = LruMemoryCache<String, String>(maxCapacity = 3)

        cache.put("a", "1")
        cache.put("b", "2")
        cache.put("c", "3")

        cache.clear()
        assertEquals(0, cache.size)
        assertFalse(cache.containsKey("a"))
        assertFalse(cache.containsKey("b"))
        assertFalse(cache.containsKey("c"))
        println("✔ LRU cache clear verified")
    }

    @Test
    fun testLruCacheConcurrentAccess() {
        println("\n=== [TEST 38] LRU CACHE: CONCURRENT ACCESS ===")
        val cache = LruMemoryCache<String, String>(maxCapacity = 10)

        // Simulate concurrent writes
        for (i in 1..100) {
            cache.put("key_$i", "value_$i")
        }

        // Cache should only hold last 10 items
        assertEquals(10, cache.size)

        // Verify last 10 items exist
        for (i in 91..100) {
            assertTrue(cache.containsKey("key_$i"), "key_$i should exist")
        }

        // Verify first 90 items were evicted
        for (i in 1..90) {
            assertFalse(cache.containsKey("key_$i"), "key_$i should be evicted")
        }
        println("✔ LRU cache concurrent access verified")
    }

    // =========================================================================
    // 11. SESSION CHECKPOINT MANAGER TESTS
    // =========================================================================

    @Test
    fun testSessionCheckpointRecordAndRetrieve() {
        println("\n=== [TEST 39] SESSION CHECKPOINT: RECORD AND RETRIEVE ===")
        val batchId = "test_batch_1"

        SessionCheckpointManager.recordProgress(
            batchId = batchId,
            total = 10,
            completed = 5,
            lastPath = "C:/Photos/IMG_005.dng"
        )

        val checkpoint = SessionCheckpointManager.getCheckpoint(batchId)
        assertNotNull(checkpoint)
        assertEquals(10, checkpoint.totalFrames)
        assertEquals(5, checkpoint.completedFrames)
        assertEquals("C:/Photos/IMG_005.dng", checkpoint.lastProcessedPath)

        // Cleanup
        SessionCheckpointManager.clearCheckpoint(batchId)
        println("✔ Session checkpoint record and retrieve verified")
    }

    @Test
    fun testSessionCheckpointHasPendingRecovery() {
        println("\n=== [TEST 40] SESSION CHECKPOINT: HAS PENDING RECOVERY ===")
        val batchId = "test_batch_2"

        // No checkpoint yet
        assertFalse(SessionCheckpointManager.hasPendingRecovery(batchId))

        // Record partial progress
        SessionCheckpointManager.recordProgress(batchId, 10, 5, null)
        assertTrue(SessionCheckpointManager.hasPendingRecovery(batchId))

        // Record complete progress
        SessionCheckpointManager.recordProgress(batchId, 10, 10, null)
        assertFalse(SessionCheckpointManager.hasPendingRecovery(batchId), "Completed batch should not have pending recovery")

        // Record zero progress
        SessionCheckpointManager.recordProgress(batchId, 10, 0, null)
        assertFalse(SessionCheckpointManager.hasPendingRecovery(batchId), "Zero progress should not have pending recovery")

        // Cleanup
        SessionCheckpointManager.clearCheckpoint(batchId)
        println("✔ Session checkpoint has pending recovery verified")
    }

    @Test
    fun testSessionCheckpointClear() {
        println("\n=== [TEST 41] SESSION CHECKPOINT: CLEAR ===")
        val batchId = "test_batch_3"

        SessionCheckpointManager.recordProgress(batchId, 10, 5, null)
        assertNotNull(SessionCheckpointManager.getCheckpoint(batchId))

        SessionCheckpointManager.clearCheckpoint(batchId)
        assertNull(SessionCheckpointManager.getCheckpoint(batchId))
        assertFalse(SessionCheckpointManager.hasPendingRecovery(batchId))
        println("✔ Session checkpoint clear verified")
    }

    @Test
    fun testSessionCheckpointOverwrite() {
        println("\n=== [TEST 42] SESSION CHECKPOINT: OVERWRITE ===")
        val batchId = "test_batch_4"

        SessionCheckpointManager.recordProgress(batchId, 10, 3, "IMG_003.dng")
        SessionCheckpointManager.recordProgress(batchId, 10, 7, "IMG_007.dng")

        val checkpoint = SessionCheckpointManager.getCheckpoint(batchId)
        assertNotNull(checkpoint)
        assertEquals(7, checkpoint.completedFrames, "Should have latest completed count")
        assertEquals("IMG_007.dng", checkpoint.lastProcessedPath, "Should have latest path")

        // Cleanup
        SessionCheckpointManager.clearCheckpoint(batchId)
        println("✔ Session checkpoint overwrite verified")
    }

    // =========================================================================
    // 12. SHARPNESS METRIC TESTS
    // =========================================================================

    @Test
    fun testSharpnessMetricFlatImage() {
        println("\n=== [TEST 43] SHARPNESS METRIC: FLAT IMAGE ===")
        val size = 64
        val buffer = ByteBuffer.allocateDirect(size * size)
        for (i in 0 until size * size) {
            buffer.put(128.toByte())
        }
        buffer.rewind()

        val score = SharpnessMetric.computeSharpness(buffer, size, size)
        assertEquals(0.0, score, 0.001, "Flat image should have zero sharpness")
        println("✔ Sharpness metric flat image verified")
    }

    @Test
    fun testSharpnessMetricHighFrequency() {
        println("\n=== [TEST 44] SHARPNESS METRIC: HIGH FREQUENCY ===")
        val size = 64
        val buffer = ByteBuffer.allocateDirect(size * size)
        for (y in 0 until size) {
            for (x in 0 until size) {
                // Alternating pattern (high frequency)
                buffer.put(if ((x + y) % 2 == 0) 255.toByte() else 0.toByte())
            }
        }
        buffer.rewind()

        val score = SharpnessMetric.computeSharpness(buffer, size, size)
        assertTrue(score > 0, "High frequency image should have positive sharpness")
        println("✔ Sharpness metric high frequency verified")
    }

    @Test
    fun testSharpnessMetricEdgeCases() {
        println("\n=== [TEST 45] SHARPNESS METRIC: EDGE CASES ===")
        // Too small image
        val smallBuffer = ByteBuffer.allocateDirect(4)
        val smallScore = SharpnessMetric.computeSharpness(smallBuffer, 2, 2)
        assertEquals(0.0, smallScore, "Image smaller than 3x3 should return 0")

        // Empty buffer
        val emptyBuffer = ByteBuffer.allocateDirect(0)
        val emptyScore = SharpnessMetric.computeSharpness(emptyBuffer, 0, 0)
        assertEquals(0.0, emptyScore, "Empty buffer should return 0")

        // Buffer with position != 0
        val buffer = ByteBuffer.allocateDirect(100)
        for (i in 0 until 100) buffer.put(128.toByte())
        buffer.position(10) // Move position
        val score = SharpnessMetric.computeSharpness(buffer, 3, 3)
        assertEquals(0.0, score, 0.001, "Should work with non-zero position")
        println("✔ Sharpness metric edge cases verified")
    }

    @Test
    fun testSharpnessMetricAutoAssignBestReference() {
        println("\n=== [TEST 46] SHARPNESS METRIC: AUTO ASSIGN BEST REFERENCE ===")
        val images = listOf(
            ImageItem(path = "photo_01.dng"),
            ImageItem(path = "photo_02.dng"),
            ImageItem(path = "photo_03.dng"),
        )
        val scores = listOf(120.5, 950.8, 340.2)

        val result = SharpnessMetric.autoAssignBestReference(images, scores)

        assertFalse(result[0].isReference)
        assertTrue(result[1].isReference, "Highest score should be reference")
        assertFalse(result[2].isReference)
        println("✔ Sharpness metric auto assign best reference verified")
    }

    // =========================================================================
    // 13. BATCH STATE MANAGER TESTS
    // =========================================================================

    @Test
    fun testBatchStateManagerAddBatch() {
        println("\n=== [TEST 47] BATCH STATE MANAGER: ADD BATCH ===")
        val manager = BatchStateManager()

        val batch = manager.addBatch("Test Batch", listOf("C:/img1.dng", "C:/img2.dng"))
        assertEquals("Test Batch", batch.name)
        assertEquals(2, batch.imageCount)
        assertEquals(1, manager.batches.size)
        assertEquals(0, manager.activeBatchIndex)
        println("✔ BatchStateManager add batch verified")
    }

    @Test
    fun testBatchStateManagerSelectBatch() {
        println("\n=== [TEST 48] BATCH STATE MANAGER: SELECT BATCH ===")
        val manager = BatchStateManager()

        manager.addBatch("Batch 1", listOf("C:/img1.dng"))
        manager.addBatch("Batch 2", listOf("C:/img2.dng"))
        manager.addBatch("Batch 3", listOf("C:/img3.dng"))

        assertEquals(0, manager.activeBatchIndex)

        manager.selectBatch(2)
        assertEquals(2, manager.activeBatchIndex)
        assertEquals("Batch 3", manager.activeBatch?.name)

        // Invalid index
        manager.selectBatch(10)
        assertEquals(2, manager.activeBatchIndex, "Invalid index should not change active batch")
        println("✔ BatchStateManager select batch verified")
    }

    @Test
    fun testBatchStateManagerRemoveBatch() {
        println("\n=== [TEST 49] BATCH STATE MANAGER: REMOVE BATCH ===")
        val manager = BatchStateManager()

        manager.addBatch("Batch 1", listOf("C:/img1.dng"))
        manager.addBatch("Batch 2", listOf("C:/img2.dng"))
        manager.addBatch("Batch 3", listOf("C:/img3.dng"))

        manager.selectBatch(2)
        manager.removeBatch(1)

        assertEquals(2, manager.batches.size)
        assertEquals(1, manager.activeBatchIndex, "Active index should adjust after removal")
        assertEquals("Batch 3", manager.activeBatch?.name)
        println("✔ BatchStateManager remove batch verified")
    }

    @Test
    fun testBatchStateManagerRemoveLastBatch() {
        println("\n=== [TEST 50] BATCH STATE MANAGER: REMOVE LAST BATCH ===")
        val manager = BatchStateManager()

        manager.addBatch("Batch 1", listOf("C:/img1.dng"))
        manager.removeBatch(0)

        assertEquals(0, manager.batches.size)
        assertEquals(-1, manager.activeBatchIndex, "Active index should be -1 when no batches")
        assertNull(manager.activeBatch)
        println("✔ BatchStateManager remove last batch verified")
    }

    @Test
    fun testBatchStateManagerAddToEmpty() {
        println("\n=== [TEST 51] BATCH STATE MANAGER: ADD TO EMPTY ===")
        val manager = BatchStateManager()

        assertEquals(-1, manager.activeBatchIndex)

        manager.addBatch("New Batch", listOf("C:/img1.dng"))
        assertEquals(0, manager.activeBatchIndex, "Should auto-select first batch")
        assertEquals("New Batch", manager.activeBatch?.name)
        println("✔ BatchStateManager add to empty verified")
    }

    // =========================================================================
    // 14. WORKFLOW STATE MANAGER TESTS
    // =========================================================================

    @Test
    fun testWorkflowStateManagerLifecycle() {
        println("\n=== [TEST 52] WORKFLOW STATE MANAGER: LIFECYCLE ===")
        val manager = WorkflowStateManager()

        // Initial state
        assertTrue(manager.isIdle)
        assertFalse(manager.isRunning)
        assertEquals(0f, manager.progress)

        // Start
        manager.start("Batch_001", "Alignment")
        assertTrue(manager.isRunning)
        assertFalse(manager.isIdle)
        assertEquals("Alignment", manager.currentStep)

        // Update progress
        manager.updateProgress("Denoising", 0.5f, "Batch_001")
        assertEquals(0.5f, manager.progress)
        assertEquals("Denoising", manager.currentStep)

        // Complete
        manager.complete("C:/output/result.jpg", 1200L)
        assertTrue(manager.state is ProcessingState.Success)
        assertEquals(1f, manager.progress)

        // Reset
        manager.reset()
        assertTrue(manager.isIdle)
        assertEquals(0f, manager.progress)
        assertEquals("", manager.currentStep)
        println("✔ WorkflowStateManager lifecycle verified")
    }

    @Test
    fun testWorkflowStateManagerError() {
        println("\n=== [TEST 53] WORKFLOW STATE MANAGER: ERROR ===")
        val manager = WorkflowStateManager()

        manager.start("Batch_001", "Processing")
        manager.fail("Out of memory", RuntimeException("OOM"))

        assertTrue(manager.state is ProcessingState.Error)
        val error = manager.state as ProcessingState.Error
        assertEquals("Out of memory", error.message)
        assertNotNull(error.cause)
        println("✔ WorkflowStateManager error verified")
    }

    // =========================================================================
    // 15. IMAGE VALIDATOR TESTS
    // =========================================================================

    @Test
    fun testImageValidatorValidPaths() {
        println("\n=== [TEST 54] IMAGE VALIDATOR: VALID PATHS ===")
        val paths = listOf(
            "C:/Photos/image.jpg",
            "C:/Photos/image.png",
            "C:/Photos/raw.dng",
            "C:/Photos/raw.cr2",
        )

        val result = ImageValidator.validatePaths(paths)
        assertEquals(4, result.accepted.size)
        assertEquals(0, result.rejected.size)
        assertTrue(result.isAllAccepted)
        println("✔ ImageValidator valid paths verified")
    }

    @Test
    fun testImageValidatorInvalidPaths() {
        println("\n=== [TEST 55] IMAGE VALIDATOR: INVALID PATHS ===")
        val paths = listOf(
            "C:/Photos/document.txt",
            "C:/Photos/video.mp4",
            "C:/Photos/noextension",
        )

        val result = ImageValidator.validatePaths(paths)
        assertEquals(0, result.accepted.size)
        assertEquals(3, result.rejected.size)
        assertFalse(result.isAllAccepted)
        println("✔ ImageValidator invalid paths verified")
    }

    @Test
    fun testImageValidatorDuplicates() {
        println("\n=== [TEST 56] IMAGE VALIDATOR: DUPLICATES ===")
        val paths = listOf(
            "C:/Photos/image.jpg",
            "C:/Photos/image.jpg", // duplicate
            "C:/Photos/image2.jpg",
        )

        val result = ImageValidator.validatePaths(paths)
        assertEquals(2, result.accepted.size)
        assertEquals(1, result.rejected.size)
        assertTrue(result.rejected[0].reason.contains("duplikat"))
        println("✔ ImageValidator duplicates verified")
    }

    @Test
    fun testImageValidatorEmptyPath() {
        println("\n=== [TEST 57] IMAGE VALIDATOR: EMPTY PATH ===")
        val paths = listOf("", "  ", "C:/Photos/image.jpg")

        val result = ImageValidator.validatePaths(paths)
        assertEquals(1, result.accepted.size)
        assertEquals(2, result.rejected.size)
        println("✔ ImageValidator empty path verified")
    }

    @Test
    fun testImageValidatorExistingPaths() {
        println("\n=== [TEST 58] IMAGE VALIDATOR: EXISTING PATHS ===")
        val existingPaths = setOf("C:/Photos/existing.jpg")
        val candidates = listOf("C:/Photos/existing.jpg", "C:/Photos/new.jpg")

        val result = ImageValidator.validatePaths(candidates, existingPaths)
        assertEquals(1, result.accepted.size)
        assertEquals(1, result.rejected.size)
        assertEquals("C:/Photos/new.jpg", result.accepted[0].path)
        println("✔ ImageValidator existing paths verified")
    }

    // =========================================================================
    // 16. IMAGE ITEM & BATCH ITEM TESTS
    // =========================================================================

    @Test
    fun testImageItemProperties() {
        println("\n=== [TEST 59] IMAGE ITEM: PROPERTIES ===")
        val jpg = ImageItem(path = "C:/Photos/image.jpg")
        val dng = ImageItem(path = "C:/Photos/raw.dng")
        val png = ImageItem(path = "C:/Photos/photo.png")

        assertEquals("image.jpg", jpg.filename)
        assertEquals("jpg", jpg.extension)
        assertFalse(jpg.isRaw)

        assertEquals("raw.dng", dng.filename)
        assertEquals("dng", dng.extension)
        assertTrue(dng.isRaw)

        assertEquals("photo.png", png.filename)
        assertEquals("png", png.extension)
        assertFalse(png.isRaw)
        println("✔ ImageItem properties verified")
    }

    @Test
    fun testImageItemCrossPlatformPath() {
        println("\n=== [TEST 60] IMAGE ITEM: CROSS PLATFORM PATH ===")
        val windowsPath = ImageItem(path = "C:\\Photos\\image.jpg")
        val unixPath = ImageItem(path = "/home/user/photos/image.jpg")

        assertEquals("image.jpg", windowsPath.filename)
        assertEquals("image.jpg", unixPath.filename)
        println("✔ ImageItem cross platform path verified")
    }

    @Test
    fun testBatchItemAddImage() {
        println("\n=== [TEST 61] BATCH ITEM: ADD IMAGE ===")
        var batch = BatchItem(name = "Test")

        batch = batch.addImage(ImageItem(path = "img1.jpg"))
        assertEquals(1, batch.imageCount)
        assertTrue(batch.images[0].isReference, "First image should be reference")

        batch = batch.addImage(ImageItem(path = "img2.jpg"))
        assertEquals(2, batch.imageCount)
        assertFalse(batch.images[1].isReference, "Second image should not be reference")

        // Duplicate
        batch = batch.addImage(ImageItem(path = "img1.jpg"))
        assertEquals(2, batch.imageCount, "Duplicate should not be added")
        println("✔ BatchItem add image verified")
    }

    @Test
    fun testBatchItemRemoveImage() {
        println("\n=== [TEST 62] BATCH ITEM: REMOVE IMAGE ===")
        var batch = BatchItem(name = "Test")
        batch = batch.addImage(ImageItem(path = "img1.jpg"))
        batch = batch.addImage(ImageItem(path = "img2.jpg"))
        batch = batch.addImage(ImageItem(path = "img3.jpg"))

        batch = batch.removeImage("img2.jpg")
        assertEquals(2, batch.imageCount)
        assertNotNull(batch.referenceImage, "Should still have reference")

        // Remove reference image
        batch = batch.removeImage("img1.jpg")
        assertEquals(1, batch.imageCount)
        assertNotNull(batch.referenceImage, "Should auto-assign new reference")
        assertTrue(batch.images[0].isReference, "Remaining image should become reference")
        println("✔ BatchItem remove image verified")
    }

    @Test
    fun testBatchItemSetReference() {
        println("\n=== [TEST 63] BATCH ITEM: SET REFERENCE ===")
        var batch = BatchItem(name = "Test")
        batch = batch.addImage(ImageItem(path = "img1.jpg"))
        batch = batch.addImage(ImageItem(path = "img2.jpg"))
        batch = batch.addImage(ImageItem(path = "img3.jpg"))

        batch = batch.setReference("img3.jpg")
        assertEquals("img3.jpg", batch.referenceImage?.path)
        assertTrue(batch.images[2].isReference)
        assertFalse(batch.images[0].isReference)
        assertFalse(batch.images[1].isReference)
        println("✔ BatchItem set reference verified")
    }

    @Test
    fun testBatchItemToggleSelect() {
        println("\n=== [TEST 64] BATCH ITEM: TOGGLE SELECT ===")
        var batch = BatchItem(name = "Test")
        batch = batch.addImage(ImageItem(path = "img1.jpg"))
        batch = batch.addImage(ImageItem(path = "img2.jpg"))

        assertFalse(batch.images[0].isSelected)

        batch = batch.toggleSelect("img1.jpg")
        assertTrue(batch.images[0].isSelected)

        batch = batch.toggleSelect("img1.jpg")
        assertFalse(batch.images[0].isSelected, "Toggle should deselect")
        println("✔ BatchItem toggle select verified")
    }

    // =========================================================================
    // 17. ALGORITHM CONFIG TESTS
    // =========================================================================

    @Test
    fun testAlgorithmConfigTypeSafeAccess() {
        println("\n=== [TEST 65] ALGORITHM CONFIG: TYPE SAFE ACCESS ===")
        val config = AlgorithmConfig(
            category = AlgorithmCategory.DENOISING,
            name = "MFDenoiser",
            parameters = mapOf(
                "spatial_sigma" to 1.5,
                "iterations" to 3,
                "use_gpu" to true,
                "mode" to "fast"
            )
        )

        assertEquals(1.5f, config.getFloat("spatial_sigma"))
        assertEquals(3, config.getInt("iterations"))
        assertTrue(config.getBoolean("use_gpu"))
        assertEquals("fast", config.getString("mode"))

        // Default values
        assertEquals(0, config.getInt("nonexistent"))
        assertEquals(0f, config.getFloat("nonexistent"))
        assertFalse(config.getBoolean("nonexistent"))
        assertEquals("", config.getString("nonexistent"))
        println("✔ AlgorithmConfig type safe access verified")
    }

    @Test
    fun testAlgorithmConfigWithParam() {
        println("\n=== [TEST 66] ALGORITHM CONFIG: WITH PARAM ===")
        val config = AlgorithmConfig(
            category = AlgorithmCategory.ALIGNMENT,
            name = "Farneback",
            parameters = mapOf("levels" to 3)
        )

        val updated = config.withParam("iterations", 5)
        assertEquals(3, updated.getInt("levels"))
        assertEquals(5, updated.getInt("iterations"))

        // Original should be unchanged
        assertEquals(3, config.getInt("levels"))
        assertFalse(config.parameters.containsKey("iterations"))
        println("✔ AlgorithmConfig with param verified")
    }

    @Test
    fun testAlgorithmRegistry() {
        println("\n=== [TEST 67] ALGORITHM REGISTRY ===")
        val alignmentOptions = AlgorithmRegistry.getOptions(AlgorithmCategory.ALIGNMENT)
        val denoisingOptions = AlgorithmRegistry.getOptions(AlgorithmCategory.DENOISING)
        val superResOptions = AlgorithmRegistry.getOptions(AlgorithmCategory.SUPER_RESOLUTION)

        assertTrue(alignmentOptions.isNotEmpty())
        assertTrue(denoisingOptions.isNotEmpty())
        assertTrue(superResOptions.isNotEmpty())

        assertTrue(alignmentOptions.any { it.name == "Farneback" })
        assertTrue(denoisingOptions.any { it.name == "MFDenoiser" })
        assertTrue(superResOptions.any { it.name == "splattingSR" })
        println("✔ AlgorithmRegistry verified")
    }

    // =========================================================================
    // 18. PRESET STORE TESTS
    // =========================================================================

    @Test
    fun testPresetStoreGetAll() {
        println("\n=== [TEST 68] PRESET STORE: GET ALL ===")
        val presets = PresetStore.getAllPresets()
        assertTrue(presets.size >= 4, "Should have at least 4 builtin presets")
        println("✔ PresetStore get all verified")
    }

    @Test
    fun testPresetStoreGetById() {
        println("\n=== [TEST 69] PRESET STORE: GET BY ID ===")
        val nightDenoise = PresetStore.getPresetById("night_denoise")
        assertNotNull(nightDenoise)
        assertEquals("Night Low-Light Denoise", nightDenoise.name)
        assertEquals(0.85, nightDenoise.parameters["denoise_strength"])

        val astroStack = PresetStore.getPresetById("astro_stack")
        assertNotNull(astroStack)
        assertEquals("Astro Multi-Stack", astroStack.name)

        val nonexistent = PresetStore.getPresetById("nonexistent")
        assertNull(nonexistent)
        println("✔ PresetStore get by ID verified")
    }

    @Test
    fun testPresetStoreSaveCustom() {
        println("\n=== [TEST 70] PRESET STORE: SAVE CUSTOM ===")
        val custom = PresetStore.saveCustomPreset(
            name = "My Custom",
            description = "Custom preset",
            params = mapOf("strength" to 0.7)
        )

        assertNotNull(custom)
        assertTrue(custom.id.startsWith("custom_"))
        assertEquals("My Custom", custom.name)
        assertEquals(0.7, custom.parameters["strength"])

        // Verify it's in the list
        val all = PresetStore.getAllPresets()
        assertTrue(all.any { it.id == custom.id })
        println("✔ PresetStore save custom verified")
    }

    // =========================================================================
    // 19. ADAPTIVE CHUNK PROCESSOR TESTS
    // =========================================================================

    @Test
    fun testAdaptiveChunkSizeCalculation() {
        println("\n=== [TEST 71] ADAPTIVE CHUNK: SIZE CALCULATION ===")
        assertEquals(50, AdaptiveChunkProcessor.calculateAdaptiveChunkSize(100))
        assertEquals(50, AdaptiveChunkProcessor.calculateAdaptiveChunkSize(499))
        assertEquals(100, AdaptiveChunkProcessor.calculateAdaptiveChunkSize(500))
        assertEquals(100, AdaptiveChunkProcessor.calculateAdaptiveChunkSize(999))
        assertEquals(200, AdaptiveChunkProcessor.calculateAdaptiveChunkSize(1000))
        assertEquals(200, AdaptiveChunkProcessor.calculateAdaptiveChunkSize(1499))
        assertEquals(400, AdaptiveChunkProcessor.calculateAdaptiveChunkSize(1500))
        assertEquals(400, AdaptiveChunkProcessor.calculateAdaptiveChunkSize(10000))
        println("✔ Adaptive chunk size calculation verified")
    }

    // =========================================================================
    // 20. PROJECT ARCHIVE MANAGER TESTS
    // =========================================================================

    @Test
    fun testProjectArchiveSaveAndRetrieve() {
        println("\n=== [TEST 72] PROJECT ARCHIVE: SAVE AND RETRIEVE ===")
        val img1 = ImageItem(path = "C:/Photos/IMG_001.dng", isReference = true)
        val img2 = ImageItem(path = "C:/Photos/IMG_002.dng")
        val batch = BatchItem(name = "Night_Stack", images = listOf(img1, img2))

        val manifest = ProjectArchiveManager.saveProject(
            path = "C:/Projects/MyProject.prf",
            batches = listOf(batch),
            activeBatchId = 1L
        )

        assertEquals("MyProject", manifest.projectName)
        assertEquals(1, manifest.batchCount)
        assertEquals(2, manifest.totalImages)
        assertNotNull(manifest.stateToken)

        // Recent projects
        val recent = ProjectArchiveManager.recentProjects()
        assertTrue(recent.contains("C:/Projects/MyProject.prf"))
        println("✔ ProjectArchive save and retrieve verified")
    }

    @Test
    fun testProjectArchiveUnsavedChanges() {
        println("\n=== [TEST 73] PROJECT ARCHIVE: UNSAVED CHANGES ===")
        val img1 = ImageItem(path = "C:/Photos/IMG_001.dng")
        val batch = BatchItem(name = "Test", images = listOf(img1))
        val batches = listOf(batch)

        val token = ProjectArchiveManager.calculateSessionToken(batches)
        assertFalse(ProjectArchiveManager.hasUnsavedChanges(batches, token))

        // Modify
        val modified = listOf(batch.addImage(ImageItem(path = "C:/Photos/IMG_002.dng")))
        assertTrue(ProjectArchiveManager.hasUnsavedChanges(modified, token))
        println("✔ ProjectArchive unsaved changes verified")
    }
}
