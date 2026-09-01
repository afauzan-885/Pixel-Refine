package org.pixelrefine.genericui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.input.key.Key
import androidx.compose.ui.input.key.KeyEventType
import androidx.compose.ui.input.key.isCtrlPressed
import androidx.compose.ui.input.key.isMetaPressed
import androidx.compose.ui.input.key.isShiftPressed
import androidx.compose.ui.input.key.key
import androidx.compose.ui.input.key.onPreviewKeyEvent
import androidx.compose.ui.input.key.type
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.theme.LocalGenericTheme

data class KeyboardShortcut(
    val key: Key,
    val ctrl: Boolean = false,
    val shift: Boolean = false,
    val alt: Boolean = false,
    val meta: Boolean = false,
    val description: String = "",
    val action: () -> Unit,
)

@Composable
fun Modifier.keyboardShortcuts(
    shortcuts: List<KeyboardShortcut>,
): Modifier {
    return this.onPreviewKeyEvent { event ->
        if (event.type == KeyEventType.KeyDown) {
            val matchedShortcut = shortcuts.find { shortcut ->
                shortcut.key == event.key &&
                    shortcut.ctrl == event.isCtrlPressed &&
                    shortcut.shift == event.isShiftPressed &&
                    shortcut.meta == event.isMetaPressed
            }
            matchedShortcut?.let {
                it.action()
                true
            } ?: false
        } else {
            false
        }
    }
}

object ShortcutKeys {
    val CTRL_C = KeyboardShortcut(
        key = Key.C,
        ctrl = true,
        description = "Copy",
        action = {},
    )

    val CTRL_V = KeyboardShortcut(
        key = Key.V,
        ctrl = true,
        description = "Paste",
        action = {},
    )

    val CTRL_X = KeyboardShortcut(
        key = Key.X,
        ctrl = true,
        description = "Cut",
        action = {},
    )

    val CTRL_Z = KeyboardShortcut(
        key = Key.Z,
        ctrl = true,
        description = "Undo",
        action = {},
    )

    val CTRL_Y = KeyboardShortcut(
        key = Key.Y,
        ctrl = true,
        description = "Redo",
        action = {},
    )

    val CTRL_S = KeyboardShortcut(
        key = Key.S,
        ctrl = true,
        description = "Save",
        action = {},
    )

    val ESC = KeyboardShortcut(
        key = Key.Escape,
        description = "Cancel/Close",
        action = {},
    )

    val ENTER = KeyboardShortcut(
        key = Key.Enter,
        description = "Confirm/Submit",
        action = {},
    )
}

@Composable
fun ShortcutDisplay(shortcut: KeyboardShortcut, modifier: Modifier = Modifier) {
    Row(
        modifier = modifier,
        horizontalArrangement = Arrangement.spacedBy(4.dp),
    ) {
        if (shortcut.ctrl) KeyBadge("Ctrl")
        if (shortcut.shift) KeyBadge("Shift")
        if (shortcut.alt) KeyBadge("Alt")
        if (shortcut.meta) KeyBadge("Meta")
        KeyBadge(shortcut.key.toString().take(1))
    }
}

@Composable
private fun KeyBadge(label: String) {
    val theme = LocalGenericTheme.current
    Box(
        modifier = Modifier
            .clip(RoundedCornerShape(3.dp))
            .background(theme.bgSecondary)
            .border(1.dp, theme.borderColor, RoundedCornerShape(3.dp))
            .padding(horizontal = 4.dp, vertical = 2.dp),
    ) {
        Text(
            text = label,
            color = theme.textPrimary,
            fontSize = 10.sp,
        )
    }
}
