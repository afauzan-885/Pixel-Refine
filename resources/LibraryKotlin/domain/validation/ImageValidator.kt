package org.pixelrefine.genericui.domain.validation

import org.pixelrefine.genericui.domain.models.ImageItem

/**
 * Informasi berkas yang ditolak saat validasi
 */
data class RejectedPathInfo(
    val path: String,
    val reason: String,
)

/**
 * Hasil validasi import sekumpulan berkas gambar
 */
data class ValidationResult(
    val accepted: List<ImageItem>,
    val rejected: List<RejectedPathInfo>,
) {
    val totalCount: Int get() = accepted.size + rejected.size
    val isAllAccepted: Boolean get() = rejected.isEmpty() && accepted.isNotEmpty()
}

/**
 * Validator berkas gambar terpusat (Mirror `image_import_validation.py` - KISS & Pure Logic)
 */
object ImageValidator {

    /**
     * Memvalidasi sekumpulan path file gambar.
     *
     * @param candidates Daftar path berkas yang dipilih pengguna
     * @param existingPaths Daftar path yang sudah ada di batch (untuk deduplikasi)
     */
    fun validatePaths(
        candidates: List<String>,
        existingPaths: Set<String> = emptySet(),
    ): ValidationResult {
        val accepted = mutableListOf<ImageItem>()
        val rejected = mutableListOf<RejectedPathInfo>()
        val seen = existingPaths.toMutableSet()

        for (candidate in candidates) {
            val trimmed = candidate.trim()
            if (trimmed.isEmpty()) {
                rejected.add(RejectedPathInfo(candidate, "Path kosong"))
                continue
            }

            val ext = trimmed.substringAfterLast('.', "").lowercase()
            if (ext.isEmpty() || ext !in ImageItem.AllSupportedExtensions) {
                rejected.add(RejectedPathInfo(candidate, "Format file tidak didukung: .$ext"))
                continue
            }

            if (trimmed in seen) {
                rejected.add(RejectedPathInfo(candidate, "Gambar sudah ada dalam batch (duplikat)"))
                continue
            }

            seen.add(trimmed)
            accepted.add(ImageItem(path = trimmed))
        }

        return ValidationResult(accepted = accepted, rejected = rejected)
    }
}
