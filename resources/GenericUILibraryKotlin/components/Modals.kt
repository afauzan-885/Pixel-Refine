package org.pixelrefine.genericui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import org.pixelrefine.genericui.theme.LocalGenericTheme

/**
 * Python: `Modal(title="", visible=False)`
 */
@Composable
fun Modal(
    visible: Boolean,
    onDismissRequest: () -> Unit = {},
    title: String = "",
    modifier: Modifier = Modifier,
    content: @Composable ColumnScope.() -> Unit,
) {
    if (!visible) return
    val theme = LocalGenericTheme.current

    Dialog(
        onDismissRequest = onDismissRequest,
        properties = DialogProperties(usePlatformDefaultWidth = false),
    ) {
        Column(
            modifier = modifier
                .widthIn(min = 280.dp, max = 450.dp)
                .clip(RoundedCornerShape(theme.radiusLg))
                .background(theme.bgCard)
                .border(1.dp, theme.borderColor, RoundedCornerShape(theme.radiusLg))
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            if (title.isNotEmpty()) {
                Text(title, color = theme.textPrimary, fontWeight = FontWeight.Bold, fontSize = 16.sp)
            }
            content()
        }
    }
}

/** Python: `ModalHeader(title="")` */
@Composable
fun ModalHeader(
    title: String,
    modifier: Modifier = Modifier,
) {
    val theme = LocalGenericTheme.current
    Text(title, color = theme.textPrimary, fontWeight = FontWeight.Bold, fontSize = 16.sp, modifier = modifier)
}

/** Python: `ModalBody()` */
@Composable
fun ModalBody(
    modifier: Modifier = Modifier,
    content: @Composable ColumnScope.() -> Unit,
) {
    Column(modifier = modifier.fillMaxWidth(), content = content)
}

/** Python: `ModalFooter()` */
@Composable
fun ModalFooter(
    modifier: Modifier = Modifier,
    content: @Composable androidx.compose.foundation.layout.RowScope.() -> Unit,
) {
    Row(
        modifier = modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.End,
        verticalAlignment = Alignment.CenterVertically,
        content = content,
    )
}

/**
 * Python: `ModalDialog(title="", message="", visible=False)`
 */
@Composable
fun ModalDialog(
    visible: Boolean,
    title: String = "Dialog",
    message: String = "",
    confirmText: String = "OK",
    cancelText: String = "Cancel",
    onConfirm: () -> Unit = {},
    onCancel: () -> Unit = {},
    onDismissRequest: () -> Unit = onCancel,
) {
    val theme = LocalGenericTheme.current
    Modal(visible = visible, onDismissRequest = onDismissRequest, title = title) {
        if (message.isNotEmpty()) {
            Text(message, color = theme.textSecondary, fontSize = 13.sp)
        }
        Row(
            modifier = Modifier.fillMaxWidth().padding(top = 8.dp),
            horizontalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            Box(Modifier.weight(1f)) {
                Button(text = cancelText, variant = Variant.Secondary, onClick = onCancel)
            }
            Box(Modifier.weight(1f)) {
                Button(text = confirmText, variant = Variant.Primary, onClick = onConfirm)
            }
        }
    }
}

/** Python: `ModalConfirm` & `modal_confirm` alias */
@Composable
fun ModalConfirm(
    visible: Boolean,
    title: String = "Confirm",
    message: String = "Are you sure?",
    onConfirm: () -> Unit = {},
    onCancel: () -> Unit = {},
) {
    ModalDialog(
        visible = visible,
        title = title,
        message = message,
        confirmText = "Confirm",
        cancelText = "Cancel",
        onConfirm = onConfirm,
        onCancel = onCancel,
    )
}

@Composable
fun modal_confirm(
    visible: Boolean,
    title: String = "Confirm",
    message: String = "Are you sure?",
    onConfirm: () -> Unit = {},
    onCancel: () -> Unit = {},
) = ModalConfirm(visible, title, message, onConfirm, onCancel)

/**
 * Python: `AlertModal(title="Alert", message="", variant="warning")`
 */
@Composable
fun AlertModal(
    visible: Boolean,
    title: String = "Alert",
    message: String = "",
    variant: Variant = Variant.Warning,
    onDismiss: () -> Unit = {},
) {
    val theme = LocalGenericTheme.current
    Modal(visible = visible, onDismissRequest = onDismiss, title = title) {
        Text(message, color = theme.textPrimary, fontSize = 13.sp)
        Button(
            text = "OK",
            variant = variant,
            onClick = onDismiss,
            modifier = Modifier.fillMaxWidth().padding(top = 8.dp),
        )
    }
}

/**
 * Python: `ProgressModal(title="", message="", progress=0)`
 */
@Composable
fun ProgressModal(
    visible: Boolean,
    title: String = "Processing...",
    message: String = "",
    progress: Int = 0,
    maxProgress: Int = 100,
    onCancel: (() -> Unit)? = null,
) {
    val theme = LocalGenericTheme.current
    Modal(visible = visible, onDismissRequest = { onCancel?.invoke() }, title = title) {
        if (message.isNotEmpty()) {
            Text(message, color = theme.textSecondary, fontSize = 12.sp)
        }
        ProgressBar(value = progress, maxValue = maxProgress)
        if (onCancel != null) {
            Button(
                text = "Cancel",
                variant = Variant.Secondary,
                onClick = onCancel,
                modifier = Modifier.fillMaxWidth().padding(top = 4.dp),
            )
        }
    }
}
