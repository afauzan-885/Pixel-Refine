package org.pixelrefine.genericui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.theme.LocalGenericTheme
import androidx.compose.material3.Text

enum class FloatButtonPosition {
    BottomRight, BottomLeft, TopRight, TopLeft, BottomCenter
}

@Composable
fun FloatButton(
    icon: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    label: String? = null,
    variant: Variant = Variant.Primary,
    size: Dp = 56.dp,
    position: FloatButtonPosition = FloatButtonPosition.BottomRight,
    extended: Boolean = false,
    offsetX: Dp = 16.dp,
    offsetY: Dp = 16.dp,
) {
    val theme = LocalGenericTheme.current
    val variantColor = variantColor(theme, variant)

    val alignment = when (position) {
        FloatButtonPosition.BottomRight -> Alignment.BottomEnd
        FloatButtonPosition.BottomLeft -> Alignment.BottomStart
        FloatButtonPosition.TopRight -> Alignment.TopEnd
        FloatButtonPosition.TopLeft -> Alignment.TopStart
        FloatButtonPosition.BottomCenter -> Alignment.BottomCenter
    }

    Box(
        modifier = modifier.fillMaxSize(),
        contentAlignment = alignment,
    ) {
        Box(
            modifier = Modifier
                .padding(end = if (position == FloatButtonPosition.BottomRight || position == FloatButtonPosition.TopRight) offsetX else 0.dp)
                .padding(start = if (position == FloatButtonPosition.BottomLeft || position == FloatButtonPosition.TopLeft) offsetX else 0.dp)
                .padding(bottom = if (position.toString().startsWith("Bottom")) offsetY else 0.dp)
                .padding(top = if (position.toString().startsWith("Top")) offsetY else 0.dp)
                .then(
                    if (extended && label != null) {
                        Modifier.height(48.dp)
                    } else {
                        Modifier.size(size)
                    }
                )
                .clip(
                    if (extended && label != null) RoundedCornerShape(24.dp) else CircleShape
                )
                .background(variantColor)
                .clickable { onClick() }
                .padding(horizontal = if (extended) 16.dp else 0.dp),
            contentAlignment = Alignment.Center,
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                Text(
                    text = icon,
                    color = theme.light,
                    fontSize = if (size.value <= 40) 16.sp else 24.sp,
                )
                if (extended && label != null) {
                    Text(
                        text = label,
                        color = theme.light,
                        fontSize = 14.sp,
                        fontWeight = FontWeight.SemiBold,
                    )
                }
            }
        }
    }
}

@Composable
fun MiniFloatButton(
    icon: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    variant: Variant = Variant.Primary,
) {
    val theme = LocalGenericTheme.current
    val variantColor = variantColor(theme, variant)

    Box(
        modifier = modifier
            .size(40.dp)
            .clip(CircleShape)
            .background(variantColor)
            .clickable { onClick() },
        contentAlignment = Alignment.Center,
    ) {
        Text(
            text = icon,
            color = theme.light,
            fontSize = 16.sp,
        )
    }
}
