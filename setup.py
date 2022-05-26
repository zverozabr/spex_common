#!/usr/bin/env python

import pathlib
import pkg_resources
import setuptools

with open("readme.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with pathlib.Path('requirements.txt').open() as requirements:
    install_requires = [
        str(requirement)
        for requirement
        in pkg_resources.parse_requirements(requirements)
    ]

print(install_requires)

setuptools.setup(
    name="spex_common",
    version="0.1",
    author="Artem Zubkov",
    author_email="zubkov.artem@gene.com",
    description="The packages contains common code of spex",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://code.roche.com/spex/common",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    python_requires=">=3.9",
    install_requires=install_requires
)
