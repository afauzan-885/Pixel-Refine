package org.pixelrefine.mobile.ui.sections

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.components.Variant
import org.pixelrefine.genericui.segmented_control
import org.pixelrefine.genericui.theme.LocalGenericTheme
import org.pixelrefine.genericui.toast

/**
 * Section 2: Segmented Algorithm Method Bar & Parameter Settings (Sesuai Sketsa).
 * [ Align | SR/Denoise | Ake2A | Smart Merging  ⚙️ ]
 */
@Composable
fun AlgorithmMethodBar(
    methods: List<String>,
    selectedIndex: Int,
    onSelectMethod: (Int) -> Unit,
    modifier: Modifier = Modifier,
) {
    val theme = LocalGenericTheme.current

    Row(
        modifier = modifier
            .fillMaxWidth()
            .padding(horizontal = 12.dp, vertical = 6.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        // 1. Segmented Control Bar gaya Pythonic 1-baris
        Box(modifier = Modifier.weight(1f)) {
            segmented_control(
                items = methods,
                selected_index = selectedIndex,
                on_select = onSelectMethod,
                variant = Variant.Primary,
            )
        }

        // 2. Tombol Parameter Settings ⚙️ (Name Parameter di Sketsa)
        Box(
            modifier = Modifier
                .size(36.dp)
                .clip(RoundedCornerShape(theme.radiusMd))
                .background(theme.bgCard)
                .border(1.dp, theme.borderColor, RoundedCornerShape(theme.radiusMd))
                .clickable {
                    toast("Parameter ${methods[selectedIndex]}: Preset Pro Active", Variant.Info)
                },
            contentAlignment = Alignment.Center,
        ) {
            Text(
                text = "⚙️",
                fontSize = 15.sp,
            )
        }
    }
}
