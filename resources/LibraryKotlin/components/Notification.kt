package org.pixelrefine.genericui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.theme.LocalGenericTheme
import androidx.compose.material3.Text

data class NotificationData(
    val title: String,
    val description: String? = null,
    val variant: Variant = Variant.Info,
    val icon: String? = null,
    val timestamp: String = "",
    val isRead: Boolean = false,
    val id: Long = System.currentTimeMillis(),
)

object NotificationManager {
    private val _notifications = mutableStateListOf<NotificationData>()
    val notifications: List<NotificationData> = _notifications

    fun add(notification: NotificationData) {
        _notifications.add(0, notification)
    }

    fun remove(id: Long) {
        _notifications.removeAll { it.id == id }
    }

    fun markAsRead(id: Long) {
        val index = _notifications.indexOfFirst { it.id == id }
        if (index >= 0) {
            _notifications[index] = _notifications[index].copy(isRead = true)
        }
    }

    fun markAllAsRead() {
        for (i in _notifications.indices) {
            _notifications[i] = _notifications[i].copy(isRead = true)
        }
    }

    fun clear() {
        _notifications.clear()
    }
}

@Composable
fun Notification(
    notification: NotificationData,
    modifier: Modifier = Modifier,
    onClick: (() -> Unit)? = null,
    onDismiss: (() -> Unit)? = null,
) {
    val theme = LocalGenericTheme.current
    val variantColor = variantColor(theme, notification.variant)

    Row(
        modifier = modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(8.dp))
            .background(if (notification.isRead) theme.bgCard else variantColor.copy(alpha = 0.05f))
            .border(1.dp, theme.borderColor, RoundedCornerShape(8.dp))
            .then(
                if (onClick != null) {
                    Modifier.clickable {
                        onClick()
                        NotificationManager.markAsRead(notification.id)
                    }
                } else {
                    Modifier
                }
            )
            .padding(12.dp),
        verticalAlignment = Alignment.Top,
        horizontalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        if (notification.icon != null) {
            Box(
                modifier = Modifier
                    .size(36.dp)
                    .clip(CircleShape)
                    .background(variantColor.copy(alpha = 0.2f)),
                contentAlignment = Alignment.Center,
            ) {
                Text(
                    text = notification.icon,
                    color = variantColor,
                    fontSize = 18.sp,
                )
            }
        }

        Column(
            modifier = Modifier.weight(1f),
            verticalArrangement = Arrangement.spacedBy(2.dp),
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
            ) {
                Text(
                    text = notification.title,
                    color = theme.textPrimary,
                    fontSize = 14.sp,
                    fontWeight = FontWeight.SemiBold,
                )

                if (!notification.isRead) {
                    Box(
                        modifier = Modifier
                            .size(8.dp)
                            .background(variantColor, CircleShape),
                    )
                }
            }

            if (notification.description != null) {
                Text(
                    text = notification.description,
                    color = theme.textSecondary,
                    fontSize = 12.sp,
                )
            }

            if (notification.timestamp.isNotEmpty()) {
                Text(
                    text = notification.timestamp,
                    color = theme.textMuted,
                    fontSize = 10.sp,
                )
            }
        }

        if (onDismiss != null) {
            Box(
                modifier = Modifier
                    .size(20.dp)
                    .clip(CircleShape)
                    .background(theme.bgSecondary)
                    .clickable { onDismiss() },
                contentAlignment = Alignment.Center,
            ) {
                Text(
                    text = "×",
                    color = theme.textMuted,
                    fontSize = 12.sp,
                )
            }
        }
    }
}

@Composable
fun NotificationList(
    modifier: Modifier = Modifier,
    onNotificationClick: ((NotificationData) -> Unit)? = null,
    onMarkAllAsRead: (() -> Unit)? = null,
) {
    val notifications = NotificationManager.notifications
    val theme = LocalGenericTheme.current

    Column(modifier = modifier) {
        if (notifications.isNotEmpty() && onMarkAllAsRead != null) {
            Row(
                modifier = Modifier.fillMaxWidth().padding(bottom = 8.dp),
                horizontalArrangement = Arrangement.End,
            ) {
                Text(
                    text = "Mark all as read",
                    color = theme.primary,
                    fontSize = 12.sp,
                    modifier = Modifier.clickable { onMarkAllAsRead() },
                )
            }
        }

        if (notifications.isEmpty()) {
            Text(
                text = "No notifications",
                color = theme.textMuted,
                fontSize = 14.sp,
                modifier = Modifier.fillMaxWidth().padding(16.dp),
            )
        } else {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                notifications.forEach { notification ->
                    Notification(
                        notification = notification,
                        onClick = onNotificationClick?.let { { it(notification) } },
                        onDismiss = { NotificationManager.remove(notification.id) },
                    )
                }
            }
        }
    }
}

@Composable
fun NotificationBadge(
    count: Int,
    modifier: Modifier = Modifier,
    maxCount: Int = 99,
    variant: Variant = Variant.Danger,
) {
    val theme = LocalGenericTheme.current
    val variantColor = variantColor(theme, variant)
    val displayCount = if (count > maxCount) "$maxCount+" else count.toString()

    if (count > 0) {
        Box(
            modifier = modifier
                .size(18.dp)
                .clip(CircleShape)
                .background(variantColor),
            contentAlignment = Alignment.Center,
        ) {
            Text(
                text = displayCount,
                color = theme.light,
                fontSize = 10.sp,
                fontWeight = FontWeight.Bold,
            )
        }
    }
}
