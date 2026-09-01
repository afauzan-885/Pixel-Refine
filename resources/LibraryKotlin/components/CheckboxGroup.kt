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

@Composable
fun CheckboxGroup(
    options: List<String>,
    selectedOptions: Set<String>,
    onSelectionChange: (Set<String>) -> Unit,
    modifier: Modifier = Modifier,
    title: String? = null,
    orientation: Orientation = Orientation.Vertical,
    enabled: Boolean = true,
    selectAll: Boolean = false,
    variant: Variant = Variant.Primary,
) {
    val theme = LocalGenericTheme.current
    val variantColor = variantColor(theme, variant)

    val layoutModifier = when (orientation) {
        Orientation.Vertical -> Modifier
        Orientation.Horizontal -> Modifier
    }

    Column(modifier = modifier) {
        if (title != null) {
            Row(
                modifier = Modifier.fillMaxWidth().padding(bottom = 8.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Text(
                    text = title,
                    color = theme.textPrimary,
                    fontSize = 14.sp,
                    fontWeight = FontWeight.SemiBold,
                )

                if (selectAll) {
                    Text(
                        text = if (selectedOptions.size == options.size) "Deselect All" else "Select All",
                        color = variantColor,
                        fontSize = 12.sp,
                        modifier = Modifier.clickable(enabled = enabled) {
                            if (selectedOptions.size == options.size) {
                                onSelectionChange(emptySet())
                            } else {
                                onSelectionChange(options.toSet())
                            }
                        },
                    )
                }
            }
        }

        if (orientation == Orientation.Horizontal) {
            Row(
                modifier = layoutModifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp),
            ) {
                options.forEach { option ->
                    CheckboxItem(
                        text = option,
                        checked = selectedOptions.contains(option),
                        enabled = enabled,
                        variant = variant,
                        onCheckedChange = { checked ->
                            val newSelection = selectedOptions.toMutableSet()
                            if (checked) {
                                newSelection.add(option)
                            } else {
                                newSelection.remove(option)
                            }
                            onSelectionChange(newSelection)
                        },
                    )
                }
            }
        } else {
            Column(
                modifier = layoutModifier,
                verticalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                options.forEach { option ->
                    CheckboxItem(
                        text = option,
                        checked = selectedOptions.contains(option),
                        enabled = enabled,
                        variant = variant,
                        onCheckedChange = { checked ->
                            val newSelection = selectedOptions.toMutableSet()
                            if (checked) {
                                newSelection.add(option)
                            } else {
                                newSelection.remove(option)
                            }
                            onSelectionChange(newSelection)
                        },
                    )
                }
            }
        }
    }
}

@Composable
private fun CheckboxItem(
    text: String,
    checked: Boolean,
    enabled: Boolean,
    variant: Variant,
    onCheckedChange: (Boolean) -> Unit,
) {
    val theme = LocalGenericTheme.current
    val variantColor = variantColor(theme, variant)

    Row(
        modifier = Modifier
            .clickable(enabled = enabled) { onCheckedChange(!checked) }
            .padding(vertical = 4.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        Box(
            modifier = Modifier
                .size(18.dp)
                .clip(RoundedCornerShape(2.dp))
                .background(if (checked) variantColor else theme.bgSecondary)
                .border(
                    1.dp,
                    if (checked) variantColor else theme.borderColor,
                    RoundedCornerShape(2.dp)
                ),
            contentAlignment = Alignment.Center,
        ) {
            if (checked) {
                Text(
                    text = "✓",
                    color = theme.light,
                    fontSize = 12.sp,
                    fontWeight = FontWeight.Bold,
                )
            }
        }

        Text(
            text = text,
            color = if (enabled) theme.textPrimary else theme.textMuted,
            fontSize = 14.sp,
        )
    }
}

enum class Orientation {
    Vertical, Horizontal
}
