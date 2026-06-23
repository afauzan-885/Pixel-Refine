from . import BaseAOTBackend

class CudaAOTBackend(BaseAOTBackend):
    def __init__(self):
        super().__init__("taichi_aot_cuda.dll")
