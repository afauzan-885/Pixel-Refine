"""Stable GPU preference helpers.

Vulkan adapter ordinals are assigned by the driver and may change after a
driver update.  Preferences therefore store a small, human-readable device
fingerprint and use the ordinal only as a cache for the next launch.
"""
from __future__ import annotations

import re
import ctypes
import subprocess
import time
from pathlib import Path

from taichi_vision.cuda_arch_matrix import architecture_name, normalize_compute_capability


def normalize_device_name(value: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9]+", " ", str(value or "").lower()).split())


def device_vendor(value: str) -> str:
    name = normalize_device_name(value)
    if any(token in name for token in ("nvidia", "geforce", "quadro", "rtx", "gtx")):
        return "nvidia"
    if any(token in name for token in ("intel", "arc", "iris", "uhd graphics")):
        return "intel"
    if any(token in name for token in ("amd", "radeon", "advanced micro devices")):
        return "amd"
    return "unknown"


def _parse_int(value):
    try:
        return int(str(value).strip(), 0)
    except (TypeError, ValueError):
        return None


def is_translation_device(device) -> bool:
    """Return whether a record is a Vulkan-on-D3D translation adapter."""
    if isinstance(device, dict):
        name = str(device.get("name") or device.get("device_name") or "")
        driver_id = str(device.get("driver_id") or "")
        driver_name = str(device.get("driver_name") or "")
    else:
        name = str(device or "")
        driver_id = ""
        driver_name = ""
    value = " ".join((name, driver_id, driver_name)).lower()
    return any(token in value for token in ("mesa_dozen", "dozen", "direct3d12"))


def parse_vulkaninfo_summary(output: str) -> list[dict]:
    """Parse ``vulkaninfo --summary`` into stable JSON-safe device records."""
    records = []
    current = None
    aliases = {
        "apiversion": "api_version",
        "driverversion": "driver_version",
        "vendorid": "vendor_id",
        "deviceid": "device_id",
        "devicetype": "device_type",
        "devicename": "name",
        "driverid": "driver_id",
        "drivername": "driver_name",
        "driverinfo": "driver_info",
        "conformanceversion": "conformance_version",
        "deviceuuid": "device_uuid",
        "driveruuid": "driver_uuid",
    }
    for raw_line in str(output or "").splitlines():
        line = raw_line.strip()
        match = re.fullmatch(r"GPU(\d+):", line, flags=re.IGNORECASE)
        if match:
            if current is not None:
                records.append(current)
            current = {"ordinal": int(match.group(1))}
            continue
        if current is None or "=" not in line:
            continue
        key, value = (part.strip() for part in line.split("=", 1))
        normalized = aliases.get(key.lower())
        if normalized:
            current[normalized] = value
    if current is not None:
        records.append(current)

    for record in records:
        record["vendor_id"] = _parse_int(record.get("vendor_id"))
        record["device_id"] = _parse_int(record.get("device_id"))
        record["vendor"] = device_vendor(record.get("name", ""))
        record["translation"] = is_translation_device(record)
        record["native"] = not record["translation"]
        record["fingerprint"] = device_fingerprint(record)
    return records


def device_fingerprint(device) -> str:
    """Return an ordinal-independent physical adapter identity."""
    if not isinstance(device, dict):
        return f"{device_vendor(device)}:{normalize_device_name(device)}"
    vendor_id = _parse_int(device.get("vendor_id"))
    device_id = _parse_int(device.get("device_id"))
    device_uuid = normalize_device_name(device.get("device_uuid", ""))
    driver_id = normalize_device_name(device.get("driver_id", ""))
    native_kind = "translation" if is_translation_device(device) else "native"
    if vendor_id is not None and device_id is not None:
        base = f"{vendor_id:04x}:{device_id:04x}"
    else:
        base = f"{device_vendor(device.get('name', ''))}:{normalize_device_name(device.get('name', ''))}"
    # Device UUID distinguishes identical adapters while remaining independent
    # from the Vulkan enumeration ordinal. Driver UUID is deliberately omitted
    # because it can change after a driver update.
    return ":".join(part for part in (base, device_uuid, driver_id, native_kind) if part)


def make_device_selector(name) -> dict:
    """Create a JSON-safe preference independent of a Vulkan ordinal."""
    if isinstance(name, dict):
        record = name
        selector = {
            "vendor": str(record.get("vendor") or device_vendor(record.get("name", ""))),
            "name": normalize_device_name(record.get("name", "")),
            "native": not is_translation_device(record),
            "fingerprint": device_fingerprint(record),
        }
        for key in ("vendor_id", "device_id", "device_uuid", "driver_id"):
            value = record.get(key)
            if value not in (None, ""):
                selector[key] = value
        return selector
    return {
        "vendor": device_vendor(name),
        "name": normalize_device_name(name),
        "native": not is_translation_device(name),
        "fingerprint": device_fingerprint(name),
    }


def parse_nvidia_smi_summary(output: str) -> list[dict]:
    """Parse the compact CUDA device query used by backend diagnostics.

    Both the historical five-column query (without ``compute_cap``) and the
    current six-column query are accepted so persisted hardware-test logs stay
    readable.  A missing compute capability is represented as ``None`` rather
    than inferred from a product name; GT/GTX branding is not an architecture.
    """

    records: list[dict] = []
    for raw_line in str(output or "").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        fields = [part.strip() for part in line.split(",")]
        if len(fields) < 5:
            continue
        try:
            ordinal = _parse_int(fields[0])
        except Exception:
            ordinal = None
        if ordinal is None:
            continue
        # New query: index,name,uuid,driver_version,compute_cap,memory.total
        has_cc = len(fields) >= 6
        cc_raw = fields[4] if has_cc else ""
        memory_raw = fields[5] if has_cc else fields[4]
        cc = None
        if cc_raw:
            try:
                cc = normalize_compute_capability(cc_raw)
            except ValueError:
                # Keep the device visible even when an older driver omits or
                # formats the capability unexpectedly.
                cc = None
        record = {
            "ordinal": ordinal,
            "name": fields[1],
            "device_name": fields[1],
            "device_uuid": fields[2],
            "driver_version": fields[3],
            "vendor": "nvidia",
            "backend": "cuda",
            "native": True,
            "translation": False,
            "fingerprint": f"nvidia:{fields[2]}" if fields[2] else f"nvidia:{normalize_device_name(fields[1])}",
            "compute_capability": cc,
        }
        if cc is not None:
            record["architecture"] = architecture_name(cc)
        try:
            record["memory_total_mb"] = int(float(memory_raw))
        except (TypeError, ValueError):
            record["memory_total_mb"] = None
        records.append(record)
    return records


def scan_vulkan_device_records(timeout=15.0) -> list[dict]:
    """Enumerate Vulkan adapters with stable identity and driver metadata."""
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    result = subprocess.run(
        ["vulkaninfo", "--summary"],
        capture_output=True,
        text=True,
        timeout=float(timeout),
        creationflags=flags,
        check=False,
    )
    # Loader warnings are normally on stderr while the device summary is on
    # stdout. Include both so unusual loader builds remain parseable.
    records = parse_vulkaninfo_summary(
        "\n".join(part for part in (result.stdout, result.stderr) if part)
    )
    if not records:
        raise RuntimeError(
            f"vulkaninfo did not report any devices (exit={result.returncode})"
        )
    return records


def scan_cuda_device_records() -> list[dict]:
    """Enumerate CUDA adapters using nvidia-smi with stable metadata."""
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=index,name,uuid,driver_version,compute_cap,memory.total",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=10.0,
            creationflags=flags,
            check=False,
        )
        return parse_nvidia_smi_summary(result.stdout or "")
    except Exception:
        return []


def query_vulkan_device_limits(device_id: int, timeout=30.0) -> dict:
    """Stream compute limits for one Vulkan device without buffering output.

    Full ``vulkaninfo`` output can be hundreds of megabytes on systems with
    several ICDs. Keeping it in memory caused the qualification process to be
    terminated on hybrid Intel/NVIDIA laptops, so only the selected physical
    device's relevant property lines are retained.
    """
    fields = {
        "maxStorageBufferRange",
        "maxPerStageDescriptorStorageBuffers",
        "maxDescriptorSetStorageBuffers",
        "maxComputeWorkGroupInvocations",
    }
    ordinal = int(device_id)
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    process = subprocess.Popen(
        ["vulkaninfo"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        bufsize=1,
        creationflags=flags,
    )
    current = -1
    result = {"device_ordinal": ordinal}
    workgroup_values = []
    collect_workgroup = False
    started = time.monotonic()
    try:
        assert process.stdout is not None
        for line in process.stdout:
            if time.monotonic() - started > float(timeout):
                raise TimeoutError(
                    f"vulkaninfo limit query exceeded {float(timeout):.1f}s"
                )
            stripped = line.strip()
            if stripped == "VkPhysicalDeviceProperties:":
                current += 1
                if current > ordinal:
                    break
                continue
            if current != ordinal:
                continue
            if collect_workgroup:
                if stripped.isdigit():
                    workgroup_values.append(int(stripped))
                    if len(workgroup_values) == 3:
                        result["maxComputeWorkGroupSize"] = workgroup_values
                        collect_workgroup = False
                    continue
                collect_workgroup = False
            if stripped.startswith("deviceName"):
                result["device_name"] = stripped.split("=", 1)[-1].strip()
            elif stripped.startswith("maxComputeWorkGroupSize:"):
                collect_workgroup = True
                workgroup_values = []
            elif "=" in stripped:
                field, value = (
                    part.strip() for part in stripped.split("=", 1)
                )
                if field in fields and value.isdigit():
                    result[field] = int(value)
    finally:
        if process.poll() is None:
            process.terminate()
        try:
            process.wait(timeout=3.0)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=3.0)
    missing = fields.difference(result)
    if missing or "device_name" not in result:
        raise RuntimeError(
            f"Incomplete Vulkan limits for ordinal {ordinal}: "
            + ", ".join(sorted(missing))
        )
    return result


def query_vulkan_memory_budget(device_id: int) -> dict:
    """Query native Vulkan heap budget/usage without creating a logical device.

    ``VK_EXT_memory_budget`` is preferred. Drivers that expose only core heap
    sizes still return a conservative fallback record with ``supported=False``.
    """
    VK_SUCCESS = 0
    VK_STRUCTURE_TYPE_APPLICATION_INFO = 0
    VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO = 1
    VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_MEMORY_PROPERTIES_2 = 1000059001
    VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_MEMORY_BUDGET_PROPERTIES_EXT = 1000237000
    VK_MEMORY_HEAP_DEVICE_LOCAL_BIT = 0x1

    class VkApplicationInfo(ctypes.Structure):
        _fields_ = [
            ("sType", ctypes.c_uint32),
            ("pNext", ctypes.c_void_p),
            ("pApplicationName", ctypes.c_char_p),
            ("applicationVersion", ctypes.c_uint32),
            ("pEngineName", ctypes.c_char_p),
            ("engineVersion", ctypes.c_uint32),
            ("apiVersion", ctypes.c_uint32),
        ]

    class VkInstanceCreateInfo(ctypes.Structure):
        _fields_ = [
            ("sType", ctypes.c_uint32),
            ("pNext", ctypes.c_void_p),
            ("flags", ctypes.c_uint32),
            ("pApplicationInfo", ctypes.POINTER(VkApplicationInfo)),
            ("enabledLayerCount", ctypes.c_uint32),
            ("ppEnabledLayerNames", ctypes.c_void_p),
            ("enabledExtensionCount", ctypes.c_uint32),
            ("ppEnabledExtensionNames", ctypes.c_void_p),
        ]

    class VkMemoryType(ctypes.Structure):
        _fields_ = [
            ("propertyFlags", ctypes.c_uint32),
            ("heapIndex", ctypes.c_uint32),
        ]

    class VkMemoryHeap(ctypes.Structure):
        _fields_ = [
            ("size", ctypes.c_uint64),
            ("flags", ctypes.c_uint32),
        ]

    class VkPhysicalDeviceMemoryProperties(ctypes.Structure):
        _fields_ = [
            ("memoryTypeCount", ctypes.c_uint32),
            ("memoryTypes", VkMemoryType * 32),
            ("memoryHeapCount", ctypes.c_uint32),
            ("memoryHeaps", VkMemoryHeap * 16),
        ]

    class VkPhysicalDeviceMemoryBudgetPropertiesEXT(ctypes.Structure):
        _fields_ = [
            ("sType", ctypes.c_uint32),
            ("pNext", ctypes.c_void_p),
            ("heapBudget", ctypes.c_uint64 * 16),
            ("heapUsage", ctypes.c_uint64 * 16),
        ]

    class VkPhysicalDeviceMemoryProperties2(ctypes.Structure):
        _fields_ = [
            ("sType", ctypes.c_uint32),
            ("pNext", ctypes.c_void_p),
            ("memoryProperties", VkPhysicalDeviceMemoryProperties),
        ]

    class VkExtensionProperties(ctypes.Structure):
        _fields_ = [
            ("extensionName", ctypes.c_char * 256),
            ("specVersion", ctypes.c_uint32),
        ]

    _feature_names = (
        "robustBufferAccess",
        "fullDrawIndexUint32",
        "imageCubeArray",
        "independentBlend",
        "geometryShader",
        "tessellationShader",
        "sampleRateShading",
        "dualSrcBlend",
        "logicOp",
        "multiDrawIndirect",
        "drawIndirectFirstInstance",
        "depthClamp",
        "depthBiasClamp",
        "fillModeNonSolid",
        "depthBounds",
        "wideLines",
        "largePoints",
        "alphaToOne",
        "multiViewport",
        "samplerAnisotropy",
        "textureCompressionETC2",
        "textureCompressionASTC_LDR",
        "textureCompressionBC",
        "occlusionQueryPrecise",
        "pipelineStatisticsQuery",
        "vertexPipelineStoresAndAtomics",
        "fragmentStoresAndAtomics",
        "shaderTessellationAndGeometryPointSize",
        "shaderImageGatherExtended",
        "shaderStorageImageExtendedFormats",
        "shaderStorageImageMultisample",
        "shaderStorageImageReadWithoutFormat",
        "shaderStorageImageWriteWithoutFormat",
        "shaderUniformBufferArrayDynamicIndexing",
        "shaderSampledImageArrayDynamicIndexing",
        "shaderStorageBufferArrayDynamicIndexing",
        "shaderStorageImageArrayDynamicIndexing",
        "shaderClipDistance",
        "shaderCullDistance",
        "shaderFloat64",
        "shaderInt64",
        "shaderInt16",
        "shaderResourceResidency",
        "shaderResourceMinLod",
        "sparseBinding",
        "sparseResidencyBuffer",
        "sparseResidencyImage2D",
        "sparseResidencyImage3D",
        "sparseResidency2Samples",
        "sparseResidency4Samples",
        "sparseResidency8Samples",
        "sparseResidency16Samples",
        "sparseResidencyAliased",
        "variableMultisampleRate",
        "inheritedQueries",
    )

    class VkPhysicalDeviceFeatures(ctypes.Structure):
        _fields_ = [(name, ctypes.c_uint32) for name in _feature_names]

    vk = ctypes.CDLL("vulkan-1.dll")
    vk.vkCreateInstance.argtypes = [
        ctypes.POINTER(VkInstanceCreateInfo),
        ctypes.c_void_p,
        ctypes.POINTER(ctypes.c_void_p),
    ]
    vk.vkCreateInstance.restype = ctypes.c_int32
    vk.vkDestroyInstance.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    vk.vkEnumeratePhysicalDevices.argtypes = [
        ctypes.c_void_p,
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.POINTER(ctypes.c_void_p),
    ]
    vk.vkEnumeratePhysicalDevices.restype = ctypes.c_int32
    vk.vkGetPhysicalDeviceMemoryProperties.argtypes = [
        ctypes.c_void_p,
        ctypes.POINTER(VkPhysicalDeviceMemoryProperties),
    ]
    vk.vkEnumerateDeviceExtensionProperties.argtypes = [
        ctypes.c_void_p,
        ctypes.c_char_p,
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.POINTER(VkExtensionProperties),
    ]
    vk.vkEnumerateDeviceExtensionProperties.restype = ctypes.c_int32
    vk.vkGetPhysicalDeviceFeatures.argtypes = [
        ctypes.c_void_p,
        ctypes.POINTER(VkPhysicalDeviceFeatures),
    ]

    app = VkApplicationInfo(
        VK_STRUCTURE_TYPE_APPLICATION_INFO,
        None,
        b"PixelRefineMemoryProbe",
        1,
        b"PixelRefine",
        1,
        (1 << 22) | (1 << 12),  # Vulkan 1.1
    )
    create = VkInstanceCreateInfo(
        VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO,
        None,
        0,
        ctypes.pointer(app),
        0,
        None,
        0,
        None,
    )
    instance = ctypes.c_void_p()
    result = vk.vkCreateInstance(ctypes.byref(create), None, ctypes.byref(instance))
    if result != VK_SUCCESS or not instance:
        raise RuntimeError(f"vkCreateInstance failed with VkResult {result}")
    try:
        count = ctypes.c_uint32()
        result = vk.vkEnumeratePhysicalDevices(instance, ctypes.byref(count), None)
        if result != VK_SUCCESS or not count.value:
            raise RuntimeError(
                f"vkEnumeratePhysicalDevices failed with VkResult {result}"
            )
        devices = (ctypes.c_void_p * count.value)()
        result = vk.vkEnumeratePhysicalDevices(
            instance, ctypes.byref(count), devices
        )
        ordinal = int(device_id)
        if result != VK_SUCCESS or not 0 <= ordinal < count.value:
            raise IndexError(
                f"Vulkan device ordinal {ordinal} is unavailable "
                f"(count={count.value}, VkResult={result})"
            )
        physical = devices[ordinal]
        feature_values = VkPhysicalDeviceFeatures()
        vk.vkGetPhysicalDeviceFeatures(physical, ctypes.byref(feature_values))

        extension_count = ctypes.c_uint32()
        vk.vkEnumerateDeviceExtensionProperties(
            physical, None, ctypes.byref(extension_count), None
        )
        extensions = (VkExtensionProperties * extension_count.value)()
        if extension_count.value:
            vk.vkEnumerateDeviceExtensionProperties(
                physical, None, ctypes.byref(extension_count), extensions
            )
        extension_names = {
            bytes(item.extensionName).split(b"\0", 1)[0].decode(
                "ascii", errors="replace"
            )
            for item in extensions
        }
        supported = "VK_EXT_memory_budget" in extension_names

        properties = VkPhysicalDeviceMemoryProperties()
        budgets = None
        get_properties2 = getattr(
            vk, "vkGetPhysicalDeviceMemoryProperties2", None
        )
        if supported and get_properties2 is not None:
            get_properties2.argtypes = [
                ctypes.c_void_p,
                ctypes.POINTER(VkPhysicalDeviceMemoryProperties2),
            ]
            budget = VkPhysicalDeviceMemoryBudgetPropertiesEXT()
            budget.sType = (
                VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_MEMORY_BUDGET_PROPERTIES_EXT
            )
            props2 = VkPhysicalDeviceMemoryProperties2()
            props2.sType = (
                VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_MEMORY_PROPERTIES_2
            )
            props2.pNext = ctypes.cast(
                ctypes.pointer(budget), ctypes.c_void_p
            )
            get_properties2(physical, ctypes.byref(props2))
            properties = props2.memoryProperties
            budgets = budget
        else:
            vk.vkGetPhysicalDeviceMemoryProperties(
                physical, ctypes.byref(properties)
            )

        heaps = []
        for index in range(int(properties.memoryHeapCount)):
            heap = properties.memoryHeaps[index]
            size = int(heap.size)
            reported_budget = int(budgets.heapBudget[index]) if budgets else size
            usage = int(budgets.heapUsage[index]) if budgets else 0
            heaps.append(
                {
                    "index": index,
                    "size": size,
                    "flags": int(heap.flags),
                    "device_local": bool(
                        heap.flags & VK_MEMORY_HEAP_DEVICE_LOCAL_BIT
                    ),
                    "budget": min(size, reported_budget) if reported_budget else size,
                    "usage": min(size, usage),
                    "available": max(
                        0,
                        (min(size, reported_budget) if reported_budget else size)
                        - usage,
                    ),
                }
            )
        local = [heap for heap in heaps if heap["device_local"]] or heaps
        return {
            "supported": bool(supported and budgets is not None),
            "device_ordinal": ordinal,
            "heaps": heaps,
            "device_local_size": sum(heap["size"] for heap in local),
            "device_local_budget": sum(heap["budget"] for heap in local),
            "device_local_usage": sum(heap["usage"] for heap in local),
            "device_local_available": sum(heap["available"] for heap in local),
            "features": {
                name: bool(getattr(feature_values, name))
                for name in _feature_names
            },
        }
    finally:
        vk.vkDestroyInstance(instance, None)


def scan_vulkan_device_names(project_root) -> list[str]:
    """Read bridge enumeration without importing ``taichi_aot``.

    Importing the package can create a runtime through legacy module imports,
    which is too late for startup-time device selection.
    """
    dll = (
        Path(project_root)
        / "taichi_vision"
        / "taichi_algorithm"
        / "aot_py"
        / "aot_dll"
        / "vulkan"
        / "taichi_aot_engine.dll"
    )
    if not dll.is_file():
        raise FileNotFoundError(f"AOT Vulkan bridge not found: {dll}")
    bridge = ctypes.CDLL(str(dll))
    scanner = bridge.scan_vulkan_devices
    scanner.argtypes = []
    scanner.restype = ctypes.c_char_p
    raw = scanner() or b""
    return [name.strip() for name in raw.decode("utf-8", errors="replace").split(";") if name.strip()]


def resolve_device_selector(selector, devices, cached_id=None):
    """Resolve a saved selector against the current Vulkan enumeration.

    Returns an ordinal or ``None``.  It never maps a saved NVIDIA/Intel/AMD
    preference onto a device from a different vendor.
    """
    selector = selector if isinstance(selector, dict) else {}
    wanted_name = normalize_device_name(selector.get("name", ""))
    wanted_vendor = str(selector.get("vendor", "unknown")).lower()
    candidates = []
    for idx, device in enumerate(devices):
        if isinstance(device, dict):
            ordinal = int(device.get("ordinal", idx))
            name = str(device.get("name") or device.get("device_name") or "")
            record = device
        else:
            ordinal = idx
            name = str(device)
            record = {"ordinal": ordinal, "name": name}
        if name.strip():
            candidates.append((ordinal, name, record))

    wanted_fingerprint = str(selector.get("fingerprint") or "")
    if wanted_fingerprint:
        for idx, _name, record in candidates:
            if device_fingerprint(record) == wanted_fingerprint:
                return idx

    wanted_vendor_id = _parse_int(selector.get("vendor_id"))
    wanted_device_id = _parse_int(selector.get("device_id"))
    wanted_native = selector.get("native")
    if wanted_vendor_id is not None and wanted_device_id is not None:
        hardware_matches = []
        for idx, _name, record in candidates:
            if (
                _parse_int(record.get("vendor_id")) == wanted_vendor_id
                and _parse_int(record.get("device_id")) == wanted_device_id
                and (
                    wanted_native is None
                    or bool(wanted_native) == (not is_translation_device(record))
                )
            ):
                hardware_matches.append((idx, record))
        if len(hardware_matches) == 1:
            return hardware_matches[0][0]

    if wanted_name:
        for idx, name, record in candidates:
            if (
                normalize_device_name(name) == wanted_name
                and (
                    wanted_native is None
                    or bool(wanted_native) == (not is_translation_device(record))
                )
            ):
                return idx

    if wanted_vendor and wanted_vendor != "unknown":
        vendor_matches = [
            (idx, name, record)
            for idx, name, record in candidates
            if device_vendor(name) == wanted_vendor
            and (
                wanted_native is None
                or bool(wanted_native) == (not is_translation_device(record))
            )
        ]
        if len(vendor_matches) == 1:
            return vendor_matches[0][0]
        # Keep a cached ordinal only when it still identifies the same vendor.
        try:
            cached_id = int(cached_id)
        except (TypeError, ValueError):
            cached_id = None
        for idx, _name, _record in vendor_matches:
            if idx == cached_id:
                return idx
    return None
