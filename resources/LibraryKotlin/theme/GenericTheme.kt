package org.pixelrefine.genericui.theme

import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.staticCompositionLocalOf
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.TextUnit
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

/**
 * Representasi shadow dari design tokens
 */
data class ThemeShadow(
    val offsetX: Dp,
    val offsetY: Dp,
    val blur: Dp,
    val spread: Dp = 0.dp,
    val color: Color,
)

/**
 * Font size scale — memetakan level heading/body dari Typography system.
 */
data class FontSizes(
    val h1: TextUnit = 32.sp,
    val h2: TextUnit = 28.sp,
    val h3: TextUnit = 24.sp,
    val h4: TextUnit = 20.sp,
    val h5: TextUnit = 18.sp,
    val h6: TextUnit = 16.sp,
    val body1: TextUnit = 15.sp,
    val body2: TextUnit = 13.sp,
    val caption: TextUnit = 12.sp,
    val overline: TextUnit = 11.sp,
    val code: TextUnit = 13.sp,
)

/**
 * Design tokens — dipetakan 1:1 dari `resources/GenericUILibrary/theme.py`
 * lewat `resources/GenericUILibraryKotlin/tokens/design_tokens.json`.
 * (Light = `Theme` / `LightTheme`, Dark = `DarkTheme`.)
 */
data class GenericTheme(
    val name: String,
    // ---- variant colors ----
    val primary: Color,
    val secondary: Color,
    val success: Color,
    val danger: Color,
    val warning: Color,
    val info: Color,
    val light: Color,
    val dark: Color,
    // ---- variant hover colors ----
    val primaryHover: Color,
    val secondaryHover: Color,
    val successHover: Color,
    val dangerHover: Color,
    val warningHover: Color,
    val infoHover: Color,
    // ---- backgrounds ----
    val bgPrimary: Color,
    val bgSecondary: Color,
    val bgDark: Color,
    val bgCard: Color,
    // ---- text ----
    val textPrimary: Color,
    val textSecondary: Color,
    val textMuted: Color,
    val textWhite: Color,
    // ---- borders ----
    val borderColor: Color,
    val borderDark: Color,
    // ---- interactive states ----
    val hoverOverlay: Color,
    val activeOverlay: Color,
    val focusColor: Color,
    // ---- radius ----
    val radiusSm: Dp,
    val radiusMd: Dp,
    val radiusLg: Dp,
    val radiusXl: Dp,
    // ---- spacing ----
    val spacingXs: Dp,
    val spacingSm: Dp,
    val spacingMd: Dp,
    val spacingLg: Dp,
    val spacingXl: Dp,
    // ---- font sizes ----
    val fontXs: TextUnit,
    val fontSm: TextUnit,
    val fontMd: TextUnit,
    val fontLg: TextUnit,
    val fontXl: TextUnit,
    // ---- shadows (dari design_tokens.json) ----
    val shadowSm: ThemeShadow,
    val shadowMd: ThemeShadow,
    val shadowLg: ThemeShadow,
    // ---- font size scale (Typography system) ----
    val fontSizes: FontSizes = FontSizes(),
)

val LightTheme = GenericTheme(
    name = "light",
    primary = Color(0xFF0D9488),
    secondary = Color(0xFF64748B),
    success = Color(0xFF10B981),
    danger = Color(0xFFEF4444),
    warning = Color(0xFFF59E0B),
    info = Color(0xFF6366F1),
    light = Color(0xFFF8FAFC),
    dark = Color(0xFF0F172A),
    primaryHover = Color(0xFF0F766E),
    secondaryHover = Color(0xFF475569),
    successHover = Color(0xFF059669),
    dangerHover = Color(0xFFDC2626),
    warningHover = Color(0xFFD97706),
    infoHover = Color(0xFF4F46E5),
    bgPrimary = Color(0xFFFAFBFC),
    bgSecondary = Color(0xFFF1F5F9),
    bgDark = Color(0xFF0F172A),
    bgCard = Color(0xFFFFFFFF),
    textPrimary = Color(0xFF1E293B),
    textSecondary = Color(0xFF475569),
    textMuted = Color(0xFF94A3B8),
    textWhite = Color(0xFFFFFFFF),
    borderColor = Color(0xFFE2E8F0),
    borderDark = Color(0xFFCBD5E1),
    hoverOverlay = Color(0x0A0F172A),
    activeOverlay = Color(0x140F172A),
    focusColor = Color(0xFF0D9488),
    radiusSm = 4.dp,
    radiusMd = 5.dp,
    radiusLg = 8.dp,
    radiusXl = 10.dp,
    spacingXs = 5.dp,
    spacingSm = 10.dp,
    spacingMd = 15.dp,
    spacingLg = 20.dp,
    spacingXl = 30.dp,
    fontXs = 12.sp,
    fontSm = 13.sp,
    fontMd = 15.sp,
    fontLg = 19.sp,
    fontXl = 24.sp,
    // Shadows dari design_tokens.json
    shadowSm = ThemeShadow(offsetX = 0.dp, offsetY = 1.dp, blur = 2.dp, color = Color(0x0D000000)),
    shadowMd = ThemeShadow(offsetX = 0.dp, offsetY = 2.dp, blur = 4.dp, color = Color(0x1A000000)),
    shadowLg = ThemeShadow(offsetX = 0.dp, offsetY = 4.dp, blur = 8.dp, color = Color(0x26000000)),
)

val DarkTheme = GenericTheme(
    name = "dark",
    primary = Color(0xFF2DD4BF),
    secondary = Color(0xFF94A3B8),
    success = Color(0xFF34D399),
    danger = Color(0xFFF87171),
    warning = Color(0xFFFBBF24),
    info = Color(0xFF818CF8),
    light = Color(0xFF334155),
    dark = Color(0xFF020617),
    primaryHover = Color(0xFF5EEAD4),
    secondaryHover = Color(0xFFCBD5E1),
    successHover = Color(0xFF6EE7B7),
    dangerHover = Color(0xFFFCA5A5),
    warningHover = Color(0xFFFCD34D),
    infoHover = Color(0xFFA5B4FC),
    bgPrimary = Color(0xFF0F172A),
    bgSecondary = Color(0xFF1E293B),
    bgDark = Color(0xFF020617),
    bgCard = Color(0xFF1E293B),
    textPrimary = Color(0xFFF1F5F9),
    textSecondary = Color(0xFFCBD5E1),
    textMuted = Color(0xFF64748B),
    textWhite = Color(0xFFFFFFFF),
    borderColor = Color(0xFF334155),
    borderDark = Color(0xFF1E293B),
    hoverOverlay = Color(0x14F1F5F9),
    activeOverlay = Color(0x26F1F5F9),
    focusColor = Color(0xFF2DD4BF),
    radiusSm = 4.dp,
    radiusMd = 5.dp,
    radiusLg = 8.dp,
    radiusXl = 10.dp,
    spacingXs = 5.dp,
    spacingSm = 10.dp,
    spacingMd = 15.dp,
    spacingLg = 20.dp,
    spacingXl = 30.dp,
    fontXs = 12.sp,
    fontSm = 13.sp,
    fontMd = 15.sp,
    fontLg = 19.sp,
    fontXl = 24.sp,
    // Shadows dari design_tokens.json
    shadowSm = ThemeShadow(offsetX = 0.dp, offsetY = 1.dp, blur = 2.dp, color = Color(0x0D000000)),
    shadowMd = ThemeShadow(offsetX = 0.dp, offsetY = 2.dp, blur = 4.dp, color = Color(0x1A000000)),
    shadowLg = ThemeShadow(offsetX = 0.dp, offsetY = 4.dp, blur = 8.dp, color = Color(0x26000000)),
)

val Theme = LightTheme

/** CompositionLocal untuk tema aktif (setara get_theme()). */
val LocalGenericTheme = staticCompositionLocalOf { LightTheme }
val LocalTheme = LocalGenericTheme

/** Provider tema deklaratif (setara set_theme(theme)). */
@Composable
fun GenericThemeProvider(
    theme: GenericTheme = LightTheme,
    content: @Composable () -> Unit,
) {
    CompositionLocalProvider(LocalGenericTheme provides theme, content = content)
}
