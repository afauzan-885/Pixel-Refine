package org.pixelrefine.genericui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.RowScope
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import org.pixelrefine.genericui.domain.state.ProcessingState
import org.pixelrefine.genericui.domain.state.WorkflowStateManager
import org.pixelrefine.genericui.theme.LocalGenericTheme

/**
 * Python: `Modal(title, ...)`
 */
@Composable
fun Modal(
    visible: Boolean,
    title: String,
    onDismissRequest: () -> Unit,
    modifier: Modifier = Modifier,
    width: Dp = 420.dp,
    content: @Composable () -> Unit,
) {
    if (!visible) return

    val theme = LocalGenericTheme.current
    Dialog(
        onDismissRequest = onDismissRequest,
        properties = DialogProperties(usePlatformDefaultWidth = false),
    ) {
        Box(
            modifier = Modifier
                .widthIn(max = width)
                .fillMaxWidth(0.9f)
                .clip(RoundedCornerShape(theme.radiusLg))
                .background(theme.bgCard)
                .border(1.dp, theme.borderColor, RoundedCornerShape(theme.radiusLg))
                .padding(16.dp),
        ) {
            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                if (title.isNotEmpty()) {
                    ModalHeader(title = title, onClose = onDismissRequest)
                }
                content()
            }
        }
    }
}

/**
 * Header modal dengan judul dan tombol tutup
 */
@Composable
fun ModalHeader(
    title: String,
    onClose: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val theme = LocalGenericTheme.current
    Row(
        modifier = modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(
            text = title,
            color = theme.textPrimary,
            fontWeight = FontWeight.Bold,
            fontSize = 15.sp,
        )
        Text(
            text = "✕",
            color = theme.textMuted,
            fontSize = 14.sp,
            fontWeight = FontWeight.Bold,
            modifier = Modifier.clickable { onClose() },
        )
    }
}

/**
 * Body modal untuk konten utama
 */
@Composable
fun ModalBody(
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit,
) {
    Box(modifier = modifier.fillMaxWidth()) {
        content()
    }
}

/**
 * Footer modal untuk tombol aksi
 */
@Composable
fun ModalFooter(
    modifier: Modifier = Modifier,
    content: @Composable RowScope.() -> Unit,
) {
    Row(
        modifier = modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.spacedBy(8.dp, Alignment.End),
        verticalAlignment = Alignment.CenterVertically,
        content = content,
    )
}

/**
 * Python: `ModalDialog()`
 */
@Composable
fun ModalDialog(
    visible: Boolean,
    title: String,
    onDismissRequest: () -> Unit,
    onConfirm: () -> Unit = {},
    confirmText: String = "OK",
    cancelText: String = "Cancel",
    confirmVariant: Variant = Variant.Primary,
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit,
) {
    Modal(
        visible = visible,
        title = title,
        onDismissRequest = onDismissRequest,
        modifier = modifier,
    ) {
        ModalBody { content() }
        ModalFooter {
            Button(text = cancelText, variant = Variant.Ghost, onClick = onDismissRequest)
            Button(text = confirmText, variant = confirmVariant, onClick = onConfirm)
        }
    }
}

/**
 * Python: `ModalConfirm(title, message, ...)`
 */
@Composable
fun ModalConfirm(
    visible: Boolean,
    title: String = "Confirmation",
    message: String = "Are you sure?",
    onConfirm: () -> Unit = {},
    onCancel: () -> Unit = {},
    confirmText: String = "Yes",
    cancelText: String = "No",
    confirmVariant: Variant = Variant.Danger,
) {
    val theme = LocalGenericTheme.current
    ModalDialog(
        visible = visible,
        title = title,
        onDismissRequest = onCancel,
        onConfirm = onConfirm,
        confirmText = confirmText,
        cancelText = cancelText,
        confirmVariant = confirmVariant,
    ) {
        Text(text = message, color = theme.textPrimary, fontSize = 13.sp)
    }
}

/** Alias Python: `modal_confirm` */
@Composable
fun modal_confirm(
    visible: Boolean,
    title: String = "Confirmation",
    message: String = "Are you sure?",
    onConfirm: () -> Unit = {},
    onCancel: () -> Unit = {},
) = ModalConfirm(visible, title, message, onConfirm, onCancel)

/**
 * Python: `AlertModal()`
 */
@Composable
fun AlertModal(
    visible: Boolean,
    title: String = "Alert",
    message: String = "",
    onClose: () -> Unit = {},
    variant: Variant = Variant.Primary,
) {
    val theme = LocalGenericTheme.current
    Modal(visible = visible, title = title, onDismissRequest = onClose) {
        ModalBody {
            Text(text = message, color = theme.textPrimary, fontSize = 13.sp)
        }
        ModalFooter {
            Button(text = "OK", variant = variant, onClick = onClose)
        }
    }
}

/**
 * Python: `ProgressModal()`
 * Built-in deklaratif: otomatis mengikat `WorkflowStateManager`
 */
@Composable
fun ProgressModal(
    visible: Boolean,
    title: String = "Processing...",
    progress: Int = 0,
    maxProgress: Int = 100,
    statusText: String = "",
    workflow: WorkflowStateManager? = null,
    onCancel: (() -> Unit)? = null,
) {
    val theme = LocalGenericTheme.current
    val isVisible = if (workflow != null) workflow.isRunning else visible
    if (!isVisible) return

    val currentStatus = if (workflow != null) workflow.currentStep else statusText
    val currentProgress = if (workflow != null) (workflow.progress * 100).toInt() else progress

    Modal(
        visible = true,
        title = title,
        onDismissRequest = { onCancel?.invoke() },
    ) {
        ModalBody {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                if (currentStatus.isNotEmpty()) {
                    Text(text = currentStatus, color = theme.textSecondary, fontSize = 12.sp)
                }
                ProgressBar(value = currentProgress, maxValue = maxProgress, showLabel = true)
            }
        }
        if (onCancel != null) {
            ModalFooter {
                Button(text = "Cancel", variant = Variant.Ghost, onClick = onCancel)
            }
        }
    }
}
