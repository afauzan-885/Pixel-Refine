package org.pixelrefine.genericui.components

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.AnnotatedString
import androidx.compose.ui.text.rememberTextMeasurer
import androidx.compose.ui.text.drawText
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.theme.LocalGenericTheme

@Composable
fun Watermark(
    text: String,
    modifier: Modifier = Modifier,
    rotation: Float = -22f,
    opacity: Float = 0.1f,
    fontSize: Dp = 14.dp,
    color: Color? = null,
    gap: Dp = 80.dp,
) {
    val theme = LocalGenericTheme.current
    val watermarkColor = color ?: theme.textPrimary
    val textMeasurer = rememberTextMeasurer()
    val style = TextStyle(
        color = watermarkColor.copy(alpha = opacity),
        fontSize = fontSize.value.sp,
        textAlign = TextAlign.Center,
    )

    Box(modifier = modifier.fillMaxSize()) {
        Canvas(modifier = Modifier.fillMaxSize()) {
            val measuredText = textMeasurer.measure(AnnotatedString(text), style)
            val textWidth = measuredText.size.width.toFloat()
            val textHeight = measuredText.size.height.toFloat()
            val gapValue = gap.toPx()

            // Calculate offset to center pattern
            val offsetX = (size.width % (textWidth + gapValue)) / 2
            val offsetY = (size.height % (textHeight + gapValue)) / 2

            // Draw diagonal text pattern
            var y = -offsetY
            while (y < size.height) {
                var x = -offsetX
                while (x < size.width) {
                    drawContext.canvas.save()
                    drawContext.canvas.translate(x + textWidth / 2, y + textHeight / 2)
                    drawContext.canvas.rotate(rotation)
                    drawText(
                        textMeasurer = textMeasurer,
                        text = text,
                        topLeft = Offset(-textWidth / 2, -textHeight / 2),
                        style = style,
                    )
                    drawContext.canvas.restore()
                    x += textWidth + gapValue
                }
                y += textHeight + gapValue
            }
        }
    }
}

@Composable
fun TextWatermark(
    text: String,
    modifier: Modifier = Modifier,
    rotation: Float = 0f,
    opacity: Float = 0.3f,
    color: Color? = null,
) {
    val theme = LocalGenericTheme.current
    val watermarkColor = color ?: theme.textPrimary
    val textMeasurer = rememberTextMeasurer()
    val style = TextStyle(
        color = watermarkColor.copy(alpha = opacity),
        fontSize = 48.sp,
    )

    Box(modifier = modifier.fillMaxSize()) {
        Canvas(modifier = Modifier.fillMaxSize()) {
            val measuredText = textMeasurer.measure(AnnotatedString(text), style)

            drawContext.canvas.save()
            drawContext.canvas.translate(
                (size.width - measuredText.size.width) / 2,
                (size.height - measuredText.size.height) / 2,
            )
            drawContext.canvas.rotate(rotation)
            drawText(
                textMeasurer = textMeasurer,
                text = text,
                topLeft = Offset(0f, 0f),
                style = style,
            )
            drawContext.canvas.restore()
        }
    }
}
