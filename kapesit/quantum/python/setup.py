from setuptools import setup, find_packages

setup(
    name="kapesit-quantum",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.21.0",
        "scipy>=1.7.0",
        "qutip>=4.6.0",
    ],
    author="KAPESIT Team",
    author_email="info@kapesit.org",
    description="Quantum computing implementations for KAPESIT",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/kapesit/quantum",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    python_requires=">=3.8",
) 