package org.pixelrefine.genericui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.theme.LocalGenericTheme

/**
 * Tab model
 */
data class TabPane(
    val title: String,
    val content: @Composable () -> Unit,
)

/**
 * Python: `TabContainer()`
 */
@Composable
fun TabContainer(
    tabs: List<TabPane>,
    selectedIndex: Int = 0,
    onTabSelected: (Int) -> Unit = {},
    modifier: Modifier = Modifier,
) {
    val theme = LocalGenericTheme.current
    Column(modifier = modifier.fillMaxWidth()) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .background(theme.bgSecondary),
            horizontalArrangement = Arrangement.Start,
        ) {
            tabs.forEachIndexed { index, tab ->
                val active = index == selectedIndex
                Column(
                    modifier = Modifier
                        .clickable { onTabSelected(index) }
                        .padding(horizontal = 16.dp, vertical = 10.dp),
                    horizontalAlignment = Alignment.CenterHorizontally,
                ) {
                    Text(
                        text = tab.title,
                        color = if (active) theme.primary else theme.textSecondary,
                        fontWeight = if (active) FontWeight.Bold else FontWeight.Normal,
                        fontSize = 13.sp,
                    )
                }
            }
        }
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(2.dp)
                .background(theme.borderColor),
        )

        // Content
        if (selectedIndex in tabs.indices) {
            Box(modifier = Modifier.fillMaxWidth().padding(top = 10.dp)) {
                tabs[selectedIndex].content()
            }
        }
    }
}

/**
 * Python: `SimpleTabs(tabs=[...], active_index=0)`
 */
@Composable
fun SimpleTabs(
    tabTitles: List<String>,
    activeIndex: Int = 0,
    onSelect: (Int) -> Unit = {},
    modifier: Modifier = Modifier,
) {
    val theme = LocalGenericTheme.current
    Row(
        modifier = modifier
            .fillMaxWidth()
            .background(theme.bgSecondary),
        horizontalArrangement = Arrangement.Start,
    ) {
        tabTitles.forEachIndexed { index, title ->
            val active = index == activeIndex
            Column(
                modifier = Modifier
                    .clickable { onSelect(index) }
                    .padding(horizontal = 14.dp, vertical = 8.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
            ) {
                Text(
                    text = title,
                    color = if (active) theme.primary else theme.textSecondary,
                    fontWeight = if (active) FontWeight.Bold else FontWeight.Normal,
                    fontSize = 12.sp,
                )
            }
        }
    }
}
