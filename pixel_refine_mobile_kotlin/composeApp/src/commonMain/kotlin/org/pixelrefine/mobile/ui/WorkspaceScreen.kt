package org.pixelrefine.mobile.ui

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.delay
import org.pixelrefine.genericui.components.BackButton
import org.pixelrefine.genericui.components.BatchCard
import org.pixelrefine.genericui.components.BottomActionBar
import org.pixelrefine.genericui.components.BottomNavItem
import org.pixelrefine.genericui.components.ButtonGroup
import org.pixelrefine.genericui.components.DotIndicator
import org.pixelrefine.genericui.components.HorizontalScrollRow
import org.pixelrefine.genericui.components.NewBatchCard
import org.pixelrefine.genericui.components.ProgressBar
import org.pixelrefine.genericui.components.Row
import org.pixelrefine.genericui.components.Spacer
import org.pixelrefine.genericui.theme.LocalTheme
import org.pixelrefine.mobile.model.SAMPLE_BATCHES

/**
 * Screen Workspace ("Project Page") — mengikuti wireframe desain UI user:
 * status bar + header + batch strip + tab algoritma + panel parameter
 * + area preview + swipe batch + progress + bottom nav + FAB Start/Stop.
 * FAB benar-benar menjalankan simulasi pipeline.
 */
@Composable
fun WorkspaceScreen(
    toolName: String,
    onHome: () -> Unit,
    onSwitchTool: (String) -> Unit,
) {
    val theme = LocalTheme.current

    // State lokal (KISS — tidak perlu ViewModel untuk simulasi sederhana).
    var running by remember { mutableStateOf(false) }
    var progress by remember { mutableIntStateOf(0) }
    var status by remember { mutableStateOf("Ready") }
    var activeAlgo by remember { mutableIntStateOf(0) }
    var activeDot by remember { mutableIntStateOf(0) }
    var selectedBatch by remember { mutableStateOf(SAMPLE_BATCHES[0].first) }

    // Data tab algoritma + parameter (wireframe: Name / Parameter).
    val algoNames = listOf("Align", "SR/Denoise", "Ake2A", "Smart Merging")
    val algoParams = listOf("Method: AKAZE", "Strength: High", "Mode: Ake2A", "Merge: Smart")

    // Simulasi pipeline: Align -> Denoise -> SR -> Merge (placeholder processing).
    LaunchedEffect(running) {
        if (!running) return@LaunchedEffect
        val stages = listOf("Aligning frames...", "Denoising...", "Super resolving...", "Merging...")
        for (stage in stages) {
            status = stage
            val base = stages.indexOf(stage) * 25
            for (i in 1..25) {
                progress = base + i
                delay(80)
            }
        }
        status = "Done"
        progress = 100
        running = false
    }

    Column(modifier = Modifier.fillMaxSize().background(theme.bgSecondary)) {
        // ---- Status bar (wireframe: "12.30" + ikon sinyal/baterai) ----
        StatusBar()

        // ---- Header: kembali + "Project Page" ----
        Row(
            spacing = 8.dp,
            modifier = Modifier.fillMaxWidth().padding(horizontal = 10.dp),
        ) {
            BackButton(onClick = onHome)
            Text(
                "Project Page",
                color = theme.textPrimary,
                fontWeight = FontWeight.Bold,
                fontSize = 20.sp,
                modifier = Modifier.padding(start = 4.dp),
            )
        }

        // ---- Konten scrollable ----
        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 10.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            // Header batch + dropdown list (wireframe: "New Batch" / "Dropdown Batch list")
            Row(spacing = 8.dp, modifier = Modifier.fillMaxWidth()) {
                Text(
                    "Batches",
                    color = theme.textSecondary,
                    fontWeight = FontWeight.Bold,
                    fontSize = 11.sp,
                    modifier = Modifier.weight(1f),
                )
                Text(
                    "▾ Batch list",
                    color = theme.textMuted,
                    fontSize = 11.sp,
                    modifier = Modifier
                        .clip(RoundedCornerShape(theme.radiusSm))
                        .clickable { status = "Batch list dropdown tapped" }
                        .padding(2.dp),
                )
            }

            // Batch strip horizontal
            HorizontalScrollRow(spacing = 8.dp) {
                NewBatchCard(onClick = { status = "Create new batch tapped" })
                SAMPLE_BATCHES.forEach { (name, count) ->
                    BatchCard(
                        name = name,
                        imageCount = count,
                        onClick = { selectedBatch = name; status = "Selected: $name" },
                    )
                }
            }

            // Tab algoritma (wireframe: Align / SR-Denoise / ... / Smart Merging)
            ButtonGroup(
                options = algoNames,
                activeIndex = activeAlgo,
                onSelect = { activeAlgo = it },
            )

            // Panel parameter (wireframe: Name / Parameter)
            ParameterPanel(name = algoNames[activeAlgo], parameter = algoParams[activeAlgo])

            // Area preview (placeholder)
            PreviewArea()

            // Swipe batch + indikator titik (wireframe: "Swipe batch")
            Row(
                spacing = 8.dp,
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.Center,
            ) {
                Text("Swipe batch", color = theme.textMuted, fontSize = 10.sp)
            }
            DotIndicator(count = 7, activeIndex = activeDot, onIndexChanged = { activeDot = it })

            // Progress + status
            ProgressBar(value = progress)
            Text(
                status,
                color = if (running) theme.textSecondary else theme.textMuted,
                fontSize = 11.sp,
                modifier = Modifier.padding(bottom = 8.dp),
            )
        }

        // ---- Bottom action bar (wireframe: Home / Denoiser / MF Resolution + FAB) ----
        val activeNav = when (toolName) {
            "MFDenoiser" -> "Denoiser"
            "MFResolution" -> "MF Resolution"
            else -> "Home"
        }
        BottomActionBar(
            items = listOf(
                BottomNavItem("Home", "🏠"),
                BottomNavItem("Denoiser", "🖼️"),
                BottomNavItem("MF Resolution", "🌟"),
            ),
            activeItem = activeNav,
            primaryLabel = if (running) "Stop" else "Start",
            primaryRunning = running,
            onNavClick = { item ->
                when (item) {
                    "Home" -> onHome()
                    "Denoiser" -> onSwitchTool("MFDenoiser")
                    "MF Resolution" -> onSwitchTool("MFResolution")
                }
            },
            onPrimaryClick = { running = !running },
            modifier = Modifier.padding(10.dp),
        )
    }
}

/** Status bar — mirror wireframe: jam "12:30" kiri, ikon sinyal/baterai kanan. */
@Composable
private fun StatusBar() {
    val theme = LocalTheme.current
    Row(
        modifier = Modifier.fillMaxWidth().padding(horizontal = 10.dp, vertical = 4.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text("12:30", color = theme.textPrimary, fontWeight = FontWeight.Bold, fontSize = 14.sp)
        Box(Modifier.weight(1f))
        Text("📶", fontSize = 12.sp)
        Spacer(width = 8.dp)
        Text("🔋", fontSize = 12.sp)
    }
}

/** Panel parameter — wireframe "Name / Parameter". */
@Composable
private fun ParameterPanel(name: String, parameter: String) {
    val theme = LocalTheme.current
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(theme.radiusLg))
            .background(theme.bgCard)
            .border(1.dp, theme.borderColor, RoundedCornerShape(theme.radiusLg))
            .padding(12.dp),
        verticalArrangement = Arrangement.spacedBy(4.dp),
    ) {
        Text("Name: $name", color = theme.textPrimary, fontWeight = FontWeight.Bold, fontSize = 12.sp)
        Text("Parameter: $parameter", color = theme.textSecondary, fontSize = 11.sp)
    }
}

/** Area preview — placeholder Canvas (matahari + gunung), badge, label. */
@Composable
private fun PreviewArea() {
    val theme = LocalTheme.current
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .height(220.dp)
            .clip(RoundedCornerShape(theme.radiusLg))
            .background(theme.bgCard)
            .border(1.dp, theme.borderColor, RoundedCornerShape(theme.radiusLg)),
    ) {
        Canvas(modifier = Modifier.fillMaxSize()) {
            // Matahari
            drawCircle(
                color = Color(0xFFF39C12),
                radius = 22.dp.toPx(),
                center = Offset(size.width * 0.5f, size.height * 0.4f),
            )
            // Dua gunung (line art)
            val stroke = Stroke(width = 3.dp.toPx())
            val mountain1 = Path().apply {
                moveTo(0f, size.height * 0.78f)
                lineTo(size.width * 0.3f, size.height * 0.45f)
                lineTo(size.width * 0.55f, size.height * 0.78f)
            }
            val mountain2 = Path().apply {
                moveTo(size.width * 0.35f, size.height * 0.78f)
                lineTo(size.width * 0.7f, size.height * 0.4f)
                lineTo(size.width, size.height * 0.78f)
            }
            drawPath(mountain1, theme.textPrimary, style = stroke)
            drawPath(mountain2, theme.textPrimary, style = stroke)
        }
        // Badge kiri atas
        Box(
            modifier = Modifier
                .align(Alignment.TopStart)
                .padding(8.dp)
                .clip(RoundedCornerShape(4.dp))
                .background(Color(0x80000000))
                .padding(horizontal = 6.dp, vertical = 3.dp),
        ) {
            Text("IMG_001", color = Color.White, fontWeight = FontWeight.Bold, fontSize = 10.sp)
        }
        // Badge kanan atas
        Box(
            modifier = Modifier
                .align(Alignment.TopEnd)
                .padding(8.dp)
                .clip(RoundedCornerShape(4.dp))
                .background(Color(0x80000000))
                .padding(horizontal = 6.dp, vertical = 3.dp),
        ) {
            Text("📷 13 Images", color = Color.White, fontWeight = FontWeight.Bold, fontSize = 10.sp)
        }
        // Label bawah tengah
        Text(
            "Image (Reference)",
            color = theme.textSecondary,
            fontWeight = FontWeight.Bold,
            fontSize = 11.sp,
            modifier = Modifier.align(Alignment.BottomCenter).padding(bottom = 10.dp),
        )
    }
}
