package org.pixelrefine.genericui.components

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.input.pointer.PointerEventType
import androidx.compose.ui.input.pointer.onPointerEvent
import androidx.compose.ui.layout.onGloballyPositioned
import androidx.compose.ui.layout.positionInRoot
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.IntOffset
import androidx.compose.ui.unit.IntSize
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Popup
import androidx.compose.ui.window.PopupProperties
import kotlinx.coroutines.delay
import org.pixelrefine.genericui.theme.LocalGenericTheme
import androidx.compose.material3.Text
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.foundation.ExperimentalFoundationApi

enum class TooltipPosition {
    TOP, BOTTOM, LEFT, RIGHT
}

@OptIn(ExperimentalFoundationApi::class)
@Suppress("OPT_IN_USAGE")
@Composable
fun Tooltip(
    text: String,
    modifier: Modifier = Modifier,
    position: TooltipPosition = TooltipPosition.TOP,
    delayMs: Long = 500,
    backgroundColor: Color? = null,
    textColor: Color? = null,
    maxWidth: Dp = 200.dp,
    arrowSize: Dp = 6.dp,
    content: @Composable () -> Unit,
) {
    val theme = LocalGenericTheme.current
    var isVisible by remember { mutableStateOf(false) }
    var isHovered by remember { mutableStateOf(false) }
    var parentSize by remember { mutableStateOf(IntSize.Zero) }
    var parentPosition by remember { mutableStateOf(IntOffset.Zero) }

    val bgColor = backgroundColor ?: theme.dark
    val txtColor = textColor ?: theme.light

    LaunchedEffect(isHovered) {
        if (isHovered) {
            delay(delayMs)
            isVisible = true
        } else {
            isVisible = false
        }
    }

    Box(modifier = modifier) {
        Box(
            modifier = Modifier
                .onGloballyPositioned { coordinates ->
                    parentSize = coordinates.size
                    parentPosition = IntOffset(
                        coordinates.positionInRoot().x.toInt(),
                        coordinates.positionInRoot().y.toInt()
                    )
                }
                .clickable { isHovered = !isHovered }
        ) {
            content()
        }

        if (isVisible) {
            Popup(
                alignment = when (position) {
                    TooltipPosition.TOP -> Alignment.BottomCenter
                    TooltipPosition.BOTTOM -> Alignment.TopCenter
                    TooltipPosition.LEFT -> Alignment.CenterEnd
                    TooltipPosition.RIGHT -> Alignment.CenterStart
                },
                properties = PopupProperties(focusable = false),
            ) {
                Box(
                    modifier = Modifier
                        .widthIn(max = maxWidth)
                        .clip(RoundedCornerShape(4.dp))
                        .background(bgColor)
                        .border(1.dp, bgColor.copy(alpha = 0.2f), RoundedCornerShape(4.dp))
                        .padding(horizontal = 8.dp, vertical = 4.dp),
                ) {
                    Text(
                        text = text,
                        color = txtColor,
                        fontSize = 12.sp,
                    )
                }
            }
        }
    }
}

@Composable
fun TooltipBox(
    tooltip: String,
    modifier: Modifier = Modifier,
    position: TooltipPosition = TooltipPosition.TOP,
    content: @Composable () -> Unit,
) {
    Tooltip(
        text = tooltip,
        modifier = modifier,
        position = position,
        content = content,
    )
}

@OptIn(ExperimentalFoundationApi::class)
@Suppress("OPT_IN_USAGE")
@Composable
fun RichTooltip(
    title: String? = null,
    description: String? = null,
    modifier: Modifier = Modifier,
    position: TooltipPosition = TooltipPosition.TOP,
    delayMs: Long = 500,
    backgroundColor: Color? = null,
    maxWidth: Dp = 250.dp,
    content: @Composable () -> Unit,
) {
    val theme = LocalGenericTheme.current
    var isVisible by remember { mutableStateOf(false) }
    var isHovered by remember { mutableStateOf(false) }

    val bgColor = backgroundColor ?: theme.dark

    LaunchedEffect(isHovered) {
        if (isHovered) {
            delay(delayMs)
            isVisible = true
        } else {
            isVisible = false
        }
    }

    Box(modifier = modifier) {
        Box(
            modifier = Modifier
                .clickable { isHovered = !isHovered }
        ) {
            content()
        }

        if (isVisible) {
            Popup(
                alignment = when (position) {
                    TooltipPosition.TOP -> Alignment.BottomCenter
                    TooltipPosition.BOTTOM -> Alignment.TopCenter
                    TooltipPosition.LEFT -> Alignment.CenterEnd
                    TooltipPosition.RIGHT -> Alignment.CenterStart
                },
                properties = PopupProperties(focusable = false),
            ) {
                Box(
                    modifier = Modifier
                        .widthIn(max = maxWidth)
                        .clip(RoundedCornerShape(8.dp))
                        .background(bgColor)
                        .border(1.dp, bgColor.copy(alpha = 0.2f), RoundedCornerShape(8.dp))
                        .padding(12.dp),
                ) {
                    Column {
                        if (title != null) {
                            Text(
                                text = title,
                                color = theme.light,
                                fontSize = 14.sp,
                                fontWeight = androidx.compose.ui.text.font.FontWeight.Bold,
                            )
                            if (description != null) {
                                Spacer(modifier = Modifier.height(4.dp))
                            }
                        }
                        if (description != null) {
                            Text(
                                text = description,
                                color = theme.light.copy(alpha = 0.8f),
                                fontSize = 12.sp,
                            )
                        }
                    }
                }
            }
        }
    }
}
