#!/usr/bin/env python3

from setuptools import find_packages, setup

with open("README.md", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="project-management-dashboard",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A real-time system metrics dashboard with WebSocket support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/project-management-dashboard",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: System :: Monitoring",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "black",
            "flake8",
            "mypy",
            "isort",
            "pre-commit",
        ],
        "test": [
            "pytest",
            "pytest-asyncio",
            "pytest-cov",
            "pytest-env",
            "pytest-mock",
            "pytest-timeout",
            "pytest-xdist",
            "pytest-playwright",
        ],
    },
    entry_points={
        "console_scripts": [
            "dashboard=dashboard.app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "dashboard": [
            "templates/*.html",
            "static/css/*.css",
            "static/js/*.js",
        ],
    },
    zip_safe=False,
    project_urls={
        "Bug Reports": "https://github.com/yourusername/project-management-dashboard/issues",
        "Source": "https://github.com/yourusername/project-management-dashboard",
    },
)
