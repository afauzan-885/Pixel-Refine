package org.pixelrefine.genericui.components

import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import org.pixelrefine.genericui.theme.LocalGenericTheme

/**
 * Python: `SkeletonLoader(width=None, height=20)`
 */
@Composable
fun SkeletonLoader(
    modifier: Modifier = Modifier,
    width: Dp? = null,
    height: Dp = 20.dp,
    borderRadius: Dp = 4.dp,
) {
    val theme = LocalGenericTheme.current
    val infiniteTransition = rememberInfiniteTransition()
    val alpha by infiniteTransition.animateFloat(
        initialValue = 0.3f,
        targetValue = 0.8f,
        animationSpec = infiniteRepeatable(
            animation = tween(800, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse,
        ),
    )

    val sizeModifier = when {
        width != null -> Modifier.width(width).height(height)
        else -> Modifier.fillMaxWidth().height(height)
    }

    Box(
        modifier = modifier
            .then(sizeModifier)
            .clip(RoundedCornerShape(borderRadius))
            .background(theme.bgSecondary.copy(alpha = alpha)),
    )
}
