#!/usr/bin/env python3
"""
Setup script for Ironclad AI Guardrails
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Ironclad AI Guardrails - A comprehensive code generation and validation framework"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

# Define version
VERSION = "1.0.0"

setup(
    name="ironclad-ai-guardrails",
    version=VERSION,
    author="Ironclad AI Team",
    author_email="team@ironclad.ai",
    description="AI-powered code generation, validation, and UI generation framework",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/ironclad-ai/ironclad",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    package_data={
        "": [
            "*.py",
            "*.json",
            "*.txt",
            "*.md",
        ],
        "verified_bricks": [
            "*.py",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: User Interfaces",
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
    install_requires=[
        "requests>=2.25.0",
        "typing-extensions>=4.0.0",
        "dataclasses>=0.6; python_version<'3.7'",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.900",
            "isort>=5.0",
        ],
        "ui": [
            "rich>=13.0.0",
            "textual>=0.41.0",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
        "test": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "coverage>=5.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "ironclad=ironclad.cli:main",
            "ironclad-ui=ui_cli:main",
        ],
    },
    keywords=[
        "ai", "code-generation", "validation", "ui-generation", 
        "testing", "guardrails", "automation", "module-forge",
        "cli", "web-ui", "api-generation"
    ],
    project_urls={
        "Bug Reports": "https://github.com/ironclad-ai/ironclad/issues",
        "Source": "https://github.com/ironclad-ai/ironclad",
        "Documentation": "https://ironclad-ai.readthedocs.io/",
    },
    zip_safe=False,
)