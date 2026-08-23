package org.pixelrefine.mobile.ui.sections

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.gestures.detectTransformGestures
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.badge
import org.pixelrefine.genericui.components.Variant
import org.pixelrefine.genericui.domain.models.BatchItem
import org.pixelrefine.genericui.domain.models.ImageItem
import org.pixelrefine.genericui.theme.LocalGenericTheme

/**
 * Section 3: Main Viewport (Image Reference Canvas).
 * Sesuai sketsa:
 * - Kiri Atas: Nama Gambar (e.g. IMG_001.dng)
 * - Kanan Atas: Jumlah Gambar (e.g. 13 Images)
 * - Tengah: Gambar Referensi (Landscape / Mountain Vector Canvas dengan Gesture Pan & Zoom)
 * - Kanan Bawah: Indikator "Reference Frame ★"
 */
@Composable
fun MainViewportSection(
    batch: BatchItem?,
    activeImage: ImageItem?,
    modifier: Modifier = Modifier,
) {
    val theme = LocalGenericTheme.current

    // State Transformasi Gesture Pan & Zoom
    var scale by remember { mutableFloatStateOf(1f) }
    var offset by remember { mutableStateOf(Offset.Zero) }

    val imageName = activeImage?.filename ?: "IMG_001.dng"
    val totalImages = batch?.imageCount ?: 13

    Box(
        modifier = modifier
            .fillMaxWidth()
            .height(280.dp)
            .padding(horizontal = 12.dp, vertical = 6.dp)
            .clip(RoundedCornerShape(theme.radiusLg))
            .background(theme.bgCard)
            .border(1.5.dp, theme.borderColor, RoundedCornerShape(theme.radiusLg)),
    ) {
        // 1. Gambar Vektor Interaktif (Mountain / Sun Sesuai Gambar Sketsa)
        Box(
            modifier = Modifier
                .fillMaxSize()
                .clip(RoundedCornerShape(theme.radiusLg))
                .pointerInput(Unit) {
                    detectTransformGestures { _, pan, zoom, _ ->
                        scale = (scale * zoom).coerceIn(0.8f, 5.0f)
                        offset = Offset(offset.x + pan.x, offset.y + pan.y)
                    }
                }
                .graphicsLayer(
                    scaleX = scale,
                    scaleY = scale,
                    translationX = offset.x,
                    translationY = offset.y,
                ),
            contentAlignment = Alignment.Center,
        ) {
            Canvas(modifier = Modifier.fillMaxSize().padding(16.dp)) {
                val w = size.width
                val h = size.height

                // Gambar Matahari Terbit di antara Gunung
                drawCircle(
                    color = Color(0xFFF59E0B),
                    radius = 28f,
                    center = Offset(w * 0.52f, h * 0.45f),
                )

                // Gambar Garis Sinar Matahari (Sesuai Sketsa)
                for (angle in 0 until 5) {
                    val a = Math.toRadians((180.0 + angle * 30.0))
                    val r1 = 34.0
                    val r2 = 46.0
                    val cx = w * 0.52f
                    val cy = h * 0.45f
                    drawLine(
                        color = Color(0xFFD97706),
                        start = Offset((cx + r1 * Math.cos(a)).toFloat(), (cy + r1 * Math.sin(a)).toFloat()),
                        end = Offset((cx + r2 * Math.cos(a)).toFloat(), (cy + r2 * Math.sin(a)).toFloat()),
                        strokeWidth = 2.5f,
                    )
                }

                // Jalur Gunung Kiri (Tinggi)
                val mountainLeft = Path().apply {
                    moveTo(0f, h * 0.85f)
                    lineTo(w * 0.38f, h * 0.35f)
                    lineTo(w * 0.65f, h * 0.88f)
                    close()
                }
                drawPath(
                    path = mountainLeft,
                    color = Color(0xFF10B981).copy(alpha = 0.15f),
                )
                drawPath(
                    path = mountainLeft,
                    color = Color(0xFF0F766E),
                    style = Stroke(width = 3.5f),
                )

                // Jalur Gunung Kanan (Sedang)
                val mountainRight = Path().apply {
                    moveTo(w * 0.52f, h * 0.55f)
                    lineTo(w * 0.78f, h * 0.42f)
                    lineTo(w, h * 0.82f)
                }
                drawPath(
                    path = mountainRight,
                    color = Color(0xFF0F766E),
                    style = Stroke(width = 3.5f),
                )
            }
        }

        // 2. Overlay Header (Kiri Atas: Nama Gambar, Kanan Atas: Jumlah Gambar)
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(10.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically,
        ) {
            // Nama Gambar (Kiri Atas)
            Box(
                modifier = Modifier
                    .clip(RoundedCornerShape(theme.radiusSm))
                    .background(theme.bgCard.copy(alpha = 0.85f))
                    .border(1.dp, theme.borderColor.copy(alpha = 0.5f), RoundedCornerShape(theme.radiusSm))
                    .padding(horizontal = 8.dp, vertical = 4.dp),
            ) {
                Text(
                    text = imageName,
                    color = theme.textPrimary,
                    fontWeight = FontWeight.Bold,
                    fontSize = 12.sp,
                )
            }

            // Jumlah Gambar Badge (Kanan Atas) gaya Pythonic 1-baris
            badge(
                text = "🖼️ $totalImages Images",
                variant = Variant.Primary,
                show_pulse = false,
                show_dot = true,
            )
        }

        // 3. Overlay Footer (Kanan Bawah: Reference Indicator)
        Box(
            modifier = Modifier
                .align(Alignment.BottomEnd)
                .padding(10.dp),
        ) {
            badge(
                text = "★ Best Reference Frame",
                variant = Variant.Success,
                show_pulse = true,
                show_dot = true,
            )
        }
    }
}
