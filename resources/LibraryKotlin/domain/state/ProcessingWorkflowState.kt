package org.pixelrefine.genericui.domain.state

import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue

/**
 * State mesin alur pemrosesan gambar
 */
sealed interface ProcessingState {
    object Idle : ProcessingState
    data class Running(val step: String, val progressFraction: Float, val currentBatch: String) : ProcessingState
    data class Success(val resultPath: String, val durationMs: Long) : ProcessingState
    data class Error(val message: String, val cause: Throwable? = null) : ProcessingState
}

/**
 * State manager untuk kontrol workflow eksekusi algoritma
 */
class WorkflowStateManager {
    var state by mutableStateOf<ProcessingState>(ProcessingState.Idle)
    var progress by mutableFloatStateOf(0f)
    var currentStep by mutableStateOf("")

    val isRunning: Boolean get() = state is ProcessingState.Running
    val isIdle: Boolean get() = state is ProcessingState.Idle

    fun start(batchName: String, initialStep: String = "Initializing") {
        progress = 0f
        currentStep = initialStep
        state = ProcessingState.Running(initialStep, 0f, batchName)
    }

    fun updateProgress(step: String, progressFraction: Float, batchName: String = "") {
        currentStep = step
        progress = progressFraction.coerceIn(0f, 1f)
        state = ProcessingState.Running(step, progress, batchName)
    }

    fun complete(resultPath: String, durationMs: Long) {
        progress = 1f
        state = ProcessingState.Success(resultPath, durationMs)
    }

    fun fail(errorMessage: String, cause: Throwable? = null) {
        state = ProcessingState.Error(errorMessage, cause)
    }

    fun reset() {
        progress = 0f
        currentStep = ""
        state = ProcessingState.Idle
    }
}

@Composable
fun rememberWorkflowStateManager(): WorkflowStateManager {
    return remember { WorkflowStateManager() }
}
