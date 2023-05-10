#!/usr/bin/env python
from setuptools import find_packages, setup

with open("README.md") as f:
    long_description = f.read()


setup(
    name="pkgsettings",
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    description="Python package to ease the configuration of packages",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="KPN DE Platform",
    author_email="de-platform@kpn.com",
    url="https://github.com/kpn/py-pkgsettings",
    install_requires=[
        "typing-extensions>=4.5.0,<5.0.0",
    ],
    packages=find_packages(exclude=["tests*"]),
    tests_require=["tox"],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
