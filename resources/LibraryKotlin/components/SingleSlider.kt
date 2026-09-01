package org.pixelrefine.genericui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.gestures.detectDragGestures
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.layout.onSizeChanged
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.IntSize
import androidx.compose.ui.unit.dp
import org.pixelrefine.genericui.theme.LocalGenericTheme
import androidx.compose.material3.Text
import androidx.compose.foundation.gestures.detectTransformGestures

@Composable
fun Slider(
    value: Float,
    onValueChange: (Float) -> Unit,
    modifier: Modifier = Modifier,
    minVal: Float = 0f,
    maxVal: Float = 1f,
    step: Float = 0f,
    enabled: Boolean = true,
    variant: Variant = Variant.Primary,
    thumbSize: Dp = 20.dp,
    trackHeight: Dp = 6.dp,
    title: String? = null,
    showValue: Boolean = false,
    valueFormatter: ((Float) -> String)? = null,
) {
    val theme = LocalGenericTheme.current
    val variantColor = variantColor(theme, variant)
    val trackColor = if (enabled) theme.borderColor else theme.borderColor.copy(alpha = 0.5f)
    val thumbColor = if (enabled) variantColor else variantColor.copy(alpha = 0.5f)

    var trackWidth by remember { mutableStateOf(0f) }
    val span = (maxVal - minVal).coerceAtLeast(1f)
    val fraction = ((value - minVal) / span).coerceIn(0f, 1f)

    Column(modifier = modifier) {
        if (title != null || showValue) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
            ) {
                if (title != null) {
                    Text(
                        text = title,
                        color = theme.textSecondary,
                        fontSize = theme.fontSizes.caption,
                    )
                }
                if (showValue) {
                    val displayValue = valueFormatter?.invoke(value) ?: "%.2f".format(value)
                    Text(
                        text = displayValue,
                        color = theme.textMuted,
                        fontSize = theme.fontSizes.caption,
                    )
                }
            }
            Spacer(modifier = Modifier.height(4.dp))
        }

        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(thumbSize)
                .onSizeChanged { trackWidth = it.width.toFloat() }
                .pointerInput(enabled, minVal, maxVal, fraction) {
                    if (!enabled) return@pointerInput
                    detectTapGestures { offset ->
                        val newFrac = (offset.x / trackWidth).coerceIn(0f, 1f)
                        var newValue = minVal + newFrac * span
                        if (step > 0f) {
                            newValue = (newValue / step).toInt() * step
                        }
                        newValue = newValue.coerceIn(minVal, maxVal)
                        onValueChange(newValue)
                    }
                }
                .pointerInput(enabled, minVal, maxVal, fraction) {
                    if (!enabled) return@pointerInput
                    detectDragGestures { change, dragAmount ->
                        change.consume()
                        val delta = dragAmount.x / trackWidth * span
                        var newValue = (value + delta).coerceIn(minVal, maxVal)
                        if (step > 0f) {
                            newValue = (newValue / step).toInt() * step
                        }
                        newValue = newValue.coerceIn(minVal, maxVal)
                        onValueChange(newValue)
                    }
                },
        ) {
            // Track background
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(trackHeight)
                    .align(androidx.compose.ui.Alignment.CenterStart)
                    .clip(CircleShape)
                    .background(trackColor),
            )

            // Active track
            Box(
                modifier = Modifier
                    .fillMaxWidth(fraction)
                    .height(trackHeight)
                    .align(androidx.compose.ui.Alignment.CenterStart)
                    .clip(CircleShape)
                    .background(thumbColor),
            )

            // Thumb
            Box(
                modifier = Modifier
                    .size(thumbSize)
                    .offset(x = with(LocalDensity.current) { (fraction * trackWidth - thumbSize.toPx() / 2).toDp() })
                    .clip(CircleShape)
                    .background(thumbColor),
            )
        }
    }
}

@Composable
fun IntSlider(
    value: Int,
    onValueChange: (Int) -> Unit,
    modifier: Modifier = Modifier,
    minVal: Int = 0,
    maxVal: Int = 100,
    step: Int = 1,
    enabled: Boolean = true,
    variant: Variant = Variant.Primary,
    thumbSize: Dp = 20.dp,
    trackHeight: Dp = 6.dp,
    title: String? = null,
    showValue: Boolean = false,
) {
    Slider(
        value = value.toFloat(),
        onValueChange = { onValueChange(it.toInt()) },
        modifier = modifier,
        minVal = minVal.toFloat(),
        maxVal = maxVal.toFloat(),
        step = step.toFloat(),
        enabled = enabled,
        variant = variant,
        thumbSize = thumbSize,
        trackHeight = trackHeight,
        title = title,
        showValue = showValue,
        valueFormatter = { "%.0f".format(it) },
    )
}

@Composable
fun PercentageSlider(
    value: Float,
    onValueChange: (Float) -> Unit,
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
    variant: Variant = Variant.Primary,
    thumbSize: Dp = 20.dp,
    trackHeight: Dp = 6.dp,
    title: String? = null,
) {
    Slider(
        value = value,
        onValueChange = { onValueChange(it.coerceIn(0f, 1f)) },
        modifier = modifier,
        minVal = 0f,
        maxVal = 1f,
        step = 0.01f,
        enabled = enabled,
        variant = variant,
        thumbSize = thumbSize,
        trackHeight = trackHeight,
        title = title,
        showValue = true,
        valueFormatter = { "%.0f%%".format(it * 100) },
    )
}
