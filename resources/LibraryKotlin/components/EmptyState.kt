package org.pixelrefine.genericui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.theme.LocalGenericTheme

/**
 * Python: `EmptyState(title="No Data", description="", icon="📂")`
 */
@Composable
fun EmptyState(
    title: String = "No Data",
    description: String = "",
    icon: String = "📂",
    actionLabel: String = "",
    onAction: (() -> Unit)? = null,
    modifier: Modifier = Modifier,
) {
    val theme = LocalGenericTheme.current
    Column(
        modifier = modifier
            .fillMaxWidth()
            .padding(32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        Text(text = icon, fontSize = 40.sp)
        Text(
            text = title,
            color = theme.textPrimary,
            fontWeight = FontWeight.Bold,
            fontSize = 15.sp,
            textAlign = TextAlign.Center,
        )
        if (description.isNotEmpty()) {
            Text(
                text = description,
                color = theme.textMuted,
                fontSize = 12.sp,
                textAlign = TextAlign.Center,
            )
        }
        if (actionLabel.isNotEmpty() && onAction != null) {
            Spacer(height = 8.dp)
            Button(
                text = actionLabel,
                variant = Variant.Primary,
                onClick = onAction,
            )
        }
    }
}
