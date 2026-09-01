package org.pixelrefine.genericui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.theme.LocalGenericTheme
import androidx.compose.material3.Text

enum class AvatarSize {
    XS, SM, MD, LG, XL
}

@Composable
fun Avatar(
    modifier: Modifier = Modifier,
    size: AvatarSize = AvatarSize.MD,
    imageUrl: String? = null,
    icon: ImageVector? = null,
    initials: String? = null,
    backgroundColor: Color? = null,
    contentColor: Color? = null,
    borderColor: Color? = null,
    borderWidth: Dp = 0.dp,
) {
    val theme = LocalGenericTheme.current
    val avatarSize = when (size) {
        AvatarSize.XS -> 24.dp
        AvatarSize.SM -> 32.dp
        AvatarSize.MD -> 40.dp
        AvatarSize.LG -> 56.dp
        AvatarSize.XL -> 72.dp
    }
    val fontSize = when (size) {
        AvatarSize.XS -> 10.sp
        AvatarSize.SM -> 12.sp
        AvatarSize.MD -> 14.sp
        AvatarSize.LG -> 20.sp
        AvatarSize.XL -> 28.sp
    }
    val iconSize = when (size) {
        AvatarSize.XS -> 12.dp
        AvatarSize.SM -> 16.dp
        AvatarSize.MD -> 20.dp
        AvatarSize.LG -> 28.dp
        AvatarSize.XL -> 36.dp
    }

    val bgColor = backgroundColor ?: theme.primary
    val fgColor = contentColor ?: theme.light

    Box(
        modifier = modifier
            .size(avatarSize)
            .clip(CircleShape)
            .background(bgColor)
            .then(
                if (borderWidth > 0.dp) {
                    Modifier.border(borderWidth, borderColor ?: theme.borderColor, CircleShape)
                } else {
                    Modifier
                }
            ),
        contentAlignment = Alignment.Center,
    ) {
        when {
            imageUrl != null -> {
                // In real implementation, use AsyncImage or similar
                // For now, show initials as fallback
                if (initials != null) {
                    Text(
                        text = initials.take(2).uppercase(),
                        color = fgColor,
                        fontSize = fontSize,
                        fontWeight = FontWeight.Medium,
                    )
                }
            }
            icon != null -> {
                // Icon would be rendered here
                // For now, show placeholder
                Box(
                    modifier = Modifier
                        .size(iconSize)
                        .background(fgColor.copy(alpha = 0.3f), CircleShape),
                )
            }
            initials != null -> {
                Text(
                    text = initials.take(2).uppercase(),
                    color = fgColor,
                    fontSize = fontSize,
                    fontWeight = FontWeight.Medium,
                )
            }
            else -> {
                // Default person icon placeholder
                Box(
                    modifier = Modifier
                        .size(iconSize)
                        .background(fgColor.copy(alpha = 0.3f), CircleShape),
                )
            }
        }
    }
}

@Composable
fun AvatarGroup(
    avatars: List<AvatarData>,
    modifier: Modifier = Modifier,
    size: AvatarSize = AvatarSize.MD,
    maxVisible: Int = 5,
    spacing: Dp = (-8).dp,
) {
    val theme = LocalGenericTheme.current
    val visibleAvatars = avatars.take(maxVisible)
    val remainingCount = avatars.size - maxVisible

    Row(
        modifier = modifier,
        horizontalArrangement = Arrangement.spacedBy(spacing),
    ) {
        visibleAvatars.forEach { avatar ->
            Avatar(
                size = size,
                initials = avatar.initials,
                backgroundColor = avatar.backgroundColor,
                borderColor = theme.bgPrimary,
                borderWidth = 2.dp,
            )
        }

        if (remainingCount > 0) {
            Avatar(
                size = size,
                initials = "+$remainingCount",
                backgroundColor = theme.bgSecondary,
                contentColor = theme.textSecondary,
                borderColor = theme.bgPrimary,
                borderWidth = 2.dp,
            )
        }
    }
}

data class AvatarData(
    val initials: String,
    val backgroundColor: Color? = null,
    val imageUrl: String? = null,
)

@Composable
fun AvatarWithStatus(
    modifier: Modifier = Modifier,
    size: AvatarSize = AvatarSize.MD,
    initials: String? = null,
    status: AvatarStatus = AvatarStatus.OFFLINE,
    backgroundColor: Color? = null,
) {
    val theme = LocalGenericTheme.current
    val statusColor = when (status) {
        AvatarStatus.ONLINE -> theme.success
        AvatarStatus.OFFLINE -> theme.textMuted
        AvatarStatus.BUSY -> theme.danger
        AvatarStatus.AWAY -> theme.warning
    }
    val statusSize = when (size) {
        AvatarSize.XS -> 6.dp
        AvatarSize.SM -> 8.dp
        AvatarSize.MD -> 10.dp
        AvatarSize.LG -> 12.dp
        AvatarSize.XL -> 14.dp
    }

    Box {
        Avatar(
            size = size,
            initials = initials,
            backgroundColor = backgroundColor,
        )
        Box(
            modifier = Modifier
                .size(statusSize)
                .align(Alignment.BottomEnd)
                .background(statusColor, CircleShape)
                .border(2.dp, theme.bgPrimary, CircleShape),
        )
    }
}

enum class AvatarStatus {
    ONLINE, OFFLINE, BUSY, AWAY
}
