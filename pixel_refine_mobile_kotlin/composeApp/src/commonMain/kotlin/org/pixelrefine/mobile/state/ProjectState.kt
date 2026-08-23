package org.pixelrefine.mobile.state

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import org.pixelrefine.genericui.components.Variant
import org.pixelrefine.genericui.domain.models.BatchItem
import org.pixelrefine.genericui.domain.models.BatchStatus
import org.pixelrefine.genericui.domain.models.ImageItem
import org.pixelrefine.genericui.save_checkpoint
import org.pixelrefine.genericui.toast

/**
 * State Holder untuk Mobile Project Page (Mengadopsi pola WorkspaceState pada Desktop).
 */
class ProjectState {
    // 1. Daftar Batch
    val batches = mutableStateListOf<BatchItem>().apply {
        add(
            BatchItem(
                id = 1L,
                name = "Batch 1",
                status = BatchStatus.IDLE,
                images = (1..13).map { idx ->
                    ImageItem(
                        id = idx.toLong(),
                        path = "/storage/emulated/0/DCIM/Raw/IMG_${idx.toString().padStart(3, '0')}.dng",
                        isReference = idx == 1,
                    )
                },
            )
        )
        add(
            BatchItem(
                id = 2L,
                name = "Batch 2",
                status = BatchStatus.IDLE,
                images = (1..8).map { idx ->
                    ImageItem(
                        id = (100 + idx).toLong(),
                        path = "/storage/emulated/0/DCIM/Raw/RAW_${idx.toString().padStart(3, '0')}.dng",
                        isReference = idx == 1,
                    )
                },
            )
        )
        add(
            BatchItem(
                id = 3L,
                name = "Batch 3",
                status = BatchStatus.IDLE,
                images = (1..20).map { idx ->
                    ImageItem(
                        id = (200 + idx).toLong(),
                        path = "/storage/emulated/0/DCIM/Raw/PHOTO_${idx.toString().padStart(3, '0')}.dng",
                        isReference = idx == 1,
                    )
                },
            )
        )
        add(
            BatchItem(
                id = 4L,
                name = "Batch 4",
                status = BatchStatus.IDLE,
                images = (1..15).map { idx ->
                    ImageItem(
                        id = (300 + idx).toLong(),
                        path = "/storage/emulated/0/DCIM/Raw/FRAME_${idx.toString().padStart(3, '0')}.dng",
                        isReference = idx == 1,
                    )
                },
            )
        )
    }

    // 2. Indeks Terpilih
    var selectedBatchIndex by mutableIntStateOf(0)
    var selectedImageIndex by mutableIntStateOf(0)

    // 3. Algorithm Methods
    val algorithmMethods = listOf("Align", "SR/Denoise", "Ake2A", "Smart Merging")
    var selectedMethodIndex by mutableIntStateOf(1) // Default: SR/Denoise

    // 4. Status Proses & Progress
    var isProcessing by mutableStateOf(false)
    var progressPercent by mutableIntStateOf(60)
    var statusMessage by mutableStateOf("Ready to process • 13 RAW frames loaded")

    // 5. Active Navigation Tab
    var activeNavTab by mutableStateOf("Denoiser")

    val activeBatch: BatchItem?
        get() = batches.getOrNull(selectedBatchIndex)

    val activeImage: ImageItem?
        get() = activeBatch?.images?.getOrNull(selectedImageIndex) ?: activeBatch?.images?.firstOrNull()

    // ---- Actions ----

    fun addNewBatch() {
        val newNum = batches.size + 1
        val newBatch = BatchItem(
            id = newNum.toLong(),
            name = "Batch $newNum",
            status = BatchStatus.IDLE,
            images = (1..10).map { idx ->
                ImageItem(
                    id = (newNum * 1000 + idx).toLong(),
                    path = "/storage/DCIM/BURST_$idx.dng",
                    isReference = idx == 1,
                )
            },
        )
        batches.add(newBatch)
        selectedBatchIndex = batches.lastIndex
        toast("Batch baru ditambahkan: ${newBatch.name}", Variant.Success)
    }

    fun selectBatch(index: Int) {
        if (index in batches.indices) {
            selectedBatchIndex = index
            selectedImageIndex = 0
            val b = batches[index]
            statusMessage = "Loaded ${b.name} (${b.imageCount} images)"
        }
    }

    fun toggleProcessing() {
        isProcessing = !isProcessing
        if (isProcessing) {
            progressPercent = 60
            statusMessage = "Processing Batch ${selectedBatchIndex + 1} (${algorithmMethods[selectedMethodIndex]}) • 60%"
            activeBatch?.let {
                save_checkpoint(it.id?.toString() ?: "batch_${selectedBatchIndex + 1}", it.imageCount, (it.imageCount * 0.6).toInt(), activeImage?.path ?: "")
            }
            toast("Memulai pemrosesan ${algorithmMethods[selectedMethodIndex]}...", Variant.Primary)
        } else {
            statusMessage = "Processing stopped"
            toast("Pemrosesan dihentikan", Variant.Warning)
        }
    }
}
