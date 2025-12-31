#!/usr/bin/env python3
"""
Setup script for opencode-restore
"""

from setuptools import setup, find_packages
import os

def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "OpenCode Session Restore - Parse and summarize OpenCode session logs"

def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

VERSION = "1.0.0"

setup(
    name="opencode-restore",
    version=VERSION,
    author="OpenCode Team",
    author_email="team@opencode.ai",
    description="Parse and summarize OpenCode session logs for session restoration",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/opencode/opencode-restore",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    package_data={
        "": [
            "*.py",
            "*.md",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Version Control",
        "Topic :: System :: Logging",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "pytest-mock>=3.6",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.900",
        ],
        "test": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "pytest-mock>=3.6",
        ]
    },
    entry_points={
        "console_scripts": [
            "opencode-restore=opencode_restore.cli:main",
        ],
    },
    keywords=[
        "opencode", "session-restore", "log-parser", "ai", "cli",
        "terminal-logs", "llm", "summarization"
    ],
    project_urls={
        "Bug Reports": "https://github.com/opencode/opencode-restore/issues",
        "Source": "https://github.com/opencode/opencode-restore",
        "Documentation": "https://opencode-restore.readthedocs.io/",
    },
    zip_safe=False,
)
