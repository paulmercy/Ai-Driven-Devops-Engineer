# setup.py
from setuptools import setup, Extension
import pybind11

# Define the C++ extension module
ext_modules = [
    Extension(
        'text_analyzer',  # The name of the module in Python (import text_analyzer)
        ['analyzer.cpp'], # List of source files
        include_dirs=[
            pybind11.get_include(),
        ],
        language='c++',
        extra_compile_args=['-std=c++11'], # Use C++11 standard
    ),
]

setup(
    name='text_analyzer',
    version='1.0',
    author='Paul Ikeadim',
    description='A basic C++ text analyzer exposed with Pybind11',
    ext_modules=ext_modules,
)