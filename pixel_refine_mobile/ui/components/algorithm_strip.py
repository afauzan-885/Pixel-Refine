"""
pixel_refine_mobile/ui/components/algorithm_strip.py
----------------------------------------------------
Algorithm method selector strip.
Desktop equivalent: AlgorithmPanel (method selector).
Uses GenericUILibrary ButtonGroup.
"""

from resources.GenericUILibrary.containers import Container
from resources.GenericUILibrary.buttons import ButtonGroup


# Algorithm options per category
ALIGNMENT_OPTIONS = ["No Alignment", "ORB", "AKAZE", "Farneback Optical Flow", "Light Glue"]
DENOISING_OPTIONS = ["No Denoising", "Average", "Median", "Similarity"]
SR_OPTIONS = ["No Super Resolution", "WSR", "Interpolation"]


def build_algorithm_strip(bridge, tool_type: str = "MFDenoiser") -> Container:
    """
    Build the algorithm method strip.

    Args:
        bridge: AppBridge instance
        tool_type: Current tool type (determines default selections)

    Returns:
        Container with algorithm method buttons
    """
    from pixel_refine_mobile.core.config import TOOL_DEFAULTS

    section = Container(padding=8)
    defaults = TOOL_DEFAULTS.get(tool_type, {})

    # Alignment row
    align_group = ButtonGroup(orientation="horizontal")
    for opt in ALIGNMENT_OPTIONS:
        align_group.add_button(opt.replace("No Alignment", "None"),
                               variant="secondary", checkable=True)
    section.add_widget(align_group)

    # Denoising row
    denoise_group = ButtonGroup(orientation="horizontal")
    for opt in DENOISING_OPTIONS:
        denoise_group.add_button(opt.replace("No Denoising", "None"),
                                 variant="secondary", checkable=True)
    section.add_widget(denoise_group)

    # SR row
    sr_group = ButtonGroup(orientation="horizontal")
    for opt in SR_OPTIONS:
        sr_group.add_button(opt.replace("No Super Resolution", "None"),
                            variant="secondary", checkable=True)
    section.add_widget(sr_group)

    return section
