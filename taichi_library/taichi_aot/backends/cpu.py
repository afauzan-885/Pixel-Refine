from . import BaseAOTBackend

class CpuAOTBackend(BaseAOTBackend):
    def __init__(self):
        super().__init__("taichi_aot_cpu.dll")
