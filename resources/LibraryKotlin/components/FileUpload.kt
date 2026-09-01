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
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.theme.LocalGenericTheme
import androidx.compose.material3.Text

data class FileUploadData(
    val name: String,
    val size: Long = 0,
    val progress: Float = 0f,
    val error: String? = null,
    val isComplete: Boolean = false,
    val id: String = name,
)

@Composable
fun FileUpload(
    onFileSelected: ((List<String>) -> Unit)? = null,
    modifier: Modifier = Modifier,
    label: String = "Drop files here or click to upload",
    sublabel: String? = null,
    acceptTypes: List<String> = emptyList(),
    multiple: Boolean = true,
    variant: Variant = Variant.Primary,
) {
    val theme = LocalGenericTheme.current
    val variantColor = variantColor(theme, variant)
    var isDragOver by remember { mutableStateOf(false) }

    Column(modifier = modifier.fillMaxWidth()) {
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(150.dp)
                .clip(RoundedCornerShape(8.dp))
                .background(
                    if (isDragOver) variantColor.copy(alpha = 0.1f) else theme.bgCard
                )
                .border(
                    width = if (isDragOver) 2.dp else 1.dp,
                    color = if (isDragOver) variantColor else theme.borderColor,
                    shape = RoundedCornerShape(8.dp),
                )
                .clickable {
                    // In real implementation, open file picker
                    onFileSelected?.invoke(emptyList())
                }
                .padding(16.dp),
            contentAlignment = Alignment.Center,
        ) {
            Column(
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                Text(
                    text = "📁",
                    fontSize = 32.sp,
                )
                Text(
                    text = label,
                    color = theme.textPrimary,
                    fontSize = 14.sp,
                    fontWeight = FontWeight.SemiBold,
                )
                if (sublabel != null) {
                    Text(
                        text = sublabel,
                        color = theme.textMuted,
                        fontSize = 12.sp,
                    )
                }
                if (acceptTypes.isNotEmpty()) {
                    Text(
                        text = "Accepted: ${acceptTypes.joinToString(", ")}",
                        color = theme.textMuted,
                        fontSize = 11.sp,
                    )
                }
            }
        }
    }
}

@Composable
fun FileUploadList(
    files: List<FileUploadData>,
    modifier: Modifier = Modifier,
    onRemove: ((String) -> Unit)? = null,
    onRetry: ((String) -> Unit)? = null,
) {
    val theme = LocalGenericTheme.current

    Column(
        modifier = modifier,
        verticalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        files.forEach { file ->
            FileUploadItem(
                file = file,
                onRemove = onRemove?.let { { it(file.id) } },
                onRetry = onRetry?.let { { it(file.id) } },
            )
        }
    }
}

@Composable
private fun FileUploadItem(
    file: FileUploadData,
    onRemove: (() -> Unit)?,
    onRetry: (() -> Unit)?,
) {
    val theme = LocalGenericTheme.current

    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(6.dp))
            .background(theme.bgCard)
            .border(1.dp, theme.borderColor, RoundedCornerShape(6.dp))
            .padding(12.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        // File icon
        Box(
            modifier = Modifier
                .size(40.dp)
                .clip(RoundedCornerShape(4.dp))
                .background(theme.primary.copy(alpha = 0.1f)),
            contentAlignment = Alignment.Center,
        ) {
            Text(
                text = "📄",
                fontSize = 20.sp,
            )
        }

        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = file.name,
                color = theme.textPrimary,
                fontSize = 13.sp,
                fontWeight = FontWeight.Medium,
                maxLines = 1,
            )

            Text(
                text = formatFileSize(file.size),
                color = theme.textMuted,
                fontSize = 11.sp,
            )

            if (!file.isComplete && file.error == null) {
                Spacer(modifier = Modifier.height(4.dp))
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(4.dp)
                        .clip(RoundedCornerShape(2.dp))
                        .background(theme.bgSecondary),
                ) {
                    Box(
                        modifier = Modifier
                            .fillMaxWidth(file.progress.coerceIn(0f, 1f))
                            .height(4.dp)
                            .clip(RoundedCornerShape(2.dp))
                            .background(theme.primary),
                    )
                }
            }

            if (file.error != null) {
                Text(
                    text = file.error,
                    color = theme.danger,
                    fontSize = 11.sp,
                )
            }
        }

        // Status icon
        when {
            file.error != null && onRetry != null -> {
                Box(
                    modifier = Modifier
                        .size(28.dp)
                        .clip(CircleShape)
                        .background(theme.warning.copy(alpha = 0.2f))
                        .clickable { onRetry() },
                    contentAlignment = Alignment.Center,
                ) {
                    Text(
                        text = "↻",
                        color = theme.warning,
                        fontSize = 14.sp,
                    )
                }
            }
            file.isComplete -> {
                Box(
                    modifier = Modifier
                        .size(28.dp)
                        .clip(CircleShape)
                        .background(theme.success.copy(alpha = 0.2f)),
                    contentAlignment = Alignment.Center,
                ) {
                    Text(
                        text = "✓",
                        color = theme.success,
                        fontSize = 14.sp,
                    )
                }
            }
            else -> {
                CircularProgressIndicator(
                    color = theme.primary,
                    strokeWidth = 2.dp,
                    modifier = Modifier.size(20.dp),
                )
            }
        }

        if (onRemove != null) {
            Box(
                modifier = Modifier
                    .size(28.dp)
                    .clip(CircleShape)
                    .background(theme.bgSecondary)
                    .clickable { onRemove() },
                contentAlignment = Alignment.Center,
            ) {
                Text(
                    text = "×",
                    color = theme.textMuted,
                    fontSize = 14.sp,
                )
            }
        }
    }
}

private fun formatFileSize(bytes: Long): String {
    if (bytes < 1024) return "$bytes B"
    if (bytes < 1024 * 1024) return "${bytes / 1024} KB"
    if (bytes < 1024 * 1024 * 1024) return "${bytes / (1024 * 1024)} MB"
    return "${bytes / (1024 * 1024 * 1024)} GB"
}
