package org.pixelrefine.genericui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.AnnotatedString
import androidx.compose.ui.text.SpanStyle
import androidx.compose.ui.text.buildAnnotatedString
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.theme.LocalGenericTheme
import androidx.compose.material3.Text

@Composable
fun CodeBlock(
    code: String,
    modifier: Modifier = Modifier,
    language: String = "kotlin",
    showLineNumbers: Boolean = true,
    showCopyButton: Boolean = true,
    title: String? = null,
    maxLines: Int? = null,
) {
    val theme = LocalGenericTheme.current
    val lines = code.lines()
    val displayedLines = if (maxLines != null) lines.take(maxLines) else lines

    Column(
        modifier = modifier
            .clip(RoundedCornerShape(8.dp))
            .background(theme.dark)
            .border(1.dp, theme.borderColor, RoundedCornerShape(8.dp)),
    ) {
        if (title != null || showCopyButton) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(theme.bgDark)
                    .padding(horizontal = 12.dp, vertical = 8.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically,
            ) {
                if (title != null) {
                    Text(
                        text = title,
                        color = theme.light.copy(alpha = 0.8f),
                        fontSize = 12.sp,
                    )
                }

                if (showCopyButton) {
                    CopyButton(
                        textToCopy = code,
                        label = "Copy",
                        copiedLabel = "Copied!",
                    )
                }
            }
        }

        Row(
            modifier = Modifier
                .fillMaxWidth()
                .heightIn(max = (displayedLines.size * 18 + 16).dp)
                .verticalScroll(rememberScrollState())
                .padding(12.dp),
        ) {
            if (showLineNumbers) {
                Column(
                    horizontalAlignment = Alignment.End,
                    modifier = Modifier.padding(end = 12.dp),
                ) {
                    displayedLines.forEachIndexed { index, _ ->
                        Text(
                            text = (index + 1).toString(),
                            color = theme.light.copy(alpha = 0.4f),
                            fontSize = 12.sp,
                            fontFamily = FontFamily.Monospace,
                        )
                    }
                }
            }

            Column(modifier = Modifier.weight(1f)) {
                displayedLines.forEach { line ->
                    Text(
                        text = highlightCode(line, language),
                        color = theme.light,
                        fontSize = 12.sp,
                        fontFamily = FontFamily.Monospace,
                    )
                }
            }
        }
    }
}

private fun highlightCode(line: String, language: String): AnnotatedString {
    if (line.isBlank()) return AnnotatedString(line)

    return buildAnnotatedString {
        when (language.lowercase()) {
            "kotlin", "kt", "java", "javascript", "js", "typescript", "ts" -> {
                val keywords = setOf(
                    "fun", "val", "var", "if", "else", "when", "for", "while",
                    "class", "object", "interface", "package", "import", "return",
                    "private", "public", "protected", "internal", "override",
                    "data", "sealed", "enum", "companion", "this", "super",
                    "true", "false", "null", "is", "as", "in", "out", "by",
                )
                val tokens = tokenize(line)
                tokens.forEach { token ->
                    when {
                        token.startsWith("//") -> {
                            pushStyle(SpanStyle(color = Color(0xFF888888)))
                            append(token)
                        }
                        token.startsWith("\"") -> {
                            pushStyle(SpanStyle(color = Color(0xFF6ABF69)))
                            append(token)
                        }
                        token in keywords -> {
                            pushStyle(SpanStyle(color = Color(0xFFCC7832), fontWeight = FontWeight.Bold))
                            append(token)
                        }
                        token.toIntOrNull() != null -> {
                            pushStyle(SpanStyle(color = Color(0xFF6897BB)))
                            append(token)
                        }
                        else -> {
                            pushStyle(SpanStyle(color = Color(0xFFA9B7C6)))
                            append(token)
                        }
                    }
                    pop()
                }
            }
            else -> {
                pushStyle(SpanStyle(color = Color(0xFFA9B7C6)))
                append(line)
            }
        }
    }
}

private fun tokenize(line: String): List<String> {
    val tokens = mutableListOf<String>()
    val current = StringBuilder()
    var inString = false
    var inComment = false

    if (line.trimStart().startsWith("//")) {
        return listOf(line)
    }

    for (i in line.indices) {
        val c = line[i]
        when {
            inComment -> {
                current.append(c)
            }
            inString -> {
                current.append(c)
                if (c == '"' && (i == 0 || line[i - 1] != '\\')) {
                    tokens.add(current.toString())
                    current.clear()
                    inString = false
                }
            }
            c == '/' && i + 1 < line.length && line[i + 1] == '/' -> {
                inComment = true
                if (current.isNotEmpty()) {
                    tokens.add(current.toString())
                    current.clear()
                }
                current.append(c)
            }
            c == '"' -> {
                if (current.isNotEmpty()) {
                    tokens.add(current.toString())
                    current.clear()
                }
                inString = true
                current.append(c)
            }
            c.isWhitespace() || c in "(){}[];," -> {
                if (current.isNotEmpty()) {
                    tokens.add(current.toString())
                    current.clear()
                }
                if (!c.isWhitespace()) {
                    tokens.add(c.toString())
                } else {
                    current.append(c)
                    if (current.isNotEmpty()) {
                        tokens.add(current.toString())
                        current.clear()
                    }
                }
            }
            else -> {
                current.append(c)
            }
        }
    }

    if (current.isNotEmpty()) {
        tokens.add(current.toString())
    }

    return tokens
}
