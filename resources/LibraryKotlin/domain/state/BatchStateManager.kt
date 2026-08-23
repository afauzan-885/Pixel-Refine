package org.pixelrefine.genericui.domain.state

import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import org.pixelrefine.genericui.domain.models.BatchItem
import org.pixelrefine.genericui.domain.models.ImageItem
import org.pixelrefine.genericui.domain.validation.ImageValidator

/**
 * State Manager untuk pengelolaan Batch & Gambar — Reaktif, Ringan, Zero-Boilerplate.
 */
class BatchStateManager(initialBatches: List<BatchItem> = emptyList()) {
    private val lock = Any()
    val batches = mutableStateListOf<BatchItem>().apply { addAll(initialBatches) }
    var activeBatchIndex by mutableStateOf(if (initialBatches.isNotEmpty()) 0 else -1)

    val activeBatch: BatchItem?
        get() = synchronized(lock) {
            if (activeBatchIndex in batches.indices) batches[activeBatchIndex] else null
        }

    fun selectBatch(index: Int) = synchronized(lock) {
        if (index in batches.indices) {
            activeBatchIndex = index
        }
    }

    fun addBatch(name: String, imagePaths: List<String> = emptyList()): BatchItem = synchronized(lock) {
        val validated = ImageValidator.validatePaths(imagePaths).accepted
        val newBatch = BatchItem(name = name, images = validated)
        batches.add(newBatch)
        if (activeBatchIndex == -1) {
            activeBatchIndex = batches.lastIndex
        }
        newBatch
    }

    fun removeBatch(index: Int) = synchronized(lock) {
        if (index in batches.indices) {
            batches.removeAt(index)
            if (batches.isEmpty()) {
                activeBatchIndex = -1
            } else if (activeBatchIndex >= batches.size) {
                activeBatchIndex = batches.lastIndex
            }
        }
    }

    fun addImagesToActiveBatch(paths: List<String>) = synchronized(lock) {
        val current = activeBatch ?: return
        val existingPaths = current.images.map { it.path }.toSet()
        val result = ImageValidator.validatePaths(paths, existingPaths)
        var updated = current
        result.accepted.forEach { img ->
            updated = updated.addImage(img)
        }
        batches[activeBatchIndex] = updated
    }

    fun removeImageFromActiveBatch(path: String) {
        val current = activeBatch ?: return
        batches[activeBatchIndex] = current.removeImage(path)
    }

    fun setReferenceImage(path: String) {
        val current = activeBatch ?: return
        batches[activeBatchIndex] = current.setReference(path)
    }

    fun toggleSelectImage(path: String) {
        val current = activeBatch ?: return
        batches[activeBatchIndex] = current.toggleSelect(path)
    }
}

/**
 * Composable factory helper
 */
@Composable
fun rememberBatchStateManager(initialBatches: List<BatchItem> = emptyList()): BatchStateManager {
    return remember { BatchStateManager(initialBatches) }
}
