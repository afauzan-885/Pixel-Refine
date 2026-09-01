package org.pixelrefine.genericui.components

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.*
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextDecoration
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.TextUnit
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.theme.GenericTheme
import org.pixelrefine.genericui.theme.LocalGenericTheme

// ============================================================================
// TYPOGRAPHY SYSTEM
// ============================================================================

enum class TypographyVariant {
    H1, H2, H3, H4, H5, H6,
    BODY1, BODY2,
    CAPTION,
    OVERLINE,
    CODE
}

@Composable
fun Heading(
    text: String,
    level: Int = 1,
    modifier: Modifier = Modifier,
    color: Color? = null,
    fontWeight: FontWeight? = null,
    maxLines: Int = Int.MAX_VALUE,
    overflow: TextOverflow = TextOverflow.Ellipsis,
) {
    val theme = LocalGenericTheme.current
    val fontSize = when (level) {
        1 -> theme.fontSizes.h1
        2 -> theme.fontSizes.h2
        3 -> theme.fontSizes.h3
        4 -> theme.fontSizes.h4
        5 -> theme.fontSizes.h5
        6 -> theme.fontSizes.h6
        else -> theme.fontSizes.h6
    }
    val weight = fontWeight ?: FontWeight.Bold

    Text(
        text = text,
        modifier = modifier,
        color = color ?: theme.textPrimary,
        fontSize = fontSize,
        fontWeight = weight,
        maxLines = maxLines,
        overflow = overflow,
    )
}

@Composable
fun H1(
    text: String,
    modifier: Modifier = Modifier,
    color: Color? = null,
    fontWeight: FontWeight? = null,
    maxLines: Int = Int.MAX_VALUE,
) = Heading(text = text, level = 1, modifier = modifier, color = color, fontWeight = fontWeight, maxLines = maxLines)

@Composable
fun H2(
    text: String,
    modifier: Modifier = Modifier,
    color: Color? = null,
    fontWeight: FontWeight? = null,
    maxLines: Int = Int.MAX_VALUE,
) = Heading(text = text, level = 2, modifier = modifier, color = color, fontWeight = fontWeight, maxLines = maxLines)

@Composable
fun H3(
    text: String,
    modifier: Modifier = Modifier,
    color: Color? = null,
    fontWeight: FontWeight? = null,
    maxLines: Int = Int.MAX_VALUE,
) = Heading(text = text, level = 3, modifier = modifier, color = color, fontWeight = fontWeight, maxLines = maxLines)

@Composable
fun H4(
    text: String,
    modifier: Modifier = Modifier,
    color: Color? = null,
    fontWeight: FontWeight? = null,
    maxLines: Int = Int.MAX_VALUE,
) = Heading(text = text, level = 4, modifier = modifier, color = color, fontWeight = fontWeight, maxLines = maxLines)

@Composable
fun H5(
    text: String,
    modifier: Modifier = Modifier,
    color: Color? = null,
    fontWeight: FontWeight? = null,
    maxLines: Int = Int.MAX_VALUE,
) = Heading(text = text, level = 5, modifier = modifier, color = color, fontWeight = fontWeight, maxLines = maxLines)

@Composable
fun H6(
    text: String,
    modifier: Modifier = Modifier,
    color: Color? = null,
    fontWeight: FontWeight? = null,
    maxLines: Int = Int.MAX_VALUE,
) = Heading(text = text, level = 6, modifier = modifier, color = color, fontWeight = fontWeight, maxLines = maxLines)

@Composable
fun BodyText(
    text: String,
    variant: TypographyVariant = TypographyVariant.BODY1,
    modifier: Modifier = Modifier,
    color: Color? = null,
    fontWeight: FontWeight? = null,
    maxLines: Int = Int.MAX_VALUE,
    overflow: TextOverflow = TextOverflow.Ellipsis,
) {
    val theme = LocalGenericTheme.current
    val fontSize = when (variant) {
        TypographyVariant.BODY1 -> theme.fontSizes.body1
        TypographyVariant.BODY2 -> theme.fontSizes.body2
        else -> theme.fontSizes.body1
    }

    Text(
        text = text,
        modifier = modifier,
        color = color ?: theme.textPrimary,
        fontSize = fontSize,
        fontWeight = fontWeight,
        maxLines = maxLines,
        overflow = overflow,
    )
}

@Composable
fun CaptionText(
    text: String,
    modifier: Modifier = Modifier,
    color: Color? = null,
    fontWeight: FontWeight? = null,
    maxLines: Int = Int.MAX_VALUE,
) {
    val theme = LocalGenericTheme.current

    Text(
        text = text,
        modifier = modifier,
        color = color ?: theme.textMuted,
        fontSize = theme.fontSizes.caption,
        fontWeight = fontWeight,
        maxLines = maxLines,
        overflow = TextOverflow.Ellipsis,
    )
}

@Composable
fun OverlineText(
    text: String,
    modifier: Modifier = Modifier,
    color: Color? = null,
    fontWeight: FontWeight? = null,
) {
    val theme = LocalGenericTheme.current

    Text(
        text = text.uppercase(),
        modifier = modifier,
        color = color ?: theme.textMuted,
        fontSize = theme.fontSizes.overline,
        fontWeight = fontWeight ?: FontWeight.Medium,
        letterSpacing = 1.sp,
    )
}

@Composable
fun CodeText(
    text: String,
    modifier: Modifier = Modifier,
    color: Color? = null,
    backgroundColor: Color? = null,
) {
    val theme = LocalGenericTheme.current

    Text(
        text = text,
        modifier = modifier
            .then(
                if (backgroundColor != null) {
                    Modifier.padding(horizontal = 4.dp, vertical = 2.dp)
                } else {
                    Modifier
                }
            ),
        color = color ?: theme.primary,
        fontSize = theme.fontSizes.body2,
        fontFamily = FontFamily.Monospace,
        fontWeight = FontWeight.Normal,
    )
}

@Composable
fun TruncatedText(
    text: String,
    maxLines: Int = 2,
    modifier: Modifier = Modifier,
    color: Color? = null,
    fontSize: TextUnit? = null,
    fontWeight: FontWeight? = null,
    expandText: String = "Show more",
    collapseText: String = "Show less",
    showExpandButton: Boolean = true,
) {
    val theme = LocalGenericTheme.current
    var isExpanded by remember { mutableStateOf(false) }
    var isTruncated by remember { mutableStateOf(false) }

    Column(modifier = modifier) {
        Text(
            text = text,
            color = color ?: theme.textPrimary,
            fontSize = fontSize ?: theme.fontSizes.body1,
            fontWeight = fontWeight,
            maxLines = if (isExpanded) Int.MAX_VALUE else maxLines,
            overflow = TextOverflow.Ellipsis,
            onTextLayout = { result ->
                isTruncated = result.hasVisualOverflow
            },
        )

        if (showExpandButton && isTruncated) {
            Text(
                text = if (isExpanded) collapseText else expandText,
                color = theme.primary,
                fontSize = theme.fontSizes.caption,
                fontWeight = FontWeight.Medium,
                modifier = Modifier
                    .clickable { isExpanded = !isExpanded }
                    .padding(top = 4.dp),
            )
        }
    }
}

@Composable
fun TextWithIcon(
    text: String,
    icon: @Composable () -> Unit,
    modifier: Modifier = Modifier,
    color: Color? = null,
    fontSize: TextUnit? = null,
    iconPosition: IconPosition = IconPosition.START,
    spacing: Dp = 4.dp,
) {
    val theme = LocalGenericTheme.current

    when (iconPosition) {
        IconPosition.START -> {
            Row(
                modifier = modifier,
                horizontalArrangement = Arrangement.spacedBy(spacing),
            ) {
                icon()
                Text(
                    text = text,
                    color = color ?: theme.textPrimary,
                    fontSize = fontSize ?: theme.fontSizes.body1,
                )
            }
        }
        IconPosition.END -> {
            Row(
                modifier = modifier,
                horizontalArrangement = Arrangement.spacedBy(spacing),
            ) {
                Text(
                    text = text,
                    color = color ?: theme.textPrimary,
                    fontSize = fontSize ?: theme.fontSizes.body1,
                )
                icon()
            }
        }
    }
}

enum class IconPosition {
    START, END
}

@Composable
fun LinkText(
    text: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    color: Color? = null,
    fontSize: TextUnit? = null,
    fontWeight: FontWeight? = null,
    textDecoration: TextDecoration = TextDecoration.Underline,
) {
    val theme = LocalGenericTheme.current

    Text(
        text = text,
        modifier = modifier.clickable { onClick() },
        color = color ?: theme.primary,
        fontSize = fontSize ?: theme.fontSizes.body1,
        fontWeight = fontWeight,
        textDecoration = textDecoration,
    )
}

@Composable
fun EllipsisText(
    text: String,
    modifier: Modifier = Modifier,
    color: Color? = null,
    fontSize: TextUnit? = null,
    fontWeight: FontWeight? = null,
    maxLines: Int = 1,
) {
    val theme = LocalGenericTheme.current

    Text(
        text = text,
        modifier = modifier,
        color = color ?: theme.textPrimary,
        fontSize = fontSize ?: theme.fontSizes.body1,
        fontWeight = fontWeight,
        maxLines = maxLines,
        overflow = TextOverflow.Ellipsis,
    )
}
