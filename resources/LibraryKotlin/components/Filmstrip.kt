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
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.domain.models.ImageItem
import org.pixelrefine.genericui.theme.LocalGenericTheme

/**
 * Pita Filmstrip Horizontal untuk Penjelajahan Burst Image & Frame Ranking (Gaya Klasik Konsisten).
 */
@Composable
fun Filmstrip(
    images: List<ImageItem>,
    selectedIndex: Int = 0,
    onSelectImage: (Int) -> Unit = {},
    onSetReference: ((Int) -> Unit)? = null,
    height: Dp = 90.dp,
    modifier: Modifier = Modifier,
) {
    val theme = LocalGenericTheme.current

    LazyRow(
        modifier = modifier
            .fillMaxWidth()
            .height(height)
            .clip(RoundedCornerShape(theme.radiusMd))
            .background(theme.bgCard)
            .border(1.dp, theme.borderColor, RoundedCornerShape(theme.radiusMd))
            .padding(6.dp),
        horizontalArrangement = Arrangement.spacedBy(6.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        itemsIndexed(images) { index, item ->
            val isSelected = index == selectedIndex
            val borderColor = if (isSelected) theme.primary else if (item.isReference) theme.warning else theme.borderColor
            val borderWidth = if (isSelected) 2.dp else 1.dp

            Column(
                modifier = Modifier
                    .width(70.dp)
                    .height(height - 12.dp)
                    .clip(RoundedCornerShape(theme.radiusSm))
                    .background(theme.bgSecondary)
                    .border(borderWidth, borderColor, RoundedCornerShape(theme.radiusSm))
                    .clickable {
                        onSelectImage(index)
                        // Long-press-like behavior: jika item sudah selected dan bukan reference,
                        // set sebagai reference
                        if (isSelected && !item.isReference && onSetReference != null) {
                            onSetReference(index)
                        }
                    }
                    .padding(4.dp),
                verticalArrangement = Arrangement.SpaceBetween,
                horizontalAlignment = Alignment.CenterHorizontally,
            ) {
                Text(
                    text = "#${index + 1}",
                    color = theme.textMuted,
                    fontSize = 9.sp,
                    fontWeight = FontWeight.Bold,
                )
                if (item.isReference) {
                    Text("★", color = theme.warning, fontSize = 12.sp)
                }
                Text(
                    text = item.extension.uppercase(),
                    color = theme.textPrimary,
                    fontSize = 9.sp,
                    fontWeight = FontWeight.SemiBold,
                )
            }
        }
    }
}
