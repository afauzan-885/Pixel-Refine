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
)

val LightTheme = GenericTheme(
    name = "light",
    primary = Color(0xFF2ECC71),
    secondary = Color(0xFF95A5A6),
    success = Color(0xFF2ECC71),
    danger = Color(0xFFE74C3C),
    warning = Color(0xFFF39C12),
    info = Color(0xFF0DCAF0),
    light = Color(0xFFF8F9FA),
    dark = Color(0xFF2C3E50),
    primaryHover = Color(0xFF27AE60),
    secondaryHover = Color(0xFF7F8C8D),
    successHover = Color(0xFF27AE60),
    dangerHover = Color(0xFFC0392B),
    warningHover = Color(0xFFD68910),
    infoHover = Color(0xFF0BACCC),
    bgPrimary = Color(0xFFFFFFFF),
    bgSecondary = Color(0xFFF5F8FA),
    bgDark = Color(0xFF2C3E50),
    bgCard = Color(0xFFFFFFFF),
    textPrimary = Color(0xFF333333),
    textSecondary = Color(0xFF666666),
    textMuted = Color(0xFF999999),
    textWhite = Color(0xFFFFFFFF),
    borderColor = Color(0xFFE8EDF2),
    borderDark = Color(0xFFDCDCDC),
    hoverOverlay = Color(0x0D000000),
    activeOverlay = Color(0x1A000000),
    focusColor = Color(0xFF0078D4),
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
)

val DarkTheme = GenericTheme(
    name = "dark",
    primary = Color(0xFF2ECC71),
    secondary = Color(0xFF78909C),
    success = Color(0xFF2ECC71),
    danger = Color(0xFFE74C3C),
    warning = Color(0xFFF39C12),
    info = Color(0xFF0DCAF0),
    light = Color(0xFF37474F),
    dark = Color(0xFF11171A),
    primaryHover = Color(0xFF27AE60),
    secondaryHover = Color(0xFF607D8B),
    successHover = Color(0xFF27AE60),
    dangerHover = Color(0xFFC0392B),
    warningHover = Color(0xFFD68910),
    infoHover = Color(0xFF0BACCC),
    bgPrimary = Color(0xFF1E272C),
    bgSecondary = Color(0xFF263238),
    bgDark = Color(0xFF11171A),
    bgCard = Color(0xFF1E272C),
    textPrimary = Color(0xFFECEFF1),
    textSecondary = Color(0xFFB0BEC5),
    textMuted = Color(0xFF78909C),
    textWhite = Color(0xFFFFFFFF),
    borderColor = Color(0xFF37474F),
    borderDark = Color(0xFF263238),
    hoverOverlay = Color(0x14FFFFFF),
    activeOverlay = Color(0x26FFFFFF),
    focusColor = Color(0xFF2BC7BD),
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
