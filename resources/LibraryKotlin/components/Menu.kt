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
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Popup
import androidx.compose.ui.window.PopupProperties
import org.pixelrefine.genericui.theme.LocalGenericTheme
import androidx.compose.material3.Text

data class MenuEntry(
    val id: String,
    val label: String,
    val icon: String? = null,
    val shortcut: String? = null,
    val disabled: Boolean = false,
    val isDivider: Boolean = false,
    val submenu: List<MenuEntry>? = null,
    val onClick: (() -> Unit)? = null,
)

@Composable
fun Menu(
    items: List<MenuEntry>,
    modifier: Modifier = Modifier,
    trigger: @Composable () -> Unit,
) {
    val theme = LocalGenericTheme.current
    var isOpen by remember { mutableStateOf(false) }

    Box(modifier = modifier) {
        Box(modifier = Modifier.clickable { isOpen = !isOpen }) {
            trigger()
        }

        if (isOpen) {
            Popup(
                alignment = Alignment.TopStart,
                properties = PopupProperties(focusable = true),
                onDismissRequest = { isOpen = false },
            ) {
                Column(
                    modifier = Modifier
                        .widthIn(min = 200.dp)
                        .clip(RoundedCornerShape(4.dp))
                        .background(theme.bgCard)
                        .border(1.dp, theme.borderColor, RoundedCornerShape(4.dp))
                        .padding(4.dp),
                ) {
                    items.forEach { item ->
                        if (item.isDivider) {
                            Box(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .height(1.dp)
                                    .background(theme.borderColor)
                                    .padding(vertical = 4.dp),
                            )
                        } else {
                            MenuItemView(
                                item = item,
                                onClick = {
                                    if (!item.disabled) {
                                        item.onClick?.invoke()
                                        if (item.submenu == null) {
                                            isOpen = false
                                        }
                                    }
                                },
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun MenuItemView(
    item: MenuEntry,
    onClick: () -> Unit,
) {
    val theme = LocalGenericTheme.current

    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(2.dp))
            .clickable(enabled = !item.disabled, onClick = onClick)
            .padding(horizontal = 8.dp, vertical = 6.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        if (item.icon != null) {
            Text(text = item.icon, fontSize = 14.sp)
        } else {
            Spacer(modifier = Modifier.width(14.sp.value.dp))
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

        if (item.submenu != null) {
            Text(
                text = "▶",
                color = theme.textMuted,
                fontSize = 10.sp,
            )
        }
    }
}

@Composable
fun DropdownMenu(
    items: List<MenuEntry>,
    isOpen: Boolean = false,
    onDismiss: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val theme = LocalGenericTheme.current

    if (isOpen) {
        Column(
            modifier = modifier
                .widthIn(min = 200.dp)
                .clip(RoundedCornerShape(4.dp))
                .background(theme.bgCard)
                .border(1.dp, theme.borderColor, RoundedCornerShape(4.dp))
                .padding(4.dp),
        ) {
            items.forEach { item ->
                if (item.isDivider) {
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(1.dp)
                            .background(theme.borderColor)
                            .padding(vertical = 4.dp),
                    )
                } else {
                    MenuItemView(
                        item = item,
                        onClick = {
                            if (!item.disabled) {
                                item.onClick?.invoke()
                                onDismiss()
                            }
                        },
                    )
                }
            }
        }
    }
}
