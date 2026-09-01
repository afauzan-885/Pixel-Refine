package org.pixelrefine.genericui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.gestures.detectDragGestures
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import org.pixelrefine.genericui.theme.LocalGenericTheme
import androidx.compose.foundation.gestures.detectTransformGestures

enum class ResizableDirection {
    Horizontal, Vertical
}

@Composable
fun Resizable(
    firstContent: @Composable () -> Unit,
    secondContent: @Composable () -> Unit,
    modifier: Modifier = Modifier,
    direction: ResizableDirection = ResizableDirection.Horizontal,
    initialFraction: Float = 0.5f,
    minFraction: Float = 0.1f,
    maxFraction: Float = 0.9f,
    handleWidth: Dp = 4.dp,
) {
    val theme = LocalGenericTheme.current
    var fraction by remember { mutableFloatStateOf(initialFraction.coerceIn(minFraction, maxFraction)) }

    if (direction == ResizableDirection.Horizontal) {
        BoxWithConstraints(
            modifier = modifier.fillMaxSize().clip(RoundedCornerShape(8.dp)).background(theme.bgPrimary),
        ) {
            val totalWidth = constraints.maxWidth.toFloat()

            Row(modifier = Modifier.fillMaxSize()) {
                Box(modifier = Modifier.weight(fraction).fillMaxHeight()) {
                    firstContent()
                }

                // Resize handle
                Box(
                    modifier = Modifier
                        .width(handleWidth)
                        .fillMaxHeight()
                        .background(theme.borderColor)
                        .pointerInput(Unit) {
                            detectDragGestures { change, dragAmount ->
                                change.consume()
                                if (totalWidth > 0) {
                                    fraction = (fraction + dragAmount.x / totalWidth).coerceIn(minFraction, maxFraction)
                                }
                            }
                        },
                )

                Box(modifier = Modifier.weight(1f - fraction).fillMaxHeight()) {
                    secondContent()
                }
            }
        }
    } else {
        BoxWithConstraints(
            modifier = modifier.fillMaxSize().clip(RoundedCornerShape(8.dp)).background(theme.bgPrimary),
        ) {
            val totalHeight = constraints.maxHeight.toFloat()

            Column(modifier = Modifier.fillMaxSize()) {
                Box(modifier = Modifier.weight(fraction).fillMaxWidth()) {
                    firstContent()
                }

                // Resize handle
                Box(
                    modifier = Modifier
                        .height(handleWidth)
                        .fillMaxWidth()
                        .background(theme.borderColor)
                        .pointerInput(Unit) {
                            detectDragGestures { change, dragAmount ->
                                change.consume()
                                if (totalHeight > 0) {
                                    fraction = (fraction + dragAmount.y / totalHeight).coerceIn(minFraction, maxFraction)
                                }
                            }
                        },
                )

                Box(modifier = Modifier.weight(1f - fraction).fillMaxWidth()) {
                    secondContent()
                }
            }
        }
    }
}
