package org.pixelrefine.genericui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.theme.LocalGenericTheme

/**
 * Kontrol Pilihan Segmen Gaya Pill Modern (Gaya Klasik Konsisten).
 */
@Composable
fun SegmentedControl(
    items: List<String>,
    selectedIndex: Int = 0,
    onItemSelected: (Int) -> Unit = {},
    variant: Variant = Variant.Primary,
    modifier: Modifier = Modifier,
    height: Dp = 32.dp,
    enabled: Boolean = true,
) {
    val theme = LocalGenericTheme.current
    val activeColor = variantColor(theme, variant)

    Row(
        modifier = modifier
            .fillMaxWidth()
            .height(height)
            .clip(RoundedCornerShape(theme.radiusMd))
            .background(theme.bgSecondary)
            .border(1.dp, theme.borderColor, RoundedCornerShape(theme.radiusMd))
            .padding(2.dp),
        horizontalArrangement = Arrangement.spacedBy(2.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        items.forEachIndexed { index, title ->
            val isSelected = index == selectedIndex
            val bg = if (isSelected) activeColor else Color.Transparent
            val textColor = if (isSelected) theme.textWhite else theme.textSecondary

            Box(
                modifier = Modifier
                    .weight(1f)
                    .clip(RoundedCornerShape(theme.radiusSm))
                    .background(bg)
                    .clickable(enabled = enabled) { onItemSelected(index) }
                    .padding(vertical = 4.dp),
                contentAlignment = Alignment.Center,
            ) {
                Text(
                    text = title,
                    color = textColor,
                    fontSize = 11.sp,
                    fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Medium,
                )
            }
        }
    }
}
