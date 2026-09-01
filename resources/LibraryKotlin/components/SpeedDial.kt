package org.pixelrefine.genericui.components

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.scaleIn
import androidx.compose.animation.scaleOut
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.theme.LocalGenericTheme
import androidx.compose.material3.Text

data class SpeedDialAction(
    val icon: String,
    val label: String,
    val onClick: () -> Unit,
    val variant: Variant = Variant.Primary,
)

enum class SpeedDialDirection {
    Up, Down, Left, Right
}

@Composable
fun SpeedDial(
    mainIcon: String = "+",
    actions: List<SpeedDialAction>,
    modifier: Modifier = Modifier,
    direction: SpeedDialDirection = SpeedDialDirection.Up,
    position: FloatButtonPosition = FloatButtonPosition.BottomRight,
    variant: Variant = Variant.Primary,
) {
    val theme = LocalGenericTheme.current
    val variantColor = variantColor(theme, variant)
    var isExpanded by remember { mutableStateOf(false) }

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
        Column(
            horizontalAlignment = Alignment.End,
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            if (direction == SpeedDialDirection.Up) {
                // Actions appear above main button
                actions.forEachIndexed { index, action ->
                    SpeedDialActionItem(
                        action = action,
                        isVisible = isExpanded,
                        delayMs = index * 50,
                        showLabel = true,
                    )
                }
            }

            // Main FAB
            Box(
                modifier = Modifier
                    .size(56.dp)
                    .clip(CircleShape)
                    .background(variantColor)
                    .clickable { isExpanded = !isExpanded },
                contentAlignment = Alignment.Center,
            ) {
                Text(
                    text = if (isExpanded) "×" else mainIcon,
                    color = theme.light,
                    fontSize = 24.sp,
                    fontWeight = FontWeight.Bold,
                )
            }

            if (direction == SpeedDialDirection.Down) {
                actions.forEachIndexed { index, action ->
                    SpeedDialActionItem(
                        action = action,
                        isVisible = isExpanded,
                        delayMs = index * 50,
                        showLabel = true,
                    )
                }
            }
        }
    }
}

@Composable
private fun SpeedDialActionItem(
    action: SpeedDialAction,
    isVisible: Boolean,
    delayMs: Int,
    showLabel: Boolean,
) {
    val theme = LocalGenericTheme.current
    val variantColor = variantColor(theme, action.variant)

    AnimatedVisibility(
        visible = isVisible,
        enter = scaleIn(animationSpec = tween(durationMillis = 200, delayMillis = delayMs)) + fadeIn(),
        exit = scaleOut(animationSpec = tween(durationMillis = 150)) + fadeOut(),
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            if (showLabel) {
                Text(
                    text = action.label,
                    color = theme.textPrimary,
                    fontSize = 12.sp,
                    modifier = Modifier
                        .clip(androidx.compose.foundation.shape.RoundedCornerShape(4.dp))
                        .background(theme.bgCard)
                        .padding(horizontal = 8.dp, vertical = 4.dp),
                )
            }

            Box(
                modifier = Modifier
                    .size(40.dp)
                    .clip(CircleShape)
                    .background(variantColor)
                    .clickable {
                        action.onClick()
                    },
                contentAlignment = Alignment.Center,
            ) {
                Text(
                    text = action.icon,
                    color = theme.light,
                    fontSize = 16.sp,
                )
            }
        }
    }
}
