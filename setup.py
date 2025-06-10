"""
Setup configuration for SuiPy SDK.
"""

from setuptools import setup, find_packages
from setuptools.command.install import install
import os
import sys

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements with fallback
requirements = []
requirements_file = "requirements.txt"
if os.path.exists(requirements_file):
    with open(requirements_file, "r", encoding="utf-8") as fh:
        requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
else:
    # Fallback requirements if file not found during build
    requirements = [
        "httpx>=0.25.0",
        "typing-extensions>=4.0.0",
        "pynacl>=1.5.0",
        "ecdsa>=0.18.0"
    ]


class PostInstallCommand(install):
    """Custom install command to display ASCII art after installation."""
    
    def run(self):
        install.run(self)
        try:
            from sui_py._ascii_art import display_install_message
            display_install_message()
        except ImportError:
            # Fallback if import fails
            print("\n🎉 SuiPy installed successfully!")
            print("✨ by OpenDive")


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
    cmdclass={
        'install': PostInstallCommand,
    },
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