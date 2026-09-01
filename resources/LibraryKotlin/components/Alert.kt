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
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.theme.LocalGenericTheme
import androidx.compose.material3.Text
import androidx.compose.foundation.shape.CircleShape

@Composable
fun Alert(
    title: String,
    description: String? = null,
    modifier: Modifier = Modifier,
    variant: Variant = Variant.Info,
    icon: String? = null,
    closable: Boolean = true,
    onClose: (() -> Unit)? = null,
    actionLabel: String? = null,
    onAction: (() -> Unit)? = null,
) {
    val theme = LocalGenericTheme.current
    val variantColor = variantColor(theme, variant)

    Row(
        modifier = modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(8.dp))
            .background(variantColor.copy(alpha = 0.1f))
            .border(1.dp, variantColor.copy(alpha = 0.3f), RoundedCornerShape(8.dp))
            .padding(12.dp),
        verticalAlignment = Alignment.Top,
        horizontalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        if (icon != null) {
            Box(
                modifier = Modifier
                    .size(32.dp)
                    .clip(CircleShape)
                    .background(variantColor.copy(alpha = 0.2f)),
                contentAlignment = Alignment.Center,
            ) {
                Text(
                    text = icon,
                    color = variantColor,
                    fontSize = 16.sp,
                )
            }
        }

        Column(
            modifier = Modifier.weight(1f),
            verticalArrangement = Arrangement.spacedBy(4.dp),
        ) {
            Text(
                text = title,
                color = theme.textPrimary,
                fontSize = 14.sp,
                fontWeight = FontWeight.SemiBold,
            )

            if (description != null) {
                Text(
                    text = description,
                    color = theme.textSecondary,
                    fontSize = 13.sp,
                )
            }

            if (actionLabel != null && onAction != null) {
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = actionLabel.uppercase(),
                    color = variantColor,
                    fontSize = 12.sp,
                    fontWeight = FontWeight.SemiBold,
                    modifier = Modifier.clickable { onAction() },
                )
            }
        }

        if (closable && onClose != null) {
            Box(
                modifier = Modifier
                    .size(24.dp)
                    .clip(CircleShape)
                    .background(variantColor.copy(alpha = 0.1f))
                    .clickable { onClose() },
                contentAlignment = Alignment.Center,
            ) {
                Text(
                    text = "×",
                    color = variantColor,
                    fontSize = 14.sp,
                )
            }
        }
    }
}

@Composable
fun SuccessAlert(
    title: String,
    description: String? = null,
    modifier: Modifier = Modifier,
    closable: Boolean = true,
    onClose: (() -> Unit)? = null,
) {
    Alert(
        title = title,
        description = description,
        modifier = modifier,
        variant = Variant.Success,
        icon = "✓",
        closable = closable,
        onClose = onClose,
    )
}

@Composable
fun WarningAlert(
    title: String,
    description: String? = null,
    modifier: Modifier = Modifier,
    closable: Boolean = true,
    onClose: (() -> Unit)? = null,
) {
    Alert(
        title = title,
        description = description,
        modifier = modifier,
        variant = Variant.Warning,
        icon = "⚠",
        closable = closable,
        onClose = onClose,
    )
}

@Composable
fun ErrorAlert(
    title: String,
    description: String? = null,
    modifier: Modifier = Modifier,
    closable: Boolean = true,
    onClose: (() -> Unit)? = null,
) {
    Alert(
        title = title,
        description = description,
        modifier = modifier,
        variant = Variant.Danger,
        icon = "✕",
        closable = closable,
        onClose = onClose,
    )
}

@Composable
fun InfoAlert(
    title: String,
    description: String? = null,
    modifier: Modifier = Modifier,
    closable: Boolean = true,
    onClose: (() -> Unit)? = null,
) {
    Alert(
        title = title,
        description = description,
        modifier = modifier,
        variant = Variant.Info,
        icon = "ⓘ",
        closable = closable,
        onClose = onClose,
    )
}
