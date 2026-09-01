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
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.theme.LocalGenericTheme
import androidx.compose.material3.Text

@Composable
fun Chip(
    text: String,
    modifier: Modifier = Modifier,
    variant: Variant = Variant.Primary,
    selected: Boolean = false,
    enabled: Boolean = true,
    closable: Boolean = false,
    icon: ImageVector? = null,
    onClick: (() -> Unit)? = null,
    onClose: (() -> Unit)? = null,
) {
    val theme = LocalGenericTheme.current
    val variantColor = variantColor(theme, variant)
    val bgColor = if (selected) variantColor else variantColor.copy(alpha = 0.1f)
    val textColor = if (selected) theme.light else variantColor
    val borderColor = if (selected) variantColor else variantColor.copy(alpha = 0.3f)

    Row(
        modifier = modifier
            .clip(RoundedCornerShape(16.dp))
            .background(if (enabled) bgColor else bgColor.copy(alpha = 0.5f))
            .border(
                1.dp,
                if (enabled) borderColor else borderColor.copy(alpha = 0.5f),
                RoundedCornerShape(16.dp)
            )
            .then(
                if (onClick != null && enabled) {
                    Modifier.clickable { onClick() }
                } else {
                    Modifier
                }
            )
            .padding(horizontal = 12.dp, vertical = 6.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(4.dp),
    ) {
        if (icon != null) {
            // Icon placeholder
            Box(
                modifier = Modifier
                    .size(16.dp)
                    .background(textColor.copy(alpha = 0.3f), CircleShape),
            )
        }

        Text(
            text = text,
            color = if (enabled) textColor else textColor.copy(alpha = 0.5f),
            fontSize = 14.sp,
            fontWeight = FontWeight.Medium,
        )

        if (closable && onClose != null) {
            Box(
                modifier = Modifier
                    .size(16.dp)
                    .clip(CircleShape)
                    .background(textColor.copy(alpha = 0.2f))
                    .clickable { onClose() },
                contentAlignment = Alignment.Center,
            ) {
                Text(
                    text = "×",
                    color = textColor,
                    fontSize = 12.sp,
                )
            }
        }
    }
}

@Composable
fun ChipGroup(
    chips: List<ChipData>,
    modifier: Modifier = Modifier,
    selectedChips: Set<String> = emptySet(),
    onChipClick: ((String) -> Unit)? = null,
    onChipClose: ((String) -> Unit)? = null,
    multiSelect: Boolean = false,
    variant: Variant = Variant.Primary,
    spacing: Dp = 8.dp,
) {
    val theme = LocalGenericTheme.current

    Column(
        modifier = modifier,
        verticalArrangement = Arrangement.spacedBy(spacing),
    ) {
        chips.forEach { chip ->
            val isSelected = selectedChips.contains(chip.id)
            Chip(
                text = chip.text,
                variant = chip.variant ?: variant,
                selected = isSelected,
                enabled = chip.enabled,
                closable = chip.closable,
                icon = chip.icon,
                onClick = { onChipClick?.invoke(chip.id) },
                onClose = if (chip.closable) { { onChipClose?.invoke(chip.id) } } else null,
            )
        }
    }
}

data class ChipData(
    val id: String,
    val text: String,
    val variant: Variant? = null,
    val enabled: Boolean = true,
    val closable: Boolean = false,
    val icon: ImageVector? = null,
)

@Composable
fun FilterChip(
    text: String,
    selected: Boolean,
    onSelectedChange: (Boolean) -> Unit,
    modifier: Modifier = Modifier,
    variant: Variant = Variant.Primary,
    enabled: Boolean = true,
) {
    Chip(
        text = text,
        modifier = modifier,
        variant = variant,
        selected = selected,
        enabled = enabled,
        onClick = { onSelectedChange(!selected) },
    )
}

@Composable
fun InputChip(
    text: String,
    modifier: Modifier = Modifier,
    variant: Variant = Variant.Primary,
    onRemove: (() -> Unit)? = null,
) {
    Chip(
        text = text,
        modifier = modifier,
        variant = variant,
        closable = onRemove != null,
        onClose = onRemove,
    )
}

@Composable
fun ActionChip(
    text: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    variant: Variant = Variant.Primary,
    enabled: Boolean = true,
    icon: ImageVector? = null,
) {
    Chip(
        text = text,
        modifier = modifier,
        variant = variant,
        enabled = enabled,
        icon = icon,
        onClick = onClick,
    )
}

@Composable
fun Tag(
    text: String,
    modifier: Modifier = Modifier,
    variant: Variant = Variant.Primary,
    closable: Boolean = false,
    onClose: (() -> Unit)? = null,
) {
    val theme = LocalGenericTheme.current
    val variantColor = variantColor(theme, variant)

    Row(
        modifier = modifier
            .clip(RoundedCornerShape(4.dp))
            .background(variantColor.copy(alpha = 0.1f))
            .border(1.dp, variantColor.copy(alpha = 0.3f), RoundedCornerShape(4.dp))
            .padding(horizontal = 8.dp, vertical = 4.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(4.dp),
    ) {
        Text(
            text = text,
            color = variantColor,
            fontSize = 12.sp,
            fontWeight = FontWeight.Medium,
        )

        if (closable && onClose != null) {
            Box(
                modifier = Modifier
                    .size(14.dp)
                    .clip(CircleShape)
                    .background(variantColor.copy(alpha = 0.2f))
                    .clickable { onClose() },
                contentAlignment = Alignment.Center,
            ) {
                Text(
                    text = "×",
                    color = variantColor,
                    fontSize = 10.sp,
                )
            }
        }
    }
}
