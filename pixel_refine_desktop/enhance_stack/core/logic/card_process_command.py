"""Commands supplied by algorithm cards to the common batch Start control."""

from dataclasses import dataclass
from typing import Callable, Mapping


@dataclass(frozen=True)
class CardProcessCommand:
    category: str
    algorithm: str
    title: str
    enabled_key: str
    direct_start: bool = True

    def apply_to(self, settings):
        settings[self.category] = self.algorithm
        settings[self.enabled_key] = True


@dataclass(frozen=True)
class StartProcessCommand:
    settings: Mapping
    stages: tuple[CardProcessCommand, ...]

    @property
    def direct_start(self):
        return any(stage.direct_start for stage in self.stages)

    def execution_settings(self):
        settings = dict(self.settings)
        for stage in self.stages:
            stage.apply_to(settings)
        return settings

    def dispatch(self, start_process: Callable):
        """Pass a fresh settings snapshot to the existing batch executor."""
        return start_process(self.execution_settings())


def create_card_command(
    settings, *, category, stored_key, enabled_key, title, none_value,
    aliases=None, supported_algorithms=None, direct_start=True,
):
    """Resolve a card selection while respecting its explicit enabled state."""
    algorithm = str(settings.get(category) or settings.get(stored_key) or "").strip()
    if not algorithm or algorithm.lower() == "none" or algorithm == none_value:
        return None
    if not settings.get(enabled_key, True):
        return None
    algorithm = (aliases or {}).get(algorithm, algorithm)
    if supported_algorithms is not None and algorithm not in supported_algorithms:
        return None
    return CardProcessCommand(category, algorithm, title, enabled_key, direct_start)


def build_start_command(settings):
    """Collect commands from each card provider; the button has no algorithm map."""
    from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution.card_content_sr import (
        get_process_command as sr_command,
    )
    from pixel_refine_desktop.enhance_stack.core.algorithm.HDR.card_content import (
        get_process_command as hdr_command,
    )
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.card_content import (
        get_process_command as denoise_command,
    )

    stages = tuple(
        command for provider in (sr_command, hdr_command, denoise_command)
        if (command := provider(settings)) is not None
    )
    return StartProcessCommand(dict(settings), stages) if stages else None
