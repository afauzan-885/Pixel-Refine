package org.pixelrefine.genericui.animations

import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.AnimationSpec
import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.keyframes
import androidx.compose.animation.core.tween
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.composed
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.scale
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.layout.layout

/**
 * Multi-Animation Chaining Modifier.
 * Menggabungkan berbagai efek transisi (Fade, Slide, Zoom, Pulse, Shake) dalam SEKALI PANGGILAN deklaratif.
 */
fun Modifier.combinedAnimation(
    visible: Boolean = true,
    fadeIn: Boolean = true,
    slideDirection: SlideDirection? = null,
    zoomIn: Boolean = false,
    durationMs: Int = 300,
    slideDistance: Float = 50f,
): Modifier = composed {
    val progress = remember { Animatable(if (visible) 1f else 0f) }

    LaunchedEffect(visible) {
        progress.animateTo(
            targetValue = if (visible) 1f else 0f,
            animationSpec = tween(durationMillis = durationMs, easing = FastOutSlowInEasing),
        )
    }

    val p = progress.value

    val alphaModifier = if (fadeIn) Modifier.alpha(p) else Modifier
    val scaleModifier = if (zoomIn) Modifier.scale(0.8f + 0.2f * p) else Modifier

    val offsetModifier = if (slideDirection != null) {
        Modifier.graphicsLayer {
            val dist = slideDistance * (1f - p)
            when (slideDirection) {
                SlideDirection.LEFT -> translationX = dist
                SlideDirection.RIGHT -> translationX = -dist
                SlideDirection.UP -> translationY = dist
                SlideDirection.DOWN -> translationY = -dist
            }
        }
    } else Modifier

    this
        .then(alphaModifier)
        .then(scaleModifier)
        .then(offsetModifier)
}

/**
 * Animasi Detak / Denyut Halus (Pulse) untuk Status Aktif / Live Indikator.
 */
fun Modifier.pulseAnimation(
    enabled: Boolean = true,
    minScale: Float = 0.92f,
    maxScale: Float = 1.08f,
    durationMs: Int = 1200,
): Modifier = composed {
    if (!enabled) return@composed this

    val scale = remember { Animatable(minScale) }

    LaunchedEffect(enabled) {
        scale.animateTo(
            targetValue = maxScale,
            animationSpec = infiniteRepeatable(
                animation = tween(durationMillis = durationMs, easing = FastOutSlowInEasing),
                repeatMode = RepeatMode.Reverse,
            ),
        )
    }

    this.scale(scale.value)
}

/**
 * Animasi Getar Horizontal (Shake) untuk Feedback Error / Invalid Input.
 */
fun Modifier.shakeAnimation(
    trigger: Any?,
    intensity: Float = 12f,
    durationMs: Int = 400,
): Modifier = composed {
    val offset = remember { Animatable(0f) }

    LaunchedEffect(trigger) {
        if (trigger != null) {
            offset.animateTo(
                targetValue = 0f,
                animationSpec = keyframes {
                    durationMillis = durationMs
                    0f at 0
                    -intensity at 50
                    intensity at 100
                    -intensity * 0.7f at 150
                    intensity * 0.7f at 200
                    -intensity * 0.3f at 270
                    intensity * 0.3f at 340
                    0f at durationMs
                },
            )
        }
    }

    this.graphicsLayer { translationX = offset.value }
}

/**
 * Animasi Gelombang Berkilau (Shimmer) untuk Skeleton / Loading State.
 */
fun shimmerBrush(
    targetValue: Float = 1000f,
    durationMs: Int = 1200,
): Brush {
    // Digunakan pada komponen Skeleton / Placeholder
    return Brush.linearGradient(
        colors = listOf(
            Color.LightGray.copy(alpha = 0.6f),
            Color.White.copy(alpha = 0.2f),
            Color.LightGray.copy(alpha = 0.6f),
        ),
        start = Offset(0f, 0f),
        end = Offset(targetValue, targetValue),
    )
}
