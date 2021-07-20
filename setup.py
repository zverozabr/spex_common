#!/usr/bin/env python

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

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
    install_requires=[
        "pymemcache==3.4.1",
        "python-dotenv==0.15.0",
        "python-arango==7.1.0",
        "requests==2.25.1",
        "redis==3.5.3",
        "ujson==4.0.2"
    ]
)
