package org.pixelrefine.mobile.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.safeDrawingPadding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.animations.ToastHost
import org.pixelrefine.genericui.theme.LocalGenericTheme
import org.pixelrefine.mobile.state.ProjectState
import org.pixelrefine.mobile.ui.sections.AlgorithmMethodBar
import org.pixelrefine.mobile.ui.sections.BatchHeaderSection
import org.pixelrefine.mobile.ui.sections.BatchIndicatorSection
import org.pixelrefine.mobile.ui.sections.BottomActionBarSection
import org.pixelrefine.mobile.ui.sections.MainViewportSection
import org.pixelrefine.mobile.ui.sections.ProgressNotificationSection

/**
 * Main Project Screen (Menyatukan seluruh sections sesuai gambar sketsa wireframe).
 */
@Composable
fun ProjectScreen(
    state: ProjectState = remember { ProjectState() },
    onBack: (() -> Unit)? = null,
    modifier: Modifier = Modifier,
) {
    val theme = LocalGenericTheme.current
    val verticalScroll = rememberScrollState()

    Box(
        modifier = modifier
            .fillMaxSize()
            .background(theme.bgPrimary)
            .safeDrawingPadding(),
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(verticalScroll),
        ) {
            // 0. Top Bar Mockup (12.30 • Project Page • Status Icons)
            TopBarHeader(onBack = onBack)

            // 1. Scrollable Batch Row (+ New Batch & Batch 1..4)
            BatchHeaderSection(
                batches = state.batches,
                selectedIndex = state.selectedBatchIndex,
                onSelectBatch = { idx -> state.selectBatch(idx) },
                onNewBatch = { state.addNewBatch() },
            )

            // 2. Algorithm Method Bar [ Align | SR/Denoise | Ake2A | Smart Merging  ⚙️ ]
            AlgorithmMethodBar(
                methods = state.algorithmMethods,
                selectedIndex = state.selectedMethodIndex,
                onSelectMethod = { idx -> state.selectedMethodIndex = idx },
            )

            // 3. Main Image Viewport (Mountain Sketch Canvas + IMG_001.dng + 13 Images Badge)
            MainViewportSection(
                batch = state.activeBatch,
                activeImage = state.activeImage,
            )

            // 4. Swipe Batch Dot Indicator (• • ● • •)
            BatchIndicatorSection(
                totalBatches = state.batches.size,
                selectedIndex = state.selectedBatchIndex,
                onSelectBatch = { idx -> state.selectBatch(idx) },
            )

            // 5. Progress Bar Notification Section (ℹ️ [======> ] 60%)
            ProgressNotificationSection(
                progressPercent = state.progressPercent,
                statusMessage = state.statusMessage,
            )

            Spacer(Modifier.height(4.dp))

            // 6. Bottom Action Bar (Nav + Big Circular Start / Stop FAB)
            BottomActionBarSection(
                activeTab = state.activeNavTab,
                onTabSelect = { tab -> state.activeNavTab = tab },
                isProcessing = state.isProcessing,
                onToggleProcessing = { state.toggleProcessing() },
            )

            Spacer(Modifier.height(16.dp))
        }

        // Host Toast Global
        ToastHost()
    }
}

@Composable
private fun TopBarHeader(
    onBack: (() -> Unit)? = null,
) {
    val theme = LocalGenericTheme.current
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 14.dp, vertical = 8.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        if (onBack != null) {
            Row(
                modifier = Modifier
                    .clip(RoundedCornerShape(theme.radiusMd))
                    .clickable(onClick = onBack)
                    .padding(end = 8.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Text(
                    text = "←",
                    color = theme.textPrimary,
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold,
                )
            }
        }

        Text(
            text = "12:30",
            color = theme.textPrimary,
            fontSize = 12.sp,
            fontWeight = FontWeight.Bold,
        )

        Spacer(Modifier.weight(1f))

        Text(
            text = "Project Page",
            color = theme.textPrimary,
            fontSize = 16.sp,
            fontWeight = FontWeight.Bold,
        )

        Spacer(Modifier.weight(1f))

        Text(
            text = "📶 🔋",
            fontSize = 12.sp,
        )
    }
}
