# Copyright 2016 128 Technology, Inc.

from setuptools import find_packages, setup


# Read in the __version__ attribute without importing the package
with open("yinsolidated/_version.py") as version_file:
    exec(version_file.read())

setup(
    name="yinsolidated",
    version=__version__,
    description=(
        "Generates and parses a YIN-like representation of a YANG model, "
        "consolidated into a single XML document"
    ),
    url="https://github.com/128technology/yinsolidated",
    author="Alex Thompson",
    author_email="alex@128technology.com",
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="yang yin pyang",
    packages=find_packages(),
    install_requires=["lxml >= 3.7.3", "xpathparser >= 1.0.0"],
    python_requires=">=2.7",
    entry_points={
        "pyang.plugin": ["yinsolidate = yinsolidated.plugin.plugin:pyang_plugin_init"]
    },
)
