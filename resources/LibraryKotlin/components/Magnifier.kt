package org.pixelrefine.genericui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.gestures.detectDragGestures
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.layout.onSizeChanged
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.IntSize
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.theme.LocalGenericTheme

/**
 * Pixel Loupe / Magnifier Widget untuk inspeksi detail noise piksel.
 *
 * Menampilkan area di bawah kursor/jari dalam zoom tinggi dengan loupe circular.
 * Mendukung drag gesture untuk menggeser area inspeksi.
 *
 * @param zoomFactor Pembesaran (2x - 16x)
 * @param loupeSize Diameter loupe dalam dp
 * @param modifier Modifier untuk container luar
 * @param content Konten yang akan di-magnify (harus punya ukuran tetap)
 */
@Composable
fun Magnifier(
    zoomFactor: Float = 4.0f,
    loupeSize: Dp = 100.dp,
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit,
) {
    val theme = LocalGenericTheme.current
    val density = LocalDensity.current

    // Posisi fokus loupe dalam pixel koordinat relatif terhadap content
    var focusOffset by remember { mutableStateOf(Offset.Zero) }
    var contentSize by remember { mutableStateOf(IntSize.Zero) }
    var isDragging by remember { mutableStateOf(false) }

    val loupeSizePx = with(density) { loupeSize.toPx() }
    val halfLoupe = loupeSizePx / 2f

    Box(
        modifier = modifier
            .size(loupeSize)
            .clip(CircleShape)
            .background(theme.bgCard)
            .border(2.dp, theme.primary, CircleShape)
            .pointerInput(Unit) {
                detectDragGestures(
                    onDragStart = { offset ->
                        isDragging = true
                        // Set fokus awal ke tengah content jika belum diinisialisasi
                        if (focusOffset == Offset.Zero && contentSize != IntSize.Zero) {
                            focusOffset = Offset(
                                contentSize.width / 2f,
                                contentSize.height / 2f
                            )
                        }
                        // Map offset loupe ke koordinat content
                        val scaleX = contentSize.width.toFloat() / loupeSizePx
                        val scaleY = contentSize.height.toFloat() / loupeSizePx
                        focusOffset = Offset(
                            (focusOffset.x + (offset.x - halfLoupe) * scaleX / zoomFactor)
                                .coerceIn(0f, contentSize.width.toFloat()),
                            (focusOffset.y + (offset.y - halfLoupe) * scaleY / zoomFactor)
                                .coerceIn(0f, contentSize.height.toFloat())
                        )
                    },
                    onDrag = { change, dragAmount ->
                        change.consume()
                        if (contentSize != IntSize.Zero) {
                            val scaleX = contentSize.width.toFloat() / loupeSizePx
                            val scaleY = contentSize.height.toFloat() / loupeSizePx
                            focusOffset = Offset(
                                (focusOffset.x + dragAmount.x * scaleX / zoomFactor)
                                    .coerceIn(0f, contentSize.width.toFloat()),
                                (focusOffset.y + dragAmount.y * scaleY / zoomFactor)
                                    .coerceIn(0f, contentSize.height.toFloat())
                            )
                        }
                    },
                    onDragEnd = { isDragging = false },
                    onDragCancel = { isDragging = false },
                )
            },
        contentAlignment = Alignment.Center,
    ) {
        // Container untuk content yang di-zoom dan di-offset
        Box(
            modifier = Modifier
                .fillMaxSize()
                .onSizeChanged { newSize ->
                    contentSize = newSize
                    // Auto-center fokus pada pertama kali
                    if (focusOffset == Offset.Zero) {
                        focusOffset = Offset(newSize.width / 2f, newSize.height / 2f)
                    }
                }
                .graphicsLayer {
                    scaleX = zoomFactor
                    scaleY = zoomFactor
                    // Offset agar fokus berada di tengah loupe
                    translationX = -(focusOffset.x - contentSize.width / 2f) * zoomFactor
                    translationY = -(focusOffset.y - contentSize.height / 2f) * zoomFactor
                },
            contentAlignment = Alignment.Center,
        ) {
            content()
        }

        // Crosshair indicator di tengah loupe
        if (isDragging) {
            Text(
                text = "+",
                color = theme.primary.copy(alpha = 0.7f),
                fontSize = 16.sp,
                modifier = Modifier.align(Alignment.Center),
            )
        }
    }
}
