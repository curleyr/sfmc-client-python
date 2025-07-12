from setuptools import setup, find_packages

with open("README.md") as f:
    long_description = f.read()

setup(
    name="sfmc-client",
    version="0.1.0",
    description="A lightweight Python client for Salesforce Marketing Cloud (SFMC) with modular object managers for common API operations.",
    author="Bobby Curley",
    url="https://github.com/curleyr/sfmc-client-python",
    keywords=["sfmc", "salesforce", "marketingcloud", "email", "api", "client"],
    python_requires=">=3.10.5",
    license="MIT",
    install_requires=[
        "aiohttp>=3.12.13,<4.0.0",
        "pipdeptree>=2.27.0,<3.0.0",
        "pytest-cov>=6.2.1,<7.0.0",
        "python-dotenv>=1.0.1,<2.0.0",
        "requests>=2.32.3,<3.0.0",
        "setuptools>=58.1.0,<59.0.0"
    ],
    packages=find_packages(include=["sfmc_client", "sfmc_client.*"], exclude=["tests", "tests.*"]),
    include_package_data=True,
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python"
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
)