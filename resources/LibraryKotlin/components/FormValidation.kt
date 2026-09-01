package org.pixelrefine.genericui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.theme.LocalGenericTheme
import androidx.compose.material3.Text

enum class ValidationRule {
    Required,
    Email,
    MinLength,
    MaxLength,
    Pattern,
    Numeric,
    Custom,
}

data class ValidationError(
    val rule: ValidationRule,
    val message: String,
)

data class FieldState(
    val value: String = "",
    val errors: List<ValidationError> = emptyList(),
    val isTouched: Boolean = false,
    val isDirty: Boolean = false,
)

data class ValidationConfig(
    val rules: List<ValidationRule> = emptyList(),
    val minLength: Int = 0,
    val maxLength: Int = Int.MAX_VALUE,
    val pattern: String? = null,
    val customValidator: ((String) -> ValidationError?)? = null,
    val requiredMessage: String = "This field is required",
    val emailMessage: String = "Please enter a valid email",
    val minLengthMessage: String = "Minimum length not met",
    val maxLengthMessage: String = "Maximum length exceeded",
    val patternMessage: String = "Invalid format",
    val numericMessage: String = "Must be a number",
)

@Composable
fun rememberFormField(
    initialValue: String = "",
    config: ValidationConfig = ValidationConfig(),
): FieldState {
    var state by remember { mutableStateOf(FieldState(value = initialValue)) }

    fun validate(value: String): List<ValidationError> {
        val errors = mutableListOf<ValidationError>()

        if (ValidationRule.Required in config.rules && value.isBlank()) {
            errors.add(ValidationError(ValidationRule.Required, config.requiredMessage))
        }

        if (ValidationRule.Email in config.rules) {
            val emailPattern = Regex("^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$")
            if (value.isNotBlank() && !emailPattern.matches(value)) {
                errors.add(ValidationError(ValidationRule.Email, config.emailMessage))
            }
        }

        if (ValidationRule.MinLength in config.rules && value.length < config.minLength) {
            errors.add(ValidationError(ValidationRule.MinLength, config.minLengthMessage))
        }

        if (ValidationRule.MaxLength in config.rules && value.length > config.maxLength) {
            errors.add(ValidationError(ValidationRule.MaxLength, config.maxLengthMessage))
        }

        if (ValidationRule.Pattern in config.rules && config.pattern != null) {
            val regex = Regex(config.pattern)
            if (value.isNotBlank() && !regex.matches(value)) {
                errors.add(ValidationError(ValidationRule.Pattern, config.patternMessage))
            }
        }

        if (ValidationRule.Numeric in config.rules) {
            if (value.isNotBlank() && value.toDoubleOrNull() == null) {
                errors.add(ValidationError(ValidationRule.Numeric, config.numericMessage))
            }
        }

        config.customValidator?.invoke(value)?.let { errors.add(it) }

        return errors
    }

    fun update(newValue: String) {
        val errors = validate(newValue)
        state = state.copy(
            value = newValue,
            errors = errors,
            isTouched = true,
            isDirty = newValue != initialValue,
        )
    }

    return state
}

@Composable
fun ValidatedInput(
    value: String,
    onValueChange: (String) -> Unit,
    config: ValidationConfig,
    modifier: Modifier = Modifier,
    label: String? = null,
    placeholder: String = "",
    showErrors: Boolean = true,
) {
    val theme = LocalGenericTheme.current
    var isTouched by remember { mutableStateOf(false) }
    val errors = remember(value, config) {
        if (isTouched) validateValue(value, config) else emptyList()
    }

    Column(modifier = modifier) {
        if (label != null) {
            Text(
                text = label,
                color = theme.textSecondary,
                fontSize = 12.sp,
                modifier = Modifier.padding(bottom = 4.dp),
            )
        }

        androidx.compose.foundation.text.BasicTextField(
            value = value,
            onValueChange = {
                onValueChange(it)
                isTouched = true
            },
            textStyle = androidx.compose.ui.text.TextStyle(
                color = theme.textPrimary,
                fontSize = 14.sp,
            ),
            modifier = Modifier
                .fillMaxWidth()
                .height(36.dp)
                .clip(RoundedCornerShape(4.dp))
                .background(theme.bgSecondary)
                .border(
                    1.dp,
                    if (errors.isNotEmpty()) theme.danger else theme.borderColor,
                    RoundedCornerShape(4.dp),
                )
                .padding(horizontal = 12.dp, vertical = 8.dp),
        )

        if (showErrors && errors.isNotEmpty()) {
            errors.forEach { error ->
                Text(
                    text = error.message,
                    color = theme.danger,
                    fontSize = 11.sp,
                    modifier = Modifier.padding(top = 4.dp),
                )
            }
        }
    }
}

private fun validateValue(value: String, config: ValidationConfig): List<ValidationError> {
    val errors = mutableListOf<ValidationError>()

    if (ValidationRule.Required in config.rules && value.isBlank()) {
        errors.add(ValidationError(ValidationRule.Required, config.requiredMessage))
    }

    if (ValidationRule.Email in config.rules && value.isNotBlank()) {
        val emailPattern = Regex("^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$")
        if (!emailPattern.matches(value)) {
            errors.add(ValidationError(ValidationRule.Email, config.emailMessage))
        }
    }

    if (ValidationRule.MinLength in config.rules && value.length < config.minLength) {
        errors.add(ValidationError(ValidationRule.MinLength, config.minLengthMessage))
    }

    if (ValidationRule.MaxLength in config.rules && value.length > config.maxLength) {
        errors.add(ValidationError(ValidationRule.MaxLength, config.maxLengthMessage))
    }

    if (ValidationRule.Pattern in config.rules && config.pattern != null && value.isNotBlank()) {
        val regex = Regex(config.pattern)
        if (!regex.matches(value)) {
            errors.add(ValidationError(ValidationRule.Pattern, config.patternMessage))
        }
    }

    if (ValidationRule.Numeric in config.rules && value.isNotBlank() && value.toDoubleOrNull() == null) {
        errors.add(ValidationError(ValidationRule.Numeric, config.numericMessage))
    }

    config.customValidator?.invoke(value)?.let { errors.add(it) }

    return errors
}

@Composable
fun FormFieldLabel(
    label: String,
    required: Boolean = false,
    modifier: Modifier = Modifier,
) {
    val theme = LocalGenericTheme.current
    Row(
        modifier = modifier,
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(
            text = label,
            color = theme.textSecondary,
            fontSize = 12.sp,
        )
        if (required) {
            Text(
                text = " *",
                color = theme.danger,
                fontSize = 12.sp,
            )
        }
    }
}
