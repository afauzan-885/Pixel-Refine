package org.pixelrefine.genericui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.unit.dp
import org.pixelrefine.genericui.theme.LocalGenericTheme

/**
 * Python: `DotIndicator(count, active_index=0)`
 */
@Composable
fun DotIndicator(
    count: Int,
    activeIndex: Int = 0,
    onIndexChanged: ((Int) -> Unit)? = null,
    modifier: Modifier = Modifier,
) {
    val theme = LocalGenericTheme.current
    Row(
        modifier = modifier.padding(vertical = 8.dp),
        horizontalArrangement = Arrangement.spacedBy(6.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        repeat(count) { index ->
            val active = index == activeIndex
            Box(
                modifier = Modifier
                    .size(if (active) 10.dp else 6.dp)
                    .clip(CircleShape)
                    .background(if (active) theme.primary else theme.textMuted)
                    .clickable(enabled = onIndexChanged != null) { onIndexChanged?.invoke(index) },
            )
        }
    }
}
