package org.pixelrefine.genericui.animations

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.scaleIn
import androidx.compose.animation.scaleOut
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier

/**
 * Python: `zoom(animator, stack_widget, target, duration=400)`
 */
@Composable
fun ZoomTransition(
    visible: Boolean,
    duration: Int = 400,
    initialScale: Float = 0.85f,
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit,
) {
    val enter = scaleIn(
        initialScale = initialScale,
        animationSpec = tween(duration, easing = AnimationCurves.InOutCirc),
    ) + fadeIn(animationSpec = tween(duration))

    val exit = scaleOut(
        targetScale = initialScale,
        animationSpec = tween(duration, easing = AnimationCurves.InOutCirc),
    ) + fadeOut(animationSpec = tween(duration))

    AnimatedVisibility(
        visible = visible,
        enter = enter,
        exit = exit,
        modifier = modifier,
    ) {
        content()
    }
}
