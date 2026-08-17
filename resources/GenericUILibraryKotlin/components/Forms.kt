package org.pixelrefine.genericui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.theme.LocalGenericTheme

/**
 * Python: `Input(placeholder="", value="")`
 */
@Composable
fun Input(
    value: String = "",
    onValueChange: (String) -> Unit = {},
    placeholder: String = "",
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
) {
    val theme = LocalGenericTheme.current
    BasicTextField(
        value = value,
        onValueChange = onValueChange,
        enabled = enabled,
        textStyle = TextStyle(color = theme.textPrimary, fontSize = 13.sp),
        cursorBrush = SolidColor(theme.primary),
        modifier = modifier
            .fillMaxWidth()
            .height(36.dp)
            .clip(RoundedCornerShape(theme.radiusMd))
            .background(theme.bgSecondary)
            .border(1.dp, theme.borderColor, RoundedCornerShape(theme.radiusMd))
            .padding(horizontal = 10.dp, vertical = 8.dp),
        decorationBox = { innerTextField ->
            if (value.isEmpty() && placeholder.isNotEmpty()) {
                Text(placeholder, color = theme.textMuted, fontSize = 13.sp)
            }
            innerTextField()
        },
    )
}

/**
 * Python: `Select(options=[...], value="")`
 */
@Composable
fun Select(
    options: List<String>,
    value: String = options.firstOrNull() ?: "",
    onValueChange: (String) -> Unit = {},
    modifier: Modifier = Modifier,
) {
    val theme = LocalGenericTheme.current
    var expanded by remember { mutableStateOf(false) }

    Box(modifier = modifier.fillMaxWidth()) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .height(36.dp)
                .clip(RoundedCornerShape(theme.radiusMd))
                .background(theme.bgSecondary)
                .border(1.dp, theme.borderColor, RoundedCornerShape(theme.radiusMd))
                .clickable { expanded = true }
                .padding(horizontal = 10.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.SpaceBetween,
        ) {
            Text(value, color = theme.textPrimary, fontSize = 13.sp)
            Text("▼", color = theme.textSecondary, fontSize = 10.sp)
        }

        DropdownMenu(
            expanded = expanded,
            onDismissRequest = { expanded = false },
            modifier = Modifier.background(theme.bgCard),
        ) {
            options.forEach { option ->
                DropdownMenuItem(
                    text = { Text(option, color = theme.textPrimary, fontSize = 13.sp) },
                    onClick = {
                        onValueChange(option)
                        expanded = false
                    },
                )
            }
        }
    }
}

/**
 * Python: `Checkbox(text="", checked=False)`
 */
@Composable
fun Checkbox(
    text: String = "",
    checked: Boolean = false,
    onCheckedChange: (Boolean) -> Unit = {},
    modifier: Modifier = Modifier,
) {
    val theme = LocalGenericTheme.current
    Row(
        modifier = modifier.clickable { onCheckedChange(!checked) }.padding(vertical = 4.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        Box(
            modifier = Modifier
                .size(18.dp)
                .clip(RoundedCornerShape(theme.radiusSm))
                .background(if (checked) theme.primary else theme.bgSecondary)
                .border(1.dp, if (checked) theme.primary else theme.borderColor, RoundedCornerShape(theme.radiusSm)),
            contentAlignment = Alignment.Center,
        ) {
            if (checked) {
                Text("✓", color = Color.White, fontSize = 12.sp, fontWeight = FontWeight.Bold)
            }
        }
        if (text.isNotEmpty()) {
            Text(text, color = theme.textPrimary, fontSize = 13.sp)
        }
    }
}

/**
 * Python: `Radio(text="", checked=False)`
 */
@Composable
fun Radio(
    text: String = "",
    checked: Boolean = false,
    onClick: () -> Unit = {},
    modifier: Modifier = Modifier,
) {
    val theme = LocalGenericTheme.current
    Row(
        modifier = modifier.clickable { onClick() }.padding(vertical = 4.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        Box(
            modifier = Modifier
                .size(18.dp)
                .clip(CircleShape)
                .background(theme.bgSecondary)
                .border(1.5.dp, if (checked) theme.primary else theme.borderColor, CircleShape),
            contentAlignment = Alignment.Center,
        ) {
            if (checked) {
                Box(
                    modifier = Modifier
                        .size(10.dp)
                        .clip(CircleShape)
                        .background(theme.primary),
                )
            }
        }
        if (text.isNotEmpty()) {
            Text(text, color = theme.textPrimary, fontSize = 13.sp)
        }
    }
}

/**
 * Python: `RadioGroup(options=[...], active_index=0)`
 */
@Composable
fun RadioGroup(
    options: List<String>,
    selectedIndex: Int = 0,
    onSelect: (Int) -> Unit = {},
    modifier: Modifier = Modifier,
) {
    Column(
        modifier = modifier,
        verticalArrangement = Arrangement.spacedBy(4.dp),
    ) {
        options.forEachIndexed { index, option ->
            Radio(
                text = option,
                checked = index == selectedIndex,
                onClick = { onSelect(index) },
            )
        }
    }
}

/**
 * Python: `FormGroup(label="", input_type="text")`
 */
@Composable
fun FormGroup(
    label: String = "",
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit,
) {
    val theme = LocalGenericTheme.current
    Column(
        modifier = modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(4.dp),
    ) {
        if (label.isNotEmpty()) {
            Text(label, color = theme.textSecondary, fontWeight = FontWeight.SemiBold, fontSize = 12.sp)
        }
        content()
    }
}

/**
 * Python: `FormRow()`
 */
@Composable
fun FormRow(
    spacing: androidx.compose.ui.unit.Dp = 10.dp,
    modifier: Modifier = Modifier,
    content: @Composable androidx.compose.foundation.layout.RowScope.() -> Unit,
) {
    Row(
        modifier = modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.spacedBy(spacing),
        verticalAlignment = Alignment.CenterVertically,
        content = content,
    )
}

/**
 * Python: `ToggleSwitch(checked=False)`
 */
@Composable
fun ToggleSwitch(
    checked: Boolean,
    onCheckedChange: (Boolean) -> Unit,
    modifier: Modifier = Modifier,
) {
    val theme = LocalGenericTheme.current
    Box(
        modifier = modifier
            .width(40.dp)
            .height(20.dp)
            .clip(CircleShape)
            .background(if (checked) theme.primary else theme.secondary)
            .clickable { onCheckedChange(!checked) },
    ) {
        Box(
            modifier = Modifier
                .size(16.dp)
                .align(Alignment.CenterStart)
                .offset(x = if (checked) 20.dp else 2.dp)
                .clip(CircleShape)
                .background(Color.White),
        )
    }
}

/** Alias `Switch` */
@Composable
fun Switch(
    checked: Boolean,
    onCheckedChange: (Boolean) -> Unit,
    modifier: Modifier = Modifier,
) {
    ToggleSwitch(checked = checked, onCheckedChange = onCheckedChange, modifier = modifier)
}
