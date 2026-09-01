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
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.pixelrefine.genericui.theme.LocalGenericTheme
import androidx.compose.material3.Text
import androidx.compose.ui.graphics.Color

/**
 * Simple date model
 */
data class SimpleDate(
    val year: Int,
    val month: Int, // 1-12
    val day: Int, // 1-31
) {
    override fun toString(): String = "$year-${month.toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}"
}

private val MONTH_NAMES = listOf(
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
)

private val WEEKDAYS = listOf("Su", "Mo", "Tu", "We", "Th", "Fr", "Sa")

@Composable
fun DatePicker(
    selectedDate: SimpleDate?,
    onDateSelected: (SimpleDate) -> Unit,
    modifier: Modifier = Modifier,
    initialDate: SimpleDate = SimpleDate(2026, 1, 1),
    minDate: SimpleDate? = null,
    maxDate: SimpleDate? = null,
    variant: Variant = Variant.Primary,
) {
    val theme = LocalGenericTheme.current
    val variantColor = variantColor(theme, variant)

    var currentMonth by remember { mutableStateOf(initialDate.month) }
    var currentYear by remember { mutableStateOf(initialDate.year) }

    Column(
        modifier = modifier
            .clip(RoundedCornerShape(8.dp))
            .background(theme.bgCard)
            .border(1.dp, theme.borderColor, RoundedCornerShape(8.dp))
            .padding(12.dp),
    ) {
        // Header
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Text(
                text = "‹",
                fontSize = 20.sp,
                color = theme.textPrimary,
                modifier = Modifier
                    .clickable {
                        if (currentMonth == 1) {
                            currentMonth = 12
                            currentYear--
                        } else {
                            currentMonth--
                        }
                    }
                    .padding(8.dp),
            )

            Text(
                text = "${MONTH_NAMES[currentMonth - 1]} $currentYear",
                color = theme.textPrimary,
                fontSize = 16.sp,
                fontWeight = FontWeight.SemiBold,
            )

            Text(
                text = "›",
                fontSize = 20.sp,
                color = theme.textPrimary,
                modifier = Modifier
                    .clickable {
                        if (currentMonth == 12) {
                            currentMonth = 1
                            currentYear++
                        } else {
                            currentMonth++
                        }
                    }
                    .padding(8.dp),
            )
        }

        Spacer(modifier = Modifier.height(8.dp))

        // Weekday headers
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceAround,
        ) {
            WEEKDAYS.forEach { day ->
                Text(
                    text = day,
                    color = theme.textMuted,
                    fontSize = 12.sp,
                    fontWeight = FontWeight.Medium,
                )
            }
        }

        Spacer(modifier = Modifier.height(4.dp))

        // Calendar grid
        val daysInMonth = getDaysInMonth(currentYear, currentMonth)
        val firstDayOfWeek = getFirstDayOfWeek(currentYear, currentMonth)

        Column {
            var dayCounter = 1
            val totalCells = ((firstDayOfWeek + daysInMonth + 6) / 7) * 7

            for (week in 0 until totalCells / 7) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceAround,
                ) {
                    for (dayOfWeek in 0 until 7) {
                        val cellIndex = week * 7 + dayOfWeek
                        if (cellIndex < firstDayOfWeek || dayCounter > daysInMonth) {
                            Box(modifier = Modifier.size(36.dp))
                        } else {
                            val date = SimpleDate(currentYear, currentMonth, dayCounter)
                            val isSelected = selectedDate == date
                            val isDisabled = isDateDisabled(date, minDate, maxDate)

                            Box(
                                modifier = Modifier
                                    .size(36.dp)
                                    .clip(CircleShape)
                                    .background(
                                        when {
                                            isSelected -> variantColor
                                            else -> Color.Transparent
                                        }
                                    )
                                    .clickable(enabled = !isDisabled) {
                                        onDateSelected(date)
                                    },
                                contentAlignment = Alignment.Center,
                            ) {
                                Text(
                                    text = dayCounter.toString(),
                                    color = when {
                                        isSelected -> theme.light
                                        isDisabled -> theme.textMuted.copy(alpha = 0.5f)
                                        else -> theme.textPrimary
                                    },
                                    fontSize = 13.sp,
                                )
                            }
                            dayCounter++
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun DatePickerInput(
    value: SimpleDate?,
    onValueChange: (SimpleDate?) -> Unit,
    modifier: Modifier = Modifier,
    label: String? = null,
    placeholder: String = "Select date",
    enabled: Boolean = true,
    variant: Variant = Variant.Primary,
) {
    val theme = LocalGenericTheme.current
    var showPicker by remember { mutableStateOf(false) }

    Column(modifier = modifier) {
        if (label != null) {
            Text(
                text = label,
                color = theme.textSecondary,
                fontSize = 12.sp,
                modifier = Modifier.padding(bottom = 4.dp),
            )
        }

        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(36.dp)
                .clip(RoundedCornerShape(4.dp))
                .background(theme.bgSecondary)
                .border(1.dp, theme.borderColor, RoundedCornerShape(4.dp))
                .clickable(enabled = enabled) { showPicker = !showPicker }
                .padding(horizontal = 12.dp),
            contentAlignment = Alignment.CenterStart,
        ) {
            Text(
                text = value?.toString() ?: placeholder,
                color = if (value != null) theme.textPrimary else theme.textMuted,
                fontSize = 14.sp,
            )
        }

        if (showPicker) {
            Spacer(modifier = Modifier.height(8.dp))
            DatePicker(
                selectedDate = value,
                onDateSelected = {
                    onValueChange(it)
                    showPicker = false
                },
                variant = variant,
            )
        }
    }
}

private fun getDaysInMonth(year: Int, month: Int): Int {
    return when (month) {
        1, 3, 5, 7, 8, 10, 12 -> 31
        4, 6, 9, 11 -> 30
        2 -> if (isLeapYear(year)) 29 else 28
        else -> 30
    }
}

private fun isLeapYear(year: Int): Boolean {
    return (year % 4 == 0 && year % 100 != 0) || (year % 400 == 0)
}

private fun getFirstDayOfWeek(year: Int, month: Int): Int {
    // Zeller's congruence
    val m = if (month < 3) month + 12 else month
    val y = if (month < 3) year - 1 else year
    val h = (1 + (13 * (m + 1)) / 5 + y + y / 4 - y / 100 + y / 400) % 7
    return (h + 6) % 7 // Convert to Sunday=0
}

private fun isDateDisabled(date: SimpleDate, min: SimpleDate?, max: SimpleDate?): Boolean {
    if (min != null && date.toComparable() < min.toComparable()) return true
    if (max != null && date.toComparable() > max.toComparable()) return true
    return false
}

private fun SimpleDate.toComparable(): Int = year * 10000 + month * 100 + day
