package org.pixelrefine.genericui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
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

@Composable
fun Pagination(
    currentPage: Int,
    totalPages: Int,
    onPageChange: (Int) -> Unit,
    modifier: Modifier = Modifier,
    siblingCount: Int = 1,
    showFirstLast: Boolean = true,
    showPrevNext: Boolean = true,
    variant: Variant = Variant.Primary,
) {
    val theme = LocalGenericTheme.current
    val variantColor = variantColor(theme, variant)

    val pageNumbers = remember(currentPage, totalPages, siblingCount) {
        buildList {
            add(1)
            val start = maxOf(2, currentPage - siblingCount)
            val end = minOf(totalPages - 1, currentPage + siblingCount)

            if (start > 2) add(-1)
            for (i in start..end) add(i)
            if (end < totalPages - 1) add(-2)
            if (totalPages > 1) add(totalPages)
        }.distinct()
    }

    Row(
        modifier = modifier,
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(4.dp),
    ) {
        if (showFirstLast && currentPage > 1) {
            PaginationButton(
                text = "«",
                enabled = currentPage > 1,
                variant = variant,
                onClick = { onPageChange(1) },
            )
        }

        if (showPrevNext && currentPage > 1) {
            PaginationButton(
                text = "‹",
                enabled = currentPage > 1,
                variant = variant,
                onClick = { onPageChange(currentPage - 1) },
            )
        }

        pageNumbers.forEach { page ->
            if (page == -1 || page == -2) {
                Text(
                    text = "...",
                    color = theme.textMuted,
                    fontSize = 14.sp,
                    modifier = Modifier.padding(horizontal = 8.dp),
                )
            } else {
                PaginationButton(
                    text = page.toString(),
                    selected = page == currentPage,
                    variant = variant,
                    onClick = { onPageChange(page) },
                )
            }
        }

        if (showPrevNext && currentPage < totalPages) {
            PaginationButton(
                text = "›",
                enabled = currentPage < totalPages,
                variant = variant,
                onClick = { onPageChange(currentPage + 1) },
            )
        }

        if (showFirstLast && currentPage < totalPages) {
            PaginationButton(
                text = "»",
                enabled = currentPage < totalPages,
                variant = variant,
                onClick = { onPageChange(totalPages) },
            )
        }
    }
}

@Composable
private fun PaginationButton(
    text: String,
    selected: Boolean = false,
    enabled: Boolean = true,
    variant: Variant,
    onClick: () -> Unit,
) {
    val theme = LocalGenericTheme.current
    val variantColor = variantColor(theme, variant)

    Box(
        modifier = Modifier
            .size(32.dp)
            .clip(RoundedCornerShape(4.dp))
            .background(
                when {
                    selected -> variantColor
                    !enabled -> theme.bgSecondary
                    else -> theme.bgCard
                }
            )
            .border(
                1.dp,
                if (selected) variantColor else theme.borderColor,
                RoundedCornerShape(4.dp)
            )
            .clickable(enabled = enabled, onClick = onClick),
        contentAlignment = Alignment.Center,
    ) {
        Text(
            text = text,
            color = when {
                selected -> theme.light
                !enabled -> theme.textMuted
                else -> theme.textPrimary
            },
            fontSize = 14.sp,
            fontWeight = if (selected) FontWeight.Bold else FontWeight.Normal,
        )
    }
}

@Composable
fun SimplePagination(
    currentPage: Int,
    totalPages: Int,
    onPageChange: (Int) -> Unit,
    modifier: Modifier = Modifier,
) {
    Pagination(
        currentPage = currentPage,
        totalPages = totalPages,
        onPageChange = onPageChange,
        modifier = modifier,
        showFirstLast = false,
    )
}
