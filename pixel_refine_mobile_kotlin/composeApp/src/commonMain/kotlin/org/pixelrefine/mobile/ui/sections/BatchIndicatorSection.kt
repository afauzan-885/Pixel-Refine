package org.pixelrefine.mobile.ui.sections

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.dot_indicator
import org.pixelrefine.genericui.theme.LocalGenericTheme

/**
 * Section 4: Swipe Batch Dot Indicator (Sesuai Sketsa: • • ● • •).
 */
@Composable
fun BatchIndicatorSection(
    totalBatches: Int,
    selectedIndex: Int,
    onSelectBatch: (Int) -> Unit,
    modifier: Modifier = Modifier,
) {
    val theme = LocalGenericTheme.current

    Column(
        modifier = modifier
            .fillMaxWidth()
            .padding(vertical = 2.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        // Dot indicator gaya Pythonic 1-baris
        dot_indicator(
            count = totalBatches.coerceAtLeast(1),
            active_index = selectedIndex,
            on_index_changed = onSelectBatch,
        )

        Text(
            text = "Swipe Batch",
            color = theme.textMuted,
            fontSize = 11.sp,
            fontWeight = FontWeight.Medium,
        )
    }
}
