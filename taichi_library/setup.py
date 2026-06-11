from setuptools import setup, find_packages

setup(
    name="taichi_library",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "taichi",
        "numpy",
    ],
    description="Shared Taichi iGPU algorithm library for Pixel Refine",
    python_requires=">=3.8",
)
