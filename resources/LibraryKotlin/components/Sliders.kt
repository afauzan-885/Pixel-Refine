package org.pixelrefine.genericui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.gestures.detectDragGestures
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.theme.LocalGenericTheme

/**
 * Dual-Thumb Range Slider untuk Min-Max Filter (Gaya Klasik Konsisten).
 *
 * Mendukung drag gesture pada kedua thumb, tap pada track untuk jump,
 * dan keyboard-friendly clamping.
 */
@Composable
fun RangeSlider(
    minVal: Float = 0f,
    maxVal: Float = 100f,
    currentRange: ClosedFloatingPointRange<Float> = 20f..80f,
    onRangeChange: (ClosedFloatingPointRange<Float>) -> Unit = {},
    title: String = "",
    variant: Variant = Variant.Primary,
    modifier: Modifier = Modifier,
) {
    val theme = LocalGenericTheme.current
    val color = variantColor(theme, variant)

    Column(
        modifier = modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(4.dp),
    ) {
        if (title.isNotEmpty()) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
            ) {
                Text(title, color = theme.textPrimary, fontSize = 11.sp, fontWeight = FontWeight.SemiBold)
                Text(
                    "${currentRange.start.toInt()} - ${currentRange.endInclusive.toInt()}",
                    color = theme.textSecondary,
                    fontSize = 11.sp,
                )
            }
        }

        BoxWithConstraints(
            modifier = Modifier
                .fillMaxWidth()
                .height(32.dp),
            contentAlignment = Alignment.CenterStart,
        ) {
            val totalWidth = constraints.maxWidth.toFloat()
            val span = (maxVal - minVal).coerceAtLeast(1f)
            val thumbSizePx = 16.dp.value * LocalDensity.current.density

            var startFrac by remember(currentRange) {
                mutableFloatStateOf(((currentRange.start - minVal) / span).coerceIn(0f, 1f))
            }
            var endFrac by remember(currentRange) {
                mutableFloatStateOf(((currentRange.endInclusive - minVal) / span).coerceIn(0f, 1f))
            }

            // Track yang bisa di-tap untuk jump
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(24.dp)
                    .pointerInput(Unit) {
                        detectTapGestures { offset ->
                            val tapFrac = (offset.x / totalWidth).coerceIn(0f, 1f)
                            val distToStart = kotlin.math.abs(tapFrac - startFrac)
                            val distToEnd = kotlin.math.abs(tapFrac - endFrac)
                            if (distToStart <= distToEnd) {
                                startFrac = tapFrac.coerceAtMost(endFrac - 0.01f)
                            } else {
                                endFrac = tapFrac.coerceAtLeast(startFrac + 0.01f)
                            }
                            onRangeChange(
                                (minVal + startFrac * span)..(minVal + endFrac * span)
                            )
                        }
                    },
            )

            // Background Track
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(4.dp)
                    .clip(RoundedCornerShape(2.dp))
                    .background(theme.bgSecondary),
            )

            // Active Track
            Box(
                modifier = Modifier
                    .offset(x = maxWidth * startFrac)
                    .fillMaxWidth(endFrac - startFrac)
                    .height(4.dp)
                    .clip(RoundedCornerShape(2.dp))
                    .background(color),
            )

            // Thumb Start (draggable)
            Box(
                modifier = Modifier
                    .offset(x = (maxWidth * startFrac) - 8.dp)
                    .size(16.dp)
                    .clip(CircleShape)
                    .background(theme.textWhite)
                    .border(2.dp, color, CircleShape)
                    .pointerInput(Unit) {
                        detectDragGestures { change, dragAmount ->
                            change.consume()
                            if (totalWidth > 0) {
                                val delta = dragAmount.x / totalWidth
                                startFrac = (startFrac + delta).coerceIn(0f, endFrac - 0.01f)
                                onRangeChange(
                                    (minVal + startFrac * span)..(minVal + endFrac * span)
                                )
                            }
                        }
                    },
            )

            // Thumb End (draggable)
            Box(
                modifier = Modifier
                    .offset(x = (maxWidth * endFrac) - 8.dp)
                    .size(16.dp)
                    .clip(CircleShape)
                    .background(theme.textWhite)
                    .border(2.dp, color, CircleShape)
                    .pointerInput(Unit) {
                        detectDragGestures { change, dragAmount ->
                            change.consume()
                            if (totalWidth > 0) {
                                val delta = dragAmount.x / totalWidth
                                endFrac = (endFrac + delta).coerceIn(startFrac + 0.01f, 1f)
                                onRangeChange(
                                    (minVal + startFrac * span)..(minVal + endFrac * span)
                                )
                            }
                        }
                    },
            )
        }
    }
}
