package org.pixelrefine.genericui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.theme.LocalGenericTheme

data class NavItem(
    val title: String,
    val icon: String = "",
    val badge: String = "",
)

/**
 * Python: `Navbar(brand="Pixel Refine", items=[...])`
 */
@Composable
fun Navbar(
    brand: String = "",
    items: List<NavItem> = emptyList(),
    selectedIndex: Int = 0,
    onSelect: (Int, NavItem) -> Unit = { _, _ -> },
    modifier: Modifier = Modifier,
    rightContent: @Composable (() -> Unit)? = null,
) {
    val theme = LocalGenericTheme.current
    Row(
        modifier = modifier
            .fillMaxWidth()
            .height(52.dp)
            .background(theme.bgCard)
            .padding(horizontal = 16.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.SpaceBetween,
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(16.dp),
        ) {
            if (brand.isNotEmpty()) {
                Text(brand, color = theme.primary, fontWeight = FontWeight.Bold, fontSize = 16.sp)
            }
            items.forEachIndexed { index, item ->
                val active = index == selectedIndex
                Text(
                    text = item.title,
                    color = if (active) theme.primary else theme.textSecondary,
                    fontWeight = if (active) FontWeight.Bold else FontWeight.Normal,
                    fontSize = 13.sp,
                    modifier = Modifier
                        .clickable { onSelect(index, item) }
                        .padding(horizontal = 8.dp, vertical = 6.dp),
                )
            }
        }
        rightContent?.invoke()
    }
}

data class SidebarItem(
    val title: String,
    val icon: String = "",
    val badge: String = "",
)

/**
 * Python: `Sidebar(items=[...])`
 */
@Composable
fun Sidebar(
    items: List<SidebarItem>,
    selectedIndex: Int = 0,
    onSelect: (Int, SidebarItem) -> Unit = { _, _ -> },
    modifier: Modifier = Modifier,
) {
    val theme = LocalGenericTheme.current
    Column(
        modifier = modifier
            .width(220.dp)
            .fillMaxHeight()
            .background(theme.bgCard)
            .padding(vertical = 12.dp),
    ) {
        items.forEachIndexed { index, item ->
            val active = index == selectedIndex
            val itemBg = if (active) theme.hoverOverlay else Color.Transparent

            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(itemBg)
                    .clickable { onSelect(index, item) }
                    .padding(horizontal = 16.dp, vertical = 10.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(10.dp),
            ) {
                if (item.icon.isNotEmpty()) {
                    Text(item.icon, fontSize = 16.sp)
                }
                Text(
                    text = item.title,
                    color = if (active) theme.primary else theme.textPrimary,
                    fontWeight = if (active) FontWeight.Bold else FontWeight.Normal,
                    fontSize = 13.sp,
                )
            }
        }
    }
}
