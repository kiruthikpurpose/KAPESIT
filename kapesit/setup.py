from setuptools import setup, find_packages
import os
import sys
from setuptools.command.build_ext import build_ext
import subprocess

class CMakeBuildExt(build_ext):
    def run(self):
        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        cmake_args = [
            f'-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir}',
            f'-DPYTHON_EXECUTABLE={sys.executable}'
        ]

        build_temp = os.path.join(self.build_temp, ext.name)
        if not os.path.exists(build_temp):
            os.makedirs(build_temp)

        subprocess.check_call(['cmake', ext.sourcedir] + cmake_args, cwd=build_temp)
        subprocess.check_call(['cmake', '--build', '.', '--config', 'Release'], cwd=build_temp)

setup(
    name="kapesit",
    version="1.0.0",
    description="Advanced Quantum Computing and AI Framework",
    author="KAPESIT Team",
    author_email="contact@kapesit.org",
    url="https://github.com/kapesit/kapesit",
    packages=find_packages(),
    install_requires=[
        'numpy>=1.21.0',
        'scipy>=1.7.0',
        'qiskit>=0.34.0',
        'torch>=1.9.0',
        'tensorflow>=2.6.0',
        'pandas>=1.3.0',
        'matplotlib>=3.4.0',
    ],
    extras_require={
        'dev': [
            'pytest>=6.2.0',
            'pytest-cov>=2.12.0',
            'black>=21.5b2',
            'flake8>=3.9.0',
            'mypy>=0.910',
            'sphinx>=4.0.0',
            'sphinx-rtd-theme>=0.5.0',
        ],
    },
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
    cmdclass={'build_ext': CMakeBuildExt},
    ext_modules=[],
) 