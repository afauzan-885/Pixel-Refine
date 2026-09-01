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
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import org.pixelrefine.genericui.theme.LocalGenericTheme
import androidx.compose.material3.Text
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp

@Composable
fun NumberInput(
    value: Double,
    onValueChange: (Double) -> Unit,
    modifier: Modifier = Modifier,
    minVal: Double = 0.0,
    maxVal: Double = 100.0,
    step: Double = 1.0,
    enabled: Boolean = true,
    label: String? = null,
    showButtons: Boolean = true,
    showLabel: Boolean = true,
    variant: Variant = Variant.Primary,
) {
    val theme = LocalGenericTheme.current
    val variantColor = variantColor(theme, variant)

    Column(modifier = modifier) {
        if (label != null) {
            Text(
                text = label,
                color = theme.textSecondary,
                fontSize = 12.sp,
                modifier = Modifier.padding(bottom = 4.dp),
            )
        }

        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(4.dp),
        ) {
            if (showButtons) {
                NumberInputButton(
                    text = "−",
                    enabled = enabled && value > minVal,
                    variant = variant,
                    onClick = { onValueChange((value - step).coerceAtLeast(minVal)) },
                )
            }

            BasicNumberField(
                value = value,
                onValueChange = { newValue ->
                    newValue.toDoubleOrNull()?.let { v ->
                        onValueChange(v.coerceIn(minVal, maxVal))
                    }
                },
                enabled = enabled,
                modifier = Modifier.weight(1f),
            )

            if (showButtons) {
                NumberInputButton(
                    text = "+",
                    enabled = enabled && value < maxVal,
                    variant = variant,
                    onClick = { onValueChange((value + step).coerceAtMost(maxVal)) },
                )
            }
        }
    }
}

@Composable
private fun NumberInputButton(
    text: String,
    enabled: Boolean,
    variant: Variant,
    onClick: () -> Unit,
) {
    val theme = LocalGenericTheme.current
    val variantColor = variantColor(theme, variant)

    Box(
        modifier = Modifier
            .size(36.dp)
            .clip(RoundedCornerShape(4.dp))
            .background(if (enabled) variantColor.copy(alpha = 0.1f) else theme.bgSecondary)
            .border(1.dp, if (enabled) variantColor.copy(alpha = 0.3f) else theme.borderColor, RoundedCornerShape(4.dp))
            .clickable(enabled = enabled, onClick = onClick),
        contentAlignment = Alignment.Center,
    ) {
        Text(
            text = text,
            color = if (enabled) variantColor else theme.textMuted,
            fontSize = 18.sp,
            fontWeight = FontWeight.Bold,
        )
    }
}

@Composable
private fun BasicNumberField(
    value: Double,
    onValueChange: (String) -> Unit,
    enabled: Boolean,
    modifier: Modifier = Modifier,
) {
    val theme = LocalGenericTheme.current

    Box(
        modifier = modifier
            .height(36.dp)
            .clip(RoundedCornerShape(4.dp))
            .background(theme.bgSecondary)
            .border(1.dp, theme.borderColor, RoundedCornerShape(4.dp))
            .padding(horizontal = 12.dp),
        contentAlignment = Alignment.Center,
    ) {
        androidx.compose.foundation.text.BasicTextField(
            value = value.toString(),
            onValueChange = onValueChange,
            enabled = enabled,
            textStyle = androidx.compose.ui.text.TextStyle(
                color = if (enabled) theme.textPrimary else theme.textMuted,
                fontSize = 14.sp,
                textAlign = TextAlign.Center,
            ),
            keyboardOptions = androidx.compose.foundation.text.KeyboardOptions(
                keyboardType = KeyboardType.Number,
            ),
            singleLine = true,
            modifier = Modifier.fillMaxWidth(),
        )
    }
}

@Composable
fun IntNumberInput(
    value: Int,
    onValueChange: (Int) -> Unit,
    modifier: Modifier = Modifier,
    minVal: Int = 0,
    maxVal: Int = 100,
    step: Int = 1,
    enabled: Boolean = true,
    label: String? = null,
    showButtons: Boolean = true,
    variant: Variant = Variant.Primary,
) {
    NumberInput(
        value = value.toDouble(),
        onValueChange = { onValueChange(it.toInt()) },
        modifier = modifier,
        minVal = minVal.toDouble(),
        maxVal = maxVal.toDouble(),
        step = step.toDouble(),
        enabled = enabled,
        label = label,
        showButtons = showButtons,
        variant = variant,
    )
}
