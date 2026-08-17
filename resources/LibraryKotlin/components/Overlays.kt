package org.pixelrefine.genericui.components

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxScope
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.delay
import org.pixelrefine.genericui.theme.LocalGenericTheme

enum class OverlayPosition {
    TopLeft, TopCenter, TopRight,
    CenterLeft, Center, CenterRight,
    BottomLeft, BottomCenter, BottomRight;

    fun toAlignment(): Alignment = when (this) {
        TopLeft -> Alignment.TopStart
        TopCenter -> Alignment.TopCenter
        TopRight -> Alignment.TopEnd
        CenterLeft -> Alignment.CenterStart
        Center -> Alignment.Center
        CenterRight -> Alignment.CenterEnd
        BottomLeft -> Alignment.BottomStart
        BottomCenter -> Alignment.BottomCenter
        BottomRight -> Alignment.BottomEnd
    }
}

/**
 * Python: `Overlay(visible=False)`
 */
@Composable
fun Overlay(
    visible: Boolean,
    modifier: Modifier = Modifier,
    backgroundColor: Color = Color(0x66000000),
    onClick: (() -> Unit)? = null,
    content: @Composable BoxScope.() -> Unit = {},
) {
    AnimatedVisibility(
        visible = visible,
        enter = fadeIn(),
        exit = fadeOut(),
    ) {
        val clickModifier = if (onClick != null) Modifier.clickable { onClick() } else Modifier
        Box(
            modifier = modifier
                .fillMaxSize()
                .background(backgroundColor)
                .then(clickModifier),
            contentAlignment = Alignment.Center,
            content = content,
        )
    }
}

/**
 * Python: `LoadingSpinner(size=24)`
 */
@Composable
fun LoadingSpinner(
    size: Dp = 24.dp,
    color: Color? = null,
    modifier: Modifier = Modifier,
) {
    val theme = LocalGenericTheme.current
    CircularProgressIndicator(
        modifier = modifier.size(size),
        color = color ?: theme.primary,
        strokeWidth = 2.5.dp,
    )
}

/**
 * Python: `LoadingOverlay(visible=False, text="Loading...")`
 */
@Composable
fun LoadingOverlay(
    visible: Boolean,
    text: String = "Loading...",
    modifier: Modifier = Modifier,
) {
    val theme = LocalGenericTheme.current
    Overlay(visible = visible, modifier = modifier) {
        Row(
            modifier = Modifier
                .clip(RoundedCornerShape(theme.radiusLg))
                .background(theme.bgCard)
                .border(1.dp, theme.borderColor, RoundedCornerShape(theme.radiusLg))
                .padding(horizontal = 20.dp, vertical = 14.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            LoadingSpinner(size = 20.dp)
            Spacer(width = 12.dp)
            Text(text, color = theme.textPrimary, fontWeight = FontWeight.SemiBold, fontSize = 13.sp)
        }
    }
}

/**
 * Python: `Toast(message="", variant="info", duration_ms=3000)`
 */
@Composable
fun Toast(
    message: String,
    visible: Boolean,
    variant: Variant = Variant.Info,
    position: OverlayPosition = OverlayPosition.BottomCenter,
    durationMs: Long = 3000L,
    onDismiss: () -> Unit = {},
) {
    val theme = LocalGenericTheme.current
    LaunchedEffect(visible, message) {
        if (visible) {
            delay(durationMs)
            onDismiss()
        }
    }

    AnimatedVisibility(
        visible = visible,
        enter = fadeIn(),
        exit = fadeOut(),
    ) {
        Box(modifier = Modifier.fillMaxSize().padding(16.dp), contentAlignment = position.toAlignment()) {
            Row(
                modifier = Modifier
                    .clip(RoundedCornerShape(theme.radiusMd))
                    .background(variantColor(theme, variant))
                    .padding(horizontal = 16.dp, vertical = 10.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Text(message, color = Color.White, fontWeight = FontWeight.Bold, fontSize = 12.sp)
            }
        }
    }
}

/**
 * Python: `OverlayContainer(position=...)`
 */
@Composable
fun OverlayContainer(
    position: OverlayPosition = OverlayPosition.Center,
    modifier: Modifier = Modifier,
    content: @Composable BoxScope.() -> Unit,
) {
    Box(
        modifier = modifier.fillMaxSize(),
        contentAlignment = position.toAlignment(),
        content = content,
    )
}
