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
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.theme.LocalGenericTheme
import androidx.compose.material3.Text

data class TreeNode(
    val id: String,
    val label: String,
    val icon: String? = null,
    val children: List<TreeNode> = emptyList(),
    val isLeaf: Boolean = false,
    val disabled: Boolean = false,
)

@Composable
fun TreeView(
    nodes: List<TreeNode>,
    modifier: Modifier = Modifier,
    level: Int = 0,
    expandedIds: Set<String> = emptySet(),
    selectedIds: Set<String> = emptySet(),
    onToggleExpand: ((String) -> Unit)? = null,
    onSelect: ((String) -> Unit)? = null,
) {
    val theme = LocalGenericTheme.current

    Column(modifier = modifier) {
        nodes.forEach { node ->
            TreeNodeView(
                node = node,
                level = level,
                expandedIds = expandedIds,
                selectedIds = selectedIds,
                onToggleExpand = onToggleExpand,
                onSelect = onSelect,
            )
        }
    }
}

@Composable
private fun TreeNodeView(
    node: TreeNode,
    level: Int,
    expandedIds: Set<String>,
    selectedIds: Set<String>,
    onToggleExpand: ((String) -> Unit)?,
    onSelect: ((String) -> Unit)?,
) {
    val theme = LocalGenericTheme.current
    val isExpanded = expandedIds.contains(node.id) || level == 0
    val isSelected = selectedIds.contains(node.id)
    val hasChildren = node.children.isNotEmpty() && !node.isLeaf

    Column {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .background(if (isSelected) theme.primary.copy(alpha = 0.1f) else Color.Transparent)
                .clickable(enabled = !node.disabled) {
                    onSelect?.invoke(node.id)
                }
                .padding(start = (level * 16 + 8).dp, end = 8.dp, top = 4.dp, bottom = 4.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            // Expand/collapse icon
            if (hasChildren) {
                Box(
                    modifier = Modifier
                        .size(16.dp)
                        .clickable { onToggleExpand?.invoke(node.id) },
                    contentAlignment = Alignment.Center,
                ) {
                    Text(
                        text = if (isExpanded) "▼" else "▶",
                        color = theme.textMuted,
                        fontSize = 8.sp,
                    )
                }
            } else {
                Spacer(modifier = Modifier.width(16.dp))
            }

            // Node icon
            if (node.icon != null) {
                Text(
                    text = node.icon,
                    fontSize = 14.sp,
                    modifier = Modifier.padding(end = 4.dp),
                )
            }

            // Node label
            Text(
                text = node.label,
                color = if (node.disabled) theme.textMuted else theme.textPrimary,
                fontSize = 13.sp,
                fontWeight = if (isSelected) FontWeight.SemiBold else FontWeight.Normal,
                modifier = Modifier.weight(1f),
            )
        }

        // Children
        if (hasChildren && isExpanded) {
            TreeView(
                nodes = node.children,
                level = level + 1,
                expandedIds = expandedIds,
                selectedIds = selectedIds,
                onToggleExpand = onToggleExpand,
                onSelect = onSelect,
            )
        }
    }
}

@Composable
fun SimpleTreeView(
    nodes: List<TreeNode>,
    modifier: Modifier = Modifier,
    initiallyExpanded: Boolean = false,
    onSelect: ((String) -> Unit)? = null,
) {
    val expandedIds = remember { mutableStateOf<Set<String>>(emptySet()) }
    val selectedIds = remember { mutableStateOf<Set<String>>(emptySet()) }

    LaunchedEffect(initiallyExpanded) {
        if (initiallyExpanded) {
            expandedIds.value = expandAll(nodes)
        }
    }

    TreeView(
        nodes = nodes,
        modifier = modifier,
        expandedIds = expandedIds.value,
        selectedIds = selectedIds.value,
        onToggleExpand = { id ->
            expandedIds.value = expandedIds.value.toMutableSet().apply {
                if (contains(id)) remove(id) else add(id)
            }
        },
        onSelect = { id ->
            selectedIds.value = setOf(id)
            onSelect?.invoke(id)
        },
    )
}

private fun expandAll(nodes: List<TreeNode>): Set<String> {
    val result = mutableSetOf<String>()
    nodes.forEach { node ->
        result.add(node.id)
        result.addAll(expandAll(node.children))
    }
    return result
}
