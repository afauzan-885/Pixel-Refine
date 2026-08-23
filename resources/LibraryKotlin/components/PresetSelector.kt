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
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.domain.presets.AlgorithmPreset
import org.pixelrefine.genericui.domain.presets.PresetStore
import org.pixelrefine.genericui.theme.LocalGenericTheme

/**
 * Dropdown / Selector Preset Algoritma Siap Pakai (Gaya Klasik Konsisten).
 */
@Composable
fun PresetSelector(
    selectedPresetId: String? = "night_denoise",
    onSelectPreset: (AlgorithmPreset) -> Unit = {},
    variant: Variant = Variant.Primary,
    modifier: Modifier = Modifier,
) {
    val theme = LocalGenericTheme.current
    val presets = PresetStore.getAllPresets()
    val activeColor = variantColor(theme, variant)

    Column(
        modifier = modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(theme.radiusMd))
            .background(theme.bgCard)
            .border(1.dp, theme.borderColor, RoundedCornerShape(theme.radiusMd))
            .padding(10.dp),
        verticalArrangement = Arrangement.spacedBy(6.dp),
    ) {
        Text("ALGORITHM PRESETS", color = theme.textMuted, fontSize = 10.sp, fontWeight = FontWeight.Bold)

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(6.dp),
        ) {
            presets.forEach { preset ->
                val isSelected = preset.id == selectedPresetId
                val bg = if (isSelected) activeColor else theme.bgSecondary
                val textColor = if (isSelected) theme.textWhite else theme.textSecondary

                Box(
                    modifier = Modifier
                        .weight(1f)
                        .clip(RoundedCornerShape(theme.radiusSm))
                        .background(bg)
                        .border(1.dp, if (isSelected) activeColor else theme.borderColor, RoundedCornerShape(theme.radiusSm))
                        .clickable { onSelectPreset(preset) }
                        .padding(vertical = 6.dp, horizontal = 4.dp),
                    contentAlignment = Alignment.Center,
                ) {
                    Text(
                        text = preset.name,
                        color = textColor,
                        fontSize = 10.sp,
                        fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Medium,
                        maxLines = 1,
                    )
                }
            }
        }
    }
}
