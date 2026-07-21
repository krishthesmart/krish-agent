#!/usr/bin/env python3
"""
Setup script for krish-agent package.
Install with: pip install -e .
"""

from setuptools import setup, find_packages

# Read README
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except:
    long_description = "KRISH-AGENT INFINITY - The ultimate AI coding assistant (1 billion percent better)"

setup(
    name="krish-agent",
    version="3.0.0",
    description="KRISH-AGENT INFINITY: The ultimate AI coding assistant. 1 billion% better with GODMODE, HYPERINFINITY, and QUANTUM UNIVERSE capabilities.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Arul Meiyappan Kannappan",
    author_email="arulmeiyappankannappan@gmail.com",
    url="https://github.com/yourusername/krish-agent",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
        "rich>=12.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.950",
        ],
    },
    entry_points={
        "console_scripts": [
            "krish-agent=krish_agent.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
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
        "Topic :: Software Development :: Testing",
    ],
    keywords="ai coding agent godmode hyperinfinity quantum universe",
    project_urls={
        "Documentation": "https://github.com/yourusername/krish-agent",
        "Source": "https://github.com/yourusername/krish-agent",
        "Tracker": "https://github.com/yourusername/krish-agent/issues",
    },
    include_package_data=True,
    zip_safe=False,
)
