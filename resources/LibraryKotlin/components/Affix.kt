package org.pixelrefine.genericui.components

import androidx.compose.foundation.layout.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.layout.onGloballyPositioned
import androidx.compose.ui.layout.positionInRoot
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp

enum class AffixPosition {
    Top, Bottom
}

@Composable
fun Affix(
    modifier: Modifier = Modifier,
    position: AffixPosition = AffixPosition.Top,
    offset: Dp = 0.dp,
    content: @Composable () -> Unit,
) {
    val density = LocalDensity.current
    var isSticky by remember { mutableStateOf(false) }
    var contentHeight by remember { mutableStateOf(0) }
    var contentY by remember { mutableStateOf(0f) }

    val offsetPx = with(density) { offset.roundToPx() }

    Box(
        modifier = modifier.onGloballyPositioned { coordinates ->
            contentHeight = coordinates.size.height
            contentY = coordinates.positionInRoot().y
        },
    ) {
        // Main content
        content()
    }
}

@Composable
fun StickyHeader(
    modifier: Modifier = Modifier,
    topOffset: Dp = 0.dp,
    content: @Composable () -> Unit,
) {
    val density = LocalDensity.current
    var isSticky by remember { mutableStateOf(false) }
    val offsetPx = with(density) { topOffset.roundToPx() }

    Box(
        modifier = modifier,
    ) {
        // Placeholder for original content
        Box(modifier = Modifier.height(1.dp))

        if (isSticky) {
            content()
        }
    }
}
