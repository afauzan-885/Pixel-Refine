package org.pixelrefine.mobile

import androidx.compose.animation.Crossfade
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import org.pixelrefine.genericui.animations.ToastHost
import org.pixelrefine.genericui.theme.GenericThemeProvider
import org.pixelrefine.genericui.theme.LightTheme
import org.pixelrefine.mobile.state.AppScreen
import org.pixelrefine.mobile.state.NavigationState
import org.pixelrefine.mobile.state.ProjectState
import org.pixelrefine.mobile.ui.HomeProjectsScreen
import org.pixelrefine.mobile.ui.HomeScreen
import org.pixelrefine.mobile.ui.ProjectScreen
import org.pixelrefine.mobile.ui.WelcomeScreen

/**
 * Root Application Container dengan Multi-Screen Router & Theme Manager.
 */
@Composable
fun App() {
    val navState = remember { NavigationState() }
    val projectState = remember { ProjectState() }

    GenericThemeProvider(theme = LightTheme) {
        Crossfade(targetState = navState.currentScreen) { screen ->
            when (screen) {
                AppScreen.WELCOME -> {
                    WelcomeScreen(
                        onTimeout = {
                            navState.navigateTo(AppScreen.HOME)
                        }
                    )
                }

                AppScreen.HOME -> {
                    HomeScreen(
                        onOpenDenoising = {
                            navState.navigateTo(AppScreen.PROJECT_WORKSPACE)
                        },
                        onOpenProjects = {
                            navState.navigateTo(AppScreen.HOME_PROJECTS)
                        },
                    )
                }

                AppScreen.HOME_PROJECTS -> {
                    HomeProjectsScreen(
                        onBack = {
                            navState.navigateTo(AppScreen.HOME)
                        },
                        onOpenProject = { projectName ->
                            navState.navigateTo(AppScreen.PROJECT_WORKSPACE)
                        },
                    )
                }

                AppScreen.PROJECT_WORKSPACE -> {
                    ProjectScreen(
                        state = projectState,
                        onBack = {
                            navState.navigateTo(AppScreen.HOME)
                        },
                    )
                }
            }
        }

        // Host Toast Notifikasi Global
        ToastHost()
    }
}
