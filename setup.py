from setuptools import setup, find_packages

with open("README.md") as f:
    long_description = f.read()

setup(
    name="sfmc-client",
    version="0.1.0",
    description="SFMC API client and object manager",
    author="Robert (Bobby) Curley",
    url="https://github.com/curleyr/sfmc-client-python",
    keywords=["sfmc", "salesforce", "marketingcloud", "email", "api", "client"],
    python_requires=">=3.10.5",
    license="MIT",
    install_requires=[
        "aiohappyeyeballs>=2.6.1,<3.0.0",
        "aiohttp>=3.12.13,<4.0.0",
        "aiosignal>=1.4.0,<2.0.0",
        "async-timeout>=5.0.1,<6.0.0",
        "attrs>=25.3.0,<26.0.0",
        "certifi>=2024.8.30,<2025.0.0",
        "charset-normalizer>=3.4.0,<4.0.0",
        "frozenlist>=1.7.0,<2.0.0",
        "idna>=3.10,<4.0.0",
        "multidict>=6.6.3,<7.0.0",
        "propcache>=0.3.2,<1.0.0",
        "python-dotenv>=1.0.1,<2.0.0",
        "requests>=2.32.3,<3.0.0",
        "typing_extensions>=4.14.1,<5.0.0",
        "urllib3>=2.2.3,<3.0.0",
        "yarl>=1.20.1,<2.0.0"
    ],
    packages=find_packages(include=["sfmc-client", "sfmc-client.*"], exclude=["tests", "tests.*"]),
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