import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='PyTrack-lib',
    version='1.0.0',
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
    ]
)
