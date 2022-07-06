import setuptools
import os


def strip_comments(l):
    return l.split('#', 1)[0].strip()


def reqs(*f):
    return list(filter(None, [strip_comments(l) for l in open(
        os.path.join(os.getcwd(), *f)).readlines()]))


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='PyTrack-lib',
    version='2.0.0',
    packages=setuptools.find_packages(),
    # namespace_packages=['pytrack'],
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
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Information Analysis"
    ],
    install_requires=reqs('requirements.txt')
)
