package org.pixelrefine.genericui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.gestures.detectDragGestures
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.domain.gestures.TransformState
import org.pixelrefine.genericui.domain.gestures.rememberTransformState
import org.pixelrefine.genericui.domain.gestures.zoomable
import org.pixelrefine.genericui.theme.LocalGenericTheme

/**
 * Item data model untuk perbandingan gambar
 */
data class ImageCompareItem(
    val title: String,
    val description: String = "",
    val tag: String = "",
)

/**
 * Python: `ImageCompareWidget(left_title="Before", right_title="After")`
 * Dilengkapi kemampuan built-in:
 * - `interactiveSplitSlider = true` -> Interactive divider drag before/after
 * - `synchronizedZoom = true` -> Zoom & Pan terikat sinkron di kedua gambar
 */
@Composable
fun ImageCompareWidget(
    leftTitle: String = "Before",
    rightTitle: String = "After",
    interactiveSplitSlider: Boolean = false,
    synchronizedZoom: Boolean = false,
    transformState: TransformState = rememberTransformState(),
    height: Dp = 180.dp,
    modifier: Modifier = Modifier,
    leftImage: @Composable () -> Unit = {},
    rightImage: @Composable () -> Unit = {},
) {
    val theme = LocalGenericTheme.current
    var splitFraction by remember { mutableFloatStateOf(0.5f) }

    Column(
        modifier = modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(theme.radiusLg))
            .background(theme.bgCard)
            .border(1.dp, theme.borderColor, RoundedCornerShape(theme.radiusLg))
            .padding(12.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        if (!interactiveSplitSlider) {
            // Mode Split Berdampingan (Side-by-Side)
            val zoomMod = if (synchronizedZoom) Modifier.zoomable(transformState) else Modifier

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                Column(
                    modifier = Modifier.weight(1f),
                    horizontalAlignment = Alignment.CenterHorizontally,
                ) {
                    Text(leftTitle, color = theme.textPrimary, fontWeight = FontWeight.Bold, fontSize = 12.sp)
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(height)
                            .clip(RoundedCornerShape(theme.radiusMd))
                            .background(theme.bgSecondary)
                            .then(zoomMod),
                        contentAlignment = Alignment.Center,
                    ) {
                        leftImage()
                    }
                }
                Column(
                    modifier = Modifier.weight(1f),
                    horizontalAlignment = Alignment.CenterHorizontally,
                ) {
                    Text(rightTitle, color = theme.textPrimary, fontWeight = FontWeight.Bold, fontSize = 12.sp)
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(height)
                            .clip(RoundedCornerShape(theme.radiusMd))
                            .background(theme.bgSecondary)
                            .then(zoomMod),
                        contentAlignment = Alignment.Center,
                    ) {
                        rightImage()
                    }
                }
            }
        } else {
            // Mode Interactive Split Slider
            BoxWithConstraints(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(height)
                    .clip(RoundedCornerShape(theme.radiusMd))
                    .background(theme.bgSecondary),
            ) {
                val totalWidthPx = constraints.maxWidth.toFloat()

                // Gambar Kanan (After)
                Box(Modifier.fillMaxSize()) { rightImage() }

                // Gambar Kiri (Before) dipotong sesuai fraction
                Box(
                    modifier = Modifier
                        .fillMaxHeight()
                        .fillMaxWidth(splitFraction)
                        .clip(RoundedCornerShape(topStart = theme.radiusMd, bottomStart = theme.radiusMd)),
                ) {
                    leftImage()
                }

                // Garis Pembagi (Draggable Handle)
                Box(
                    modifier = Modifier
                        .offset(x = (maxWidth * splitFraction) - 2.dp)
                        .width(4.dp)
                        .fillMaxHeight()
                        .background(theme.primary)
                        .pointerInput(Unit) {
                            detectDragGestures { change, dragAmount ->
                                change.consume()
                                if (totalWidthPx > 0) {
                                    val newFraction = splitFraction + (dragAmount.x / totalWidthPx)
                                    splitFraction = newFraction.coerceIn(0.05f, 0.95f)
                                }
                            }
                        },
                )
            }
        }
    }
}
