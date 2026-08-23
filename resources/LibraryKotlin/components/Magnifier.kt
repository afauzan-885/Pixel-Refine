package org.pixelrefine.genericui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.scale
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import org.pixelrefine.genericui.theme.LocalGenericTheme

/**
 * Pixel Loupe / Magnifier Widget untuk inspeksi detail noise piksel (Gaya Klasik Konsisten).
 */
@Composable
fun Magnifier(
    zoomFactor: Float = 4.0f,
    loupeSize: Dp = 100.dp,
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit,
) {
    val theme = LocalGenericTheme.current

    Box(
        modifier = modifier
            .size(loupeSize)
            .clip(CircleShape)
            .background(theme.bgCard)
            .border(2.dp, theme.primary, CircleShape),
        contentAlignment = Alignment.Center,
    ) {
        Box(
            modifier = Modifier
                .fillMaxSize()
                .scale(zoomFactor),
            contentAlignment = Alignment.Center,
        ) {
            content()
        }
    }
}
