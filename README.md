<h1 align="center">
<img src="https://raw.githubusercontent.com/cosbidev/PyTrack/main/logo/pytracklogo.svg" width="300">
</h1><br>

-----------------

# PyTrack: a Map-Matching-based Python Toolbox for Vehicle Trajectory Reconstruction
[![PyPI Latest Release](https://img.shields.io/pypi/v/PyTrack-lib)](https://pypi.org/project/PyTrack-lib/)
[![License](https://img.shields.io/pypi/l/pandas.svg)](LICENSE)

## What is it?
**PyTrack** is a Python package that integrate the recorded GPS coordinates with data provided by the open-source OpenStreetMap (OSM). 
PyTrack can serve the intelligent transport research, e.g. to develop virtual simulation environments for the first training phase in self-driving vehicle applications, to reconstruct the video of a vehicle’s route by exploiting available data and without equipping it with camera sensors, to update the urban road network, and so on.

## Main Features
The following are the main features that PyTrack includes:
- Generation of the street network graph using geospatial data from OpenStreetMap
- Map-matching
- Data cleaning
- Video reconstruction of the GPS route
- Visualisation and analysis capabilities

## Getting Started
### Installation
The source code is currently hosted on GitHub at:
https://github.com/cosbidev/PyTrack.
PyTrack can be installed using:
```sh
# conda
conda install PyTrack
```

```sh
# or PyPI
pip install PyTrack-lib
```
## Documentation
Checkout the official [documentation]().

## Contributing to PyTrack
All contributions, bug reports, bug fixes, documentation improvements, enhancements, and ideas are welcome.

## Author
Created by [Matteo Tortora](https://mtortora-ai.github.io) - feel free to contact me!

<!---
## Citation

If you use PyTrack in your work, please cite the [journal paper]().
```bibtex

```
-->

## License
PyTrack is distributed under a [BSD-3-Clause-Clear Licence]().