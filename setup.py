"""
Setup configuration for SuiPy SDK.
"""

from setuptools import setup, find_packages

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="sui-py",
    version="0.1.0",
    author="SuiPy Team",
    author_email="team@suipy.dev",
    description="A lightweight, high-performance Python SDK for the Sui blockchain",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/sui-py",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Office/Business :: Financial",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.0.0",
            "flake8>=6.0.0",
        ],
    },
    keywords="sui blockchain crypto web3 async sdk",
    project_urls={
        "Bug Reports": "https://github.com/your-org/sui-py/issues",
        "Source": "https://github.com/your-org/sui-py",
        "Documentation": "https://sui-py.readthedocs.io/",
    },
) 