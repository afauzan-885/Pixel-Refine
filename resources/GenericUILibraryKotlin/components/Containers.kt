package org.pixelrefine.genericui.components

import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxScope
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.RowScope
import androidx.compose.foundation.layout.Spacer as FoundationSpacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp

/**
 * Python: `Container(padding=10, layout="vertical")`
 */
@Composable
fun Container(
    padding: Dp = 10.dp,
    spacing: Dp = 10.dp,
    modifier: Modifier = Modifier,
    content: @Composable ColumnScope.() -> Unit,
) {
    Column(
        modifier = modifier.fillMaxWidth().padding(padding),
        verticalArrangement = Arrangement.spacedBy(spacing),
        content = content,
    )
}

/**
 * Python: `Row(spacing=10)`
 */
@Composable
fun Row(
    spacing: Dp = 10.dp,
    modifier: Modifier = Modifier,
    verticalAlignment: Alignment.Vertical? = null,
    horizontalArrangement: Arrangement.Horizontal? = null,
    content: @Composable RowScope.() -> Unit,
) {
    androidx.compose.foundation.layout.Row(
        modifier = modifier.fillMaxWidth(),
        verticalAlignment = verticalAlignment ?: Alignment.CenterVertically,
        horizontalArrangement = horizontalArrangement ?: Arrangement.spacedBy(spacing),
        content = content,
    )
}

/**
 * Python: `Col(spacing=10)`
 */
@Composable
fun Col(
    spacing: Dp = 10.dp,
    modifier: Modifier = Modifier,
    horizontalAlignment: Alignment.Horizontal? = null,
    verticalArrangement: Arrangement.Vertical? = null,
    content: @Composable ColumnScope.() -> Unit,
) {
    Column(
        modifier = modifier.fillMaxWidth(),
        horizontalAlignment = horizontalAlignment ?: Alignment.Start,
        verticalArrangement = verticalArrangement ?: Arrangement.spacedBy(spacing),
        content = content,
    )
}

/**
 * Python: `Stack()` (Z-index stacking)
 */
@Composable
fun Stack(
    modifier: Modifier = Modifier,
    contentAlignment: Alignment = Alignment.TopStart,
    content: @Composable BoxScope.() -> Unit,
) {
    Box(
        modifier = modifier.fillMaxSize(),
        contentAlignment = contentAlignment,
        content = content,
    )
}

/**
 * Python: `ScrollContainer()`
 */
@Composable
fun ScrollContainer(
    modifier: Modifier = Modifier,
    content: @Composable ColumnScope.() -> Unit,
) {
    Column(
        modifier = modifier.fillMaxSize().verticalScroll(rememberScrollState()),
        content = content,
    )
}

/**
 * Python: `Spacer(width=None, height=None)`
 */
@Composable
fun Spacer(
    width: Dp? = null,
    height: Dp? = null,
) {
    val m: Modifier = when {
        width != null && height != null -> Modifier.width(width).height(height)
        width != null -> Modifier.width(width)
        height != null -> Modifier.height(height)
        else -> Modifier
    }
    FoundationSpacer(m)
}

/**
 * Python: `HorizontalScrollRow(spacing=8)`
 */
@Composable
fun HorizontalScrollRow(
    spacing: Dp = 8.dp,
    modifier: Modifier = Modifier,
    content: @Composable RowScope.() -> Unit,
) {
    androidx.compose.foundation.layout.Row(
        modifier = modifier.fillMaxWidth().horizontalScroll(rememberScrollState()),
        horizontalArrangement = Arrangement.spacedBy(spacing),
        verticalAlignment = Alignment.CenterVertically,
        content = content,
    )
}

/**
 * Kolom scrollable layar penuh.
 */
@Composable
fun ScrollableColumn(
    modifier: Modifier = Modifier,
    content: @Composable ColumnScope.() -> Unit,
) {
    Column(
        modifier = modifier.fillMaxSize().verticalScroll(rememberScrollState()),
        content = content,
    )
}
