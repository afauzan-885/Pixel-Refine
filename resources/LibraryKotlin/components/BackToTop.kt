package org.pixelrefine.genericui.components

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.scaleIn
import androidx.compose.animation.scaleOut
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.theme.LocalGenericTheme
import androidx.compose.material3.Text
import androidx.compose.foundation.clickable

@Composable
fun BackToTop(
    visible: Boolean = true,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    threshold: Dp = 400.dp,
    icon: String = "↑",
    size: Dp = 48.dp,
    variant: Variant = Variant.Primary,
) {
    val theme = LocalGenericTheme.current
    val variantColor = variantColor(theme, variant)

    Box(
        modifier = modifier.fillMaxSize().padding(16.dp),
        contentAlignment = Alignment.BottomEnd,
    ) {
        AnimatedVisibility(
            visible = visible,
            enter = scaleIn() + fadeIn(),
            exit = scaleOut() + fadeOut(),
        ) {
            Box(
                modifier = Modifier
                    .size(size)
                    .clip(CircleShape)
                    .background(variantColor)
                    .clickable { onClick() },
                contentAlignment = Alignment.Center,
            ) {
                Text(
                    text = icon,
                    color = theme.light,
                    fontSize = 20.sp,
                )
            }
        }
    }
}

@Composable
fun ScrollToTopButton(
    scrollState: androidx.compose.foundation.ScrollState,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    threshold: Dp = 400.dp,
) {
    val density = androidx.compose.ui.platform.LocalDensity.current
    val thresholdPx = with(density) { threshold.roundToPx() }

    val showButton = scrollState.value > thresholdPx

    BackToTop(
        visible = showButton,
        onClick = onClick,
        modifier = modifier,
        threshold = threshold,
    )
}
