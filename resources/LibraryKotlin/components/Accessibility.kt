package org.pixelrefine.genericui.components

import androidx.compose.foundation.focusable
import androidx.compose.foundation.layout.Box
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.role
import androidx.compose.ui.semantics.semantics

enum class SemanticRole {
    Button, Checkbox, RadioButton, Switch, Tab
}

@Composable
fun AccessibleBox(
    modifier: Modifier = Modifier,
    contentDescription: String? = null,
    role: SemanticRole? = null,
    focusable: Boolean = true,
    focusRequester: FocusRequester? = null,
    content: @Composable () -> Unit,
) {
    val semanticRole = role?.let {
        when (it) {
            SemanticRole.Button -> Role.Button
            SemanticRole.Checkbox -> Role.Checkbox
            SemanticRole.RadioButton -> Role.RadioButton
            SemanticRole.Switch -> Role.Switch
            SemanticRole.Tab -> Role.Tab
        }
    }

    Box(
        modifier = modifier
            .then(
                if (contentDescription != null || role != null) {
                    Modifier.semantics {
                        if (contentDescription != null) {
                            this.contentDescription = contentDescription
                        }
                        if (semanticRole != null) {
                            this.role = semanticRole
                        }
                    }
                } else {
                    Modifier
                }
            )
            .then(
                if (focusRequester != null) {
                    Modifier.focusRequester(focusRequester)
                } else {
                    Modifier
                }
            )
            .then(
                if (focusable) {
                    Modifier.focusable()
                } else {
                    Modifier
                }
            ),
    ) {
        content()
    }
}

@Composable
fun Modifier.accessibilityLabel(label: String): Modifier {
    return this.semantics {
        contentDescription = label
    }
}

@Composable
fun Modifier.accessibilityRole(role: SemanticRole): Modifier {
    val semanticRole = when (role) {
        SemanticRole.Button -> Role.Button
        SemanticRole.Checkbox -> Role.Checkbox
        SemanticRole.RadioButton -> Role.RadioButton
        SemanticRole.Switch -> Role.Switch
        SemanticRole.Tab -> Role.Tab
    }

    return this.semantics {
        this.role = semanticRole
    }
}

@Composable
fun Modifier.combineAccessibility(
    label: String? = null,
    role: SemanticRole? = null,
): Modifier {
    val semanticRole = role?.let {
        when (it) {
            SemanticRole.Button -> Role.Button
            SemanticRole.Checkbox -> Role.Checkbox
            SemanticRole.RadioButton -> Role.RadioButton
            SemanticRole.Switch -> Role.Switch
            SemanticRole.Tab -> Role.Tab
        }
    }

    return this.semantics {
        if (label != null) {
            contentDescription = label
        }
        if (semanticRole != null) {
            this.role = semanticRole
        }
    }
}
