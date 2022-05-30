import setuptools
import os

lib_folder = os.path.dirname(os.path.realpath(__file__))
requirement_path = lib_folder + '/requirements.txt'

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open(requirement_path) as f:
    INSTALL_REQUIRES = [line.strip() for line in f.readlines()]

setuptools.setup(
    name='PyTrack-lib',
    version='1.0.1',
    package_dir={"": "pytrack"},
    packages=setuptools.find_packages(where="pytrack"),
    url='https://github.com/cosbidev/PyTrack',
    license='BSD-3-Clause-Clear',
    author='Matteo Tortora',
    author_email='m.tortora@unicampus.it',
    description='a Map-Matching-based Python Toolbox for Vehicle Trajectory Reconstruction',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    install_reqs=INSTALL_REQUIRES
)
