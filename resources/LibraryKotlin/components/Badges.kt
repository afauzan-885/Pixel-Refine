package org.pixelrefine.genericui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
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
import org.pixelrefine.genericui.animations.pulseAnimation
import org.pixelrefine.genericui.theme.LocalGenericTheme

/**
 * Status Badge & Live Pill Indicator (Gaya Klasik Konsisten).
 */
@Composable
fun Badge(
    text: String = "",
    variant: Variant = Variant.Primary,
    pulsing: Boolean = false,
    showDot: Boolean = true,
    modifier: Modifier = Modifier,
) {
    val theme = LocalGenericTheme.current
    val color = variantColor(theme, variant)

    val pulseMod = if (pulsing) Modifier.pulseAnimation(enabled = true) else Modifier

    Row(
        modifier = modifier
            .clip(RoundedCornerShape(12.dp))
            .background(color.copy(alpha = 0.12f))
            .border(1.dp, color.copy(alpha = 0.3f), RoundedCornerShape(12.dp))
            .then(pulseMod)
            .padding(horizontal = 8.dp, vertical = 3.dp),
        horizontalArrangement = Arrangement.spacedBy(5.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        if (showDot) {
            Box(
                modifier = Modifier
                    .size(6.dp)
                    .clip(CircleShape)
                    .background(color),
            )
        }
        if (text.isNotEmpty()) {
            Text(
                text = text,
                color = color,
                fontSize = 10.sp,
                fontWeight = FontWeight.Bold,
            )
        }
    }
}
