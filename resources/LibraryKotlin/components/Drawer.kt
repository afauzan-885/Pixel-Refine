package org.pixelrefine.genericui.components

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.slideInHorizontally
import androidx.compose.animation.slideInVertically
import androidx.compose.animation.slideOutHorizontally
import androidx.compose.animation.slideOutVertically
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.gestures.detectDragGestures
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.theme.LocalGenericTheme
import androidx.compose.material3.Text
import androidx.compose.foundation.gestures.detectTransformGestures

enum class DrawerPosition {
    Left, Right, Top, Bottom
}

@Composable
fun Drawer(
    visible: Boolean,
    onDismissRequest: () -> Unit,
    modifier: Modifier = Modifier,
    position: DrawerPosition = DrawerPosition.Left,
    width: Dp = 280.dp,
    height: Dp = 300.dp,
    showScrim: Boolean = true,
    scrimColor: Color = Color.Black.copy(alpha = 0.5f),
    closeOnScrimClick: Boolean = true,
    content: @Composable () -> Unit,
) {
    Box(modifier = modifier.fillMaxSize()) {
        // Scrim
        if (showScrim) {
            AnimatedVisibility(
                visible = visible,
                enter = fadeIn(animationSpec = tween(300)),
                exit = fadeOut(animationSpec = tween(300)),
            ) {
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .background(scrimColor)
                        .clickable(enabled = closeOnScrimClick) { onDismissRequest() },
                )
            }
        }

        // Drawer content
        AnimatedVisibility(
            visible = visible,
            enter = when (position) {
                DrawerPosition.Left -> slideInHorizontally(initialOffsetX = { -it }, animationSpec = tween(300))
                DrawerPosition.Right -> slideInHorizontally(initialOffsetX = { it }, animationSpec = tween(300))
                DrawerPosition.Top -> slideInVertically(initialOffsetY = { -it }, animationSpec = tween(300))
                DrawerPosition.Bottom -> slideInVertically(initialOffsetY = { it }, animationSpec = tween(300))
            },
            exit = when (position) {
                DrawerPosition.Left -> slideOutHorizontally(targetOffsetX = { -it }, animationSpec = tween(300))
                DrawerPosition.Right -> slideOutHorizontally(targetOffsetX = { it }, animationSpec = tween(300))
                DrawerPosition.Top -> slideOutVertically(targetOffsetY = { -it }, animationSpec = tween(300))
                DrawerPosition.Bottom -> slideOutVertically(targetOffsetY = { it }, animationSpec = tween(300))
            },
        ) {
            val drawerModifier = when (position) {
                DrawerPosition.Left, DrawerPosition.Right -> {
                    Modifier
                        .fillMaxHeight()
                        .width(width)
                        .align(if (position == DrawerPosition.Left) Alignment.CenterStart else Alignment.CenterEnd)
                }
                DrawerPosition.Top, DrawerPosition.Bottom -> {
                    Modifier
                        .fillMaxWidth()
                        .height(height)
                        .align(if (position == DrawerPosition.Top) Alignment.TopCenter else Alignment.BottomCenter)
                }
            }

            val theme = LocalGenericTheme.current
            Box(
                modifier = drawerModifier
                    .background(theme.bgCard)
                    .border(1.dp, theme.borderColor)
                    .pointerInput(Unit) {
                        detectDragGestures { change, dragAmount ->
                            // Close on swipe
                            val threshold = 100f
                            when (position) {
                                DrawerPosition.Left -> if (dragAmount.x < -threshold) onDismissRequest()
                                DrawerPosition.Right -> if (dragAmount.x > threshold) onDismissRequest()
                                DrawerPosition.Top -> if (dragAmount.y < -threshold) onDismissRequest()
                                DrawerPosition.Bottom -> if (dragAmount.y > threshold) onDismissRequest()
                            }
                        }
                    },
            ) {
                content()
            }
        }
    }
}

@Composable
fun DrawerHeader(
    title: String,
    modifier: Modifier = Modifier,
    onClose: (() -> Unit)? = null,
) {
    val theme = LocalGenericTheme.current

    Row(
        modifier = modifier
            .fillMaxWidth()
            .padding(16.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(
            text = title,
            color = theme.textPrimary,
            fontSize = 18.sp,
            fontWeight = FontWeight.SemiBold,
        )

        if (onClose != null) {
            Box(
                modifier = Modifier
                    .size(28.dp)
                    .clip(CircleShape)
                    .background(theme.bgSecondary)
                    .clickable { onClose() },
                contentAlignment = Alignment.Center,
            ) {
                Text(
                    text = "×",
                    color = theme.textSecondary,
                    fontSize = 16.sp,
                )
            }
        }
    }
}

@Composable
fun DrawerBody(
    modifier: Modifier = Modifier,
    content: @Composable ColumnScope.() -> Unit,
) {
    Column(
        modifier = modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp),
        content = content,
    )
}

@Composable
fun DrawerFooter(
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit,
) {
    Box(
        modifier = modifier
            .fillMaxWidth()
            .padding(16.dp),
    ) {
        content()
    }
}
