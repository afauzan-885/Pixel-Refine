package org.pixelrefine.genericui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.theme.LocalGenericTheme
import androidx.compose.material3.Text

enum class StatTrend {
    Up, Down, Neutral
}

data class StatData(
    val value: String,
    val label: String,
    val trend: StatTrend = StatTrend.Neutral,
    val trendValue: String? = null,
    val icon: String? = null,
    val variant: Variant = Variant.Primary,
    val prefix: String? = null,
    val suffix: String? = null,
)

@Composable
fun Statistic(
    data: StatData,
    modifier: Modifier = Modifier,
) {
    val theme = LocalGenericTheme.current
    val variantColor = variantColor(theme, data.variant)

    val trendColor = when (data.trend) {
        StatTrend.Up -> theme.success
        StatTrend.Down -> theme.danger
        StatTrend.Neutral -> theme.textMuted
    }

    val trendIcon = when (data.trend) {
        StatTrend.Up -> "↑"
        StatTrend.Down -> "↓"
        StatTrend.Neutral -> "→"
    }

    Column(
        modifier = modifier
            .clip(RoundedCornerShape(8.dp))
            .background(theme.bgCard)
            .border(1.dp, theme.borderColor, RoundedCornerShape(8.dp))
            .padding(16.dp),
    ) {
        if (data.icon != null) {
            Text(
                text = data.icon,
                fontSize = 24.sp,
                modifier = Modifier.padding(bottom = 8.dp),
            )
        }

        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.Bottom,
            horizontalArrangement = Arrangement.spacedBy(4.dp),
        ) {
            if (data.prefix != null) {
                Text(
                    text = data.prefix,
                    color = theme.textSecondary,
                    fontSize = 20.sp,
                )
            }

            Text(
                text = data.value,
                color = theme.textPrimary,
                fontSize = 28.sp,
                fontWeight = FontWeight.Bold,
            )

            if (data.suffix != null) {
                Text(
                    text = data.suffix,
                    color = theme.textSecondary,
                    fontSize = 16.sp,
                )
            }
        }

        Spacer(modifier = Modifier.height(4.dp))

        Text(
            text = data.label,
            color = theme.textMuted,
            fontSize = 13.sp,
        )

        if (data.trendValue != null) {
            Spacer(modifier = Modifier.height(8.dp))

            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(4.dp),
            ) {
                Text(
                    text = trendIcon,
                    color = trendColor,
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Bold,
                )
                Text(
                    text = data.trendValue,
                    color = trendColor,
                    fontSize = 12.sp,
                    fontWeight = FontWeight.SemiBold,
                )
            }
        }
    }
}

@Composable
fun StatisticGroup(
    stats: List<StatData>,
    modifier: Modifier = Modifier,
    columns: Int = 2,
    spacing: Dp = 12.dp,
) {
    Column(
        modifier = modifier,
        verticalArrangement = Arrangement.spacedBy(spacing),
    ) {
        stats.chunked(columns).forEach { rowStats ->
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(spacing),
            ) {
                rowStats.forEach { stat ->
                    Statistic(
                        data = stat,
                        modifier = Modifier.weight(1f),
                    )
                }
                // Fill empty cells
                repeat(columns - rowStats.size) {
                    Spacer(modifier = Modifier.weight(1f))
                }
            }
        }
    }
}
