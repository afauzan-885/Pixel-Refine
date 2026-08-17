package org.pixelrefine.mobile

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import org.pixelrefine.mobile.model.Screen
import org.pixelrefine.genericui.theme.DarkTheme
import org.pixelrefine.genericui.theme.LightTheme
import org.pixelrefine.genericui.theme.LocalGenericTheme
import org.pixelrefine.genericui.theme.LocalTheme
import org.pixelrefine.mobile.ui.HomeScreen
import org.pixelrefine.mobile.ui.SettingsScreen
import org.pixelrefine.mobile.ui.WorkspaceScreen

/**
 * Root aplikasi — mirror AppState/navigation di main_mobile.py.
 * (KISS: navigasi sederhana pakai state Compose, tanpa library nav.)
 */
@Composable
fun App() {
    var isDark by remember { mutableStateOf(false) }
    val theme = if (isDark) DarkTheme else LightTheme

    var screen by remember { mutableStateOf<Screen>(Screen.Home) }
    var currentTool by remember { mutableStateOf("MFDenoiser") }

    CompositionLocalProvider(LocalTheme provides theme) {
        MaterialTheme {
            Box(Modifier.fillMaxSize().background(theme.bgSecondary)) {
                when (screen) {
                    Screen.Home -> HomeScreen(
                        onOpenTool = { tool ->
                            currentTool = tool
                            screen = Screen.Workspace
                        },
                        onOpenSettings = { screen = Screen.Settings },
                    )
                    Screen.Workspace -> WorkspaceScreen(
                        toolName = currentTool,
                        onHome = { screen = Screen.Home },
                        onSwitchTool = { tool -> currentTool = tool },
                    )
                    Screen.Settings -> SettingsScreen(
                        isDark = isDark,
                        onToggleDark = { isDark = it },
                        onBack = { screen = Screen.Home },
                    )
                }
            }
        }
    }
}
