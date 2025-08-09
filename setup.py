from setuptools import setup, find_packages

setup(
    name="syllabreak",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "PyYAML>=6.0",
    ],
    python_requires=">=3.8",
    author="Apakabar FM",
    description="A library for syllable breaking and language detection",
    package_data={
        "syllabreak": ["data/*.yaml"],
    },
)