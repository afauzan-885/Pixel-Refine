package org.pixelrefine.genericui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Popup
import androidx.compose.ui.window.PopupProperties
import org.pixelrefine.genericui.theme.LocalGenericTheme

/**
 * Dropdown kecil untuk pilihan inline (algorithm, filter, dsb).
 * Trigger button menampilkan selected value dengan panah ▼.
 * Popup muncul di bawah trigger dengan daftar opsi.
 */
@Composable
fun SmallDropdown(
    selected: String,
    options: List<String>,
    onSelect: (String) -> Unit,
    modifier: Modifier = Modifier,
) {
    val theme = LocalGenericTheme.current
    var expanded by remember { mutableStateOf(false) }

    Box(modifier = modifier) {
        // Trigger button
        Row(
            modifier = Modifier
                .clip(RoundedCornerShape(theme.radiusSm))
                .background(theme.primary.copy(alpha = 0.12f))
                .border(1.dp, theme.primary.copy(alpha = 0.3f), RoundedCornerShape(theme.radiusSm))
                .clickable { expanded = true }
                .padding(horizontal = 8.dp, vertical = 4.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(4.dp),
        ) {
            Text(
                text = "\u25BC",
                fontSize = 8.sp,
                color = theme.primary,
            )
            Text(
                text = selected,
                fontSize = 11.sp,
                fontWeight = FontWeight.SemiBold,
                color = theme.primary,
            )
        }

        // Dropdown popup
        if (expanded) {
            Popup(
                alignment = Alignment.BottomStart,
                onDismissRequest = { expanded = false },
                properties = PopupProperties(focusable = true),
            ) {
                Column(
                    modifier = Modifier
                        .widthIn(min = 100.dp)
                        .clip(RoundedCornerShape(theme.radiusMd))
                        .background(theme.bgCard)
                        .border(1.dp, theme.borderColor, RoundedCornerShape(theme.radiusMd))
                        .padding(4.dp),
                    verticalArrangement = Arrangement.spacedBy(2.dp),
                ) {
                    options.forEach { option ->
                        val isSelected = option == selected
                        Text(
                            text = option,
                            fontSize = 11.sp,
                            fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Normal,
                            color = if (isSelected) theme.primary else theme.textPrimary,
                            modifier = Modifier
                                .fillMaxWidth()
                                .clip(RoundedCornerShape(4.dp))
                                .background(if (isSelected) theme.primary.copy(alpha = 0.08f) else androidx.compose.ui.graphics.Color.Transparent)
                                .clickable {
                                    onSelect(option)
                                    expanded = false
                                }
                                .padding(horizontal = 8.dp, vertical = 5.dp),
                        )
                    }
                }
            }
        }
    }
}
