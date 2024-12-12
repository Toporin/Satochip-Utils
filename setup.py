#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Satochip-Utils : setup data

from setuptools import setup, find_packages
from version import VERSION

with open("README.md", encoding="utf8") as readme_file:
    readme = readme_file.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name="Satochip-Utils",
    version=VERSION,
    description="Simple GUI tool to configure your Satochip/Satodime/Seedkeeper card.",
    long_description=readme + "\n\n",
    long_description_content_type="text/markdown",
    keywords="Satochip Satodime Seedkeeper bitcoin smartcard security",
    author="Satochip",
    author_email="info@satochip.io",
    url="https://github.com/Toporin/Satochip-Utils",
    license="GPLv3",
    python_requires=">=3.8.0",
    install_requires=requirements,
    include_package_data=False,
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Topic :: Office/Business :: Financial",
        "Topic :: Security :: Cryptography",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    packages=find_packages(),
    zip_safe=False,
)