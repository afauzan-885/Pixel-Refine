package org.pixelrefine.genericui.animations

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.FiniteAnimationSpec
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier

/**
 * Python: `fade_in(animator, target_widget, stack_widget=None, duration=300)`
 * Menghasilkan EnterTransition fade-in Compose dengan durasi dan kurva yang sama persis.
 */
fun fadeInTransition(
    duration: Int = 300,
    animationSpec: FiniteAnimationSpec<Float> = tween(duration, easing = AnimationCurves.OutQuad),
) = fadeIn(animationSpec = animationSpec)

/**
 * Python: `fade_out(animator, widget, duration=300, ...)`
 */
fun fadeOutTransition(
    duration: Int = 300,
    animationSpec: FiniteAnimationSpec<Float> = tween(duration, easing = AnimationCurves.OutQuad),
) = fadeOut(animationSpec = animationSpec)

/**
 * Composable wrapper untuk transisi Fade in/out.
 */
@Composable
fun FadeTransition(
    visible: Boolean,
    duration: Int = 300,
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit,
) {
    AnimatedVisibility(
        visible = visible,
        enter = fadeInTransition(duration),
        exit = fadeOutTransition(duration),
        modifier = modifier,
    ) {
        content()
    }
}
