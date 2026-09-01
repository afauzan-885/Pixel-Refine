package org.pixelrefine.genericui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.theme.LocalGenericTheme
import androidx.compose.material3.Text

@Composable
fun TextArea(
    value: String,
    onValueChange: (String) -> Unit,
    modifier: Modifier = Modifier,
    placeholder: String = "",
    label: String? = null,
    minLines: Int = 3,
    maxLines: Int = 10,
    maxLength: Int? = null,
    showCount: Boolean = false,
    enabled: Boolean = true,
    autoResize: Boolean = false,
    variant: Variant = Variant.Primary,
) {
    val theme = LocalGenericTheme.current
    val variantColor = variantColor(theme, variant)
    val currentLength = value.length
    val isOverLimit = maxLength != null && currentLength > maxLength

    Column(modifier = modifier) {
        if (label != null) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Text(
                    text = label,
                    color = theme.textSecondary,
                    fontSize = 12.sp,
                )
                if (showCount) {
                    Text(
                        text = if (maxLength != null) "$currentLength/$maxLength" else "$currentLength",
                        color = if (isOverLimit) theme.danger else theme.textMuted,
                        fontSize = 11.sp,
                    )
                }
            }
            Spacer(modifier = Modifier.height(4.dp))
        }

        val lineCount = value.count { it == '\n' } + 1
        val height = if (autoResize) {
            (lineCount.coerceIn(minLines, maxLines) * 24 + 16).dp
        } else {
            (minLines * 24 + 16).dp
        }

        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(height)
                .clip(RoundedCornerShape(4.dp))
                .background(theme.bgSecondary)
                .border(
                    1.dp,
                    if (isOverLimit) theme.danger else theme.borderColor,
                    RoundedCornerShape(4.dp)
                )
                .padding(horizontal = 12.dp, vertical = 8.dp),
        ) {
            androidx.compose.foundation.text.BasicTextField(
                value = value,
                onValueChange = { newValue ->
                    if (maxLength == null || newValue.length <= maxLength) {
                        onValueChange(newValue)
                    }
                },
                enabled = enabled,
                textStyle = TextStyle(
                    color = if (enabled) theme.textPrimary else theme.textMuted,
                    fontSize = 14.sp,
                ),
                cursorBrush = androidx.compose.ui.graphics.SolidColor(variantColor),
                modifier = Modifier.fillMaxSize(),
            )

            if (value.isEmpty() && placeholder.isNotEmpty()) {
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
fun AutoResizingTextArea(
    value: String,
    onValueChange: (String) -> Unit,
    modifier: Modifier = Modifier,
    placeholder: String = "",
    minLines: Int = 1,
    maxLines: Int = 5,
    enabled: Boolean = true,
) {
    TextArea(
        value = value,
        onValueChange = onValueChange,
        modifier = modifier,
        placeholder = placeholder,
        minLines = minLines,
        maxLines = maxLines,
        enabled = enabled,
        autoResize = true,
    )
}
