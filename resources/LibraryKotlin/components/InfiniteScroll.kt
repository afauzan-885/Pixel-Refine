package org.pixelrefine.genericui.components

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.theme.LocalGenericTheme
import androidx.compose.material3.Text
import androidx.compose.foundation.clickable

@Composable
fun <T> InfiniteScroll(
    items: List<T>,
    onLoadMore: () -> Unit,
    modifier: Modifier = Modifier,
    isLoading: Boolean = false,
    hasMore: Boolean = true,
    endReachedThreshold: Int = 5,
    endMessage: String = "No more items",
    itemContent: @Composable (T) -> Unit,
) {
    val listState = rememberLazyListState()
    val theme = LocalGenericTheme.current

    LazyColumn(
        modifier = modifier,
        state = listState,
    ) {
        items(items) { item ->
            itemContent(item)
        }

        if (hasMore) {
            item {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    contentAlignment = Alignment.Center,
                ) {
                    if (isLoading) {
                        CircularProgressIndicator(
                            color = theme.primary,
                            strokeWidth = 2.dp,
                            modifier = Modifier.size(24.dp),
                        )
                    } else {
                        Text(
                            text = "Load more",
                            color = theme.primary,
                            fontSize = 13.sp,
                            textAlign = TextAlign.Center,
                            modifier = Modifier.clickable { onLoadMore() },
                        )
                    }
                }
            }
        } else {
            item {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    contentAlignment = Alignment.Center,
                ) {
                    Text(
                        text = endMessage,
                        color = theme.textMuted,
                        fontSize = 12.sp,
                        textAlign = TextAlign.Center,
                    )
                }
            }
        }
    }

    // Trigger load more when reaching end
    LaunchedEffect(listState, items.size) {
        if (hasMore && !isLoading) {
            val lastVisibleItem = listState.layoutInfo.visibleItemsInfo.lastOrNull()?.index ?: 0
            if (lastVisibleItem >= items.size - endReachedThreshold) {
                onLoadMore()
            }
        }
    }
}
