package org.pixelrefine.mobile

import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Window
import androidx.compose.ui.window.application
import androidx.compose.ui.window.rememberWindowState

/**
 * Entry point desktop — untuk menguji UI mobile di PC (Windows/Linux/macOS)
 * tanpa emulator. Ukuran jendela 360x640 meniru viewport Android.
 */
fun main() = application {
    Window(
        onCloseRequest = ::exitApplication,
        title = "Pixel Refine Mobile",
        state = rememberWindowState(width = 360.dp, height = 640.dp),
    ) {
        App()
    }
}
