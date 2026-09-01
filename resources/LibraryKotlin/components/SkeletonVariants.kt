package org.pixelrefine.genericui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import org.pixelrefine.genericui.animations.shimmerBrush
import org.pixelrefine.genericui.theme.LocalGenericTheme

@Composable
fun SkeletonText(
    lines: Int = 1,
    modifier: Modifier = Modifier,
    lineHeight: Dp = 12.dp,
    spacing: Dp = 4.dp,
    lastLineWidth: Float = 0.7f,
) {
    val theme = LocalGenericTheme.current
    val shimmer = shimmerBrush()

    Column(
        modifier = modifier,
        verticalArrangement = Arrangement.spacedBy(spacing),
    ) {
        repeat(lines) { index ->
            val widthFraction = if (index == lines - 1) lastLineWidth else 1f
            Box(
                modifier = Modifier
                    .fillMaxWidth(widthFraction)
                    .height(lineHeight)
                    .clip(RoundedCornerShape(2.dp))
                    .background(shimmer),
            )
        }
    }
}

@Composable
fun SkeletonCircle(
    size: Dp = 40.dp,
    modifier: Modifier = Modifier,
) {
    Box(
        modifier = modifier
            .size(size)
            .clip(CircleShape)
            .background(shimmerBrush()),
    )
}

@Composable
fun SkeletonRect(
    modifier: Modifier = Modifier,
    width: Dp? = null,
    height: Dp = 100.dp,
    cornerRadius: Dp = 4.dp,
) {
    Box(
        modifier = modifier
            .then(if (width != null) Modifier.width(width) else Modifier.fillMaxWidth())
            .height(height)
            .clip(RoundedCornerShape(cornerRadius))
            .background(shimmerBrush()),
    )
}

@Composable
fun SkeletonCard(
    modifier: Modifier = Modifier,
    imageHeight: Dp = 120.dp,
    showImage: Boolean = true,
    lines: Int = 3,
) {
    Column(
        modifier = modifier
            .clip(RoundedCornerShape(8.dp))
            .background(LocalGenericTheme.current.bgCard)
            .padding(12.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        if (showImage) {
            SkeletonRect(
                width = null,
                height = imageHeight,
                cornerRadius = 4.dp,
            )
        }
        SkeletonText(lines = lines)
    }
}

@Composable
fun SkeletonAvatar(
    size: Dp = 40.dp,
    modifier: Modifier = Modifier,
) {
    SkeletonCircle(size = size, modifier = modifier)
}

@Composable
fun SkeletonButton(
    modifier: Modifier = Modifier,
    width: Dp = 100.dp,
    height: Dp = 32.dp,
) {
    SkeletonRect(
        modifier = modifier,
        width = width,
        height = height,
        cornerRadius = 4.dp,
    )
}

@Composable
fun SkeletonList(
    count: Int = 5,
    modifier: Modifier = Modifier,
    itemHeight: Dp = 60.dp,
    spacing: Dp = 8.dp,
) {
    Column(
        modifier = modifier,
        verticalArrangement = Arrangement.spacedBy(spacing),
    ) {
        repeat(count) { _ ->
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                SkeletonCircle(size = itemHeight * 0.6f)
                SkeletonText(lines = 2, modifier = Modifier.weight(1f))
            }
        }
    }
}
