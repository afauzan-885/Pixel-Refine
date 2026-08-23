package org.pixelrefine.mobile.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
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
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.badge
import org.pixelrefine.genericui.components.Variant
import org.pixelrefine.genericui.new_batch_card
import org.pixelrefine.genericui.theme.LocalGenericTheme
import org.pixelrefine.genericui.toast

/**
 * Home Page 2 (Recent Projects & Other Projects Sesuai Sketsa Home Page 2):
 * - Header: [ ← Back ] dan [ ↗ Export ]
 * - Section 1: Recent Project (+ New, IMG-001, IMG-002...)
 * - Section 2: Other project (Grid foto & batch)
 */
@Composable
fun HomeProjectsScreen(
    onBack: () -> Unit,
    onOpenProject: (String) -> Unit,
    modifier: Modifier = Modifier,
) {
    val theme = LocalGenericTheme.current
    val verticalScroll = rememberScrollState()
    val recentScroll = rememberScrollState()

    val recentProjects = listOf("IMG-001", "IMG-002", "BURST-003")
    val otherProjects = listOf("IMG-005", "IMG-004", "IMG-003", "IMG-002", "IMG-001", "IMG-000")

    Box(
        modifier = modifier
            .fillMaxSize()
            .background(theme.bgPrimary)
            .safeDrawingPadding(),
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(verticalScroll)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp),
        ) {
            // 1. Top Header Bar [ ← Back ] ... [ ↗ Export ]
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically,
            ) {
                // Back Button
                Row(
                    modifier = Modifier
                        .clip(RoundedCornerShape(theme.radiusMd))
                        .clickable(onClick = onBack)
                        .padding(horizontal = 6.dp, vertical = 4.dp),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(4.dp),
                ) {
                    Text(text = "←", fontSize = 18.sp, fontWeight = FontWeight.Bold, color = theme.textPrimary)
                    Text(text = "Back", fontSize = 14.sp, fontWeight = FontWeight.Bold, color = theme.textPrimary)
                }

                Text(
                    text = "Projects",
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Bold,
                    color = theme.textPrimary,
                )

                // Export Button
                Row(
                    modifier = Modifier
                        .clip(RoundedCornerShape(theme.radiusMd))
                        .background(theme.primary.copy(alpha = 0.1f))
                        .clickable {
                            toast("Exporting active batch results...", Variant.Success)
                        }
                        .padding(horizontal = 8.dp, vertical = 6.dp),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(4.dp),
                ) {
                    Text(text = "↗", fontSize = 14.sp, fontWeight = FontWeight.Bold, color = theme.primary)
                    Text(text = "Export", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = theme.primary)
                }
            }

            // 2. Section "Recent Project" Sesuai Sketsa
            Text(
                text = "Recent Project",
                color = theme.textPrimary,
                fontSize = 17.sp,
                fontWeight = FontWeight.Bold,
            )

            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .horizontalScroll(recentScroll),
                horizontalArrangement = Arrangement.spacedBy(10.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                // Tombol + New Sesuai Sketsa
                new_batch_card(
                    on_click = { onOpenProject("New") },
                    modifier = Modifier.size(width = 90.dp, height = 95.dp),
                )

                recentProjects.forEach { projectName ->
                    ProjectCardItem(
                        title = projectName,
                        onClick = { onOpenProject(projectName) },
                    )
                }
            }

            Spacer(Modifier.height(4.dp))

            // 3. Section "Other project" Grid Sesuai Sketsa
            Text(
                text = "Other project",
                color = theme.textPrimary,
                fontSize = 17.sp,
                fontWeight = FontWeight.Bold,
            )

            // Grid 3-Kolom Sesuai Sketsa
            Column(
                modifier = Modifier.fillMaxWidth(),
                verticalArrangement = Arrangement.spacedBy(10.dp),
            ) {
                otherProjects.chunked(3).forEach { rowItems ->
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(10.dp),
                    ) {
                        rowItems.forEach { item ->
                            Box(modifier = Modifier.weight(1f)) {
                                ProjectCardItem(
                                    title = item,
                                    onClick = { onOpenProject(item) },
                                    modifier = Modifier.fillMaxWidth(),
                                )
                            }
                        }
                        // Isi sisa kolom jika kurang dari 3
                        repeat(3 - rowItems.size) {
                            Spacer(Modifier.weight(1f))
                        }
                    }
                }
            }

            Spacer(Modifier.height(16.dp))
        }
    }
}

@Composable
private fun ProjectCardItem(
    title: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val theme = LocalGenericTheme.current

    Column(
        modifier = modifier
            .width(95.dp)
            .height(95.dp)
            .clip(RoundedCornerShape(theme.radiusLg))
            .background(theme.bgCard)
            .border(1.dp, theme.borderColor, RoundedCornerShape(theme.radiusLg))
            .clickable(onClick = onClick)
            .padding(6.dp),
        verticalArrangement = Arrangement.SpaceBetween,
    ) {
        // Checkbox icon [v] di kanan atas sesuai sketsa
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.End,
        ) {
            Box(
                modifier = Modifier
                    .size(14.dp)
                    .clip(RoundedCornerShape(3.dp))
                    .background(theme.primary.copy(alpha = 0.2f))
                    .border(1.dp, theme.primary, RoundedCornerShape(3.dp)),
                contentAlignment = Alignment.Center,
            ) {
                Text(text = "✓", color = theme.primary, fontSize = 8.sp, fontWeight = FontWeight.Bold)
            }
        }

        // Preview icon foto & garis deskripsi sesuai sketsa
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(4.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Text(text = "🖼️", fontSize = 16.sp)
            Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                Box(Modifier.width(20.dp).height(2.dp).background(theme.textMuted))
                Box(Modifier.width(14.dp).height(2.dp).background(theme.textMuted))
            }
        }

        // Nama Gambar (IMG-001)
        Text(
            text = title,
            color = theme.textPrimary,
            fontSize = 11.sp,
            fontWeight = FontWeight.Bold,
            maxLines = 1,
            overflow = TextOverflow.Ellipsis,
        )
    }
}
