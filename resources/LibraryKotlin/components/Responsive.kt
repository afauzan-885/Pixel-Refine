package org.pixelrefine.genericui.components

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier

enum class DeviceType {
    Mobile, Tablet, Desktop
}

enum class Breakpoint {
    Small, Medium, Large, XLarge
}

@Composable
fun rememberDeviceType(): DeviceType = DeviceType.Desktop

@Composable
fun rememberBreakpoint(): Breakpoint = Breakpoint.Large

@Composable
fun Responsive(
    modifier: Modifier = Modifier,
    mobile: @Composable () -> Unit = {},
    tablet: @Composable () -> Unit = mobile,
    desktop: @Composable () -> Unit = tablet,
) {
    val deviceType = rememberDeviceType()

    Box(modifier = modifier.fillMaxSize()) {
        when (deviceType) {
            DeviceType.Mobile -> mobile()
            DeviceType.Tablet -> tablet()
            DeviceType.Desktop -> desktop()
        }
    }
}

@Composable
fun ShowOn(
    vararg types: DeviceType,
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit,
) {
    val deviceType = rememberDeviceType()

    Box(modifier = modifier) {
        if (deviceType in types) {
            content()
        }
    }
}

@Composable
fun HideOn(
    vararg types: DeviceType,
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit,
) {
    val deviceType = rememberDeviceType()

    Box(modifier = modifier) {
        if (deviceType !in types) {
            content()
        }
    }
}
