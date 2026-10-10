"""Estimate queue time from completed processing and export, not stage percentages."""

import math
import time


class BatchEtaEstimator:
    def __init__(self, total, clock=time.monotonic):
        self.total = total
        self.completed = 0
        self.clock = clock
        self.average = None
        self.started_at = None
        self.reused = False

    def begin(self, reused=False):
        self.started_at = self.clock()
        self.reused = reused

    def finish(self, success):
        if success and self.started_at is not None and not self.reused:
            duration = max(0.001, self.clock() - self.started_at)
            self.average = duration if self.average is None else (
                0.75 * self.average + 0.25 * duration
            )
        self.completed += 1
        self.started_at = None

    def remaining(self):
        pending = max(0, self.total - self.completed)
        if not pending:
            return 0
        if self.average is None:
            return None
        if self.started_at is None:
            return math.ceil(self.average * pending)
        elapsed = max(0, self.clock() - self.started_at)
        current = 0 if self.reused else max(1, self.average - elapsed)
        return math.ceil(self.average * (pending - 1) + current)
