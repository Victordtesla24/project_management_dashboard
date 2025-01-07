from setuptools import find_packages, setup

setup(
    name="project_management_dashboard",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "streamlit",
        "influxdb-client",
        "prometheus-client",
        "plotly",
        "pandas",
        "psutil",
        "pytest",
        "pytest-asyncio",
        "pytest-cov",
        "pytest-mock",
        "python-dotenv",
    ],
    python_requires=">=3.9",
)
