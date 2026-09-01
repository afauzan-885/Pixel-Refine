package org.pixelrefine.genericui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.theme.LocalGenericTheme
import androidx.compose.material3.Text

data class DescriptionItem(
    val label: String,
    val value: String,
    val span: Int = 1,
)

@Composable
fun Descriptions(
    items: List<DescriptionItem>,
    modifier: Modifier = Modifier,
    columns: Int = 2,
    title: String? = null,
    bordered: Boolean = true,
    size: DescriptionSize = DescriptionSize.Medium,
) {
    val theme = LocalGenericTheme.current
    val labelWidthFraction = 0.35f

    val fontSize = when (size) {
        DescriptionSize.Small -> 12.sp
        DescriptionSize.Medium -> 14.sp
        DescriptionSize.Large -> 16.sp
    }

    Column(
        modifier = modifier
            .background(theme.bgCard)
            .then(
                if (bordered) {
                    Modifier.border(1.dp, theme.borderColor)
                } else {
                    Modifier
                }
            ),
    ) {
        if (title != null) {
            Text(
                text = title,
                color = theme.textPrimary,
                fontSize = androidx.compose.ui.unit.TextUnit(fontSize.value + 2f, fontSize.type),
                fontWeight = FontWeight.SemiBold,
                modifier = Modifier.padding(12.dp),
            )
        }

        items.forEachIndexed { index, item ->
            DescriptionRow(
                item = item,
                columns = columns,
                labelWidthFraction = labelWidthFraction,
                fontSize = fontSize,
                bordered = bordered,
                isLast = index == items.lastIndex,
            )
        }
    }
}

@Composable
private fun DescriptionRow(
    item: DescriptionItem,
    columns: Int,
    labelWidthFraction: Float,
    fontSize: androidx.compose.ui.unit.TextUnit,
    bordered: Boolean,
    isLast: Boolean,
) {
    val theme = LocalGenericTheme.current

    Row(
        modifier = Modifier
            .fillMaxWidth()
            .then(
                if (bordered && !isLast) {
                    Modifier.border(0.dp, theme.borderColor)
                } else {
                    Modifier
                }
            ),
    ) {
        Box(
            modifier = Modifier
                .weight(labelWidthFraction)
                .background(theme.bgSecondary)
                .padding(12.dp),
        ) {
            Text(
                text = item.label,
                color = theme.textSecondary,
                fontSize = fontSize,
                fontWeight = FontWeight.Medium,
            )
        }

        Box(
            modifier = Modifier
                .weight(1f - labelWidthFraction)
                .padding(12.dp),
        ) {
            Text(
                text = item.value,
                color = theme.textPrimary,
                fontSize = fontSize,
            )
        }
    }
}

enum class DescriptionSize {
    Small, Medium, Large
}
