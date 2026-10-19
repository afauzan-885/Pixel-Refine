from setuptools import setup, find_packages

setup(
    name="taichi_vision",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "taichi>=1.7.4",
        "numpy>=2.0.0",
    ],
    extras_require={
        "jpeg-cpu": ["Pillow>=10"],
        "jpeg-nvidia": ["nvidia-nvimgcodec-cu12[nvjpeg]>=0.9.0", "Pillow>=10"],
    },
    description="Shared Taichi iGPU algorithm library for Pixel Refine",
    python_requires=">=3.12.9",
)
