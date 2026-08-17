package org.pixelrefine.mobile.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import org.pixelrefine.genericui.components.BackButton
import org.pixelrefine.genericui.components.Card
import org.pixelrefine.genericui.components.Container
import org.pixelrefine.genericui.components.Row
import org.pixelrefine.genericui.components.ScrollableColumn
import org.pixelrefine.genericui.components.Switch
import org.pixelrefine.genericui.theme.LocalTheme
import org.pixelrefine.mobile.model.LANGUAGES

/**
 * Screen Settings — mirror `build_settings_page()` di main_mobile.py:
 * General (Language) + Performance (GPU) + Appearance (dark theme) + About.
 * (Versi Python belum berfungsi penuh; versi Kotlin ini fungsional.)
 */
@Composable
fun SettingsScreen(
    isDark: Boolean,
    onToggleDark: (Boolean) -> Unit,
    onBack: () -> Unit,
) {
    val theme = LocalTheme.current
    var language by remember { mutableStateOf(LANGUAGES[0]) }
    var showLanguageDialog by remember { mutableStateOf(false) }

    ScrollableColumn {
        Row(spacing = 8.dp, modifier = Modifier.fillMaxWidth().padding(10.dp)) {
            BackButton(onClick = onBack)
            Text(
                "Settings",
                color = theme.textPrimary,
                fontWeight = androidx.compose.ui.text.font.FontWeight.Bold,
                fontSize = 20.sp,
                modifier = Modifier.padding(start = 4.dp),
            )
        }
        Container(padding = 10.dp, spacing = 10.dp) {
            Card(title = "General") {
                SettingRow(label = "Language", value = language, onClick = { showLanguageDialog = true })
            }
            Card(title = "Performance") {
                SettingRow(label = "GPU Settings", value = "Auto", onClick = {})
            }
            Card(title = "Appearance") {
                Row(spacing = 8.dp, modifier = Modifier.fillMaxWidth()) {
                    Text(
                        "Dark Theme",
                        color = theme.textPrimary,
                        fontSize = 12.sp,
                        modifier = Modifier.weight(1f),
                    )
                    Switch(checked = isDark, onCheckedChange = onToggleDark)
                }
            }
            Card(title = "About") {
                Text(
                    "Pixel Refine Mobile v0.6.0\nReimplementasi Kotlin (Compose Multiplatform).",
                    color = theme.textSecondary,
                    fontSize = 11.sp,
                )
            }
        }
    }

    if (showLanguageDialog) {
        LanguageDialog(
            current = language,
            onSelect = { language = it; showLanguageDialog = false },
            onDismiss = { showLanguageDialog = false },
        )
    }
}

/** Baris pengaturan sederhana (label + nilai + chevron). */
@Composable
private fun SettingRow(label: String, value: String, onClick: () -> Unit) {
    val theme = LocalTheme.current
    Row(spacing = 8.dp, modifier = Modifier.fillMaxWidth().clickable(onClick = onClick)) {
        Text(label, color = theme.textPrimary, fontSize = 12.sp, modifier = Modifier.weight(1f))
        Text(value, color = theme.textMuted, fontSize = 11.sp)
        Text("›", color = theme.textMuted, fontSize = 14.sp)
    }
}

/** Dialog pilihan bahasa — mirror modal sederhana (KISS). */
@Composable
private fun LanguageDialog(
    current: String,
    onSelect: (String) -> Unit,
    onDismiss: () -> Unit,
) {
    val theme = LocalTheme.current
    Dialog(onDismissRequest = onDismiss) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(theme.radiusLg))
                .background(theme.bgCard)
                .border(1.dp, theme.borderColor, RoundedCornerShape(theme.radiusLg))
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            Text("Language", color = theme.textPrimary, fontWeight = androidx.compose.ui.text.font.FontWeight.Bold, fontSize = 14.sp)
            LANGUAGES.forEach { lang ->
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(theme.radiusMd))
                        .background(if (lang == current) theme.primary.copy(alpha = 0.15f) else androidx.compose.ui.graphics.Color.Transparent)
                        .clickable { onSelect(lang) }
                        .padding(10.dp),
                    contentAlignment = Alignment.CenterStart,
                ) {
                    Text(
                        lang,
                        color = if (lang == current) theme.primary else theme.textPrimary,
                        fontWeight = androidx.compose.ui.text.font.FontWeight.Bold,
                        fontSize = 12.sp,
                    )
                }
            }
        }
    }
}
