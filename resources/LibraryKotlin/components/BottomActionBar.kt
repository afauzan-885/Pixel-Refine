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
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.theme.LocalGenericTheme

/**
 * Item navigasi bawah (Python: `add_nav_item(name, icon)`).
 */
data class BottomNavItem(
    val name: String,
    val icon: String,
)

/**
 * Python: `BottomActionBar()`
 */
@Composable
fun BottomActionBar(
    items: List<BottomNavItem>,
    activeItem: String,
    primaryLabel: String = "Start",
    primaryRunning: Boolean = false,
    onNavClick: (String) -> Unit = {},
    onPrimaryClick: () -> Unit = {},
    modifier: Modifier = Modifier,
) {
    val theme = LocalGenericTheme.current
    Row(
        modifier = modifier
            .fillMaxWidth()
            .height(60.dp)
            .clip(RoundedCornerShape(theme.radiusLg))
            .background(theme.bgCard)
            .border(1.dp, theme.borderColor, RoundedCornerShape(theme.radiusLg))
            .padding(horizontal = 6.dp, vertical = 6.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        items.forEach { item ->
            val active = item.name == activeItem
            Column(
                modifier = Modifier
                    .weight(1f)
                    .clickable { onNavClick(item.name) },
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center,
            ) {
                Text(text = item.icon, fontSize = 16.sp)
                Text(
                    text = item.name,
                    fontSize = 10.sp,
                    fontWeight = if (active) FontWeight.Bold else FontWeight.Normal,
                    color = if (active) theme.primary else theme.textPrimary,
                )
            }
        }
        Box(
            modifier = Modifier
                .size(52.dp)
                .clip(CircleShape)
                .background(if (primaryRunning) theme.danger else theme.primary)
                .border(2.dp, Color.White, CircleShape)
                .clickable { onPrimaryClick() },
            contentAlignment = Alignment.Center,
        ) {
            Text(
                text = primaryLabel,
                color = Color.White,
                fontWeight = FontWeight.Bold,
                fontSize = 10.sp,
                textAlign = TextAlign.Center,
            )
        }
    }
}
