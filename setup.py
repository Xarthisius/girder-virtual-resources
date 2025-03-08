from pathlib import Path

from setuptools import find_packages, setup

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="girder-virtual-resources",
    long_description=long_description,
    long_description_content_type="text/markdown",
    version="2.0.1",
    description="Girder Plugin exposing physical folders and files as Girder objects.",
    packages=find_packages(),
    include_package_data=True,
    license="Apache 2.0",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.10",
    setup_requires=["setuptools-git"],
    install_requires=["girder>=3"],
    entry_points={
        "girder.plugin": [
            "virtual_resources = girder_virtual_resources:VirtualResourcesPlugin"
        ]
    },
    zip_safe=False,
)
