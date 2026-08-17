package org.pixelrefine.genericui.animations

import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import org.pixelrefine.genericui.components.OverlayPosition
import org.pixelrefine.genericui.components.Toast
import org.pixelrefine.genericui.components.Variant

data class ToastItem(
    val id: Long,
    val message: String,
    val variant: Variant = Variant.Info,
    val position: OverlayPosition = OverlayPosition.BottomCenter,
    val durationMs: Long = 3000L,
)

/**
 * Controller singleton / manager untuk Toast — mirror `resources/animations/toast/toast_manager.py`
 */
class ToastManager {
    private var nextId = 0L
    val activeToasts = mutableStateListOf<ToastItem>()

    fun show(
        message: String,
        variant: Variant = Variant.Info,
        position: OverlayPosition = OverlayPosition.BottomCenter,
        durationMs: Long = 3000L,
    ) {
        val item = ToastItem(
            id = ++nextId,
            message = message,
            variant = variant,
            position = position,
            durationMs = durationMs,
        )
        activeToasts.add(item)
    }

    fun dismiss(id: Long) {
        activeToasts.removeAll { it.id == id }
    }
}

val GlobalToastManager = ToastManager()

/**
 * Host Composable yang me-render semua toast aktif.
 */
@Composable
fun ToastHost(manager: ToastManager = GlobalToastManager) {
    manager.activeToasts.forEach { toast ->
        Toast(
            message = toast.message,
            visible = true,
            variant = toast.variant,
            position = toast.position,
            durationMs = toast.durationMs,
            onDismiss = { manager.dismiss(toast.id) },
        )
    }
}
