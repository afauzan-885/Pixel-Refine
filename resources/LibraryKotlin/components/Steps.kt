package org.pixelrefine.genericui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.theme.LocalGenericTheme
import androidx.compose.material3.Text

enum class StepStatus {
    Wait, Process, Finish, Error
}

data class StepItem(
    val title: String,
    val description: String? = null,
    val status: StepStatus = StepStatus.Wait,
    val icon: String? = null,
)

enum class StepsDirection {
    Horizontal, Vertical
}

@Composable
fun Steps(
    steps: List<StepItem>,
    modifier: Modifier = Modifier,
    direction: StepsDirection = StepsDirection.Horizontal,
    currentStep: Int = 0,
    onStepClick: ((Int) -> Unit)? = null,
    variant: Variant = Variant.Primary,
) {
    val theme = LocalGenericTheme.current
    val variantColor = variantColor(theme, variant)

    if (direction == StepsDirection.Horizontal) {
        Row(
            modifier = modifier.fillMaxWidth(),
            verticalAlignment = Alignment.Top,
        ) {
            steps.forEachIndexed { index, step ->
                StepItemView(
                    step = step,
                    index = index,
                    totalSteps = steps.size,
                    isLast = index == steps.lastIndex,
                    direction = direction,
                    onClick = onStepClick?.let { { it(index) } },
                    variant = variant,
                    modifier = Modifier.weight(1f),
                )
            }
        }
    } else {
        Column(
            modifier = modifier,
            verticalArrangement = Arrangement.spacedBy(0.dp),
        ) {
            steps.forEachIndexed { index, step ->
                StepItemView(
                    step = step,
                    index = index,
                    totalSteps = steps.size,
                    isLast = index == steps.lastIndex,
                    direction = direction,
                    onClick = onStepClick?.let { { it(index) } },
                    variant = variant,
                )
            }
        }
    }
}

@Composable
private fun StepItemView(
    step: StepItem,
    index: Int,
    totalSteps: Int,
    isLast: Boolean,
    direction: StepsDirection,
    onClick: (() -> Unit)?,
    variant: Variant,
    modifier: Modifier = Modifier,
) {
    val theme = LocalGenericTheme.current
    val variantColor = variantColor(theme, variant)

    val stepColor = when (step.status) {
        StepStatus.Finish -> variantColor
        StepStatus.Process -> variantColor
        StepStatus.Error -> theme.danger
        StepStatus.Wait -> theme.borderColor
    }

    if (direction == StepsDirection.Horizontal) {
        Column(
            modifier = modifier,
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Box(
                    modifier = Modifier
                        .size(28.dp)
                        .clip(CircleShape)
                        .background(stepColor)
                        .then(
                            if (onClick != null) {
                                Modifier.clickable { onClick() }
                            } else {
                                Modifier
                            }
                        ),
                    contentAlignment = Alignment.Center,
                ) {
                    if (step.icon != null) {
                        Text(
                            text = step.icon,
                            color = theme.light,
                            fontSize = 12.sp,
                        )
                    } else if (step.status == StepStatus.Finish) {
                        Text(
                            text = "✓",
                            color = theme.light,
                            fontSize = 14.sp,
                            fontWeight = FontWeight.Bold,
                        )
                    } else {
                        Text(
                            text = (index + 1).toString(),
                            color = if (step.status == StepStatus.Wait) theme.textPrimary else theme.light,
                            fontSize = 12.sp,
                            fontWeight = FontWeight.Bold,
                        )
                    }
                }

                if (!isLast) {
                    Box(
                        modifier = Modifier
                            .weight(1f)
                            .height(2.dp)
                            .background(
                                if (step.status == StepStatus.Finish) variantColor else theme.borderColor
                            ),
                    )
                }
            }

            Spacer(modifier = Modifier.height(8.dp))

            Text(
                text = step.title,
                color = if (step.status == StepStatus.Wait) theme.textMuted else theme.textPrimary,
                fontSize = 12.sp,
                fontWeight = if (step.status == StepStatus.Process) FontWeight.SemiBold else FontWeight.Normal,
            )

            if (step.description != null) {
                Text(
                    text = step.description,
                    color = theme.textMuted,
                    fontSize = 10.sp,
                )
            }
        }
    } else {
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.Top,
        ) {
            Column(
                horizontalAlignment = Alignment.CenterHorizontally,
            ) {
                Box(
                    modifier = Modifier
                        .size(28.dp)
                        .clip(CircleShape)
                        .background(stepColor)
                        .then(
                            if (onClick != null) {
                                Modifier.clickable { onClick() }
                            } else {
                                Modifier
                            }
                        ),
                    contentAlignment = Alignment.Center,
                ) {
                    if (step.icon != null) {
                        Text(
                            text = step.icon,
                            color = theme.light,
                            fontSize = 12.sp,
                        )
                    } else if (step.status == StepStatus.Finish) {
                        Text(
                            text = "✓",
                            color = theme.light,
                            fontSize = 14.sp,
                            fontWeight = FontWeight.Bold,
                        )
                    } else {
                        Text(
                            text = (index + 1).toString(),
                            color = if (step.status == StepStatus.Wait) theme.textPrimary else theme.light,
                            fontSize = 12.sp,
                            fontWeight = FontWeight.Bold,
                        )
                    }
                }

                if (!isLast) {
                    Box(
                        modifier = Modifier
                            .width(2.dp)
                            .height(40.dp)
                            .background(
                                if (step.status == StepStatus.Finish) variantColor else theme.borderColor
                            ),
                    )
                }
            }

            Spacer(modifier = Modifier.width(12.dp))

            Column(
                modifier = Modifier.padding(top = 2.dp, bottom = if (isLast) 0.dp else 20.dp),
            ) {
                Text(
                    text = step.title,
                    color = if (step.status == StepStatus.Wait) theme.textMuted else theme.textPrimary,
                    fontSize = 14.sp,
                    fontWeight = if (step.status == StepStatus.Process) FontWeight.SemiBold else FontWeight.Normal,
                )

                if (step.description != null) {
                    Text(
                        text = step.description,
                        color = theme.textMuted,
                        fontSize = 12.sp,
                    )
                }
            }
        }
    }
}
