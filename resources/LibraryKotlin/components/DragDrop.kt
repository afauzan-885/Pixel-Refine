package org.pixelrefine.genericui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.gestures.detectDragGesturesAfterLongPress
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.theme.LocalGenericTheme
import androidx.compose.material3.Text
import androidx.compose.foundation.gestures.detectTransformGestures

data class DraggableItem(
    val id: String,
    val content: @Composable () -> Unit,
)

@Composable
fun DragDropList(
    items: List<DraggableItem>,
    onReorder: (from: Int, to: Int) -> Unit,
    modifier: Modifier = Modifier,
    spacing: Dp = 8.dp,
) {
    val theme = LocalGenericTheme.current
    var draggedIndex by remember { mutableStateOf<Int?>(null) }
    var dragOffset by remember { mutableStateOf(Offset.Zero) }

    Column(
        modifier = modifier,
        verticalArrangement = Arrangement.spacedBy(spacing),
    ) {
        items.forEachIndexed { index, item ->
            val isDragging = draggedIndex == index

            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .graphicsLayer {
                        if (isDragging) {
                            translationY = dragOffset.y
                            shadowElevation = 8f
                            scaleX = 1.02f
                            scaleY = 1.02f
                        }
                    }
                    .background(
                        if (isDragging) theme.primary.copy(alpha = 0.1f) else Color.Transparent,
                        RoundedCornerShape(4.dp),
                    )
                    .pointerInput(item.id) {
                        detectDragGesturesAfterLongPress(
                            onDragStart = {
                                draggedIndex = index
                                dragOffset = Offset.Zero
                            },
                            onDrag = { change, dragAmount ->
                                change.consume()
                                dragOffset += dragAmount
                            },
                            onDragEnd = {
                                val from = draggedIndex
                                val to = index + if (dragOffset.y > 50) 1 else if (dragOffset.y < -50) -1 else 0
                                if (from != null && to in items.indices && to != from) {
                                    onReorder(from, to)
                                }
                                draggedIndex = null
                                dragOffset = Offset.Zero
                            },
                            onDragCancel = {
                                draggedIndex = null
                                dragOffset = Offset.Zero
                            },
                        )
                    },
            ) {
                item.content()
            }
        }
    }
}

@Composable
fun DropZone(
    onDrop: (String) -> Unit,
    modifier: Modifier = Modifier,
    label: String = "Drop here",
    enabled: Boolean = true,
    variant: Variant = Variant.Primary,
) {
    val theme = LocalGenericTheme.current
    val variantColor = variantColor(theme, variant)
    var isHovering by remember { mutableStateOf(false) }

    Box(
        modifier = modifier
            .fillMaxWidth()
            .height(100.dp)
            .clip(RoundedCornerShape(8.dp))
            .background(
                if (isHovering) variantColor.copy(alpha = 0.1f) else theme.bgCard,
            )
            .border(
                width = if (isHovering) 2.dp else 1.dp,
                color = if (isHovering) variantColor else theme.borderColor,
                shape = RoundedCornerShape(8.dp),
            )
            .pointerInput(enabled) {
                if (enabled) {
                    detectDragGesturesAfterLongPress(
                        onDragStart = { isHovering = true },
                        onDrag = { _, _ -> },
                        onDragEnd = { isHovering = false },
                        onDragCancel = { isHovering = false },
                    )
                }
            },
        contentAlignment = Alignment.Center,
    ) {
        Text(
            text = label,
            color = if (isHovering) variantColor else theme.textMuted,
            fontSize = 14.sp,
            fontWeight = if (isHovering) FontWeight.SemiBold else FontWeight.Normal,
        )
    }
}
