package org.pixelrefine.mobile.ui

import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.components.Button
import org.pixelrefine.genericui.components.Card
import org.pixelrefine.genericui.components.Container
import org.pixelrefine.genericui.components.ScrollableColumn
import org.pixelrefine.genericui.components.Spacer
import org.pixelrefine.genericui.components.Variant
import org.pixelrefine.genericui.theme.LocalTheme
import org.pixelrefine.mobile.model.TOOLS

/**
 * Screen Home — mirror `build_home_page()` di main_mobile.py:
 * kartu "Pixel Refine" + 4 kartu tool + kartu Settings.
 */
@Composable
fun HomeScreen(
    onOpenTool: (String) -> Unit,
    onOpenSettings: () -> Unit,
) {
    val theme = LocalTheme.current
    ScrollableColumn {
        Container(padding = 10.dp, spacing = 10.dp) {
            Card(title = "Pixel Refine") {
                Text(
                    "Computational Photography for Mobile",
                    color = theme.textSecondary,
                    fontSize = 11.sp,
                )
            }
            TOOLS.forEach { tool ->
                Card(title = "${tool.icon} ${tool.name}") {
                    Text(tool.description, color = theme.textMuted, fontSize = 11.sp)
                    Spacer(height = 4.dp)
                    Button(
                        text = "Open ${tool.name}",
                        variant = tool.variant,
                        onClick = { onOpenTool(tool.name) },
                    )
                }
            }
            Card(title = "Settings") {
                Button(
                    text = "Open Settings",
                    variant = Variant.Secondary,
                    onClick = onOpenSettings,
                )
            }
        }
    }
}
