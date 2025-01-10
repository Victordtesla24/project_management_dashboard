from setuptools import setup, find_packages

setup(
    name="project_management_dashboard",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "Flask>=3.0.0",
        "Flask-Login>=0.6.3",
        "Flask-SQLAlchemy>=3.1.1",
        "SQLAlchemy>=2.0.23",
        "psutil>=5.9.7",
        "pytest>=8.2.0",
        "pytest-playwright>=0.6.2",
        "radon>=6.0.1",
        "bandit>=1.8.0",
        "autoflake>=2.3.1"
    ],
    python_requires=">=3.11",
)
