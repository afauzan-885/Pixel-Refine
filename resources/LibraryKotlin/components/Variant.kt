package org.pixelrefine.genericui.components

import androidx.compose.ui.graphics.Color
import org.pixelrefine.genericui.theme.GenericTheme

/**
 * Varian warna — padanan 1:1 dari string `variant="..."` di GenericUILibrary PySide6.
 */
enum class Variant {
    Primary,
    Secondary,
    Success,
    Danger,
    Warning,
    Info,
    Light,
    Dark,
    Ghost,
    Outline;

    companion object {
        fun fromString(value: String): Variant = when (value.trim().lowercase()) {
            "primary" -> Primary
            "secondary" -> Secondary
            "success" -> Success
            "danger" -> Danger
            "warning" -> Warning
            "info" -> Info
            "light" -> Light
            "dark" -> Dark
            "ghost" -> Ghost
            "outline" -> Outline
            else -> Secondary
        }
    }
}

/** Helper string toVariant() ala Python */
fun String.toVariant(): Variant = Variant.fromString(this)

/** Setara `theme.get_variant_color(variant)` di Python */
fun variantColor(theme: GenericTheme, variant: Variant): Color = when (variant) {
    Variant.Primary -> theme.primary
    Variant.Secondary -> theme.secondary
    Variant.Success -> theme.success
    Variant.Danger -> theme.danger
    Variant.Warning -> theme.warning
    Variant.Info -> theme.info
    Variant.Light -> theme.light
    Variant.Dark -> theme.dark
    Variant.Ghost -> Color.Transparent
    Variant.Outline -> Color.Transparent
}

/** Setara `theme.get_variant_hover_color(variant)` di Python */
fun variantHoverColor(theme: GenericTheme, variant: Variant): Color = when (variant) {
    Variant.Primary -> theme.primaryHover
    Variant.Secondary -> theme.secondaryHover
    Variant.Success -> theme.successHover
    Variant.Danger -> theme.dangerHover
    Variant.Warning -> theme.warningHover
    Variant.Info -> theme.infoHover
    Variant.Light -> theme.hoverOverlay
    Variant.Dark -> theme.bgDark
    Variant.Ghost -> theme.hoverOverlay
    Variant.Outline -> theme.hoverOverlay
}
