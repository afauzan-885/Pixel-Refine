package org.pixelrefine.genericui.domain.state

import java.util.concurrent.ConcurrentHashMap

/**
 * State Checkpoint Data untuk Pemulihan Sesi (Fault-Tolerant Session Recovery).
 */
data class SessionCheckpoint(
    val batchId: String,
    val totalFrames: Int,
    val completedFrames: Int,
    val lastProcessedPath: String?,
    val timestamp: Long = System.currentTimeMillis(),
)

/**
 * Manajer Pemulihan Sesi jika Terjadi Crash atau Force Close (Thread-Safe).
 */
object SessionCheckpointManager {

    private val activeCheckpoints = ConcurrentHashMap<String, SessionCheckpoint>()

    fun recordProgress(batchId: String, total: Int, completed: Int, lastPath: String?) {
        activeCheckpoints[batchId] = SessionCheckpoint(
            batchId = batchId,
            totalFrames = total,
            completedFrames = completed,
            lastProcessedPath = lastPath,
        )
    }

    fun getCheckpoint(batchId: String): SessionCheckpoint? {
        return activeCheckpoints[batchId]
    }

    fun clearCheckpoint(batchId: String) {
        activeCheckpoints.remove(batchId)
    }

    fun hasPendingRecovery(batchId: String): Boolean {
        val cp = activeCheckpoints[batchId] ?: return false
        return cp.completedFrames > 0 && cp.completedFrames < cp.totalFrames
    }
}
