package org.pixelrefine.mobile.ui

import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.components.Variant
import org.pixelrefine.genericui.progress_bar
import org.pixelrefine.genericui.theme.LocalGenericTheme

/**
 * Welcome / Splash Screen (Sesuai Sketsa Welcome Page):
 * - Logo lingkaran PR dengan siluet gunung
 * - Teks "PIXEL REFINE" & "Computational Photography Tools"
 * - Animated Progress Bar 5 Detik lalu otomatis ke Home Page
 */
@Composable
fun WelcomeScreen(
    onTimeout: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val theme = LocalGenericTheme.current
    val progressAnim = remember { Animatable(0f) }

    LaunchedEffect(Unit) {
        // Animasi loading berjalan selama 5000 ms (5 detik)
        progressAnim.animateTo(
            targetValue = 100f,
            animationSpec = tween(durationMillis = 5000, easing = LinearEasing),
        )
        onTimeout()
    }

    Box(
        modifier = modifier
            .fillMaxSize()
            .background(theme.bgPrimary),
        contentAlignment = Alignment.Center,
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center,
            modifier = Modifier.padding(24.dp),
        ) {
            // 1. Logo Lingkaran PR dengan Gunung (Vector Canvas Sesuai Sketsa)
            Box(
                modifier = Modifier.size(190.dp),
                contentAlignment = Alignment.Center,
            ) {
                Canvas(modifier = Modifier.fillMaxSize()) {
                    val w = size.width
                    val h = size.height
                    val center = Offset(w / 2, h / 2)
                    val radius = w * 0.46f

                    // Lingkaran Luar
                    drawCircle(
                        color = Color(0xFF2ECC71),
                        radius = radius,
                        center = center,
                        style = Stroke(width = 4.5f),
                    )

                    // Siluet Gunung di dalam Lingkaran
                    val mountainPath = Path().apply {
                        moveTo(w * 0.15f, h * 0.72f)
                        lineTo(w * 0.42f, h * 0.48f)
                        lineTo(w * 0.60f, h * 0.65f)
                        lineTo(w * 0.78f, h * 0.46f)
                        lineTo(w * 0.88f, h * 0.68f)
                    }
                    drawPath(
                        path = mountainPath,
                        color = Color(0xFF27AE60),
                        style = Stroke(width = 3.5f),
                    )
                }

                // Inisial "PR" Mewah di Tengah Logo Sesuai Sketsa
                Text(
                    text = "PR",
                    color = Color(0xFF1E293B),
                    fontSize = 54.sp,
                    fontWeight = FontWeight.Black,
                    letterSpacing = 2.sp,
                    modifier = Modifier.padding(bottom = 20.dp),
                )
            }

            Spacer(Modifier.height(28.dp))

            // 2. Brand Name
            Text(
                text = "PIXEL REFINE",
                color = theme.textPrimary,
                fontSize = 24.sp,
                fontWeight = FontWeight.ExtraBold,
                letterSpacing = 3.sp,
            )

            Spacer(Modifier.height(6.dp))

            // 3. Subtitle Sesuai Sketsa
            Text(
                text = "Computational Photography Tools",
                color = theme.textSecondary,
                fontSize = 13.sp,
                fontWeight = FontWeight.Medium,
            )

            Spacer(Modifier.height(48.dp))

            // 4. Animated Loading Bar (Gaya Pythonic 1-baris)
            Box(
                modifier = Modifier
                    .fillMaxWidth(0.7f)
                    .height(20.dp),
            ) {
                progress_bar(
                    value = progressAnim.value.toInt(),
                    max_value = 100,
                    variant = Variant.Primary,
                    show_label = false,
                    height = 8.dp,
                )
            }

            Spacer(Modifier.height(8.dp))

            Text(
                text = "loading...",
                color = theme.textMuted,
                fontSize = 12.sp,
                fontWeight = FontWeight.SemiBold,
            )
        }
    }
}
