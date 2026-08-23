package org.pixelrefine.mobile.ui.sections

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.components.Variant
import org.pixelrefine.genericui.progress_bar
import org.pixelrefine.genericui.theme.LocalGenericTheme

/**
 * Section 5: Progress Bar & Notification Section (Sesuai Sketsa: [ ℹ️ ] [====> ] 60%).
 */
@Composable
fun ProgressNotificationSection(
    progressPercent: Int,
    statusMessage: String,
    modifier: Modifier = Modifier,
) {
    val theme = LocalGenericTheme.current

    Column(
        modifier = modifier
            .fillMaxWidth()
            .padding(horizontal = 12.dp, vertical = 6.dp),
        verticalArrangement = Arrangement.spacedBy(4.dp),
    ) {
        // Baris Progress Bar dengan Icon Info (i) & Persentase Sesuai Sketsa
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(theme.radiusLg))
                .background(theme.bgCard)
                .border(1.dp, theme.borderColor, RoundedCornerShape(theme.radiusLg))
                .padding(horizontal = 10.dp, vertical = 8.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(10.dp),
        ) {
            // Icon Info ℹ️
            Box(
                modifier = Modifier
                    .size(24.dp)
                    .clip(CircleShape)
                    .background(theme.info.copy(alpha = 0.15f))
                    .border(1.dp, theme.info.copy(alpha = 0.4f), CircleShape),
                contentAlignment = Alignment.Center,
            ) {
                Text(
                    text = "ℹ️",
                    fontSize = 11.sp,
                    fontWeight = FontWeight.Bold,
                    color = theme.info,
                )
            }

            // Real-time Progress Bar gaya Pythonic 1-baris
            Box(modifier = Modifier.weight(1f)) {
                progress_bar(
                    value = progressPercent,
                    max_value = 100,
                    variant = Variant.Primary,
                    show_label = false,
                    height = 14.dp,
                )
            }

            // Teks Persentase (60%) Sesuai Sketsa
            Text(
                text = "$progressPercent%",
                color = theme.textPrimary,
                fontSize = 13.sp,
                fontWeight = FontWeight.Bold,
            )
        }

        // Teks Notifikasi / Status Info
        Text(
            text = statusMessage,
            color = theme.textMuted,
            fontSize = 11.sp,
            modifier = Modifier.padding(horizontal = 4.dp),
        )
    }
}
