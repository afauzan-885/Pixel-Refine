package org.pixelrefine.genericui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.input.pointer.PointerEventType
import androidx.compose.ui.input.pointer.onPointerEvent
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Popup
import androidx.compose.ui.window.PopupProperties
import org.pixelrefine.genericui.theme.LocalGenericTheme
import androidx.compose.material3.Text
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.foundation.ExperimentalFoundationApi

enum class PopoverTrigger {
    Click, Hover
}

@OptIn(ExperimentalFoundationApi::class)
@Suppress("OPT_IN_USAGE")
@Composable
fun Popover(
    modifier: Modifier = Modifier,
    trigger: PopoverTrigger = PopoverTrigger.Click,
    isOpen: Boolean = false,
    onOpenChange: ((Boolean) -> Unit)? = null,
    variant: Variant = Variant.Primary,
    arrowSize: Dp = 8.dp,
    backgroundColor: androidx.compose.ui.graphics.Color? = null,
    content: @Composable () -> Unit,
    triggerContent: @Composable () -> Unit,
) {
    val theme = LocalGenericTheme.current
    val bgColor = backgroundColor ?: theme.bgCard
    val variantColor = variantColor(theme, variant)

    var isHovered by remember { mutableStateOf(false) }
    var isVisible by remember(isOpen) { mutableStateOf(isOpen) }

    LaunchedEffect(isHovered, trigger) {
        if (trigger == PopoverTrigger.Hover && isHovered) {
            isVisible = true
        } else if (trigger == PopoverTrigger.Hover && !isHovered) {
            isVisible = false
            onOpenChange?.invoke(false)
        }
    }

    Box(modifier = modifier) {
        Box(
            modifier = Modifier
                .clickable {
                    isVisible = !isVisible
                    onOpenChange?.invoke(isVisible)
                },
        ) {
            triggerContent()
        }

        if (isVisible) {
            Popup(
                alignment = Alignment.BottomCenter,
                properties = PopupProperties(focusable = true),
                onDismissRequest = {
                    isVisible = false
                    onOpenChange?.invoke(false)
                },
            ) {
                Box(
                    modifier = Modifier
                        .widthIn(min = 200.dp, max = 400.dp)
                        .padding(top = arrowSize)
                        .clip(RoundedCornerShape(8.dp))
                        .background(bgColor)
                        .border(1.dp, theme.borderColor, RoundedCornerShape(8.dp))
                        .padding(12.dp),
                ) {
                    Column {
                        content()
                    }
                }
            }
        }
    }
}

@Composable
fun PopoverContent(
    title: String? = null,
    description: String? = null,
    modifier: Modifier = Modifier,
) {
    val theme = LocalGenericTheme.current

    Column(modifier = modifier) {
        if (title != null) {
            Text(
                text = title,
                color = theme.textPrimary,
                fontSize = 14.sp,
                fontWeight = androidx.compose.ui.text.font.FontWeight.SemiBold,
            )
            if (description != null) {
                Spacer(modifier = Modifier.height(4.dp))
            }
        }
        if (description != null) {
            Text(
                text = description,
                color = theme.textSecondary,
                fontSize = 13.sp,
            )
        }
    }
}
