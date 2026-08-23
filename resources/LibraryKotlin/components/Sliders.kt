package org.pixelrefine.genericui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.gestures.detectDragGestures
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
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.theme.LocalGenericTheme

/**
 * Dual-Thumb Range Slider untuk Min-Max Filter (Gaya Klasik Konsisten).
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
                .height(24.dp),
            contentAlignment = Alignment.CenterStart,
        ) {
            val totalWidth = constraints.maxWidth.toFloat()
            val span = (maxVal - minVal).coerceAtLeast(1f)

            val startFrac = ((currentRange.start - minVal) / span).coerceIn(0f, 1f)
            val endFrac = ((currentRange.endInclusive - minVal) / span).coerceIn(0f, 1f)

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

            // Thumb Start
            Box(
                modifier = Modifier
                    .offset(x = (maxWidth * startFrac) - 8.dp)
                    .size(16.dp)
                    .clip(CircleShape)
                    .background(theme.textWhite)
                    .border(2.dp, color, CircleShape),
            )

            // Thumb End
            Box(
                modifier = Modifier
                    .offset(x = (maxWidth * endFrac) - 8.dp)
                    .size(16.dp)
                    .clip(CircleShape)
                    .background(theme.textWhite)
                    .border(2.dp, color, CircleShape),
            )
        }
    }
}
