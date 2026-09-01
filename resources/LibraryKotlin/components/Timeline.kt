package org.pixelrefine.genericui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.theme.LocalGenericTheme
import androidx.compose.material3.Text

enum class TimelineItemStatus {
    Success, Processing, Pending, Error
}

data class TimelineItemData(
    val title: String,
    val description: String? = null,
    val timestamp: String? = null,
    val status: TimelineItemStatus = TimelineItemStatus.Pending,
    val icon: String? = null,
)

@Composable
fun Timeline(
    items: List<TimelineItemData>,
    modifier: Modifier = Modifier,
    showTimestamps: Boolean = true,
) {
    Column(modifier = modifier) {
        items.forEachIndexed { index, item ->
            TimelineItem(
                item = item,
                isLast = index == items.lastIndex,
                showTimestamp = showTimestamps,
            )
        }
    }
}

@Composable
private fun TimelineItem(
    item: TimelineItemData,
    isLast: Boolean,
    showTimestamp: Boolean,
) {
    val theme = LocalGenericTheme.current

    val statusColor = when (item.status) {
        TimelineItemStatus.Success -> theme.success
        TimelineItemStatus.Processing -> theme.primary
        TimelineItemStatus.Error -> theme.danger
        TimelineItemStatus.Pending -> theme.borderColor
    }

    Row(
        modifier = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.Top,
    ) {
        // Indicator column
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            modifier = Modifier.width(40.dp),
        ) {
            Box(
                modifier = Modifier
                    .size(24.dp)
                    .clip(CircleShape)
                    .background(statusColor),
                contentAlignment = Alignment.Center,
            ) {
                if (item.icon != null) {
                    Text(
                        text = item.icon,
                        color = theme.light,
                        fontSize = 12.sp,
                    )
                } else {
                    when (item.status) {
                        TimelineItemStatus.Success -> Text("✓", color = theme.light, fontSize = 12.sp, fontWeight = FontWeight.Bold)
                        TimelineItemStatus.Error -> Text("✕", color = theme.light, fontSize = 12.sp, fontWeight = FontWeight.Bold)
                        TimelineItemStatus.Processing -> Text("•", color = theme.light, fontSize = 16.sp, fontWeight = FontWeight.Bold)
                        TimelineItemStatus.Pending -> Box(modifier = Modifier.size(8.dp).background(theme.textMuted, CircleShape))
                    }
                }
            }

            if (!isLast) {
                Box(
                    modifier = Modifier
                        .width(2.dp)
                        .height(40.dp)
                        .background(theme.borderColor),
                )
            }
        }

        // Content
        Column(
            modifier = Modifier
                .weight(1f)
                .padding(start = 12.dp, bottom = if (isLast) 0.dp else 16.dp),
        ) {
            Text(
                text = item.title,
                color = theme.textPrimary,
                fontSize = 14.sp,
                fontWeight = FontWeight.SemiBold,
            )

            if (item.description != null) {
                Text(
                    text = item.description,
                    color = theme.textSecondary,
                    fontSize = 12.sp,
                    modifier = Modifier.padding(top = 4.dp),
                )
            }

            if (showTimestamp && item.timestamp != null) {
                Text(
                    text = item.timestamp,
                    color = theme.textMuted,
                    fontSize = 11.sp,
                    modifier = Modifier.padding(top = 4.dp),
                )
            }
        }
    }
}
