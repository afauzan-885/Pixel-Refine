package org.pixelrefine.genericui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.painter.Painter
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.animations.shimmerBrush
import org.pixelrefine.genericui.theme.LocalGenericTheme
import androidx.compose.material3.Text

enum class ImageFit {
    Fit, Fill, Crop, FillWidth, FillHeight
}

@Composable
fun ImageComponent(
    imageUrl: String? = null,
    painter: Painter? = null,
    contentDescription: String? = null,
    modifier: Modifier = Modifier,
    width: Dp? = null,
    height: Dp? = null,
    fit: ImageFit = ImageFit.Fit,
    placeholder: @Composable (() -> Unit)? = null,
    error: @Composable (() -> Unit)? = null,
    isLoading: Boolean = false,
    showLoading: Boolean = true,
    onClick: (() -> Unit)? = null,
    cornerRadius: Dp = 0.dp,
    aspectRatio: Float? = null,
) {
    val theme = LocalGenericTheme.current

    Box(
        modifier = modifier
            .then(
                if (width != null) Modifier.width(width) else Modifier.fillMaxWidth()
            )
            .then(
                if (height != null) Modifier.height(height)
                else if (aspectRatio != null) Modifier.aspectRatio(aspectRatio)
                else Modifier.wrapContentHeight()
            )
            .clip(RoundedCornerShape(cornerRadius))
            .background(theme.bgSecondary)
            .then(
                if (cornerRadius > 0.dp) {
                    Modifier.border(1.dp, theme.borderColor, RoundedCornerShape(cornerRadius))
                } else {
                    Modifier
                }
            )
            .then(
                if (onClick != null) Modifier.clickable { onClick() } else Modifier
            ),
        contentAlignment = Alignment.Center,
    ) {
        when {
            isLoading && showLoading -> {
                CircularProgressIndicator(
                    color = theme.primary,
                    strokeWidth = 2.dp,
                    modifier = Modifier.size(32.dp),
                )
            }
            imageUrl != null -> {
                // In real implementation, use AsyncImage or Coil
                // For now, show placeholder
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .background(shimmerBrush(), RoundedCornerShape(cornerRadius)),
                )
            }
            painter != null -> {
                androidx.compose.foundation.Image(
                    painter = painter,
                    contentDescription = contentDescription,
                    contentScale = when (fit) {
                        ImageFit.Fit -> ContentScale.Fit
                        ImageFit.Fill -> ContentScale.FillBounds
                        ImageFit.Crop -> ContentScale.Crop
                        ImageFit.FillWidth -> ContentScale.FillWidth
                        ImageFit.FillHeight -> ContentScale.FillHeight
                    },
                    modifier = Modifier.fillMaxSize(),
                )
            }
            else -> {
                if (error != null) {
                    error()
                } else {
                    placeholder?.invoke() ?: DefaultImagePlaceholder()
                }
            }
        }
    }
}

@Composable
private fun DefaultImagePlaceholder() {
    val theme = LocalGenericTheme.current
    Box(
        modifier = Modifier.fillMaxSize(),
        contentAlignment = Alignment.Center,
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(4.dp),
        ) {
            Text(
                text = "🖼",
                fontSize = 32.sp,
            )
            Text(
                text = "No image",
                color = theme.textMuted,
                fontSize = 12.sp,
            )
        }
    }
}

@Composable
fun AvatarImage(
    imageUrl: String? = null,
    initials: String? = null,
    modifier: Modifier = Modifier,
    size: Dp = 48.dp,
    onClick: (() -> Unit)? = null,
) {
    val theme = LocalGenericTheme.current

    Box(
        modifier = modifier
            .size(size)
            .clip(CircleShape)
            .background(theme.primary)
            .then(if (onClick != null) Modifier.clickable { onClick() } else Modifier),
        contentAlignment = Alignment.Center,
    ) {
        if (initials != null) {
            Text(
                text = initials.take(2).uppercase(),
                color = theme.light,
                fontSize = (size.value * 0.4f).sp,
            )
        }
    }
}
