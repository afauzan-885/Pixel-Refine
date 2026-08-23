package org.pixelrefine.mobile.ui.sections

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.animations.pulseAnimation
import org.pixelrefine.genericui.components.BottomNavItem
import org.pixelrefine.genericui.components.Variant
import org.pixelrefine.genericui.theme.LocalGenericTheme
import org.pixelrefine.genericui.toast

/**
 * Section 6: Bottom Action Bar & Big Circular Start / Stop FAB (Sesuai Sketsa).
 * Sesuai gambar:
 * - Sisi Kiri/Tengah: [ Home | Denoiser | MFResolution | ... ] (Scrollable Navigation)
 * - Sisi Kanan: Tombol Besar Melingkar [ Start / Stop ]
 */
@Composable
fun BottomActionBarSection(
    activeTab: String,
    onTabSelect: (String) -> Unit,
    isProcessing: Boolean,
    onToggleProcessing: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val theme = LocalGenericTheme.current
    val navScrollState = rememberScrollState()

    val navItems = listOf(
        BottomNavItem(name = "Home", icon = "🏠"),
        BottomNavItem(name = "Denoiser", icon = "📚"),
        BottomNavItem(name = "MFResolution", icon = "🗂"),
        BottomNavItem(name = "Action Bar", icon = "🔍"),
    )

    Row(
        modifier = modifier
            .fillMaxWidth()
            .padding(horizontal = 12.dp, vertical = 8.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(10.dp),
    ) {
        // 1. Scrollable Navigation Bar (Sisi Kiri / Tengah Sesuai Sketsa)
        Row(
            modifier = Modifier
                .weight(1f)
                .height(64.dp)
                .clip(RoundedCornerShape(theme.radiusLg))
                .background(theme.bgCard)
                .border(1.dp, theme.borderColor, RoundedCornerShape(theme.radiusLg))
                .horizontalScroll(navScrollState)
                .padding(horizontal = 6.dp, vertical = 4.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(4.dp),
        ) {
            navItems.forEach { item ->
                val isSelected = item.name == activeTab
                Column(
                    modifier = Modifier
                        .clip(RoundedCornerShape(theme.radiusMd))
                        .background(if (isSelected) theme.primary.copy(alpha = 0.1f) else Color.Transparent)
                        .clickable {
                            onTabSelect(item.name)
                            toast("Tab aktif: ${item.name}", Variant.Info)
                        }
                        .padding(horizontal = 12.dp, vertical = 6.dp),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.Center,
                ) {
                    Text(text = item.icon, fontSize = 18.sp)
                    Text(
                        text = item.name,
                        color = if (isSelected) theme.primary else theme.textSecondary,
                        fontSize = 10.sp,
                        fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Normal,
                    )
                }
            }
        }

        // 2. Tombol Besar Melingkar [ Start / Stop ] (Sisi Kanan Sesuai Sketsa)
        val fabColor = if (isProcessing) theme.danger else theme.primary
        val pulseModifier = if (isProcessing) Modifier.pulseAnimation(enabled = true) else Modifier

        Box(
            modifier = Modifier
                .size(68.dp)
                .shadow(6.dp, CircleShape)
                .clip(CircleShape)
                .background(theme.bgCard)
                .border(2.5.dp, fabColor, CircleShape)
                .then(pulseModifier)
                .clickable(onClick = onToggleProcessing),
            contentAlignment = Alignment.Center,
        ) {
            Column(
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center,
            ) {
                Text(
                    text = if (isProcessing) "Stop" else "Start",
                    color = fabColor,
                    fontSize = 13.sp,
                    fontWeight = FontWeight.Bold,
                )
                Text(
                    text = if (isProcessing) "⏸️" else "▶️",
                    fontSize = 11.sp,
                )
            }
        }
    }
}
