package org.pixelrefine.mobile.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.safeDrawingPadding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.badge
import org.pixelrefine.genericui.components.Variant
import org.pixelrefine.genericui.theme.LocalGenericTheme
import org.pixelrefine.genericui.toast

/**
 * Home Page (Sesuai Sketsa Home Page):
 * - Card 1: Denoising ("Analyze burst image to remove noise and enhance detail") -> Project Workspace
 * - Card 2: HDR stack ("Stacking image with different exposure to produce a high dynamic range image")
 * - Card 3: Panorama
 * - Section Footer: Quick Access to Recent Projects
 */
@Composable
fun HomeScreen(
    onOpenDenoising: () -> Unit,
    onOpenProjects: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val theme = LocalGenericTheme.current
    val scrollState = rememberScrollState()

    Box(
        modifier = modifier
            .fillMaxSize()
            .background(theme.bgPrimary)
            .safeDrawingPadding(),
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(scrollState)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp),
        ) {
            // Header Top Bar
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Text(
                    text = "Home Page",
                    color = theme.textPrimary,
                    fontSize = 20.sp,
                    fontWeight = FontWeight.ExtraBold,
                )
                // Shortcut ke Home Page 2 (Recent Projects)
                Box(
                    modifier = Modifier
                        .clip(RoundedCornerShape(theme.radiusMd))
                        .background(theme.primary.copy(alpha = 0.1f))
                        .clickable(onClick = onOpenProjects)
                        .padding(horizontal = 10.dp, vertical = 6.dp),
                ) {
                    Text(
                        text = "📁 Projects ➔",
                        color = theme.primary,
                        fontSize = 12.sp,
                        fontWeight = FontWeight.Bold,
                    )
                }
            }

            Text(
                text = "Pilih modul komputasi fotografi:",
                color = theme.textSecondary,
                fontSize = 13.sp,
            )

            // 1. Modul Denoising Card (Utama) Sesuai Sketsa
            ModuleCard(
                title = "Denoising",
                description = "Analyze burst image to remove noise and enhance detail",
                icon = "✨ 📸",
                badgeText = "AOT Accelerated",
                variant = Variant.Primary,
                onClick = onOpenDenoising,
            )

            // 2. Modul HDR Stack Card Sesuai Sketsa
            ModuleCard(
                title = "HDR stack",
                description = "Stacking image with different exposure to produce a high dynamic range image",
                icon = "☀️ 🏔️",
                badgeText = "Multi-Exposure",
                variant = Variant.Info,
                onClick = {
                    toast("Modul HDR stack siap digunakan", Variant.Info)
                },
            )

            // 3. Modul Panorama Card Sesuai Sketsa
            ModuleCard(
                title = "Panorama",
                description = "Stitch multiple horizontal & vertical photos into an ultra-wide panoramic canvas",
                icon = "🖼️ 🌐",
                badgeText = "Feature Matching",
                variant = Variant.Warning,
                onClick = {
                    toast("Modul Panorama siap digunakan", Variant.Warning)
                },
            )

            Spacer(Modifier.height(10.dp))
        }
    }
}

@Composable
private fun ModuleCard(
    title: String,
    description: String,
    icon: String,
    badgeText: String,
    variant: Variant,
    onClick: () -> Unit,
) {
    val theme = LocalGenericTheme.current

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(theme.radiusLg))
            .background(theme.bgCard)
            .border(1.5.dp, theme.borderColor, RoundedCornerShape(theme.radiusLg))
            .clickable(onClick = onClick)
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp),
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                Text(text = icon, fontSize = 20.sp)
                Text(
                    text = title,
                    color = theme.textPrimary,
                    fontSize = 17.sp,
                    fontWeight = FontWeight.Bold,
                )
            }

            badge(
                text = badgeText,
                variant = variant,
                show_pulse = false,
                show_dot = true,
            )
        }

        Text(
            text = description,
            color = theme.textSecondary,
            fontSize = 13.sp,
            lineHeight = 18.sp,
        )

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.End,
        ) {
            Text(
                text = "Buka Modul ➔",
                color = theme.primary,
                fontSize = 12.sp,
                fontWeight = FontWeight.Bold,
            )
        }
    }
}
