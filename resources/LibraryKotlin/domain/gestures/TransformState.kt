package org.pixelrefine.genericui.domain.gestures

import androidx.compose.foundation.gestures.detectTransformGestures
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.input.pointer.pointerInput

/**
 * State untuk penanganan Zoom, Pan, Pinch, Clamping (Mirror `Zoomable_Handler.py` & `workflow_process.py`)
 */
class TransformState(
    val minScale: Float = 0.1f,
    val maxScale: Float = 5.0f,
    val initialScale: Float = 1.0f,
) {
    var scale by mutableFloatStateOf(initialScale)
    var offsetX by mutableFloatStateOf(0f)
    var offsetY by mutableFloatStateOf(0f)

    fun zoomIn(step: Float = 0.25f) {
        scale = (scale + step).coerceIn(minScale, maxScale)
    }

    fun zoomOut(step: Float = 0.25f) {
        scale = (scale - step).coerceIn(minScale, maxScale)
    }

    fun setZoom(newScale: Float) {
        scale = newScale.coerceIn(minScale, maxScale)
    }

    fun onTransform(panDelta: Offset, zoomDelta: Float) {
        scale = (scale * zoomDelta).coerceIn(minScale, maxScale)
        offsetX += panDelta.x
        offsetY += panDelta.y
    }

    fun reset() {
        scale = initialScale
        offsetX = 0f
        offsetY = 0f
    }
}

/**
 * Composable helper untuk remember TransformState
 */
@Composable
fun rememberTransformState(
    minScale: Float = 0.1f,
    maxScale: Float = 5.0f,
    initialScale: Float = 1.0f,
): TransformState {
    return remember { TransformState(minScale, maxScale, initialScale) }
}

/**
 * Modifier reusable untuk membuat Composable apa pun bisa di-Zoom & di-Pan secara mulus.
 */
fun Modifier.zoomable(state: TransformState): Modifier = this
    .pointerInput(Unit) {
        detectTransformGestures { _, pan, zoom, _ ->
            state.onTransform(pan, zoom)
        }
    }
    .graphicsLayer {
        scaleX = state.scale
        scaleY = state.scale
        translationX = state.offsetX
        translationY = state.offsetY
    }
