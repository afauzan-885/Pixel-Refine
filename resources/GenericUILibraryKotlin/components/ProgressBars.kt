package org.pixelrefine.genericui.components

import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.theme.LocalGenericTheme

/**
 * Python: `ProgressBar(value=0, max=100, variant="primary", show_label=True)`
 */
@Composable
fun ProgressBar(
    value: Int = 0,
    maxValue: Int = 100,
    variant: Variant = Variant.Primary,
    showLabel: Boolean = true,
    modifier: Modifier = Modifier,
    height: Dp = 12.dp,
) {
    val theme = LocalGenericTheme.current
    val fraction = (value.toFloat() / maxValue.coerceAtLeast(1)).coerceIn(0f, 1f)
    val shape = RoundedCornerShape(height / 2)

    Row(
        modifier = modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        Box(
            modifier = Modifier
                .weight(1f)
                .height(height)
                .clip(shape)
                .background(theme.bgSecondary)
                .border(1.dp, theme.borderColor, shape),
        ) {
            Box(
                modifier = Modifier
                    .fillMaxHeight()
                    .fillMaxWidth(fraction)
                    .clip(shape)
                    .background(variantColor(theme, variant)),
            )
        }
        if (showLabel) {
            Text(
                text = "${(fraction * 100).toInt()}%",
                color = theme.textSecondary,
                fontWeight = FontWeight.Bold,
                fontSize = 11.sp,
            )
        }
    }
}

/** Overload string variant */
@Composable
fun ProgressBar(
    value: Int = 0,
    maxValue: Int = 100,
    variant: String,
    showLabel: Boolean = true,
    modifier: Modifier = Modifier,
    height: Dp = 12.dp,
) {
    ProgressBar(
        value = value,
        maxValue = maxValue,
        variant = Variant.fromString(variant),
        showLabel = showLabel,
        modifier = modifier,
        height = height,
    )
}

/**
 * Python: `CustomProgressBar()`
 */
@Composable
fun CustomProgressBar(
    value: Int = 0,
    maxValue: Int = 100,
    barColor: Color? = null,
    backgroundColor: Color? = null,
    showLabel: Boolean = true,
    height: Dp = 12.dp,
    modifier: Modifier = Modifier,
) {
    val theme = LocalGenericTheme.current
    val fraction = (value.toFloat() / maxValue.coerceAtLeast(1)).coerceIn(0f, 1f)
    val shape = RoundedCornerShape(height / 2)

    Row(
        modifier = modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        Box(
            modifier = Modifier
                .weight(1f)
                .height(height)
                .clip(shape)
                .background(backgroundColor ?: theme.bgSecondary)
                .border(1.dp, theme.borderColor, shape),
        ) {
            Box(
                modifier = Modifier
                    .fillMaxHeight()
                    .fillMaxWidth(fraction)
                    .clip(shape)
                    .background(barColor ?: theme.primary),
            )
        }
        if (showLabel) {
            Text(
                text = "${(fraction * 100).toInt()}%",
                color = theme.textSecondary,
                fontWeight = FontWeight.Bold,
                fontSize = 11.sp,
            )
        }
    }
}

/**
 * Python: `CircularProgressFallback()`
 */
@Composable
fun CircularProgressFallback(
    modifier: Modifier = Modifier,
    size: Dp = 28.dp,
    color: Color? = null,
) {
    val theme = LocalGenericTheme.current
    CircularProgressIndicator(
        modifier = modifier.size(size),
        color = color ?: theme.primary,
        strokeWidth = 3.dp,
    )
}

/**
 * Python: `IndeterminateProgress()`
 */
@Composable
fun IndeterminateProgress(
    modifier: Modifier = Modifier,
    height: Dp = 6.dp,
    variant: Variant = Variant.Primary,
) {
    val theme = LocalGenericTheme.current
    val shape = RoundedCornerShape(height / 2)
    val infiniteTransition = rememberInfiniteTransition()
    val offsetFraction by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(1200, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Restart,
        ),
    )

    Box(
        modifier = modifier
            .fillMaxWidth()
            .height(height)
            .clip(shape)
            .background(theme.bgSecondary),
    ) {
        Box(
            modifier = Modifier
                .fillMaxHeight()
                .fillMaxWidth(0.3f)
                .offset(x = (offsetFraction * 200).dp)
                .clip(shape)
                .background(variantColor(theme, variant)),
        )
    }
}

/**
 * Python: `ProgressGroup(title="", value=0)`
 */
@Composable
fun ProgressGroup(
    title: String,
    value: Int = 0,
    maxValue: Int = 100,
    variant: Variant = Variant.Primary,
    modifier: Modifier = Modifier,
) {
    val theme = LocalGenericTheme.current
    Column(
        modifier = modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(4.dp),
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
        ) {
            Text(title, color = theme.textPrimary, fontWeight = FontWeight.SemiBold, fontSize = 12.sp)
        }
        ProgressBar(value = value, maxValue = maxValue, variant = variant, showLabel = true)
    }
}
