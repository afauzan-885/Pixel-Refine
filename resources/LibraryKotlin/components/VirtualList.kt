package org.pixelrefine.genericui.components

import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp

@Composable
fun VirtualList(
    itemCount: Int,
    modifier: Modifier = Modifier,
    isHorizontal: Boolean = false,
    itemHeight: Dp = 56.dp,
    contentPadding: Dp = 0.dp,
    content: @Composable (Int) -> Unit,
) {
    if (isHorizontal) {
        LazyRow(
            modifier = modifier.fillMaxWidth(),
            state = rememberLazyListState(),
            contentPadding = androidx.compose.foundation.layout.PaddingValues(horizontal = contentPadding),
        ) {
            itemsIndexed(items = (0 until itemCount).toList()) { _, index ->
                content(index)
            }
        }
    } else {
        LazyColumn(
            modifier = modifier.fillMaxSize(),
            state = rememberLazyListState(),
            contentPadding = androidx.compose.foundation.layout.PaddingValues(vertical = contentPadding),
        ) {
            itemsIndexed(items = (0 until itemCount).toList()) { _, index ->
                content(index)
            }
        }
    }
}
