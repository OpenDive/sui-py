"""
Setup configuration for SuiPy SDK.
"""

from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.develop import develop
from setuptools.command.egg_info import egg_info
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
        "ecdsa>=0.18.0",
        "base58>=2.1.0"
    ]


def display_ascii_art():
    """Display ASCII art during installation."""
    print("\n" + "="*80)
    ascii_art = """
    
    ███████╗         •• ██████╗         
    ██╔════╝██╗   ██╗██║██╔══██╗██╗   ██╗
    ███████╗██║   ██║██║██████╔╝╚██╗ ██╔╝
    ╚════██║██║   ██║██║██╔═══╝  ╚████╔╝ 
    ███████║╚██████╔╝██║██║       ╚██╔╝  
    ╚══════╝ ╚═════╝ ╚═╝╚═╝        ██║  
                                   ╚═╝   
    
    a deliciously lightweight, high-performance Python SDK for the Sui blockchain
    
    by OpenDive (@OpenDiveHQ)
    
    """
    print(ascii_art)
    print("="*80 + "\n")


class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)
        display_ascii_art()


class PostDevelopCommand(develop):
    """Post-installation for development mode."""
    def run(self):
        develop.run(self)
        display_ascii_art()


class PostEggInfoCommand(egg_info):
    """Post-installation for egg_info mode."""
    def run(self):
        egg_info.run(self)
        # Only show during pip install, not just egg_info generation
        if '--single-version-externally-managed' in sys.argv or 'install' in sys.argv:
            display_ascii_art()


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
        'develop': PostDevelopCommand,
        'egg_info': PostEggInfoCommand,
    },
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.0.0",
            "flake8>=6.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
        ],
    },
    keywords="sui blockchain crypto web3 async sdk",
    project_urls={
        "Bug Reports": "https://github.com/your-org/sui-py/issues",
        "Source": "https://github.com/your-org/sui-py",
        "Documentation": "https://sui-py.readthedocs.io/",
    },
) 