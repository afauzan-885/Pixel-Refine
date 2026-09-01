package org.pixelrefine.genericui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableLongStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.TextUnit
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.theme.LocalGenericTheme

/**
 * Python: `Button(text="", variant="secondary", object_name=None, bg_color=None, text_color=None)`
 */
@Composable
fun Button(
    text: String = "",
    variant: Variant = Variant.Secondary,
    onClick: () -> Unit = {},
    modifier: Modifier = Modifier,
    height: Dp = 28.dp,
    fontSize: TextUnit = 11.sp,
    enabled: Boolean = true,
    bgColor: Color? = null,
    textColor: Color? = null,
    debounceMs: Long = 300L,
    isLoading: Boolean = false,
    loadingText: String = "Wait...",
    timeoutMs: Long = 10000L,
) {
    val theme = LocalGenericTheme.current
    var lastClickTime by remember { mutableLongStateOf(0L) }
    var internalLoading by remember { androidx.compose.runtime.mutableStateOf(false) }

    // Efek Timeout Recovery: Jika proses hang / macet melebihi timeoutMs, otomatis pulihkan tombol
    androidx.compose.runtime.LaunchedEffect(internalLoading) {
        if (internalLoading) {
            kotlinx.coroutines.delay(timeoutMs)
            internalLoading = false // Auto-reset agar tombol tidak terkunci selamanya jika terjadi hang/crash
        }
    }

    val isBusy = isLoading || internalLoading
    val isEffectivelyEnabled = enabled && !isBusy

    val debouncedOnClick = {
        val currentTime = System.currentTimeMillis()
        if (currentTime - lastClickTime >= debounceMs && isEffectivelyEnabled) {
            lastClickTime = currentTime
            internalLoading = true
            try {
                onClick()
                // Reset setelah onClick() selesai (untuk synchronous callback)
                internalLoading = false
            } catch (e: Throwable) {
                internalLoading = false // Langsung pulihkan jika ada synchronous crash
            }
        }
    }

    val effectiveBg = when {
        !isEffectivelyEnabled -> theme.textMuted.copy(alpha = 0.4f)
        bgColor != null -> bgColor
        variant == Variant.Outline || variant == Variant.Ghost -> Color.Transparent
        else -> variantColor(theme, variant)
    }

    val effectiveText = when {
        textColor != null -> textColor
        variant == Variant.Outline || variant == Variant.Ghost -> theme.primary
        variant in listOf(Variant.Primary, Variant.Success, Variant.Danger, Variant.Dark, Variant.Info) -> theme.textWhite
        else -> theme.textPrimary
    }

    val borderModifier = if (variant == Variant.Outline) {
        Modifier.border(1.5.dp, theme.primary, RoundedCornerShape(theme.radiusMd))
    } else Modifier

    val displayText = if (isBusy) loadingText else text

    Box(
        modifier = modifier
            .height(height)
            .clip(RoundedCornerShape(theme.radiusMd))
            .then(borderModifier)
            .background(effectiveBg)
            .clickable(enabled = isEffectivelyEnabled, onClick = debouncedOnClick)
            .padding(horizontal = 12.dp),
        contentAlignment = Alignment.Center,
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(6.dp),
        ) {
            if (isBusy) {
                Box(
                    modifier = Modifier
                        .size(10.dp)
                        .clip(CircleShape)
                        .background(effectiveText.copy(alpha = 0.8f)),
                )
            }
            Text(
                text = displayText,
                color = effectiveText,
                fontSize = fontSize,
                fontWeight = FontWeight.SemiBold,
            )
        }
    }
}

/** Overload dengan string variant ala Python ("primary", "danger", dll). */
@Composable
fun Button(
    text: String = "",
    variant: String,
    onClick: () -> Unit = {},
    modifier: Modifier = Modifier,
    height: Dp = 28.dp,
    fontSize: TextUnit = 11.sp,
    enabled: Boolean = true,
    bgColor: Color? = null,
    textColor: Color? = null,
) {
    Button(
        text = text,
        variant = Variant.fromString(variant),
        onClick = onClick,
        modifier = modifier,
        height = height,
        fontSize = fontSize,
        enabled = enabled,
        bgColor = bgColor,
        textColor = textColor,
    )
}

/**
 * Python: `IconButton(icon, text="", variant="secondary")`
 */
@Composable
fun IconButton(
    icon: String,
    text: String = "",
    variant: Variant = Variant.Secondary,
    onClick: () -> Unit = {},
    modifier: Modifier = Modifier,
    height: Dp = 28.dp,
    enabled: Boolean = true,
) {
    val displayText = if (text.isNotEmpty()) "$icon $text" else icon
    Button(
        text = displayText,
        variant = variant,
        onClick = onClick,
        modifier = modifier,
        height = height,
        enabled = enabled,
    )
}

/**
 * Python: `ToggleButton(text="", checked=False, variant="primary")`
 */
@Composable
fun ToggleButton(
    text: String = "",
    checked: Boolean = false,
    variant: Variant = Variant.Primary,
    onCheckedChange: (Boolean) -> Unit = {},
    modifier: Modifier = Modifier,
    height: Dp = 28.dp,
) {
    val effectiveVariant = if (checked) variant else Variant.Secondary
    Button(
        text = text,
        variant = effectiveVariant,
        onClick = { onCheckedChange(!checked) },
        modifier = modifier,
        height = height,
    )
}

/** Tombol kembali ◀ bulat */
@Composable
fun BackButton(
    onClick: () -> Unit = {},
    modifier: Modifier = Modifier,
) {
    val theme = LocalGenericTheme.current
    Box(
        modifier = modifier
            .size(32.dp)
            .clip(CircleShape)
            .background(theme.bgCard)
            .border(1.dp, theme.borderColor, CircleShape)
            .clickable(onClick = onClick),
        contentAlignment = Alignment.Center,
    ) {
        Text("◀", fontSize = 12.sp, color = theme.textPrimary)
    }
}

/**
 * Python: `ButtonGroup(options, active_index=0)`
 */
@Composable
fun ButtonGroup(
    options: List<String>,
    activeIndex: Int = 0,
    modifier: Modifier = Modifier,
    onSelect: (Int) -> Unit = {},
) {
    val theme = LocalGenericTheme.current
    Row(
        modifier = modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(theme.radiusLg))
            .background(theme.bgCard)
            .border(1.dp, theme.borderColor, RoundedCornerShape(theme.radiusLg))
            .padding(4.dp),
        horizontalArrangement = Arrangement.spacedBy(4.dp),
    ) {
        options.forEachIndexed { index, label ->
            val active = index == activeIndex
            Box(
                modifier = Modifier
                    .weight(1f)
                    .height(32.dp)
                    .clip(RoundedCornerShape(theme.radiusLg))
                    .background(if (active) theme.primary else Color.Transparent)
                    .clickable { onSelect(index) },
                contentAlignment = Alignment.Center,
            ) {
                Text(
                    text = label,
                    color = if (active) theme.textWhite else theme.textPrimary,
                    fontWeight = if (active) FontWeight.Bold else FontWeight.Normal,
                    fontSize = 10.sp,
                    maxLines = 1,
                )
            }
        }
    }
}
