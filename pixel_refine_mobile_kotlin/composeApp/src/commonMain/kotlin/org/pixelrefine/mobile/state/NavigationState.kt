package org.pixelrefine.mobile.state

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue

/**
 * Screen Route Enum
 */
enum class AppScreen {
    WELCOME,
    HOME,
    HOME_PROJECTS,
    PROJECT_WORKSPACE,
}

/**
 * Global Navigation State Manager
 */
class NavigationState {
    var currentScreen by mutableStateOf(AppScreen.WELCOME)

    fun navigateTo(screen: AppScreen) {
        currentScreen = screen
    }

    fun goBack() {
        currentScreen = when (currentScreen) {
            AppScreen.HOME_PROJECTS -> AppScreen.HOME
            AppScreen.PROJECT_WORKSPACE -> AppScreen.HOME
            AppScreen.HOME -> AppScreen.HOME
            AppScreen.WELCOME -> AppScreen.HOME
        }
    }
}
