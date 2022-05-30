import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt") as f:
    INSTALL_REQUIRES = [line.strip() for line in f.readlines()]

setuptools.setup(
    name='PyTrack-lib',
    version='1.0.7',
    packages=setuptools.find_packages(),
    namespace_packages=['pytrack'],
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
    install_requires=INSTALL_REQUIRES
)
