package org.pixelrefine.genericui.components

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
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
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.theme.LocalGenericTheme

/**
 * Komponen Visualisasi Real-Time Histogram RGB / Luminance (Gaya Klasik Konsisten).
 */
@Composable
fun HistogramViewer(
    redData: FloatArray = FloatArray(256) { 0f },
    greenData: FloatArray = FloatArray(256) { 0f },
    blueData: FloatArray = FloatArray(256) { 0f },
    luminanceData: FloatArray? = null,
    showChannels: Boolean = true,
    variant: Variant = Variant.Dark,
    height: Dp = 110.dp,
    modifier: Modifier = Modifier,
) {
    val theme = LocalGenericTheme.current

    Column(
        modifier = modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(theme.radiusMd))
            .background(Color(0xFF0F172A))
            .border(1.dp, Color(0xFF334155), RoundedCornerShape(theme.radiusMd))
            .padding(8.dp),
        verticalArrangement = Arrangement.spacedBy(4.dp),
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Text("HISTOGRAM", color = Color(0xFF94A3B8), fontSize = 10.sp, fontWeight = FontWeight.Bold)
            if (showChannels) {
                Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                    Text("R", color = Color(0xFFEF4444), fontSize = 10.sp, fontWeight = FontWeight.Bold)
                    Text("G", color = Color(0xFF22C55E), fontSize = 10.sp, fontWeight = FontWeight.Bold)
                    Text("B", color = Color(0xFF3B82F6), fontSize = 10.sp, fontWeight = FontWeight.Bold)
                }
            }
        }

        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(height)
                .background(Color(0xFF020617)),
        ) {
            Canvas(modifier = Modifier.fillMaxSize()) {
                val w = size.width
                val h = size.height
                val bins = 256
                val step = w / bins.toFloat()

                fun drawChannel(data: FloatArray, color: Color) {
                    val maxVal = data.maxOrNull()?.coerceAtLeast(1f) ?: 1f
                    val path = Path()
                    path.moveTo(0f, h)
                    for (i in 0 until bins) {
                        val v = if (i < data.size) data[i] else 0f
                        val y = h - (v / maxVal * (h * 0.9f))
                        path.lineTo(i * step, y)
                    }
                    path.lineTo(w, h)
                    path.close()
                    drawPath(path, color = color.copy(alpha = 0.25f))
                    drawPath(path, color = color, style = Stroke(width = 1.5f))
                }

                if (showChannels) {
                    drawChannel(redData, Color(0xFFEF4444))
                    drawChannel(greenData, Color(0xFF22C55E))
                    drawChannel(blueData, Color(0xFF3B82F6))
                } else if (luminanceData != null) {
                    drawChannel(luminanceData, Color(0xFFE2E8F0))
                }
            }
        }
    }
}
