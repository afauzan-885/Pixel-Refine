from . import BaseAOTBackend

class VulkanAOTBackend(BaseAOTBackend):
    def __init__(self):
        super().__init__("taichi_aot_vulkan.dll")
