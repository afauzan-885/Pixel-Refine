package org.pixelrefine.genericui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.theme.LocalGenericTheme

/**
 * Python: `ImageCard(title="", subtitle="")`
 */
@Composable
fun ImageCard(
    title: String = "",
    subtitle: String = "",
    imageHeight: Dp = 120.dp,
    onClick: (() -> Unit)? = null,
    modifier: Modifier = Modifier,
    imageContent: @Composable () -> Unit = {},
) {
    val theme = LocalGenericTheme.current
    val clickableModifier = if (onClick != null) Modifier.clickable { onClick() } else Modifier

    Column(
        modifier = modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(theme.radiusMd))
            .background(theme.bgCard)
            .border(1.dp, theme.borderColor, RoundedCornerShape(theme.radiusMd))
            .then(clickableModifier)
            .padding(8.dp),
        verticalArrangement = Arrangement.spacedBy(6.dp),
    ) {
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(imageHeight)
                .clip(RoundedCornerShape(theme.radiusSm))
                .background(theme.bgSecondary),
            contentAlignment = Alignment.Center,
        ) {
            imageContent()
        }
        if (title.isNotEmpty()) {
            Text(title, color = theme.textPrimary, fontWeight = FontWeight.Bold, fontSize = 12.sp)
        }
        if (subtitle.isNotEmpty()) {
            Text(subtitle, color = theme.textMuted, fontSize = 10.sp)
        }
    }
}

/**
 * Python: `GridItemWidget`
 */
@Composable
fun GridItemWidget(
    title: String = "",
    selected: Boolean = false,
    onClick: () -> Unit = {},
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit = {},
) {
    val theme = LocalGenericTheme.current
    val borderColor = if (selected) theme.primary else theme.borderColor
    val borderWidth = if (selected) 2.dp else 1.dp

    Box(
        modifier = modifier
            .clip(RoundedCornerShape(theme.radiusMd))
            .background(theme.bgCard)
            .border(borderWidth, borderColor, RoundedCornerShape(theme.radiusMd))
            .clickable { onClick() }
            .padding(6.dp),
    ) {
        Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
            content()
            if (title.isNotEmpty()) {
                Text(title, color = theme.textPrimary, fontSize = 11.sp, fontWeight = FontWeight.SemiBold)
            }
        }
    }
}
