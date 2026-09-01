package org.pixelrefine.genericui.components

import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.compositionLocalOf
import androidx.compose.runtime.staticCompositionLocalOf
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.TextUnit
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.theme.GenericTheme
import org.pixelrefine.genericui.theme.LocalGenericTheme
import org.pixelrefine.genericui.theme.LightTheme
import org.pixelrefine.genericui.theme.DarkTheme

enum class LayoutDirection {
    LTR, RTL
}

enum class ComponentSize {
    Small, Medium, Large
}

data class Config(
    val direction: LayoutDirection = LayoutDirection.LTR,
    val size: ComponentSize = ComponentSize.Medium,
    val locale: String = "en",
    val theme: GenericTheme = LightTheme,
)

val LocalConfig = staticCompositionLocalOf { Config() }

@Composable
fun ConfigProvider(
    config: Config,
    content: @Composable () -> Unit,
) {
    CompositionLocalProvider(
        LocalConfig provides config,
        LocalGenericTheme provides config.theme,
        content = content,
    )
}

@Composable
fun useConfig(): Config = LocalConfig.current

@Composable
fun withConfig(
    config: Config,
    content: @Composable () -> Unit,
) {
    ConfigProvider(config = config) {
        content()
    }
}

@Composable
fun ThemedConfig(
    theme: GenericTheme = LightTheme,
    direction: LayoutDirection = LayoutDirection.LTR,
    size: ComponentSize = ComponentSize.Medium,
    locale: String = "en",
    content: @Composable () -> Unit,
) {
    ConfigProvider(
        config = Config(
            theme = theme,
            direction = direction,
            size = size,
            locale = locale,
        ),
        content = content,
    )
}

@Composable
fun DarkModeConfig(
    content: @Composable () -> Unit,
) {
    ThemedConfig(theme = DarkTheme) {
        content()
    }
}
