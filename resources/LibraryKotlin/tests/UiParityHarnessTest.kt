package org.pixelrefine.genericui

import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.animations.AnimationCurves
import org.pixelrefine.genericui.animations.AnimationType
import org.pixelrefine.genericui.animations.SlideDirection
import org.pixelrefine.genericui.animations.ToastManager
import org.pixelrefine.genericui.components.OverlayPosition
import org.pixelrefine.genericui.components.Variant
import org.pixelrefine.genericui.components.toVariant
import org.pixelrefine.genericui.components.variantColor
import org.pixelrefine.genericui.components.variantHoverColor
import org.pixelrefine.genericui.theme.DarkTheme
import org.pixelrefine.genericui.theme.LightTheme
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertNotNull

class UiParityHarnessTest {

    @Test
    fun testVariantParityWithPySide() {
        assertEquals(Variant.Primary, "primary".toVariant())
        assertEquals(Variant.Secondary, "secondary".toVariant())
        assertEquals(Variant.Success, "success".toVariant())
        assertEquals(Variant.Danger, "danger".toVariant())
        assertEquals(Variant.Warning, "warning".toVariant())
        assertEquals(Variant.Info, "info".toVariant())
        assertEquals(Variant.Light, "light".toVariant())
        assertEquals(Variant.Dark, "dark".toVariant())
        assertEquals(Variant.Ghost, "ghost".toVariant())
        assertEquals(Variant.Outline, "outline".toVariant())
    }

    @Test
    fun testThemeColorTokensParity() {
        // Light Theme Tokens
        assertEquals("light", LightTheme.name)
        assertEquals(Color(0xFF2ECC71), LightTheme.primary)
        assertEquals(Color(0xFF95A5A6), LightTheme.secondary)
        assertEquals(Color(0xFFE74C3C), LightTheme.danger)
        assertEquals(Color(0xFFF39C12), LightTheme.warning)
        assertEquals(Color(0xFF0DCAF0), LightTheme.info)
        assertEquals(Color(0xFFFFFFFF), LightTheme.bgPrimary)
        assertEquals(Color(0xFFF5F8FA), LightTheme.bgSecondary)
        assertEquals(Color(0xFFFFFFFF), LightTheme.bgCard)
        assertEquals(Color(0xFF333333), LightTheme.textPrimary)
        assertEquals(Color(0xFFE8EDF2), LightTheme.borderColor)

        // Dark Theme Tokens
        assertEquals("dark", DarkTheme.name)
        assertEquals(Color(0xFF2ECC71), DarkTheme.primary)
        assertEquals(Color(0xFF78909C), DarkTheme.secondary)
        assertEquals(Color(0xFFE74C3C), DarkTheme.danger)
        assertEquals(Color(0xFF1E272C), DarkTheme.bgPrimary)
        assertEquals(Color(0xFF263238), DarkTheme.bgSecondary)
        assertEquals(Color(0xFF1E272C), DarkTheme.bgCard)
        assertEquals(Color(0xFFECEFF1), DarkTheme.textPrimary)
        assertEquals(Color(0xFF37474F), DarkTheme.borderColor)

        // Radius & Spacing
        assertEquals(4.dp, LightTheme.radiusSm)
        assertEquals(5.dp, LightTheme.radiusMd)
        assertEquals(8.dp, LightTheme.radiusLg)
        assertEquals(10.dp, LightTheme.radiusXl)
    }

    @Test
    fun testAnimationParity() {
        // SlideDirection
        assertEquals(SlideDirection.LEFT, SlideDirection.fromString("left"))
        assertEquals(SlideDirection.RIGHT, SlideDirection.fromString("right"))
        assertEquals(SlideDirection.UP, SlideDirection.fromString("up"))
        assertEquals(SlideDirection.DOWN, SlideDirection.fromString("down"))

        // AnimationType
        assertEquals(AnimationType.FADE, AnimationType.valueOf("FADE"))
        assertEquals(AnimationType.ZOOM, AnimationType.valueOf("ZOOM"))

        // Easing curves
        assertNotNull(AnimationCurves.OutQuad)
        assertNotNull(AnimationCurves.OutExpo)
        assertNotNull(AnimationCurves.InOutCirc)

        // ToastManager
        val toastManager = ToastManager()
        toastManager.show("Test message", Variant.Success, OverlayPosition.BottomCenter, 3000L)
        assertEquals(1, toastManager.activeToasts.size)
        assertEquals("Test message", toastManager.activeToasts[0].message)
        assertEquals(Variant.Success, toastManager.activeToasts[0].variant)

        toastManager.dismiss(toastManager.activeToasts[0].id)
        assertEquals(0, toastManager.activeToasts.size)
    }
}
