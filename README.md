<h1 align="center">
<img src="https://raw.githubusercontent.com/cosbidev/PyTrack/main/logo/pytracklogo.svg" width="300">
</h1><br>

-----------------

# PyTrack: a Map-Matching-based Python Toolbox for Vehicle Trajectory Reconstruction
[![All platforms](https://dev.azure.com/conda-forge/feedstock-builds/_apis/build/status/pytrack-feedstock?branchName=main)](https://dev.azure.com/conda-forge/feedstock-builds/_build/latest?definitionId=16366&branchName=main)
[![PyPI Latest Release](https://img.shields.io/pypi/v/PyTrack-lib)](https://pypi.org/project/PyTrack-lib/)
[![Conda Version](https://img.shields.io/conda/vn/conda-forge/pytrack.svg)](https://anaconda.org/conda-forge/pytrack)
[![License](https://img.shields.io/pypi/l/pandas.svg)](LICENSE)
[![docs](https://img.shields.io/readthedocs/pytrack-lib)](https://pytrack-lib.readthedocs.io/en/latest)
[![PyPI downloads](https://img.shields.io/pypi/dm/pytrack-lib?label=PyPI%20downloads)](https://pypi.org/project/PyTrack-lib/)
[![Anaconda downloads](https://img.shields.io/conda/dn/conda-forge/pytrack?label=conda%20downloads)](https://anaconda.org/conda-forge/pytrack)

## What is it?
**PyTrack** is a Python package that integrate the recorded GPS coordinates with data provided by the open-source OpenStreetMap (OSM). 
PyTrack can serve the intelligent transport research, e.g. to reconstruct the video of a vehicle’s route by exploiting available data and without equipping it with camera sensors, to update the urban road network, and so on.

If you use PyTrack in your work, please cite the journal article.

**Citation info**: M. Tortora, E. Cordelli and P. Soda, "[PyTrack: a Map-Matching-based Python Toolbox for Vehicle Trajectory Reconstruction](https://ieeexplore.ieee.org/document/9927417)," in IEEE Access, vol. 10, pp. 112713-112720, 2022, doi: 10.1109/ACCESS.2022.3216565.

```latex
@ARTICLE{mtpytrack,  
      author={Tortora, Matteo and Cordelli, Ermanno and Soda, Paolo},
      journal={IEEE Access}, 
      title={PyTrack: A Map-Matching-Based Python Toolbox for Vehicle Trajectory Reconstruction}, 
      year={2022},
      volume={10},
      number={},
      pages={112713-112720},
      doi={10.1109/ACCESS.2022.3216565}}
```

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
PyTrack can be installed using*:
```sh
# conda
conda install pytrack 
```

```sh
# or PyPI
pip install PyTrack-lib
```
**for Mac m1 users, it is recommended to use conda in order to be able to install all dependencies.*
## Documentation
Checkout the official [documentation](https://pytrack-lib.readthedocs.io/en/latest).
Besides, [here](https://github.com/cosbidev/PyTrack/tree/main/examples) you can see some examples of the application of the library.

## Examples
### Map-Matching
To see the map-matching feature of PyTrack in action please go to [map-matching documentation](https://pytrack-lib.readthedocs.io/en/latest/notebooks/map-matching.html).

<p align="center">
    <a href="https://pytrack-lib.readthedocs.io/en/latest/notebooks/create_video_path.html"> <img width="1000" src="https://imgur.com/Inxho5F.png" alt="map-matching"></a>
</p>

### Video reconstruction of the itinerary
<p align="center">
    <a href="https://pytrack-lib.readthedocs.io/en/latest/notebooks/create_video_path.html"> <img width="400" src="https://imgur.com/M9Eche3.gif" alt="video_track"></a>
    <a href="https://pytrack-lib.readthedocs.io/en/latest/notebooks/segmentation_video_path.html"> <img width="400" src="https://imgur.com/6ncPdN6.gif" alt="video_seg_track"></a>
</p>



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
PyTrack is distributed under a [BSD-3-Clause-Clear Licence](https://github.com/cosbidev/PyTrack/blob/main/LICENSE).
