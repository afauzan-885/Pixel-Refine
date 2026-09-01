package org.pixelrefine.genericui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.theme.LocalGenericTheme
import androidx.compose.material3.Text
import androidx.compose.ui.graphics.Color

data class AnchorItem(
    val id: String,
    val title: String,
    val href: String? = null,
)

@Composable
fun Anchor(
    items: List<AnchorItem>,
    modifier: Modifier = Modifier,
    offset: Dp = 0.dp,
    showAffix: Boolean = true,
    currentSection: String? = null,
    onItemClick: ((AnchorItem) -> Unit)? = null,
) {
    val theme = LocalGenericTheme.current
    var activeSection by remember { mutableStateOf(currentSection ?: items.firstOrNull()?.id) }

    Column(
        modifier = modifier
            .clip(RoundedCornerShape(4.dp))
            .background(theme.bgCard)
            .border(1.dp, theme.borderColor, RoundedCornerShape(4.dp))
            .padding(8.dp),
    ) {
        items.forEach { item ->
            val isActive = activeSection == item.id
            val variantColor = variantColor(theme, Variant.Primary)

            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(4.dp))
                    .background(if (isActive) variantColor.copy(alpha = 0.1f) else Color.Transparent)
                    .clickable {
                        activeSection = item.id
                        onItemClick?.invoke(item)
                    }
                    .padding(horizontal = 12.dp, vertical = 8.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                // Active indicator
                Box(
                    modifier = Modifier
                        .width(2.dp)
                        .height(16.dp)
                        .background(if (isActive) variantColor else Color.Transparent)
                        .padding(end = 8.dp),
                )

                Spacer(modifier = Modifier.width(4.dp))

                Text(
                    text = item.title,
                    color = if (isActive) variantColor else theme.textPrimary,
                    fontSize = 13.sp,
                    fontWeight = if (isActive) FontWeight.SemiBold else FontWeight.Normal,
                )
            }
        }
    }
}

@Composable
fun SimpleAnchor(
    items: List<AnchorItem>,
    modifier: Modifier = Modifier,
    onItemClick: ((AnchorItem) -> Unit)? = null,
) {
    Anchor(
        items = items,
        modifier = modifier,
        onItemClick = onItemClick,
    )
}
