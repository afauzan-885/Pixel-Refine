"""Algorithm identities, aliases and process availability shared by UI and runtime.

This module imports no algorithm or UI implementation while listing options.
Factories and desktop entrypoints are loaded only when explicitly requested.
"""

from dataclasses import dataclass
from importlib import import_module
from types import MappingProxyType


CATEGORIES = ("alignment", "denoising", "super_resolution", "hdr")
_BASE = "pixel_refine_desktop.enhance_stack.core.algorithm."
_PANELS = "pixel_refine_desktop.enhance_stack.components.batch_page_v2."
_PUBLIC = ("batch", "bulk_edit", "standalone")
_RESIDENT = (*_PUBLIC, "resident")


def _load_symbol(path):
    module, symbol = path.split(":", 1)
    return getattr(import_module(module), symbol)


@dataclass(frozen=True)
class ParameterBinding:
    module: str
    stem: str
    schema: str = "PARAMETER_SCHEMA"

    def load(self):
        module = import_module(self.module)
        return {
            "schema": getattr(module, self.schema),
            "load": getattr(module, f"load_{self.stem}_config"),
            "save": getattr(module, f"save_{self.stem}_config"),
            "save_batch": getattr(module, f"save_{self.stem}_config_for_active_batch"),
        }


@dataclass(frozen=True)
class AlgorithmSpec:
    category: str
    key: str
    name: str
    description: str
    aliases: tuple[str, ...] = ()
    runtime_name: str = ""
    contexts: tuple[str, ...] = _PUBLIC
    factory: str = ""
    entrypoint: str = ""
    entrypoint_kwargs: tuple[tuple[str, object], ...] = ()
    resident_route: str = ""
    parameter_keys: tuple[str, ...] = ()
    parameters: ParameterBinding | None = None
    owns_alignment: bool = False
    disabled: bool = False
    processes: tuple[str, ...] = ()

    @property
    def implementation_name(self):
        return self.runtime_name or self.name

    def available_in(self, context=None, process=None):
        return (context is None or context in self.contexts) and (
            process is None or not self.processes or process in self.processes
        )

    def create(self, *args, **kwargs):
        if not self.factory:
            raise ValueError(f"'{self.name}' has no algorithm factory")
        return _load_symbol(self.factory)(*args, **kwargs)


def _alignment(key, name, description, module, cls, *, aliases=(),
               runtime_name="", route="", contexts=_RESIDENT, parameter_stem="",
               parameter_keys=(), entrypoint=None, schema="PARAMETER_SCHEMA", processes=()):
    return AlgorithmSpec(
        "alignment", key, name, description, aliases, runtime_name, contexts,
        factory=_BASE + module + ":" + cls,
        entrypoint=(_BASE + "denoising.MFDenoiser:running_mf_denoiser") if entrypoint is None else entrypoint,
        entrypoint_kwargs=() if entrypoint is not None else (
            ("alignment_backend", name), ("merging_mode", "none"),
        ),
        resident_route=route, parameter_keys=parameter_keys, processes=processes,
        parameters=ParameterBinding(
            _PANELS + "parameter_alignment." + parameter_stem + "_parameter_settings",
            parameter_stem, schema,
        ) if parameter_stem else None,
    )


_SPECS = (
    AlgorithmSpec("alignment", "none", "No Alignment", "Skip alignment.",
                  aliases=("None", "off"), contexts=_RESIDENT, disabled=True,
                  resident_route="none",
                  factory=_BASE + "denoising.MFDenoiser:NoAlignmentAlgorithm"),
    _alignment("ofb", "OFB", "Oriented FAST and BRIEF feature alignment.",
               "alignment.feature_matching.OFB", "OFBAlgorithm", aliases=("ORB", "feature matching"),
               route="ofb", parameter_stem="ofb", parameter_keys=("ofb_params",)),
    _alignment("akaze", "AKAZE", "Non-linear diffusion feature alignment.",
               "alignment.feature_matching.AKAZE", "AKAZEAlgorithm", route="akaze",
               parameter_stem="akaze", parameter_keys=("akaze_params",),
               entrypoint=_BASE + "alignment.feature_matching.AKAZE:running_akaze"),
    _alignment("light_glue", "Light Glue", "LightGlue feature alignment adapter.",
               "alignment.feature_matching.Light_Glue", "LightGlueAlgorithm",
               aliases=("LightGlue", "SIFT"), contexts=("standalone",),
               parameter_stem="light_glue", parameter_keys=("light_glue_params",),
               entrypoint=_BASE + "alignment.feature_matching.Light_Glue:running_light_glue"),
    _alignment("farneback", "Farneback", "Native Farneback optical flow alignment.",
               "alignment.optical_flow.farneback_flow", "FarnebackFlow",
               runtime_name="Farneback Optical Flow", aliases=("Farneback Flow CPU",),
               route="farneback", parameter_stem="farneback", parameter_keys=("farneback_params",),
               entrypoint=_BASE + "alignment.optical_flow.farneback_flow:running_farneback_flow"),
    _alignment("lucas_kanade", "Lucas Kanade", "Native Lucas-Kanade optical flow alignment.",
               "alignment.optical_flow.lucas_kanade", "LucasKanade",
               runtime_name="Lucas Kanade Optical Flow",
               aliases=("Lucas Kanade GPU", "Lucas Kanade GPU Optical Flow", "Lucas Kanade CPU", "LK"),
               route="lucas_kanade", parameter_stem="lucas_kanade", parameter_keys=("lucas_kanade_params",)),
    _alignment("block_matching", "Block Matching GPU", "Native Block Matching optical flow alignment.",
               "alignment.optical_flow.block_matching", "BlockMatching",
               runtime_name="Block Matching Optical Flow",
               aliases=("Block Matching", "Block Matching GPU Optical Flow", "blockmatching", "block align", "bm"),
               route="block_matching", parameter_stem="block_matching",
               parameter_keys=("block_matching_gpu_params", "block_matching_params"), schema="GPU_PARAMETER_SCHEMA"),
    _alignment("block_flow", "Block Flow", "Adaptive hierarchical Block Flow alignment.",
               "alignment.optical_flow.block_flow", "BlockFlow",
               aliases=("Dense Optical Flow", "compute_flow", "FlowNet", "optical_flow", "optical flow"),
               route="block_flow", parameter_stem="block_flow", parameter_keys=("block_flow_params",)),
    _alignment("raft", "RAFT", "ONNX RAFT optical flow alignment.",
               "alignment.optical_flow.raft_flow", "RAFTFlow", runtime_name="RAFT Optical Flow",
               contexts=("array",), entrypoint="", parameter_stem="raft", parameter_keys=("raft_params",)),
    AlgorithmSpec("denoising", "none", "No Denoising", "Return the reference frame unchanged.",
                  aliases=("None",), disabled=True,
                  factory=_BASE + "denoising.MFDenoiser:NoDenoisingAlgorithm"),
    AlgorithmSpec("denoising", "average", "Average", "Average all aligned frames.",
                  aliases=("Average Denoising",), owns_alignment=True,
                  factory=_BASE + "denoising.Average:AverageDenoisingAlgorithm",
                  entrypoint=_BASE + "denoising.MFDenoiser:running_mf_denoiser",
                  entrypoint_kwargs=(("merging_mode", "average"), ("output_suffix", "average"))),
    AlgorithmSpec("denoising", "similarity", "Similarity", "Similarity-weighted spatial fusion.",
                  aliases=("Spatial Fusion", "SpatialFusion", "Similarity Denoising"), owns_alignment=True,
                  factory=_BASE + "denoising.SpatialFusion:SpatialFusionDenoisingAlgorithm",
                  entrypoint=_BASE + "denoising.MFDenoiser:running_mf_denoiser",
                  entrypoint_kwargs=(("merging_mode", "Similarity"), ("output_suffix", "similarity")),
                  parameter_keys=("similarity_params",),
                  parameters=ParameterBinding(_PANELS + "parameter_denoising.similarity_parameter_settings", "similarity")),
    AlgorithmSpec("denoising", "fusionnet", "FusionNet", "Resident burst fusion with 1-channel WeightNet inference.",
                  aliases=("Spatial AI", "Spatial AI Denoising", "FusionNet Denoising", "WeightNet", "Similarity Fusion"),
                  owns_alignment=True, factory=_BASE + "denoising.FusionNet:FusionNetDenoisingAlgorithm",
                  entrypoint=_BASE + "denoising.MFDenoiser:running_mf_denoiser",
                  entrypoint_kwargs=(("merging_mode", "FusionNet"), ("output_suffix", "fusionet")),
                  parameter_keys=("fusionnet_params",),
                  parameters=ParameterBinding(_PANELS + "parameter_denoising.fusionnet_parameter_settings", "fusionnet")),
    # The legacy wrapper is resolvable, but is not offered as a supported merge adapter.
    AlgorithmSpec("denoising", "median", "Median", "Legacy median wrapper.",
                  aliases=("Median Filter",), contexts=("legacy",),
                  entrypoint=_BASE + "denoising.Median:running_median"),
    AlgorithmSpec("super_resolution", "none", "No Super Resolution", "Skip super-resolution.",
                  aliases=("None",), disabled=True),
    AlgorithmSpec("super_resolution", "splatting_sr", "splattingSR",
                  "Confidence-guided subpixel splatting super-resolution", owns_alignment=True,
                  factory=_BASE + "super_resolution.SplatSR:SplatSRAlgorithm",
                  entrypoint=_BASE + "super_resolution.SplatSR:running_splatting_sr"),
    AlgorithmSpec("hdr", "none", "No HDR", "Skip HDR fusion.", aliases=("None",),
                  contexts=("standalone",), disabled=True),
    AlgorithmSpec("hdr", "weighted", "Weighted HDR",
                  "Gabungkan frame dengan bobot eksposur, estimasi SNR Taichi, dan penyelarasan MTB.",
                  aliases=("Weighted HDR (Foundation)",), owns_alignment=True,
                  factory=_BASE + "HDR.HDR:WeightedHDRAlgorithm",
                  entrypoint=_BASE + "HDR:running_hdr_fusion", entrypoint_kwargs=(("algorithm_name", "Weighted HDR"),)),
    AlgorithmSpec("hdr", "spde_mr", "SPDE-MR HDR Fusion",
                  "Patch-based HDR using 8x8 blocks, stride 4, and structure-aware single-frame priority.",
                  aliases=("SPDE-MR (Patch-Based)",), owns_alignment=True,
                  factory=_BASE + "HDR.spde_mr:SPDEMRAlgorithm",
                  entrypoint=_BASE + "HDR:running_hdr_fusion", entrypoint_kwargs=(("algorithm_name", "SPDE-MR HDR Fusion"),)),
)


def _token(value):
    return str(value or "").strip().casefold()


def _build_index():
    index = {}
    for spec in _SPECS:
        for name in (spec.key, spec.name, spec.implementation_name, *spec.aliases):
            key = spec.category, _token(name)
            if key in index and index[key] != spec:
                raise ValueError(f"Conflicting algorithm identity: {key}")
            index[key] = spec
    return MappingProxyType(index)


_INDEX = _build_index()


def get_spec(category, name, *, context=None, process=None):
    """Resolve a stable key, display name, implementation name, or old alias."""
    spec = _INDEX.get((category, _token(name)))
    if spec is None:
        raise ValueError(f"Unknown {category} algorithm '{name}'")
    if not spec.available_in(context, process):
        raise ValueError(f"{category} algorithm '{spec.name}' is unavailable for '{context}' / '{process}'")
    return spec


def normalize_name(category, name, *, default=None):
    """Normalize known aliases; preserve unknown saved values for explicit validation."""
    value = str(name or "").strip()
    if not value:
        return default if default is not None else value
    spec = _INDEX.get((category, _token(value)))
    return spec.name if spec else value


def get_specs(category, *, context=None, process=None, include_disabled=True):
    return tuple(spec for spec in _SPECS if spec.category == category
                 and spec.available_in(context, process) and (include_disabled or not spec.disabled))


def get_options(category, *, context="batch", process=None, include_disabled=True):
    return [(spec.name, spec.description) for spec in get_specs(
        category, context=context, process=process, include_disabled=include_disabled,
    )]


def get_names(category, *, context="batch", process=None, include_disabled=True):
    return [name for name, _ in get_options(
        category, context=context, process=process, include_disabled=include_disabled,
    )]


def create_registry(category):
    """Compatibility registry; aliases share the same instance within one registry."""
    registry = {}
    for spec in get_specs(category):
        if not spec.factory:
            continue
        algorithm = spec.create()
        for name in (spec.name, spec.implementation_name, *spec.aliases):
            registry[name] = algorithm
    return registry


def get_parameter_provider(category, name):
    spec = get_spec(category, name)
    return spec.parameters.load() if spec.parameters else None


def plan_stages(selections):
    """Order desktop stages and let internal pipelines own their alignment pass."""
    selected = {
        category: get_spec(category, selections.get(category) or "none")
        for category in CATEGORIES
    }
    if any(selected[category].owns_alignment for category in CATEGORIES[1:]):
        order = ("denoising", "super_resolution", "hdr") if selected["denoising"].owns_alignment else (
            "super_resolution", "hdr",
        )
    else:
        order = ("alignment", "super_resolution", "hdr", "denoising")
    return tuple(selected[category] for category in order if not selected[category].disabled)


def run_algorithm(category, name, parent=None, *, executor=None, **kwargs):
    """Dispatch one desktop stage using its catalogue entrypoint contract."""
    spec = get_spec(category, name)
    if spec.disabled:
        return None
    if not spec.entrypoint:
        raise ValueError(f"'{spec.name}' has no desktop entrypoint")
    kwargs.update(spec.entrypoint_kwargs)
    return (executor or _load_symbol(spec.entrypoint))(parent=parent, **kwargs)
