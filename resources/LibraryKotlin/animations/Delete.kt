package org.pixelrefine.genericui.animations

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeOut
import androidx.compose.animation.slideOutVertically
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier

/**
 * Python: `delete(widget, animator=None, duration=500, drop_distance=60)`
 * Menghapus/menghilangkan elemen dengan efek runtuh/jatuh ke bawah.
 */
@Composable
fun DeleteTransition(
    visible: Boolean,
    duration: Int = 500,
    dropDistancePx: Int = 60,
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit,
) {
    AnimatedVisibility(
        visible = visible,
        exit = slideOutVertically(
            targetOffsetY = { dropDistancePx },
            animationSpec = tween(duration, easing = AnimationCurves.InQuad),
        ) + fadeOut(animationSpec = tween(duration)),
        modifier = modifier,
    ) {
        content()
    }
}
