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
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.theme.LocalGenericTheme

/**
 * Item data model untuk ListGroup
 */
data class ListItem(
    val id: String,
    val title: String,
    val subtitle: String = "",
    val badge: String = "",
)

/**
 * Python: `ListGroup(items=[...], active_index=0)`
 */
@Composable
fun ListGroup(
    items: List<ListItem>,
    selectedIndex: Int = -1,
    onSelect: (Int, ListItem) -> Unit = { _, _ -> },
    modifier: Modifier = Modifier,
) {
    val theme = LocalGenericTheme.current
    Column(
        modifier = modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(theme.radiusLg))
            .background(theme.bgCard)
            .border(1.dp, theme.borderColor, RoundedCornerShape(theme.radiusLg)),
    ) {
        items.forEachIndexed { index, item ->
            val isSelected = index == selectedIndex
            val itemBg = if (isSelected) theme.hoverOverlay else Color.Transparent

            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(itemBg)
                    .clickable { onSelect(index, item) }
                    .padding(horizontal = 14.dp, vertical = 10.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween,
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = item.title,
                        color = if (isSelected) theme.primary else theme.textPrimary,
                        fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Normal,
                        fontSize = 13.sp,
                    )
                    if (item.subtitle.isNotEmpty()) {
                        Text(item.subtitle, color = theme.textMuted, fontSize = 11.sp)
                    }
                }
                if (item.badge.isNotEmpty()) {
                    Box(
                        modifier = Modifier
                            .clip(RoundedCornerShape(theme.radiusSm))
                            .background(if (isSelected) theme.primary else theme.bgSecondary)
                            .padding(horizontal = 6.dp, vertical = 2.dp),
                    ) {
                        Text(
                            text = item.badge,
                            color = if (isSelected) theme.textWhite else theme.textSecondary,
                            fontSize = 10.sp,
                            fontWeight = FontWeight.Bold,
                        )
                    }
                }
            }
            if (index < items.size - 1) {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(1.dp)
                        .background(theme.borderColor),
                )
            }
        }
    }
}
