package org.pixelrefine.genericui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.gestures.detectDragGestures
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.unit.dp
import org.pixelrefine.genericui.theme.LocalGenericTheme

enum class SplitOrientation {
    HORIZONTAL,
    VERTICAL
}

/**
 * SplitPane Resizable Multi-Panel Container (Gaya Klasik Konsisten).
 */
@Composable
fun SplitPane(
    initialFraction: Float = 0.5f,
    orientation: SplitOrientation = SplitOrientation.HORIZONTAL,
    modifier: Modifier = Modifier,
    first: @Composable () -> Unit,
    second: @Composable () -> Unit,
) {
    val theme = LocalGenericTheme.current
    var fraction by remember { mutableFloatStateOf(initialFraction.coerceIn(0.1f, 0.9f)) }

    BoxWithConstraints(
        modifier = modifier
            .fillMaxSize()
            .clip(RoundedCornerShape(theme.radiusMd))
            .background(theme.bgPrimary),
    ) {
        val totalWidth = constraints.maxWidth.toFloat()
        val totalHeight = constraints.maxHeight.toFloat()

        if (orientation == SplitOrientation.HORIZONTAL) {
            Row(modifier = Modifier.fillMaxSize()) {
                Box(modifier = Modifier.weight(fraction).fillMaxHeight()) {
                    first()
                }
                // Resizable Divider
                Box(
                    modifier = Modifier
                        .width(4.dp)
                        .fillMaxHeight()
                        .background(theme.borderColor)
                        .pointerInput(Unit) {
                            detectDragGestures { change, dragAmount ->
                                change.consume()
                                if (totalWidth > 0) {
                                    fraction = (fraction + dragAmount.x / totalWidth).coerceIn(0.1f, 0.9f)
                                }
                            }
                        },
                )
                Box(modifier = Modifier.weight(1f - fraction).fillMaxHeight()) {
                    second()
                }
            }
        } else {
            Column(modifier = Modifier.fillMaxSize()) {
                Box(modifier = Modifier.weight(fraction).fillMaxWidth()) {
                    first()
                }
                // Resizable Divider
                Box(
                    modifier = Modifier
                        .height(4.dp)
                        .fillMaxWidth()
                        .background(theme.borderColor)
                        .pointerInput(Unit) {
                            detectDragGestures { change, dragAmount ->
                                change.consume()
                                if (totalHeight > 0) {
                                    fraction = (fraction + dragAmount.y / totalHeight).coerceIn(0.1f, 0.9f)
                                }
                            }
                        },
                )
                Box(modifier = Modifier.weight(1f - fraction).fillMaxWidth()) {
                    second()
                }
            }
        }
    }
}
