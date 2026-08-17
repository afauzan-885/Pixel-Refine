package org.pixelrefine.genericui.components

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.expandVertically
import androidx.compose.animation.shrinkVertically
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.theme.LocalGenericTheme

/**
 * Python: `Collapse(title="", expanded=False)`
 */
@Composable
fun Collapse(
    title: String,
    expanded: Boolean = false,
    onToggle: ((Boolean) -> Unit)? = null,
    modifier: Modifier = Modifier,
    content: @Composable ColumnScope.() -> Unit,
) {
    var isExpanded by remember { mutableStateOf(expanded) }
    val effectiveExpanded = onToggle?.let { expanded } ?: isExpanded
    val theme = LocalGenericTheme.current

    Column(
        modifier = modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(theme.radiusMd))
            .background(theme.bgCard)
            .border(1.dp, theme.borderColor, RoundedCornerShape(theme.radiusMd)),
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .clickable {
                    if (onToggle != null) {
                        onToggle(!effectiveExpanded)
                    } else {
                        isExpanded = !isExpanded
                    }
                }
                .padding(horizontal = 14.dp, vertical = 10.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.SpaceBetween,
        ) {
            Text(title, color = theme.textPrimary, fontWeight = FontWeight.Bold, fontSize = 13.sp)
            Text(
                text = if (effectiveExpanded) "▲" else "▼",
                color = theme.textSecondary,
                fontSize = 10.sp,
            )
        }

        AnimatedVisibility(
            visible = effectiveExpanded,
            enter = expandVertically(),
            exit = shrinkVertically(),
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 14.dp, vertical = 8.dp),
                content = content,
            )
        }
    }
}

/** Accordion item model */
data class AccordionItem(
    val title: String,
    val content: @Composable ColumnScope.() -> Unit,
)

/**
 * Python: `Accordion(items=[...])`
 */
@Composable
fun Accordion(
    items: List<AccordionItem>,
    modifier: Modifier = Modifier,
) {
    var expandedIndex by remember { mutableStateOf(-1) }
    Column(
        modifier = modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(6.dp),
    ) {
        items.forEachIndexed { index, item ->
            Collapse(
                title = item.title,
                expanded = index == expandedIndex,
                onToggle = { isExp ->
                    expandedIndex = if (isExp) index else -1
                },
                content = item.content,
            )
        }
    }
}
