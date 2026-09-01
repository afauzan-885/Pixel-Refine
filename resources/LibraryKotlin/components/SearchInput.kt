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
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.Job
import org.pixelrefine.genericui.theme.LocalGenericTheme
import androidx.compose.material3.Text

@Composable
fun SearchInput(
    value: String,
    onValueChange: (String) -> Unit,
    modifier: Modifier = Modifier,
    placeholder: String = "Search...",
    onSearch: ((String) -> Unit)? = null,
    onClear: (() -> Unit)? = null,
    debounceMs: Long = 300L,
    enabled: Boolean = true,
    showIcon: Boolean = true,
    showClearButton: Boolean = true,
    isLoading: Boolean = false,
    variant: Variant = Variant.Primary,
) {
    val theme = LocalGenericTheme.current
    val variantColor = variantColor(theme, variant)
    val scope = rememberCoroutineScope()
    val debounceJob = remember { mutableStateOf<Job?>(null) }

    LaunchedEffect(value) {
        debounceJob.value?.cancel()
        if (debounceMs > 0 && value.isNotEmpty()) {
            debounceJob.value = scope.launch {
                delay(debounceMs)
                onSearch?.invoke(value)
            }
        }
    }

    Box(
        modifier = modifier
            .height(36.dp)
            .clip(RoundedCornerShape(18.dp))
            .background(theme.bgSecondary)
            .border(1.dp, theme.borderColor, RoundedCornerShape(18.dp))
            .padding(horizontal = 12.dp),
        contentAlignment = Alignment.CenterStart,
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            if (showIcon) {
                // Search icon placeholder
                Box(
                    modifier = Modifier
                        .size(16.dp)
                        .background(theme.textMuted.copy(alpha = 0.3f), CircleShape),
                )
            }

            androidx.compose.foundation.text.BasicTextField(
                value = value,
                onValueChange = onValueChange,
                enabled = enabled,
                textStyle = TextStyle(
                    color = if (enabled) theme.textPrimary else theme.textMuted,
                    fontSize = 14.sp,
                ),
                cursorBrush = SolidColor(variantColor),
                singleLine = true,
                modifier = Modifier.weight(1f),
            )

            if (isLoading) {
                // Loading indicator placeholder
                Box(
                    modifier = Modifier
                        .size(16.dp)
                        .background(variantColor, CircleShape),
                )
            } else if (showClearButton && value.isNotEmpty()) {
                Box(
                    modifier = Modifier
                        .size(18.dp)
                        .clip(CircleShape)
                        .background(theme.textMuted.copy(alpha = 0.2f))
                        .clickable {
                            onValueChange("")
                            onClear?.invoke()
                        },
                    contentAlignment = Alignment.Center,
                ) {
                    Text(
                        text = "×",
                        color = theme.textSecondary,
                        fontSize = 12.sp,
                    )
                }
            }
        }

        if (value.isEmpty() && placeholder.isNotEmpty()) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                if (showIcon) {
                    Box(
                        modifier = Modifier
                            .size(16.dp)
                            .background(theme.textMuted.copy(alpha = 0.3f), CircleShape),
                    )
                }
                Text(
                    text = placeholder,
                    color = theme.textMuted,
                    fontSize = 14.sp,
                )
            }
        }
    }
}

@Composable
fun SearchInputWithResults(
    value: String,
    onValueChange: (String) -> Unit,
    results: List<String>,
    onResultClick: (String) -> Unit,
    modifier: Modifier = Modifier,
    placeholder: String = "Search...",
    enabled: Boolean = true,
) {
    val theme = LocalGenericTheme.current
    var isExpanded by remember { mutableStateOf(false) }

    Column(modifier = modifier) {
        SearchInput(
            value = value,
            onValueChange = {
                onValueChange(it)
                isExpanded = it.isNotEmpty()
            },
            placeholder = placeholder,
            enabled = enabled,
        )

        if (isExpanded && results.isNotEmpty()) {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(top = 4.dp)
                    .clip(RoundedCornerShape(4.dp))
                    .background(theme.bgCard)
                    .border(1.dp, theme.borderColor, RoundedCornerShape(4.dp)),
            ) {
                Column {
                    results.forEach { result ->
                        Text(
                            text = result,
                            color = theme.textPrimary,
                            fontSize = 14.sp,
                            modifier = Modifier
                                .fillMaxWidth()
                                .clickable {
                                    onResultClick(result)
                                    isExpanded = false
                                }
                                .padding(horizontal = 12.dp, vertical = 8.dp),
                        )
                    }
                }
            }
        }
    }
}
