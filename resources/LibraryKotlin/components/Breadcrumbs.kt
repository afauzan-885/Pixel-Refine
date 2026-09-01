package org.pixelrefine.genericui.components

import androidx.compose.foundation.clickable
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

data class BreadcrumbItem(
    val text: String,
    val onClick: (() -> Unit)? = null,
    val href: String? = null,
)

enum class BreadcrumbSeparator {
    Slash, Chevron, Dash, Arrow, Bullet
}

@Composable
fun Breadcrumbs(
    items: List<BreadcrumbItem>,
    modifier: Modifier = Modifier,
    separator: BreadcrumbSeparator = BreadcrumbSeparator.Slash,
    maxVisible: Int? = null,
    variant: Variant = Variant.Primary,
) {
    val theme = LocalGenericTheme.current
    val variantColor = variantColor(theme, variant)

    val visibleItems = if (maxVisible != null && items.size > maxVisible) {
        val first = items.first()
        val last = items.takeLast(maxVisible - 2)
        listOf(first) + listOf(BreadcrumbItem("...")) + last
    } else {
        items
    }

    val separatorText = when (separator) {
        BreadcrumbSeparator.Slash -> "/"
        BreadcrumbSeparator.Chevron -> "›"
        BreadcrumbSeparator.Dash -> "-"
        BreadcrumbSeparator.Arrow -> "→"
        BreadcrumbSeparator.Bullet -> "•"
    }

    Row(
        modifier = modifier,
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        visibleItems.forEachIndexed { index, item ->
            val isLast = index == visibleItems.lastIndex
            val isEllipsis = item.text == "..."

            if (isEllipsis) {
                Text(
                    text = item.text,
                    color = theme.textMuted,
                    fontSize = 13.sp,
                )
            } else {
                Text(
                    text = item.text,
                    color = if (isLast) theme.textPrimary else variantColor,
                    fontSize = 13.sp,
                    fontWeight = if (isLast) FontWeight.Medium else FontWeight.Normal,
                    modifier = if (item.onClick != null && !isLast) {
                        Modifier.clickable { item.onClick.invoke() }
                    } else {
                        Modifier
                    },
                )
            }

            if (!isLast) {
                Text(
                    text = separatorText,
                    color = theme.textMuted,
                    fontSize = 13.sp,
                )
            }
        }
    }
}

@Composable
fun SimpleBreadcrumbs(
    paths: List<String>,
    modifier: Modifier = Modifier,
    onItemClick: ((Int) -> Unit)? = null,
) {
    val items = paths.mapIndexed { index, path ->
        BreadcrumbItem(
            text = path,
            onClick = if (onItemClick != null) { { onItemClick(index) } } else null,
        )
    }

    Breadcrumbs(
        items = items,
        modifier = modifier,
    )
}
