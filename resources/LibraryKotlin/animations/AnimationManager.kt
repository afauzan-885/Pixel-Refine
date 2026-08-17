package org.pixelrefine.genericui.animations

import androidx.compose.animation.core.CubicBezierEasing
import androidx.compose.animation.core.Easing
import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.LinearEasing
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember

/**
 * Tipe animasi — padanan 1:1 dari `AnimationType` di `resources/animations/animation_manager.py`
 */
enum class AnimationType {
    FADE,
    SLIDE_LEFT,
    SLIDE_RIGHT,
    SLIDE_UP,
    SLIDE_DOWN,
    ZOOM,
}

/**
 * Arah slide — padanan 1:1 dari `SlideDirection` di `resources/animations/animation_manager.py`
 */
enum class SlideDirection {
    LEFT,
    RIGHT,
    UP,
    DOWN;

    companion object {
        fun fromString(dir: String): SlideDirection = when (dir.trim().lowercase()) {
            "left" -> LEFT
            "right" -> RIGHT
            "up" -> UP
            "down" -> DOWN
            else -> LEFT
        }
    }
}

/**
 * Kurva easing standar PySide6 mapped ke Compose Easing.
 */
object AnimationCurves {
    val OutQuad: Easing = CubicBezierEasing(0.25f, 0.46f, 0.45f, 0.94f)
    val InQuad: Easing = CubicBezierEasing(0.55f, 0.085f, 0.68f, 0.53f)
    val OutExpo: Easing = CubicBezierEasing(0.19f, 1f, 0.22f, 1f)
    val InOutCirc: Easing = CubicBezierEasing(0.785f, 0.135f, 0.15f, 0.86f)
    val Default: Easing = FastOutSlowInEasing
    val Linear: Easing = LinearEasing
}

/**
 * Animator controller untuk transisi halaman (mirror `StackedWidgetAnimator`).
 */
class StackedWidgetAnimator {
    var defaultDurationOut: Int = 150
    var defaultDurationIn: Int = 250

    fun transition(
        targetIndex: Int,
        animationType: AnimationType = AnimationType.FADE,
        duration: Int = 300,
        onFinished: (() -> Unit)? = null,
    ) {
        onFinished?.invoke()
    }
}

/**
 * Controller untuk animasi lifecycle widget (mirror `WidgetLifecycleAnimator`).
 */
class WidgetLifecycleAnimator {
    fun animateDelete(
        duration: Int = 500,
        dropDistance: Int = 60,
        onFinished: (() -> Unit)? = null,
    ) {
        onFinished?.invoke()
    }
}
