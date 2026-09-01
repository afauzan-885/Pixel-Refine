package org.pixelrefine.genericui.components

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.gestures.detectDragGestures
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.theme.LocalGenericTheme
import androidx.compose.material3.Text
import androidx.compose.foundation.gestures.detectTransformGestures

@Composable
fun ColorPicker(
    selectedColor: Color,
    onColorChange: (Color) -> Unit,
    modifier: Modifier = Modifier,
    showAlpha: Boolean = true,
    presetColors: List<Color> = listOf(
        Color(0xFFE74C3C), Color(0xFFE67E22), Color(0xFFF1C40F), Color(0xFF2ECC71),
        Color(0xFF1ABC9C), Color(0xFF3498DB), Color(0xFF9B59B6), Color(0xFF333333),
        Color(0xFFFFFFFF), Color(0xFF95A5A6), Color(0xFFE8EDF2), Color(0xFF000000),
    ),
) {
    val theme = LocalGenericTheme.current
    var hue by remember { mutableFloatStateOf(0f) }
    var saturation by remember { mutableFloatStateOf(1f) }
    var value by remember { mutableFloatStateOf(1f) }
    var alpha by remember { mutableFloatStateOf(1f) }

    LaunchedEffect(selectedColor) {
        hue = getHue(selectedColor)
        saturation = getSaturation(selectedColor)
        value = getValue(selectedColor)
        alpha = selectedColor.alpha
    }

    val currentColor = Color.hsv(hue, saturation, value).copy(alpha = alpha)

    LaunchedEffect(currentColor) {
        onColorChange(currentColor)
    }

    Column(
        modifier = modifier
            .clip(RoundedCornerShape(8.dp))
            .background(theme.bgCard)
            .border(1.dp, theme.borderColor, RoundedCornerShape(8.dp))
            .padding(12.dp),
    ) {
        // Color preview
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(48.dp)
                .clip(RoundedCornerShape(4.dp))
                .background(currentColor)
                .border(1.dp, theme.borderColor, RoundedCornerShape(4.dp)),
        )

        Spacer(modifier = Modifier.height(8.dp))

        // Hue slider
        ColorSlider(
            value = hue,
            valueRange = 0f..360f,
            onValueChange = { hue = it },
            label = "Hue",
            brush = Brush.horizontalGradient(
                colors = listOf(
                    Color(0xFFFF0000), Color(0xFFFFFF00), Color(0xFF00FF00),
                    Color(0xFF00FFFF), Color(0xFF0000FF), Color(0xFFFF00FF),
                    Color(0xFFFF0000),
                )
            ),
        )

        Spacer(modifier = Modifier.height(8.dp))

        // Saturation slider
        ColorSlider(
            value = saturation,
            valueRange = 0f..1f,
            onValueChange = { saturation = it },
            label = "Saturation",
            brush = Brush.horizontalGradient(
                colors = listOf(
                    Color.hsv(hue, 0f, value),
                    Color.hsv(hue, 1f, value),
                )
            ),
        )

        Spacer(modifier = Modifier.height(8.dp))

        // Value slider
        ColorSlider(
            value = value,
            valueRange = 0f..1f,
            onValueChange = { value = it },
            label = "Value",
            brush = Brush.horizontalGradient(
                colors = listOf(
                    Color.Black,
                    Color.hsv(hue, saturation, 1f),
                )
            ),
        )

        if (showAlpha) {
            Spacer(modifier = Modifier.height(8.dp))

            // Alpha slider
            ColorSlider(
                value = alpha,
                valueRange = 0f..1f,
                onValueChange = { alpha = it },
                label = "Alpha",
                brush = Brush.horizontalGradient(
                    colors = listOf(
                        Color.Transparent,
                        Color.hsv(hue, saturation, value),
                    )
                ),
            )
        }

        Spacer(modifier = Modifier.height(12.dp))

        // HEX value
        Text(
            text = "HEX: #${currentColor.toArgb().toString(16).uppercase().takeLast(8)}",
            color = theme.textPrimary,
            fontSize = 12.sp,
        )

        Spacer(modifier = Modifier.height(8.dp))

        // Preset colors
        if (presetColors.isNotEmpty()) {
            Text(
                text = "Presets",
                color = theme.textMuted,
                fontSize = 11.sp,
                modifier = Modifier.padding(bottom = 4.dp),
            )

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(4.dp),
            ) {
                presetColors.take(6).forEach { color ->
                    Box(
                        modifier = Modifier
                            .size(24.dp)
                            .clip(CircleShape)
                            .background(color)
                            .border(1.dp, theme.borderColor, CircleShape)
                            .pointerInput(color) {
                                detectTapGestures {
                                    hue = getHue(color)
                                    saturation = getSaturation(color)
                                    value = getValue(color)
                                    alpha = color.alpha
                                }
                            },
                    )
                }
            }

            Spacer(modifier = Modifier.height(4.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(4.dp),
            ) {
                presetColors.drop(6).take(6).forEach { color ->
                    Box(
                        modifier = Modifier
                            .size(24.dp)
                            .clip(CircleShape)
                            .background(color)
                            .border(1.dp, theme.borderColor, CircleShape)
                            .pointerInput(color) {
                                detectTapGestures {
                                    hue = getHue(color)
                                    saturation = getSaturation(color)
                                    value = getValue(color)
                                    alpha = color.alpha
                                }
                            },
                    )
                }
            }
        }
    }
}

@Composable
private fun ColorSlider(
    value: Float,
    valueRange: ClosedFloatingPointRange<Float>,
    onValueChange: (Float) -> Unit,
    label: String,
    brush: Brush,
) {
    val theme = LocalGenericTheme.current
    val fraction = ((value - valueRange.start) / (valueRange.endInclusive - valueRange.start)).coerceIn(0f, 1f)

    Column {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
        ) {
            Text(
                text = label,
                color = theme.textSecondary,
                fontSize = 11.sp,
            )
            Text(
                text = "${(value * if (valueRange.endInclusive > 10) 1 else 100).toInt()}${if (valueRange.endInclusive > 10) "°" else "%"}",
                color = theme.textMuted,
                fontSize = 11.sp,
            )
        }

        Spacer(modifier = Modifier.height(4.dp))

        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(16.dp)
                .clip(RoundedCornerShape(8.dp))
                .background(brush)
                .border(1.dp, theme.borderColor, RoundedCornerShape(8.dp))
                .pointerInput(Unit) {
                    detectDragGestures { change, _ ->
                        change.consume()
                        val newFraction = (change.position.x / size.width).coerceIn(0f, 1f)
                        val newValue = valueRange.start + newFraction * (valueRange.endInclusive - valueRange.start)
                        onValueChange(newValue)
                    }
                },
        ) {
            // Thumb indicator
            Box(
                modifier = Modifier
                    .offset(x = (fraction * 1f).let { (it * 100).toInt().dp }) // Approximate
                    .size(16.dp)
                    .background(Color.White, CircleShape)
                    .border(2.dp, theme.dark, CircleShape),
            )
        }
    }
}

private fun getHue(color: Color): Float {
    val r = color.red
    val g = color.green
    val b = color.blue
    val max = maxOf(r, g, b)
    val min = minOf(r, g, b)
    val delta = max - min
    return when {
        delta == 0f -> 0f
        max == r -> 60f * (((g - b) / delta) % 6)
        max == g -> 60f * (((b - r) / delta) + 2)
        else -> 60f * (((r - g) / delta) + 4)
    }
}

private fun getSaturation(color: Color): Float {
    val max = maxOf(color.red, color.green, color.blue)
    val min = minOf(color.red, color.green, color.blue)
    val delta = max - min
    return if (max == 0f) 0f else delta / max
}

private fun getValue(color: Color): Float {
    return maxOf(color.red, color.green, color.blue)
}
