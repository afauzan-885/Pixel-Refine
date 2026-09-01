package org.pixelrefine.genericui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.theme.LocalGenericTheme
import androidx.compose.material3.Text
import androidx.compose.ui.graphics.Color
import androidx.compose.foundation.gestures.detectDragGestures
import androidx.compose.ui.input.pointer.pointerInput

@Composable
fun Rating(
    value: Float,
    onValueChange: ((Float) -> Unit)? = null,
    modifier: Modifier = Modifier,
    maxRating: Int = 5,
    allowHalf: Boolean = true,
    readOnly: Boolean = false,
    size: Dp = 24.dp,
    activeColor: androidx.compose.ui.graphics.Color? = null,
    inactiveColor: androidx.compose.ui.graphics.Color? = null,
) {
    val theme = LocalGenericTheme.current
    val active = activeColor ?: theme.warning
    val inactive = inactiveColor ?: theme.borderColor

    Row(
        modifier = modifier,
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(4.dp),
    ) {
        for (i in 1..maxRating) {
            val isFull = value >= i
            val isHalf = allowHalf && value >= i - 0.5f && value < i

            StarItem(
                isFull = isFull,
                isHalf = isHalf,
                activeColor = active,
                inactiveColor = inactive,
                size = size,
                enabled = !readOnly && onValueChange != null,
                onClick = { rating ->
                    onValueChange?.invoke(rating)
                },
                position = i,
            )
        }
    }
}

@Composable
private fun StarItem(
    isFull: Boolean,
    isHalf: Boolean,
    activeColor: androidx.compose.ui.graphics.Color,
    inactiveColor: androidx.compose.ui.graphics.Color,
    size: Dp,
    enabled: Boolean,
    onClick: (Float) -> Unit,
    position: Int,
) {
    val theme = LocalGenericTheme.current

    Box(
        modifier = Modifier
            .size(size)
            .clickable(enabled = enabled) { onClick(position.toFloat()) },
        contentAlignment = Alignment.Center,
    ) {
        Text(
            text = "★",
            color = if (isFull) activeColor else inactiveColor,
            fontSize = (size.value * 0.8f).sp,
        )

        if (isHalf) {
            Box(
                modifier = Modifier
                    .fillMaxHeight()
                    .fillMaxWidth(0.5f)
                    .background(theme.bgCard.copy(alpha = 0.001f)),
            )
        }
    }
}

@Composable
fun StarRating(
    value: Int,
    onValueChange: ((Int) -> Unit)? = null,
    modifier: Modifier = Modifier,
    maxRating: Int = 5,
    readOnly: Boolean = false,
) {
    Rating(
        value = value.toFloat(),
        onValueChange = { onValueChange?.invoke(it.toInt()) },
        modifier = modifier,
        maxRating = maxRating,
        allowHalf = false,
        readOnly = readOnly,
    )
}

@Composable
fun RatingDisplay(
    value: Float,
    modifier: Modifier = Modifier,
    maxRating: Int = 5,
    showValue: Boolean = true,
) {
    val theme = LocalGenericTheme.current

    Row(
        modifier = modifier,
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(4.dp),
    ) {
        Rating(value = value, readOnly = true, size = 16.dp)

        if (showValue) {
            Text(
                text = "${"%.1f".format(value)}/$maxRating",
                color = theme.textSecondary,
                fontSize = 12.sp,
            )
        }
    }
}
