package org.pixelrefine.genericui.components

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import org.pixelrefine.genericui.theme.LocalGenericTheme
import androidx.compose.material3.Text
import androidx.compose.ui.unit.sp

enum class QRErrorCorrection {
    L, // ~7%
    M, // ~15%
    Q, // ~25%
    H  // ~30%
}

@Composable
fun QRCode(
    data: String,
    modifier: Modifier = Modifier,
    size: Dp = 200.dp,
    foregroundColor: Color? = null,
    backgroundColor: Color? = null,
    errorCorrection: QRErrorCorrection = QRErrorCorrection.M,
) {
    val theme = LocalGenericTheme.current
    val fgColor = foregroundColor ?: theme.dark
    val bgColor = backgroundColor ?: theme.bgCard

    // Generate QR matrix (simplified - just visual placeholder)
    val matrix = remember(data, errorCorrection) {
        generateQRMatrix(data, 25, 25) // 25x25 matrix
    }

    Box(
        modifier = modifier
            .size(size)
            .clip(RoundedCornerShape(8.dp))
            .background(bgColor)
            .border(1.dp, theme.borderColor, RoundedCornerShape(8.dp))
            .padding(8.dp),
    ) {
        Canvas(modifier = Modifier.fillMaxSize()) {
            val cellSize = this.size.width / matrix.size.toFloat()

            // Draw background
            drawRect(color = bgColor, size = this.size)

            // Draw modules
            for (y in matrix.indices) {
                for (x in matrix[y].indices) {
                    if (matrix[y][x]) {
                        drawRect(
                            color = fgColor,
                            topLeft = Offset(x * cellSize, y * cellSize),
                            size = Size(cellSize, cellSize),
                        )
                    }
                }
            }
        }
    }
}

/**
 * Simplified QR matrix generator.
 * In production, use a real QR encoding library.
 * This generates a deterministic pattern based on the data.
 */
private fun generateQRMatrix(data: String, rows: Int, cols: Int): Array<BooleanArray> {
    val matrix = Array(rows) { BooleanArray(cols) }

    // Simple hash-based pattern
    val hash = data.hashCode()
    val random = java.util.Random(hash.toLong())

    // Add finder patterns (corners) - 7x7 squares
    addFinderPattern(matrix, 0, 0)
    addFinderPattern(matrix, 0, cols - 7)
    addFinderPattern(matrix, rows - 7, 0)

    // Add alignment pattern (center)
    if (rows > 14 && cols > 14) {
        addAlignmentPattern(matrix, rows / 2 - 1, cols / 2 - 1)
    }

    // Fill data with deterministic pattern
    for (i in 0 until rows * cols) {
        val r = i / cols
        val c = i % cols
        if (!isReservedArea(r, c, rows, cols)) {
            matrix[r][c] = random.nextBoolean()
        }
    }

    return matrix
}

private fun addFinderPattern(matrix: Array<BooleanArray>, startRow: Int, startCol: Int) {
    for (r in 0 until 7) {
        for (c in 0 until 7) {
            val isOuter = r == 0 || r == 6 || c == 0 || c == 6
            val isCenter = r in 2..4 && c in 2..4
            matrix[startRow + r][startCol + c] = isOuter || isCenter
        }
    }
}

private fun addAlignmentPattern(matrix: Array<BooleanArray>, centerRow: Int, centerCol: Int) {
    for (r in -2..2) {
        for (c in -2..2) {
            val isOuter = kotlin.math.abs(r) == 2 || kotlin.math.abs(c) == 2
            val isCenter = r == 0 && c == 0
            val targetRow = centerRow + r
            val targetCol = centerCol + c
            if (targetRow in matrix.indices && targetCol in matrix[0].indices) {
                matrix[targetRow][targetCol] = isOuter || isCenter
            }
        }
    }
}

private fun isReservedArea(row: Int, col: Int, rows: Int, cols: Int): Boolean {
    // Top-left finder
    if (row < 8 && col < 8) return true
    // Top-right finder
    if (row < 8 && col >= cols - 8) return true
    // Bottom-left finder
    if (row >= rows - 8 && col < 8) return true
    // Center alignment
    if (row >= rows / 2 - 3 && row <= rows / 2 + 3 && col >= cols / 2 - 3 && col <= cols / 2 + 3) return true
    return false
}

@Composable
fun QRCodeWithLabel(
    data: String,
    label: String,
    modifier: Modifier = Modifier,
    size: Dp = 200.dp,
) {
    val theme = LocalGenericTheme.current

    Column(
        modifier = modifier,
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        QRCode(
            data = data,
            size = size,
        )

        Spacer(modifier = Modifier.height(8.dp))

        Text(
            text = label,
            color = theme.textPrimary,
            fontSize = 14.sp,
        )
    }
}
