# setup.py
from setuptools import setup, find_packages

setup(
    name="halvita-core",
    version="0.1.0",
    description="HALVITA_2.0 — инженерия активационного поля",
    author="HALVITA",
    packages=find_packages(),
    install_requires=[
        "ollama",
        "sentence-transformers",
        "numpy",
        "scikit-learn",
    ],
    python_requires=">=3.10",
)
