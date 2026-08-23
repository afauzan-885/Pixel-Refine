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
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.domain.models.BatchItem
import org.pixelrefine.genericui.new_batch_card
import org.pixelrefine.genericui.theme.LocalGenericTheme

/**
 * Section 1: Top Scrollable Batch Cards & New Batch Button (Sesuai Sketsa).
 */
@Composable
fun BatchHeaderSection(
    batches: List<BatchItem>,
    selectedIndex: Int,
    onSelectBatch: (Int) -> Unit,
    onNewBatch: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val theme = LocalGenericTheme.current
    val scrollState = rememberScrollState()

    Row(
        modifier = modifier
            .fillMaxWidth()
            .horizontalScroll(scrollState)
            .padding(horizontal = 12.dp, vertical = 6.dp),
        horizontalArrangement = Arrangement.spacedBy(10.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        // 1. New Batch Button Card (Gaya Pythonic 1-baris)
        new_batch_card(
            on_click = onNewBatch,
            modifier = Modifier.size(width = 85.dp, height = 95.dp),
        )

        // 2. Daftar Batch Cards dengan Dropdown Indicator & Mountain/Landscape Preview
        batches.forEachIndexed { index, batch ->
            val isSelected = index == selectedIndex
            BatchCardItem(
                batch = batch,
                isSelected = isSelected,
                onClick = { onSelectBatch(index) },
            )
        }
    }
}

@Composable
private fun BatchCardItem(
    batch: BatchItem,
    isSelected: Boolean,
    onClick: () -> Unit,
) {
    val theme = LocalGenericTheme.current
    val borderColor = if (isSelected) theme.primary else theme.borderColor
    val borderWidth = if (isSelected) 2.dp else 1.dp
    val bgColor = if (isSelected) theme.primary.copy(alpha = 0.06f) else theme.bgCard

    Column(
        modifier = Modifier
            .width(105.dp)
            .height(95.dp)
            .clip(RoundedCornerShape(theme.radiusLg))
            .background(bgColor)
            .border(borderWidth, borderColor, RoundedCornerShape(theme.radiusLg))
            .clickable(onClick = onClick)
            .padding(6.dp),
        verticalArrangement = Arrangement.SpaceBetween,
    ) {
        // Judul Batch
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Text(
                text = batch.name,
                color = theme.textPrimary,
                fontWeight = FontWeight.Bold,
                fontSize = 12.sp,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis,
            )
            Text(
                text = "${batch.imageCount}",
                color = theme.primary,
                fontWeight = FontWeight.SemiBold,
                fontSize = 10.sp,
            )
        }

        // Mountain / Landscape Sketch Placeholder Preview Sesuai Gambar
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(38.dp)
                .clip(RoundedCornerShape(theme.radiusSm))
                .background(theme.bgDark.copy(alpha = 0.05f))
                .border(1.dp, theme.borderColor.copy(alpha = 0.4f), RoundedCornerShape(theme.radiusSm)),
            contentAlignment = Alignment.Center,
        ) {
            Text(
                text = "⛰️ 🌄",
                fontSize = 16.sp,
            )
        }

        // Dropdown List Indicator (▼) di bagian bawah card
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.Center,
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Text(
                text = "▼",
                color = if (isSelected) theme.primary else theme.textMuted,
                fontSize = 8.sp,
                fontWeight = FontWeight.Bold,
            )
        }
    }
}
