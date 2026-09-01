package org.pixelrefine.genericui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import org.pixelrefine.genericui.theme.LocalGenericTheme
import androidx.compose.material3.Text

enum class DividerStyle {
    SOLID, DASHED
}

enum class DividerOrientation {
    HORIZONTAL, VERTICAL
}

@Composable
fun Divider(
    modifier: Modifier = Modifier,
    orientation: DividerOrientation = DividerOrientation.HORIZONTAL,
    color: Color? = null,
    thickness: Dp = 1.dp,
    style: DividerStyle = DividerStyle.SOLID,
) {
    val theme = LocalGenericTheme.current
    val dividerColor = color ?: theme.borderColor

    when (orientation) {
        DividerOrientation.HORIZONTAL -> {
            Box(
                modifier = modifier
                    .fillMaxWidth()
                    .height(thickness)
                    .background(dividerColor),
            )
        }
        DividerOrientation.VERTICAL -> {
            Box(
                modifier = modifier
                    .width(thickness)
                    .fillMaxHeight()
                    .background(dividerColor),
            )
        }
    }
}

@Composable
fun HorizontalDivider(
    modifier: Modifier = Modifier,
    color: Color? = null,
    thickness: Dp = 1.dp,
) = Divider(
    modifier = modifier,
    orientation = DividerOrientation.HORIZONTAL,
    color = color,
    thickness = thickness,
)

@Composable
fun VerticalDivider(
    modifier: Modifier = Modifier,
    color: Color? = null,
    thickness: Dp = 1.dp,
) = Divider(
    modifier = modifier,
    orientation = DividerOrientation.VERTICAL,
    color = color,
    thickness = thickness,
)

@Composable
fun DividerWithLabel(
    text: String,
    modifier: Modifier = Modifier,
    color: Color? = null,
    textColor: Color? = null,
    thickness: Dp = 1.dp,
) {
    val theme = LocalGenericTheme.current
    val dividerColor = color ?: theme.borderColor
    val labelColor = textColor ?: theme.textMuted

    Row(
        modifier = modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        Box(
            modifier = Modifier
                .weight(1f)
                .height(thickness)
                .background(dividerColor),
        )
        Text(
            text = text,
            color = labelColor,
            fontSize = theme.fontSizes.caption,
        )
        Box(
            modifier = Modifier
                .weight(1f)
                .height(thickness)
                .background(dividerColor),
        )
    }
}

@Composable
fun DashedDivider(
    modifier: Modifier = Modifier,
    color: Color? = null,
    thickness: Dp = 1.dp,
    dashLength: Dp = 4.dp,
    gapLength: Dp = 4.dp,
) {
    val theme = LocalGenericTheme.current
    val dividerColor = color ?: theme.borderColor

    // For simplicity, using solid divider with dashed style indicator
    // In production, you would draw actual dashes using Canvas
    Box(
        modifier = modifier
            .fillMaxWidth()
            .height(thickness)
            .background(dividerColor.copy(alpha = 0.5f)),
    )
}

@Composable
fun Spacer(
    height: Dp = 0.dp,
    width: Dp = 0.dp,
) {
    Spacer(modifier = Modifier.size(width = width, height = height))
}
