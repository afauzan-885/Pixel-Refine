package org.pixelrefine.genericui.domain.project

import org.pixelrefine.genericui.domain.models.BatchItem

/**
 * Manifest metadata untuk file arsip proyek Pixel Refine (.prf)
 */
data class ProjectManifest(
    val formatVersion: String = "1.0",
    val appVersion: String = "1.0.0",
    val projectName: String,
    val activeBatchId: Long? = null,
    val batchCount: Int,
    val totalImages: Int,
    val stateToken: String,
)

/**
 * Manager untuk penyimpanan dan pemuatan berkas proyek `.prf` (Mirror `project_archive.py`)
 */
object ProjectArchiveManager {

    private val recentProjectsList = mutableListOf<String>()

    fun recentProjects(): List<String> = recentProjectsList.toList()

    fun calculateSessionToken(batches: List<BatchItem>): String {
        val raw = batches.joinToString(";") { b ->
            "${b.name}:${b.imageCount}:${b.images.joinToString(",") { it.path }}"
        }
        return raw.hashCode().toString(16)
    }

    /**
     * Memeriksa apakah terdapat perubahan yang belum tersimpan dibandingkan baseline token.
     */
    fun hasUnsavedChanges(currentBatches: List<BatchItem>, baselineToken: String?): Boolean {
        if (baselineToken == null) {
            return currentBatches.any { it.images.isNotEmpty() }
        }
        return calculateSessionToken(currentBatches) != baselineToken
    }

    /**
     * Menyimpan proyek ke format manifest/archive.
     */
    fun saveProject(
        path: String,
        batches: List<BatchItem>,
        activeBatchId: Long? = null,
    ): ProjectManifest {
        val totalImages = batches.sumOf { it.imageCount }
        val token = calculateSessionToken(batches)
        val projectName = path.substringAfterLast('/').substringAfterLast('\\').removeSuffix(".prf")

        val manifest = ProjectManifest(
            projectName = projectName,
            activeBatchId = activeBatchId,
            batchCount = batches.size,
            totalImages = totalImages,
            stateToken = token,
        )

        recentProjectsList.remove(path)
        recentProjectsList.add(0, path)

        return manifest
    }
}
