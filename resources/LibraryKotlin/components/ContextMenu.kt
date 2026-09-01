package org.pixelrefine.genericui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.input.pointer.PointerEventType
import androidx.compose.ui.input.pointer.onPointerEvent
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Popup
import androidx.compose.ui.window.PopupProperties
import org.pixelrefine.genericui.theme.LocalGenericTheme
import androidx.compose.material3.Text
import androidx.compose.foundation.ExperimentalFoundationApi

data class ContextMenuItem(
    val id: String,
    val label: String,
    val icon: String? = null,
    val shortcut: String? = null,
    val disabled: Boolean = false,
    val onClick: () -> Unit,
)

@OptIn(ExperimentalFoundationApi::class)
@Suppress("OPT_IN_USAGE")
@Composable
fun ContextMenu(
    items: List<ContextMenuItem>,
    modifier: Modifier = Modifier,
    trigger: @Composable () -> Unit,
) {
    val theme = LocalGenericTheme.current
    var isOpen by remember { mutableStateOf(false) }
    var triggerPosition by remember { mutableStateOf(androidx.compose.ui.unit.IntOffset.Zero) }

    Box(
        modifier = modifier
            .clickable { isOpen = true },
    ) {
        trigger()

        if (isOpen) {
            Popup(
                alignment = Alignment.TopStart,
                offset = triggerPosition,
                properties = PopupProperties(focusable = true),
                onDismissRequest = { isOpen = false },
            ) {
                Column(
                    modifier = Modifier
                        .widthIn(min = 180.dp)
                        .clip(RoundedCornerShape(4.dp))
                        .background(theme.bgCard)
                        .border(1.dp, theme.borderColor, RoundedCornerShape(4.dp))
                        .padding(4.dp),
                ) {
                    items.forEach { item ->
                        ContextMenuItemView(
                            item = item,
                            onClick = {
                                if (!item.disabled) {
                                    item.onClick()
                                    isOpen = false
                                }
                            },
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun ContextMenuItemView(
    item: ContextMenuItem,
    onClick: () -> Unit,
) {
    val theme = LocalGenericTheme.current

    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(2.dp))
            .background(Color.Transparent)
            .clickable(enabled = !item.disabled, onClick = onClick)
            .padding(horizontal = 8.dp, vertical = 6.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        if (item.icon != null) {
            Text(
                text = item.icon,
                fontSize = 14.sp,
            )
        }

        Text(
            text = item.label,
            color = if (item.disabled) theme.textMuted else theme.textPrimary,
            fontSize = 13.sp,
            modifier = Modifier.weight(1f),
        )

        if (item.shortcut != null) {
            Text(
                text = item.shortcut,
                color = theme.textMuted,
                fontSize = 11.sp,
            )
        }
    }
}
