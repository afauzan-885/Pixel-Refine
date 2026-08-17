package org.pixelrefine.genericui.domain.state

import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue

/**
 * Single source of truth untuk toggle fitur thumbnail di seluruh aplikasi.
 *
 * Mirror: `ThumbnailPolicy.py`
 */
class ThumbnailPolicyState(initialEnabled: Boolean = true) {
    var isEnabled by mutableStateOf(initialEnabled)

    fun toggle() {
        isEnabled = !isEnabled
    }

    fun set(enabled: Boolean) {
        isEnabled = enabled
    }
}

val GlobalThumbnailPolicy = ThumbnailPolicyState(initialEnabled = true)

@Composable
fun rememberThumbnailPolicy(initialEnabled: Boolean = true): ThumbnailPolicyState {
    return remember { ThumbnailPolicyState(initialEnabled) }
}
