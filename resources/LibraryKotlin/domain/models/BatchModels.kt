package org.pixelrefine.genericui.domain.models

/**
 * Entitas data gambar murni (Mirror `ImageModel.py` - KISS & Immutable)
 */
data class ImageItem(
    val id: Long? = null,
    val path: String,
    val isReference: Boolean = false,
    val isSelected: Boolean = false,
) {
    val filename: String
        get() = path.substringAfterLast('/').substringAfterLast('\\')

    val extension: String
        get() = path.substringAfterLast('.', "").lowercase()

    val isRaw: Boolean
        get() = extension in RawExtensions

    companion object {
        val RawExtensions = setOf("dng", "raw", "cr2", "nef", "arw", "orf", "rw2", "pef", "raf")
        val StandardExtensions = setOf("jpg", "jpeg", "png", "tif", "tiff", "webp", "bmp")
        val AllSupportedExtensions = StandardExtensions + RawExtensions
    }
}

/**
 * Status proses batch
 */
enum class BatchStatus {
    IDLE,
    PROCESSING,
    COMPLETED,
    ERROR,
}

/**
 * Entitas data batch gambar murni (Mirror `BatchModel.py` - KISS & Immutable)
 */
data class BatchItem(
    val id: Long? = null,
    val name: String,
    val images: List<ImageItem> = emptyList(),
    val status: BatchStatus = BatchStatus.IDLE,
) {
    val imageCount: Int
        get() = images.size

    val referenceImage: ImageItem?
        get() = images.firstOrNull { it.isReference } ?: images.firstOrNull()

    val selectedImages: List<ImageItem>
        get() = images.filter { it.isSelected }

    /**
     * Menambahkan gambar dengan otomatis menjadikan gambar pertama sebagai reference.
     */
    fun addImage(image: ImageItem): BatchItem {
        if (images.any { it.path == image.path }) return this
        val makeReference = images.isEmpty() || image.isReference
        val newImage = if (makeReference) image.copy(isReference = true) else image
        return copy(images = images + newImage)
    }

    /**
     * Menghapus gambar berdasarkan path.
     */
    fun removeImage(path: String): BatchItem {
        val filtered = images.filterNot { it.path == path }
        // Pastikan ada satu reference jika masih ada gambar tersisa
        val updated = if (filtered.isNotEmpty() && filtered.none { it.isReference }) {
            filtered.mapIndexed { index, img -> if (index == 0) img.copy(isReference = true) else img }
        } else {
            filtered
        }
        return copy(images = updated)
    }

    /**
     * Mengatur reference image berdasarkan path.
     */
    fun setReference(path: String): BatchItem {
        return copy(images = images.map { img ->
            img.copy(isReference = img.path == path)
        })
    }

    /**
     * Toggle status seleksi gambar.
     */
    fun toggleSelect(path: String): BatchItem {
        return copy(images = images.map { img ->
            if (img.path == path) img.copy(isSelected = !img.isSelected) else img
        })
    }
}
