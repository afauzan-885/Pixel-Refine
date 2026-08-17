package org.pixelrefine.genericui.animations

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.slideInHorizontally
import androidx.compose.animation.slideInVertically
import androidx.compose.animation.slideOutHorizontally
import androidx.compose.animation.slideOutVertically
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier

/**
 * Python: `slide(animator, stack_widget, target, direction, duration=400, curve=...)`
 */
@Composable
fun SlideTransition(
    visible: Boolean,
    direction: SlideDirection = SlideDirection.LEFT,
    duration: Int = 400,
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit,
) {
    val enterTransition = when (direction) {
        SlideDirection.LEFT -> slideInHorizontally(
            initialOffsetX = { fullWidth -> fullWidth },
            animationSpec = tween(duration, easing = AnimationCurves.OutExpo),
        ) + fadeIn(animationSpec = tween(duration))

        SlideDirection.RIGHT -> slideInHorizontally(
            initialOffsetX = { fullWidth -> -fullWidth },
            animationSpec = tween(duration, easing = AnimationCurves.OutExpo),
        ) + fadeIn(animationSpec = tween(duration))

        SlideDirection.UP -> slideInVertically(
            initialOffsetY = { fullHeight -> fullHeight },
            animationSpec = tween(duration, easing = AnimationCurves.OutExpo),
        ) + fadeIn(animationSpec = tween(duration))

        SlideDirection.DOWN -> slideInVertically(
            initialOffsetY = { fullHeight -> -fullHeight },
            animationSpec = tween(duration, easing = AnimationCurves.OutExpo),
        ) + fadeIn(animationSpec = tween(duration))
    }

    val exitTransition = when (direction) {
        SlideDirection.LEFT -> slideOutHorizontally(
            targetOffsetX = { fullWidth -> -fullWidth },
            animationSpec = tween(duration, easing = AnimationCurves.OutExpo),
        ) + fadeOut(animationSpec = tween(duration))

        SlideDirection.RIGHT -> slideOutHorizontally(
            targetOffsetX = { fullWidth -> fullWidth },
            animationSpec = tween(duration, easing = AnimationCurves.OutExpo),
        ) + fadeOut(animationSpec = tween(duration))

        SlideDirection.UP -> slideOutVertically(
            targetOffsetY = { fullHeight -> -fullHeight },
            animationSpec = tween(duration, easing = AnimationCurves.OutExpo),
        ) + fadeOut(animationSpec = tween(duration))

        SlideDirection.DOWN -> slideOutVertically(
            targetOffsetY = { fullHeight -> fullHeight },
            animationSpec = tween(duration, easing = AnimationCurves.OutExpo),
        ) + fadeOut(animationSpec = tween(duration))
    }

    AnimatedVisibility(
        visible = visible,
        enter = enterTransition,
        exit = exitTransition,
        modifier = modifier,
    ) {
        content()
    }
}
