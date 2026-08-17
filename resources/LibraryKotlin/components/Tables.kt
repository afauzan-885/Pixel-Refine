package org.pixelrefine.genericui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.theme.LocalGenericTheme

/**
 * Python: `DataTable(headers=[...], rows=[[...]])`
 */
@Composable
fun DataTable(
    headers: List<String>,
    rows: List<List<String>>,
    modifier: Modifier = Modifier,
) {
    val theme = LocalGenericTheme.current
    Column(
        modifier = modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(theme.radiusMd))
            .background(theme.bgCard)
            .border(1.dp, theme.borderColor, RoundedCornerShape(theme.radiusMd))
            .horizontalScroll(rememberScrollState()),
    ) {
        // Header row
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .background(theme.bgSecondary)
                .padding(horizontal = 12.dp, vertical = 8.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            headers.forEach { header ->
                Box(modifier = Modifier.weight(1f)) {
                    Text(
                        text = header,
                        color = theme.textPrimary,
                        fontWeight = FontWeight.Bold,
                        fontSize = 12.sp,
                    )
                }
            }
        }

        Box(modifier = Modifier.fillMaxWidth().height(1.dp).background(theme.borderColor))

        // Data rows
        rows.forEachIndexed { rowIndex, rowData ->
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 12.dp, vertical = 8.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                rowData.forEach { cell ->
                    Box(modifier = Modifier.weight(1f)) {
                        Text(
                            text = cell,
                            color = theme.textSecondary,
                            fontSize = 12.sp,
                        )
                    }
                }
            }
            if (rowIndex < rows.size - 1) {
                Box(modifier = Modifier.fillMaxWidth().height(1.dp).background(theme.borderColor))
            }
        }
    }
}
