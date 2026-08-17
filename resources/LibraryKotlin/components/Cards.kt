package org.pixelrefine.genericui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.theme.LocalGenericTheme

/**
 * Python: `Card(title="")`
 */
@Composable
fun Card(
    title: String = "",
    modifier: Modifier = Modifier,
    padding: Dp = 16.dp,
    spacing: Dp = 8.dp,
    content: @Composable ColumnScope.() -> Unit = {},
) {
    val theme = LocalGenericTheme.current
    Column(
        modifier = modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(theme.radiusLg))
            .background(theme.bgCard)
            .border(1.dp, theme.borderColor, RoundedCornerShape(theme.radiusLg))
            .padding(padding),
        verticalArrangement = Arrangement.spacedBy(spacing),
    ) {
        if (title.isNotEmpty()) {
            Text(
                text = title,
                color = theme.textPrimary,
                fontWeight = FontWeight.Bold,
                fontSize = 16.sp,
            )
        }
        content()
    }
}

/** Python: `CardHeader(title="")` */
@Composable
fun CardHeader(
    title: String = "",
    modifier: Modifier = Modifier,
    action: (@Composable () -> Unit)? = null,
) {
    val theme = LocalGenericTheme.current
    Row(
        modifier = modifier.fillMaxWidth().padding(bottom = 8.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(title, color = theme.textPrimary, fontWeight = FontWeight.Bold, fontSize = 15.sp)
        action?.invoke()
    }
}

/** Python: `CardBody()` */
@Composable
fun CardBody(
    modifier: Modifier = Modifier,
    content: @Composable ColumnScope.() -> Unit,
) {
    Column(modifier = modifier.fillMaxWidth(), content = content)
}

/** Python: `CardFooter()` */
@Composable
fun CardFooter(
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit,
) {
    Box(modifier = modifier.fillMaxWidth().padding(top = 8.dp)) {
        content()
    }
}

/** Python: `CardGroup()` */
@Composable
fun CardGroup(
    modifier: Modifier = Modifier,
    spacing: Dp = 10.dp,
    content: @Composable ColumnScope.() -> Unit,
) {
    Column(
        modifier = modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(spacing),
        content = content,
    )
}

/**
 * Python: `FeatureCard(title="", description="", icon="")`
 */
@Composable
fun FeatureCard(
    title: String = "",
    description: String = "",
    icon: String = "",
    onClick: (() -> Unit)? = null,
    modifier: Modifier = Modifier,
) {
    val theme = LocalGenericTheme.current
    val clickableModifier = if (onClick != null) Modifier.clickable { onClick() } else Modifier

    Row(
        modifier = modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(theme.radiusLg))
            .background(theme.bgCard)
            .border(1.dp, theme.borderColor, RoundedCornerShape(theme.radiusLg))
            .then(clickableModifier)
            .padding(14.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        if (icon.isNotEmpty()) {
            Box(
                modifier = Modifier
                    .size(40.dp)
                    .clip(RoundedCornerShape(theme.radiusMd))
                    .background(theme.bgSecondary),
                contentAlignment = Alignment.Center,
            ) {
                Text(icon, fontSize = 20.sp)
            }
        }
        Column(modifier = Modifier.weight(1f)) {
            Text(title, color = theme.textPrimary, fontWeight = FontWeight.Bold, fontSize = 14.sp)
            if (description.isNotEmpty()) {
                Text(description, color = theme.textMuted, fontSize = 12.sp)
            }
        }
    }
}
