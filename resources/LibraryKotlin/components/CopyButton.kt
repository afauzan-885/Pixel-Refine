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
import androidx.compose.ui.platform.LocalClipboardManager
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.delay
import org.pixelrefine.genericui.theme.LocalGenericTheme
import androidx.compose.material3.Text

@Composable
fun CopyButton(
    textToCopy: String,
    modifier: Modifier = Modifier,
    label: String = "Copy",
    copiedLabel: String = "Copied!",
    timeoutMs: Long = 2000L,
    variant: Variant = Variant.Primary,
) {
    val theme = LocalGenericTheme.current
    val variantColor = variantColor(theme, variant)
    val clipboardManager = LocalClipboardManager.current
    var isCopied by remember { mutableStateOf(false) }

    LaunchedEffect(isCopied) {
        if (isCopied) {
            delay(timeoutMs)
            isCopied = false
        }
    }

    Box(
        modifier = modifier
            .clip(RoundedCornerShape(4.dp))
            .background(if (isCopied) theme.success.copy(alpha = 0.1f) else variantColor.copy(alpha = 0.1f))
            .border(1.dp, if (isCopied) theme.success else variantColor, RoundedCornerShape(4.dp))
            .clickable {
                clipboardManager.setText(androidx.compose.ui.text.AnnotatedString(textToCopy))
                isCopied = true
            }
            .padding(horizontal = 12.dp, vertical = 6.dp),
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(4.dp),
        ) {
            Text(
                text = if (isCopied) "✓" else "📋",
                fontSize = 12.sp,
            )
            Text(
                text = if (isCopied) copiedLabel else label,
                color = if (isCopied) theme.success else variantColor,
                fontSize = 12.sp,
                fontWeight = FontWeight.Medium,
            )
        }
    }
}

@Composable
fun CopyText(
    text: String,
    modifier: Modifier = Modifier,
    showIcon: Boolean = true,
    variant: Variant = Variant.Primary,
) {
    val theme = LocalGenericTheme.current
    val variantColor = variantColor(theme, variant)
    val clipboardManager = LocalClipboardManager.current
    var isCopied by remember { mutableStateOf(false) }

    LaunchedEffect(isCopied) {
        if (isCopied) {
            delay(2000L)
            isCopied = false
        }
    }

    Row(
        modifier = modifier
            .clip(RoundedCornerShape(4.dp))
            .background(theme.bgSecondary)
            .border(1.dp, theme.borderColor, RoundedCornerShape(4.dp))
            .padding(horizontal = 12.dp, vertical = 8.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.SpaceBetween,
    ) {
        Text(
            text = text,
            color = theme.textPrimary,
            fontSize = 13.sp,
            modifier = Modifier.weight(1f),
            maxLines = 1,
        )

        if (showIcon) {
            Box(
                modifier = Modifier
                    .size(24.dp)
                    .clip(RoundedCornerShape(4.dp))
                    .background(if (isCopied) theme.success else variantColor)
                    .clickable {
                        clipboardManager.setText(androidx.compose.ui.text.AnnotatedString(text))
                        isCopied = true
                    },
                contentAlignment = Alignment.Center,
            ) {
                Text(
                    text = if (isCopied) "✓" else "📋",
                    color = theme.light,
                    fontSize = 12.sp,
                )
            }
        }
    }
}
