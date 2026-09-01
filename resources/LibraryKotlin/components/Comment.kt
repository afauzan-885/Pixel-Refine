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

data class CommentData(
    val author: String,
    val content: String,
    val avatar: String? = null,
    val timestamp: String? = null,
    val likes: Int = 0,
    val replies: List<CommentData> = emptyList(),
)

@Composable
fun Comment(
    comment: CommentData,
    modifier: Modifier = Modifier,
    onLike: (() -> Unit)? = null,
    onReply: (() -> Unit)? = null,
    showReplies: Boolean = true,
) {
    val theme = LocalGenericTheme.current

    Column(
        modifier = modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(8.dp))
            .background(theme.bgCard)
            .border(1.dp, theme.borderColor, RoundedCornerShape(8.dp))
            .padding(12.dp),
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.Top,
        ) {
            // Avatar
            Box(
                modifier = Modifier
                    .size(36.dp)
                    .clip(CircleShape)
                    .background(theme.primary),
                contentAlignment = Alignment.Center,
            ) {
                Text(
                    text = comment.avatar ?: comment.author.take(1).uppercase(),
                    color = theme.light,
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Bold,
                )
            }

            Spacer(modifier = Modifier.width(12.dp))

            Column(
                modifier = Modifier.weight(1f),
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                ) {
                    Text(
                        text = comment.author,
                        color = theme.textPrimary,
                        fontSize = 13.sp,
                        fontWeight = FontWeight.SemiBold,
                    )

                    if (comment.timestamp != null) {
                        Text(
                            text = comment.timestamp,
                            color = theme.textMuted,
                            fontSize = 11.sp,
                        )
                    }
                }

                Spacer(modifier = Modifier.height(4.dp))

                Text(
                    text = comment.content,
                    color = theme.textPrimary,
                    fontSize = 13.sp,
                )

                Spacer(modifier = Modifier.height(8.dp))

                Row(
                    horizontalArrangement = Arrangement.spacedBy(16.dp),
                ) {
                    if (onLike != null) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(4.dp),
                            modifier = Modifier.clickable { onLike() },
                        ) {
                            Text(
                                text = "♥",
                                color = theme.danger,
                                fontSize = 12.sp,
                            )
                            Text(
                                text = comment.likes.toString(),
                                color = theme.textSecondary,
                                fontSize = 12.sp,
                            )
                        }
                    }

                    if (onReply != null) {
                        Text(
                            text = "Reply",
                            color = theme.primary,
                            fontSize = 12.sp,
                            modifier = Modifier.clickable { onReply() },
                        )
                    }
                }
            }
        }

        // Replies
        if (showReplies && comment.replies.isNotEmpty()) {
            Spacer(modifier = Modifier.height(12.dp))

            Column(
                modifier = Modifier.padding(start = 48.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                comment.replies.forEach { reply ->
                    ReplyComment(reply = reply, onLike = onLike)
                }
            }
        }
    }
}

@Composable
private fun ReplyComment(
    reply: CommentData,
    onLike: (() -> Unit)?,
) {
    val theme = LocalGenericTheme.current

    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(6.dp))
            .background(theme.bgSecondary)
            .padding(8.dp),
        verticalAlignment = Alignment.Top,
    ) {
        Box(
            modifier = Modifier
                .size(24.dp)
                .clip(CircleShape)
                .background(theme.primary),
            contentAlignment = Alignment.Center,
        ) {
            Text(
                text = reply.avatar ?: reply.author.take(1).uppercase(),
                color = theme.light,
                fontSize = 10.sp,
                fontWeight = FontWeight.Bold,
            )
        }

        Spacer(modifier = Modifier.width(8.dp))

        Column(
            modifier = Modifier.weight(1f),
        ) {
            Text(
                text = reply.author,
                color = theme.textPrimary,
                fontSize = 12.sp,
                fontWeight = FontWeight.SemiBold,
            )

            Text(
                text = reply.content,
                color = theme.textSecondary,
                fontSize = 12.sp,
            )
        }
    }
}
