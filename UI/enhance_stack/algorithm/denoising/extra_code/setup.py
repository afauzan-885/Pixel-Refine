# setup.py
import os
from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy

# Tentukan modul ekstensi
ext_modules = [
    Extension(
        "alignment_optim",  # Nama modul yang akan di-import
        ["alignment_optim.pyx"],
        # Tambahkan flag kompilator untuk performa dan paralelisasi (OpenMP)
        extra_compile_args=["/openmp" if os.name == 'nt' else "-fopenmp"],
        extra_link_args=["/openmp" if os.name == 'nt' else "-fopenmp"],
    )
]

setup(
    name='Alignment Optimizer',
    ext_modules=cythonize(ext_modules, compiler_directives={'language_level' : "3"}),
    # Sertakan header NumPy yang diperlukan untuk kompilasi
    include_dirs=[numpy.get_include()]
)