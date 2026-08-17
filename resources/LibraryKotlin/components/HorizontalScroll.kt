package org.pixelrefine.genericui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
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
import org.pixelrefine.genericui.domain.models.BatchStatus
import org.pixelrefine.genericui.theme.LocalGenericTheme

/**
 * Python: `BatchCard(name, image_count)`
 * Built-in deklaratif: bisa langsung menerima objek domain `BatchItem`
 */
@Composable
fun BatchCard(
    name: String,
    imageCount: Int,
    onClick: () -> Unit = {},
    status: BatchStatus = BatchStatus.IDLE,
    modifier: Modifier = Modifier,
) {
    val theme = LocalGenericTheme.current
    val statusColor = when (status) {
        BatchStatus.IDLE -> theme.primary
        BatchStatus.PROCESSING -> theme.warning
        BatchStatus.COMPLETED -> theme.success
        BatchStatus.ERROR -> theme.danger
    }

    Column(
        modifier = modifier
            .width(120.dp)
            .height(90.dp)
            .clip(RoundedCornerShape(theme.radiusLg))
            .background(theme.bgCard)
            .border(1.dp, theme.borderColor, RoundedCornerShape(theme.radiusLg))
            .clickable(onClick = onClick)
            .padding(8.dp),
        verticalArrangement = Arrangement.spacedBy(4.dp),
    ) {
        Text(
            text = name,
            color = theme.textPrimary,
            fontWeight = FontWeight.Bold,
            fontSize = 12.sp,
            maxLines = 1,
            overflow = TextOverflow.Ellipsis,
        )
        Box(Modifier.weight(1f))
        Text(
            text = "🖼 $imageCount",
            color = statusColor,
            fontWeight = FontWeight.Bold,
            fontSize = 10.sp,
        )
    }
}

/**
 * Overload plug-and-play untuk `BatchItem` domain model
 */
@Composable
fun BatchCard(
    batch: BatchItem,
    onClick: () -> Unit = {},
    modifier: Modifier = Modifier,
) {
    BatchCard(
        name = batch.name,
        imageCount = batch.imageCount,
        status = batch.status,
        onClick = onClick,
        modifier = modifier,
    )
}

/**
 * Python: `NewBatchCard()`
 */
@Composable
fun NewBatchCard(
    onClick: () -> Unit = {},
    modifier: Modifier = Modifier,
) {
    val theme = LocalGenericTheme.current
    Column(
        modifier = modifier
            .width(90.dp)
            .height(90.dp)
            .clip(RoundedCornerShape(theme.radiusLg))
            .background(Color(0xFFF0FDF4))
            .border(2.dp, theme.primary, RoundedCornerShape(theme.radiusLg))
            .clickable(onClick = onClick)
            .padding(8.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center,
    ) {
        Text("+", color = theme.primary, fontSize = 24.sp, fontWeight = FontWeight.Bold)
        Text("New Batch", color = theme.primary, fontSize = 10.sp, fontWeight = FontWeight.Bold)
    }
}
