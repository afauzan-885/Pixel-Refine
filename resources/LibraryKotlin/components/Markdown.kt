package org.pixelrefine.genericui.components

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.theme.LocalGenericTheme
import androidx.compose.material3.Text

@Composable
fun Markdown(
    markdown: String,
    modifier: Modifier = Modifier,
) {
    val theme = LocalGenericTheme.current
    val lines = markdown.lines()

    Column(
        modifier = modifier.fillMaxWidth(),
    ) {
        var inCodeBlock = false
        var inList = false
        val currentList = mutableListOf<String>()

        lines.forEach { line ->
            when {
                line.startsWith("```") -> {
                    if (inCodeBlock) {
                        // End code block
                        CodeBlock(
                            code = currentList.joinToString("\n"),
                            showLineNumbers = false,
                            showCopyButton = false,
                        )
                        currentList.clear()
                        inCodeBlock = false
                    } else {
                        inCodeBlock = true
                    }
                }
                inCodeBlock -> {
                    currentList.add(line)
                }
                line.startsWith("# ") -> {
                    Heading(text = line.removePrefix("# "), level = 1)
                }
                line.startsWith("## ") -> {
                    Heading(text = line.removePrefix("## "), level = 2)
                }
                line.startsWith("### ") -> {
                    Heading(text = line.removePrefix("### "), level = 3)
                }
                line.startsWith("- ") || line.startsWith("* ") -> {
                    val item = line.removePrefix("- ").removePrefix("* ")
                    if (!inList) {
                        inList = true
                    }
                    currentList.add(item)
                }
                line.isBlank() -> {
                    if (inList) {
                        // Render list
                        currentList.forEach { item ->
                            Text(
                                text = "• $item",
                                color = theme.textPrimary,
                                fontSize = 14.sp,
                                modifier = Modifier.padding(start = 16.dp, top = 2.dp, bottom = 2.dp),
                            )
                        }
                        currentList.clear()
                        inList = false
                    }
                }
                else -> {
                    if (inList) {
                        currentList.forEach { item ->
                            Text(
                                text = "• $item",
                                color = theme.textPrimary,
                                fontSize = 14.sp,
                                modifier = Modifier.padding(start = 16.dp, top = 2.dp, bottom = 2.dp),
                            )
                        }
                        currentList.clear()
                        inList = false
                    }
                    Text(
                        text = parseInlineMarkdown(line),
                        color = theme.textPrimary,
                        fontSize = 14.sp,
                        modifier = Modifier.padding(vertical = 4.dp),
                    )
                }
            }
        }

        // Render remaining list items
        if (inList) {
            currentList.forEach { item ->
                Text(
                    text = "• $item",
                    color = theme.textPrimary,
                    fontSize = 14.sp,
                    modifier = Modifier.padding(start = 16.dp, top = 2.dp, bottom = 2.dp),
                )
            }
        }
    }
}

private fun parseInlineMarkdown(text: String): String {
    return text
        .replace(Regex("\\*\\*(.+?)\\*\\*"), "$1")
        .replace(Regex("\\*(.+?)\\*"), "$1")
        .replace(Regex("`(.+?)`"), "$1")
        .replace(Regex("__(.+?)__"), "$1")
        .replace(Regex("_(.+?)_"), "$1")
}
