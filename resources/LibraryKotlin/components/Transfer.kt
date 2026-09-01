package org.pixelrefine.genericui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
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

data class TransferItem(
    val id: String,
    val label: String,
    val description: String? = null,
    val disabled: Boolean = false,
)

@Composable
fun Transfer(
    sourceItems: List<TransferItem>,
    targetItems: List<TransferItem>,
    onSourceChange: (List<TransferItem>) -> Unit,
    onTargetChange: (List<TransferItem>) -> Unit,
    modifier: Modifier = Modifier,
    titles: Pair<String, String> = "Source" to "Target",
    showSearch: Boolean = false,
) {
    val theme = LocalGenericTheme.current
    var sourceSearch by remember { mutableStateOf("") }
    var targetSearch by remember { mutableStateOf("") }
    var selectedSource by remember { mutableStateOf<Set<String>>(emptySet()) }
    var selectedTarget by remember { mutableStateOf<Set<String>>(emptySet()) }

    val filteredSource = if (showSearch && sourceSearch.isNotEmpty()) {
        sourceItems.filter { it.label.contains(sourceSearch, ignoreCase = true) }
    } else sourceItems

    val filteredTarget = if (showSearch && targetSearch.isNotEmpty()) {
        targetItems.filter { it.label.contains(targetSearch, ignoreCase = true) }
    } else targetItems

    fun moveToTarget() {
        val itemsToMove = sourceItems.filter { selectedSource.contains(it.id) }
        onSourceChange(sourceItems.filterNot { selectedSource.contains(it.id) })
        onTargetChange(targetItems + itemsToMove)
        selectedSource = emptySet()
    }

    fun moveToSource() {
        val itemsToMove = targetItems.filter { selectedTarget.contains(it.id) }
        onTargetChange(targetItems.filterNot { selectedTarget.contains(it.id) })
        onSourceChange(sourceItems + itemsToMove)
        selectedTarget = emptySet()
    }

    Row(
        modifier = modifier,
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        // Source list
        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = titles.first,
                color = theme.textPrimary,
                fontSize = 14.sp,
                fontWeight = FontWeight.SemiBold,
                modifier = Modifier.padding(bottom = 8.dp),
            )

            if (showSearch) {
                SearchInput(
                    value = sourceSearch,
                    onValueChange = { sourceSearch = it },
                    placeholder = "Search source...",
                    modifier = Modifier.padding(bottom = 8.dp),
                )
            }

            TransferList(
                items = filteredSource,
                selectedIds = selectedSource,
                onSelectionChange = { selectedSource = it },
            )
        }

        // Control buttons
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            TransferButton(
                text = ">",
                enabled = selectedSource.isNotEmpty(),
                onClick = { moveToTarget() },
            )
            TransferButton(
                text = "<",
                enabled = selectedTarget.isNotEmpty(),
                onClick = { moveToSource() },
            )
        }

        // Target list
        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = titles.second,
                color = theme.textPrimary,
                fontSize = 14.sp,
                fontWeight = FontWeight.SemiBold,
                modifier = Modifier.padding(bottom = 8.dp),
            )

            if (showSearch) {
                SearchInput(
                    value = targetSearch,
                    onValueChange = { targetSearch = it },
                    placeholder = "Search target...",
                    modifier = Modifier.padding(bottom = 8.dp),
                )
            }

            TransferList(
                items = filteredTarget,
                selectedIds = selectedTarget,
                onSelectionChange = { selectedTarget = it },
            )
        }
    }
}

@Composable
private fun TransferList(
    items: List<TransferItem>,
    selectedIds: Set<String>,
    onSelectionChange: (Set<String>) -> Unit,
) {
    val theme = LocalGenericTheme.current

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .heightIn(min = 200.dp, max = 400.dp)
            .clip(RoundedCornerShape(4.dp))
            .background(theme.bgCard)
            .border(1.dp, theme.borderColor, RoundedCornerShape(4.dp)),
    ) {
        items.forEach { item ->
            val isSelected = selectedIds.contains(item.id)

            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(if (isSelected) theme.primary.copy(alpha = 0.1f) else Color.Transparent)
                    .clickable(enabled = !item.disabled) {
                        val newSelection = selectedIds.toMutableSet()
                        if (isSelected) {
                            newSelection.remove(item.id)
                        } else {
                            newSelection.add(item.id)
                        }
                        onSelectionChange(newSelection)
                    }
                    .padding(horizontal = 12.dp, vertical = 8.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Text(
                    text = item.label,
                    color = if (item.disabled) theme.textMuted else theme.textPrimary,
                    fontSize = 13.sp,
                    modifier = Modifier.weight(1f),
                )

                if (item.description != null) {
                    Text(
                        text = item.description,
                        color = theme.textMuted,
                        fontSize = 11.sp,
                    )
                }
            }
        }

        if (items.isEmpty()) {
            Text(
                text = "No items",
                color = theme.textMuted,
                fontSize = 12.sp,
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
            )
        }
    }
}

@Composable
private fun TransferButton(
    text: String,
    enabled: Boolean,
    onClick: () -> Unit,
) {
    val theme = LocalGenericTheme.current

    Box(
        modifier = Modifier
            .size(32.dp)
            .clip(CircleShape)
            .background(if (enabled) theme.primary else theme.bgSecondary)
            .clickable(enabled = enabled, onClick = onClick),
        contentAlignment = Alignment.Center,
    ) {
        Text(
            text = text,
            color = if (enabled) theme.light else theme.textMuted,
            fontSize = 14.sp,
            fontWeight = FontWeight.Bold,
        )
    }
}
