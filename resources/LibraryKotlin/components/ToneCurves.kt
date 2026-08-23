package org.pixelrefine.genericui.components

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.gestures.detectDragGestures
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
import androidx.compose.runtime.mutableStateListOf
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
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.theme.LocalGenericTheme

data class ControlPoint(val x: Float, val y: Float)

/**
 * Editor Kurva Nada Spline Interaktif untuk Pengaturan Kontras & Warna (Gaya Klasik Konsisten).
 */
@Composable
fun ToneCurveEditor(
    onCurveChanged: (List<ControlPoint>) -> Unit = {},
    initialPoints: List<ControlPoint> = listOf(
        ControlPoint(0.0f, 0.0f),
        ControlPoint(0.25f, 0.25f),
        ControlPoint(0.75f, 0.75f),
        ControlPoint(1.0f, 1.0f),
    ),
    variant: Variant = Variant.Primary,
    height: Dp = 150.dp,
    modifier: Modifier = Modifier,
) {
    val theme = LocalGenericTheme.current
    val points = remember { mutableStateListOf<ControlPoint>().apply { addAll(initialPoints) } }
    var selectedPointIndex by remember { mutableStateOf<Int?>(null) }

    val curveColor = variantColor(theme, variant)

    Column(
        modifier = modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(theme.radiusMd))
            .background(Color(0xFF0F172A))
            .border(1.dp, Color(0xFF334155), RoundedCornerShape(theme.radiusMd))
            .padding(10.dp),
        verticalArrangement = Arrangement.spacedBy(6.dp),
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Text("TONE CURVE", color = Color(0xFF94A3B8), fontSize = 10.sp, fontWeight = FontWeight.Bold)
            Text("RGB Spline", color = curveColor, fontSize = 10.sp, fontWeight = FontWeight.SemiBold)
        }

        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(height)
                .background(Color(0xFF020617))
                .pointerInput(Unit) {
                    detectDragGestures(
                        onDragStart = { offset ->
                            val w = size.width.toFloat()
                            val h = size.height.toFloat()
                            if (w <= 0 || h <= 0) return@detectDragGestures
                            val maxGrabDistSq = 45f * 45f // radius sentuh 45px
                            var bestIdx: Int? = null
                            var minSq = Float.MAX_VALUE
                            points.indices.forEach { idx ->
                                val pt = points[idx]
                                val px = pt.x * w
                                val py = (1f - pt.y) * h
                                val distSq = (px - offset.x) * (px - offset.x) + (py - offset.y) * (py - offset.y)
                                if (distSq < minSq && distSq <= maxGrabDistSq) {
                                    minSq = distSq
                                    bestIdx = idx
                                }
                            }
                            selectedPointIndex = bestIdx
                        },
                        onDrag = { change, _ ->
                            change.consume()
                            val idx = selectedPointIndex ?: return@detectDragGestures
                            if (idx == 0 || idx == points.lastIndex) return@detectDragGestures // Kunci ujung

                            val w = size.width.toFloat()
                            val h = size.height.toFloat()
                            if (w > 0 && h > 0) {
                                val nx = (change.position.x / w).coerceIn(0.05f, 0.95f)
                                val ny = (1f - (change.position.y / h)).coerceIn(0f, 1f)
                                points[idx] = ControlPoint(nx, ny)
                                onCurveChanged(points.toList())
                            }
                        },
                        onDragEnd = { selectedPointIndex = null },
                    )
                },
        ) {
            Canvas(modifier = Modifier.fillMaxSize()) {
                val w = size.width
                val h = size.height

                // Grid Garis Pandu
                val gridColor = Color(0xFF1E293B)
                drawLine(gridColor, Offset(w * 0.25f, 0f), Offset(w * 0.25f, h), strokeWidth = 1f)
                drawLine(gridColor, Offset(w * 0.5f, 0f), Offset(w * 0.5f, h), strokeWidth = 1f)
                drawLine(gridColor, Offset(w * 0.75f, 0f), Offset(w * 0.75f, h), strokeWidth = 1f)
                drawLine(gridColor, Offset(0f, h * 0.25f), Offset(w, h * 0.25f), strokeWidth = 1f)
                drawLine(gridColor, Offset(0f, h * 0.5f), Offset(w, h * 0.5f), strokeWidth = 1f)
                drawLine(gridColor, Offset(0f, h * 0.75f), Offset(w, h * 0.75f), strokeWidth = 1f)

                // Garis Diagonal Netral
                drawLine(Color(0xFF334155), Offset(0f, h), Offset(w, 0f), strokeWidth = 1f)

                // Gambar Kurva Spline
                val path = Path()
                if (points.isNotEmpty()) {
                    path.moveTo(points[0].x * w, (1f - points[0].y) * h)
                    for (i in 0 until points.size - 1) {
                        val p0 = points[i]
                        val p1 = points[i + 1]
                        val x0 = p0.x * w
                        val y0 = (1f - p0.y) * h
                        val x1 = p1.x * w
                        val y1 = (1f - p1.y) * h
                        val cx = (x0 + x1) / 2f
                        path.cubicTo(cx, y0, cx, y1, x1, y1)
                    }
                    drawPath(path, color = curveColor, style = Stroke(width = 2f))
                }

                // Gambar Titik Kontrol
                points.forEachIndexed { _, pt ->
                    val cx = pt.x * w
                    val cy = (1f - pt.y) * h
                    drawCircle(Color.White, radius = 5f, center = Offset(cx, cy))
                    drawCircle(curveColor, radius = 3f, center = Offset(cx, cy))
                }
            }
        }
    }
}
