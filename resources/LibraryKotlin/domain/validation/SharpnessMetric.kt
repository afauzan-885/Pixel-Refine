package org.pixelrefine.genericui.domain.validation

import org.pixelrefine.genericui.domain.models.ImageItem
import java.nio.ByteBuffer

/**
 * Evaluator Ketajaman Otomatis Berbasis Laplacian Variance (Smart AI Culling).
 *
 * Mengidentifikasi frame tertajam di antara burst shot dan menetapkannya
 * sebagai Best/Reference Image (★).
 */
object SharpnessMetric {

    /**
     * Menghitung nilai estimasi fokus/ketajaman (Laplacian Variance approximation)
     * dari raw buffer grayscale.
     */
    fun computeSharpness(buffer: ByteBuffer, width: Int, height: Int): Double {
        if (width < 3 || height < 3) return 0.0
        // Pastikan buffer punya cukup data dari posisi saat ini
        val requiredBytes = width * height
        if (buffer.remaining() < requiredBytes) return 0.0

        val startPos = buffer.position()
        val rowStride = width
        var sumLaplacian = 0.0
        var sumSquareLaplacian = 0.0
        var count = 0

        // Subsample cepat 4x4 grid untuk kecepatan maksimal
        for (y in 1 until height - 1 step 4) {
            for (x in 1 until width - 1 step 4) {
                val center = buffer.get(startPos + y * rowStride + x).toInt() and 0xFF
                val up = buffer.get(startPos + (y - 1) * rowStride + x).toInt() and 0xFF
                val down = buffer.get(startPos + (y + 1) * rowStride + x).toInt() and 0xFF
                val left = buffer.get(startPos + y * rowStride + (x - 1)).toInt() and 0xFF
                val right = buffer.get(startPos + y * rowStride + (x + 1)).toInt() and 0xFF

                // Discrete Laplace kernel: 4*center - (up + down + left + right)
                val lap = (4 * center - (up + down + left + right)).toDouble()
                sumLaplacian += lap
                sumSquareLaplacian += lap * lap
                count++
            }
        }

        if (count == 0) return 0.0
        val mean = sumLaplacian / count
        val variance = (sumSquareLaplacian / count) - (mean * mean)
        return variance.coerceAtLeast(0.0)
    }

    /**
     * Smart Culling: Menandai foto dengan skor ketajaman tertinggi sebagai reference frame (★).
     */
    fun autoAssignBestReference(images: List<ImageItem>, scores: List<Double>): List<ImageItem> {
        if (images.isEmpty() || images.size != scores.size) return images

        val maxIndex = scores.indices.maxByOrNull { scores[it] } ?: 0

        return images.mapIndexed { index, item ->
            item.copy(isReference = (index == maxIndex))
        }
    }
}
