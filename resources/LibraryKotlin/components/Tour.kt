package org.pixelrefine.genericui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.theme.LocalGenericTheme
import androidx.compose.material3.Text

data class TourStep(
    val title: String,
    val description: String,
    val targetId: String? = null,
)

@Composable
fun Tour(
    steps: List<TourStep>,
    currentStep: Int = 0,
    onStepChange: ((Int) -> Unit)? = null,
    onComplete: (() -> Unit)? = null,
    onSkip: (() -> Unit)? = null,
    modifier: Modifier = Modifier,
    showOverlay: Boolean = true,
    overlayColor: Color = Color.Black.copy(alpha = 0.7f),
) {
    val theme = LocalGenericTheme.current

    Box(modifier = modifier.fillMaxSize()) {
        // Scrim overlay
        if (showOverlay) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(overlayColor),
            )
        }

        // Tour popover
        if (currentStep in steps.indices) {
            val step = steps[currentStep]
            Box(
                modifier = Modifier
                    .align(Alignment.BottomCenter)
                    .padding(16.dp)
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(12.dp))
                    .background(theme.bgCard)
                    .border(1.dp, theme.borderColor, RoundedCornerShape(12.dp))
                    .padding(16.dp),
            ) {
                Column {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        Text(
                            text = "Step ${currentStep + 1} of ${steps.size}",
                            color = theme.textMuted,
                            fontSize = 11.sp,
                        )
                        if (onSkip != null) {
                            Text(
                                text = "Skip",
                                color = theme.textMuted,
                                fontSize = 12.sp,
                                modifier = Modifier.clickable { onSkip() },
                            )
                        }
                    }

                    Spacer(modifier = Modifier.height(8.dp))

                    Text(
                        text = step.title,
                        color = theme.textPrimary,
                        fontSize = 16.sp,
                        fontWeight = FontWeight.SemiBold,
                    )

                    Spacer(modifier = Modifier.height(4.dp))

                    Text(
                        text = step.description,
                        color = theme.textSecondary,
                        fontSize = 13.sp,
                    )

                    Spacer(modifier = Modifier.height(16.dp))

                    // Step indicators
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.Center,
                    ) {
                        steps.forEachIndexed { index, _ ->
                            Box(
                                modifier = Modifier
                                    .size(8.dp)
                                    .clip(CircleShape)
                                    .background(
                                        if (index == currentStep) theme.primary
                                        else theme.borderColor
                                    )
                                    .padding(horizontal = 2.dp),
                            )
                        }
                    }

                    Spacer(modifier = Modifier.height(12.dp))

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp, Alignment.End),
                    ) {
                        if (currentStep > 0) {
                            Button(
                                text = "Previous",
                                variant = Variant.Ghost,
                                onClick = { onStepChange?.invoke(currentStep - 1) },
                            )
                        }
                        Button(
                            text = if (currentStep == steps.lastIndex) "Finish" else "Next",
                            variant = Variant.Primary,
                            onClick = {
                                if (currentStep == steps.lastIndex) {
                                    onComplete?.invoke()
                                } else {
                                    onStepChange?.invoke(currentStep + 1)
                                }
                            },
                        )
                    }
                }
            }
        }
    }
}

@Composable
fun TourHost(
    steps: List<TourStep>,
    modifier: Modifier = Modifier,
    visible: Boolean = true,
    onComplete: (() -> Unit)? = null,
) {
    var currentStep by remember { mutableStateOf(0) }

    if (visible) {
        Tour(
            steps = steps,
            currentStep = currentStep,
            onStepChange = { currentStep = it },
            onComplete = {
                currentStep = 0
                onComplete?.invoke()
            },
            onSkip = {
                currentStep = 0
                onComplete?.invoke()
            },
            modifier = modifier,
        )
    }
}
