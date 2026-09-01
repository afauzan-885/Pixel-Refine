package org.pixelrefine.genericui.components

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.slideInVertically
import androidx.compose.animation.slideOutVertically
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
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.delay
import org.pixelrefine.genericui.theme.LocalGenericTheme
import androidx.compose.material3.Text

enum class SnackbarPosition {
    Top, Bottom
}

data class SnackbarData(
    val message: String,
    val variant: Variant = Variant.Info,
    val actionLabel: String? = null,
    val onAction: (() -> Unit)? = null,
    val duration: Long = 4000L,
    val id: Long = System.currentTimeMillis(),
)

object SnackbarManager {
    private val _snackbars = mutableStateListOf<SnackbarData>()
    val snackbars: List<SnackbarData> = _snackbars

    fun show(
        message: String,
        variant: Variant = Variant.Info,
        actionLabel: String? = null,
        onAction: (() -> Unit)? = null,
        duration: Long = 4000L,
    ) {
        _snackbars.add(
            SnackbarData(
                message = message,
                variant = variant,
                actionLabel = actionLabel,
                onAction = onAction,
                duration = duration,
            )
        )
    }

    fun dismiss(id: Long) {
        _snackbars.removeAll { it.id == id }
    }

    fun clear() {
        _snackbars.clear()
    }
}

@Composable
fun Snackbar(
    message: String,
    modifier: Modifier = Modifier,
    variant: Variant = Variant.Info,
    visible: Boolean = true,
    actionLabel: String? = null,
    onAction: (() -> Unit)? = null,
    durationMs: Long = 4000L,
    onDismiss: () -> Unit = {},
    position: SnackbarPosition = SnackbarPosition.Bottom,
) {
    val theme = LocalGenericTheme.current
    val variantColor = variantColor(theme, variant)

    LaunchedEffect(visible) {
        if (visible && durationMs > 0) {
            delay(durationMs)
            onDismiss()
        }
    }

    val slideIn = if (position == SnackbarPosition.Top) {
        slideInVertically(initialOffsetY = { -it })
    } else {
        slideInVertically(initialOffsetY = { it })
    }
    val slideOut = if (position == SnackbarPosition.Top) {
        slideOutVertically(targetOffsetY = { -it })
    } else {
        slideOutVertically(targetOffsetY = { it })
    }

    AnimatedVisibility(
        visible = visible,
        enter = slideIn + fadeIn(),
        exit = slideOut + fadeOut(),
    ) {
        Row(
            modifier = modifier
                .clip(RoundedCornerShape(8.dp))
                .background(theme.dark)
                .padding(horizontal = 16.dp, vertical = 12.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            Text(
                text = message,
                color = theme.light,
                fontSize = 14.sp,
                modifier = Modifier.weight(1f),
            )

            if (actionLabel != null && onAction != null) {
                Text(
                    text = actionLabel.uppercase(),
                    color = variantColor,
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier.clickable {
                        onAction()
                        onDismiss()
                    },
                )
            }

            Box(
                modifier = Modifier
                    .size(20.dp)
                    .clip(CircleShape)
                    .background(theme.light.copy(alpha = 0.2f))
                    .clickable { onDismiss() },
                contentAlignment = Alignment.Center,
            ) {
                Text(
                    text = "×",
                    color = theme.light,
                    fontSize = 12.sp,
                )
            }
        }
    }
}

@Composable
fun SnackbarHost(
    position: SnackbarPosition = SnackbarPosition.Bottom,
) {
    val snackbars = SnackbarManager.snackbars

    Column(
        modifier = Modifier.fillMaxWidth().padding(16.dp),
        verticalArrangement = if (position == SnackbarPosition.Top) Arrangement.Top else Arrangement.Bottom,
    ) {
        snackbars.forEach { data ->
            key(data.id) {
                Snackbar(
                    message = data.message,
                    variant = data.variant,
                    actionLabel = data.actionLabel,
                    onAction = data.onAction,
                    durationMs = data.duration,
                    onDismiss = { SnackbarManager.dismiss(data.id) },
                    position = position,
                )
            }
        }
    }
}
