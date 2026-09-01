package org.pixelrefine.genericui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
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
 * Python: `GridContainer(columns=2, spacing=10)`
 */
@Composable
fun GridContainer(
    itemsCount: Int,
    columns: Int = 2,
    spacing: Dp = 10.dp,
    modifier: Modifier = Modifier,
    itemContent: @Composable (Int) -> Unit,
) {
    val rows = (itemsCount + columns - 1) / columns
    Column(
        modifier = modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(spacing),
    ) {
        for (r in 0 until rows) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(spacing),
            ) {
                for (c in 0 until columns) {
                    val index = r * columns + c
                    if (index < itemsCount) {
                        Box(modifier = Modifier.weight(1f)) {
                            itemContent(index)
                        }
                    } else {
                        Box(modifier = Modifier.weight(1f))
                    }
                }
            }
        }
    }
}

/**
 * Python: `GridItem(title="", subtitle="")`
 */
@Composable
fun GridItem(
    title: String = "",
    subtitle: String = "",
    onClick: (() -> Unit)? = null,
    modifier: Modifier = Modifier,
    content: @Composable (() -> Unit)? = null,
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
            .padding(10.dp),
        verticalArrangement = Arrangement.spacedBy(6.dp),
    ) {
        content?.invoke()
        if (title.isNotEmpty()) {
            Text(title, color = theme.textPrimary, fontWeight = FontWeight.Bold, fontSize = 12.sp)
        }
        if (subtitle.isNotEmpty()) {
            Text(subtitle, color = theme.textMuted, fontSize = 10.sp)
        }
    }
}

/**
 * Python: `Gallery(images=[...], columns=3)`
 */
@Composable
fun Gallery(
    imagesCount: Int,
    columns: Int = 3,
    spacing: Dp = 8.dp,
    modifier: Modifier = Modifier,
    imageRenderer: @Composable (Int) -> Unit,
) {
    GridContainer(
        itemsCount = imagesCount,
        columns = columns,
        spacing = spacing,
        modifier = modifier,
        itemContent = imageRenderer,
    )
}

/**
 * Python: `ThumbnailGrid(items=[...])`
 */
@Composable
fun ThumbnailGrid(
    itemsCount: Int,
    columns: Int = 4,
    spacing: Dp = 6.dp,
    modifier: Modifier = Modifier,
    thumbnailRenderer: @Composable (Int) -> Unit,
) {
    GridContainer(
        itemsCount = itemsCount,
        columns = columns,
        spacing = spacing,
        modifier = modifier,
        itemContent = thumbnailRenderer,
    )
}
