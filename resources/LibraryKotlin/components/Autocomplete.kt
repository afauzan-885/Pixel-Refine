package org.pixelrefine.genericui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.theme.LocalGenericTheme
import androidx.compose.material3.Text

@Composable
fun Autocomplete(
    value: String,
    onValueChange: (String) -> Unit,
    options: List<String>,
    onOptionSelected: ((String) -> Unit)? = null,
    modifier: Modifier = Modifier,
    placeholder: String = "Type to search...",
    enabled: Boolean = true,
    maxSuggestions: Int = 10,
    variant: Variant = Variant.Primary,
) {
    val theme = LocalGenericTheme.current
    val variantColor = variantColor(theme, variant)
    var isExpanded by remember { mutableStateOf(false) }

    val filteredOptions = remember(value, options) {
        if (value.isEmpty()) {
            options.take(maxSuggestions)
        } else {
            options.filter { it.contains(value, ignoreCase = true) }.take(maxSuggestions)
        }
    }

    Column(modifier = modifier) {
        Box {
            androidx.compose.foundation.text.BasicTextField(
                value = value,
                onValueChange = {
                    onValueChange(it)
                    isExpanded = it.isNotEmpty() && filteredOptions.isNotEmpty()
                },
                enabled = enabled,
                textStyle = TextStyle(
                    color = if (enabled) theme.textPrimary else theme.textMuted,
                    fontSize = 14.sp,
                ),
                modifier = Modifier
                    .fillMaxWidth()
                    .height(36.dp)
                    .clip(RoundedCornerShape(4.dp))
                    .background(theme.bgSecondary)
                    .border(1.dp, theme.borderColor, RoundedCornerShape(4.dp))
                    .padding(horizontal = 12.dp, vertical = 8.dp),
            )

            if (value.isEmpty() && placeholder.isNotEmpty()) {
                Text(
                    text = placeholder,
                    color = theme.textMuted,
                    fontSize = 14.sp,
                    modifier = Modifier
                        .padding(start = 12.dp, top = 8.dp)
                        .clickable { isExpanded = true },
                )
            }
        }

        DropdownMenu(
            expanded = isExpanded && filteredOptions.isNotEmpty(),
            onDismissRequest = { isExpanded = false },
            modifier = Modifier
                .fillMaxWidth(0.9f)
                .background(theme.bgCard),
        ) {
            filteredOptions.forEach { option ->
                DropdownMenuItem(
                    text = {
                        Text(
                            text = option,
                            color = theme.textPrimary,
                            fontSize = 13.sp,
                        )
                    },
                    onClick = {
                        onValueChange(option)
                        onOptionSelected?.invoke(option)
                        isExpanded = false
                    },
                )
            }
        }
    }
}

@Composable
fun AutocompleteWithFilter(
    value: String,
    onValueChange: (String) -> Unit,
    options: List<String>,
    filter: (String, String) -> Boolean = { option, query -> option.contains(query, ignoreCase = true) },
    modifier: Modifier = Modifier,
    placeholder: String = "Search...",
    enabled: Boolean = true,
    onOptionSelected: ((String) -> Unit)? = null,
) {
    val theme = LocalGenericTheme.current
    var isExpanded by remember { mutableStateOf(false) }

    val filtered = remember(value, options) {
        if (value.isEmpty()) options else options.filter { filter(it, value) }
    }

    Column(modifier = modifier) {
        Box {
            androidx.compose.foundation.text.BasicTextField(
                value = value,
                onValueChange = {
                    onValueChange(it)
                    isExpanded = it.isNotEmpty() && filtered.isNotEmpty()
                },
                enabled = enabled,
                textStyle = TextStyle(
                    color = if (enabled) theme.textPrimary else theme.textMuted,
                    fontSize = 14.sp,
                ),
                modifier = Modifier
                    .fillMaxWidth()
                    .height(36.dp)
                    .clip(RoundedCornerShape(4.dp))
                    .background(theme.bgSecondary)
                    .border(1.dp, theme.borderColor, RoundedCornerShape(4.dp))
                    .padding(horizontal = 12.dp, vertical = 8.dp),
            )

            if (value.isEmpty() && placeholder.isNotEmpty()) {
                Text(
                    text = placeholder,
                    color = theme.textMuted,
                    fontSize = 14.sp,
                    modifier = Modifier.padding(start = 12.dp, top = 8.dp),
                )
            }
        }

        DropdownMenu(
            expanded = isExpanded && filtered.isNotEmpty(),
            onDismissRequest = { isExpanded = false },
            modifier = Modifier
                .fillMaxWidth(0.9f)
                .background(theme.bgCard),
        ) {
            filtered.forEach { option ->
                DropdownMenuItem(
                    text = {
                        Text(
                            text = option,
                            color = theme.textPrimary,
                            fontSize = 13.sp,
                        )
                    },
                    onClick = {
                        onValueChange(option)
                        onOptionSelected?.invoke(option)
                        isExpanded = false
                    },
                )
            }
        }
    }
}
