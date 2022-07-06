import networkx as nx
import numpy as np
from pyproj import Geod
from shapely.geometry import Point, LineString

from pytrack.graph import utils

geod = Geod(ellps="WGS84")
EARTH_RADIUS_M = 6_371_009  # distance in meters


def get_bearing(lat1, lon1, lat2, lon2):
    """ Get bearing between two points.

    Parameters
    ----------
    lat1: float
        Latitude of the first point specified in decimal degrees
    lon1: float
        Longitude of the first point specified in decimal degrees
    lat2: float
        Latitude of the second point specified in decimal degrees
    lon2: float
        Longitude of the second point specified in decimal degrees

    Returns
    ----------
    bearing: float
        Bearing between two points.
    """

    bearing, _, _ = geod.inv(lon1, lat1, lon2, lat2)
    return bearing


def haversine_dist(lat1, lon1, lat2, lon2, earth_radius=EARTH_RADIUS_M):
    """ Calculate the great circle distance between two points on the earth (specified in decimal degrees)

    Parameters
    ----------
    lat1: float
        Latitude of the first point specified in decimal degrees
    lon1: float
        Longitude of the first point specified in decimal degrees
    lat2: float
        Latitude of the second point specified in decimal degrees
    lon2: float
        Longitude of the second point specified in decimal degrees

    earth_radius: float, optional, default: 6371009.0 meters
        Earth's radius
    Returns
    ----------
    dists: float
        Distance in units of earth_radius
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(np.deg2rad, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    # haversine formula 
    h = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    h = np.minimum(1, h)  # protect against floating point errors
    arc = 2 * np.arcsin(np.sqrt(h))

    dist = arc * earth_radius

    return dist


def enlarge_bbox(north, south, west, east, dist):
    """ Method that expands a bounding box by a specified distance.

    Parameters
    ----------
    north: float
        Northern latitude of bounding box.
    south: float
        Southern latitude of bounding box.
    west: float
        Western longitude of bounding box.
    east: float
        Eastern longitude of bounding box.

    dist: float
        Distance in meters indicating how much to expand the bounding box.

    Returns
    ----------
    north, south, west, east: float
        North, south, west, east coordinates of the expanded bounding box
    """
    delta_lat = (dist / EARTH_RADIUS_M) * (180 / np.pi)
    lat_mean = np.mean([north, south])
    delta_lng = (dist / EARTH_RADIUS_M) * (180 / np.pi) / np.cos(lat_mean * np.pi / 180)
    north = north + delta_lat
    south = south - delta_lat
    east = east + delta_lng
    west = west - delta_lng

    return north, south, west, east


def add_edge_lengths(G, precision=3):
    """ Method that adds the length of individual edges to the graph.

    Parameters
    ----------
    G: networkx.MultiDiGraph
        Road network graph.
    precision: float, optional, default: 3
        Number of decimal digits of the length of individual edges.
    Returns
    ----------
    G: networkx.MultiDiGraph
        Street network graph.
    """
    uvk = tuple(G.edges)

    lat = G.nodes(data='y')
    lon = G.nodes(data='x')

    lat_u, lon_u, lat_v, lon_v = list(zip(*[(lat[u], lon[u], lat[v], lon[v]) for u, v, _ in uvk]))

    dists = haversine_dist(lat_u, lon_u, lat_v, lon_v).round(precision)
    dists[np.isnan(dists)] = 0
    nx.set_edge_attributes(G, values=dict(zip(uvk, dists)), name='length')
    return G


def interpolate_graph(G, dist=1):
    """ Method that creates a graph by interpolating the nodes of a graph.

    Parameters
    ----------
    G: networkx.MultiDiGraph
        Road network graph.
    dist: float, optional, default: 1
        Distance between one node and the next.
    Returns
    ----------
    G: networkx.MultiDiGraph
        Street network graph.
    """
    G = G.copy()

    edges_toadd = []
    nodes_toadd = []

    for edge in list(G.edges(data=True)):
        u, v, data = edge
        # oneway = data["oneway"]
        geom = data["geometry"]
        data["length"] = dist

        G.remove_edge(u, v)

        XY = [xy for xy in _interpolate_geom(geom, dist=dist)]

        # generate nodes id
        uv = [(utils.get_unique_number(*u), utils.get_unique_number(*v)) for u, v in zip(XY[:-1], XY[1:])]
        # edges_interp = [LineString([u, v]) for u, v in zip(XY[:-1], XY[1:])]
        data_edges = [(lambda d: d.update({"geometry": LineString([u, v])}) or d)(data.copy()) for u, v in
                      zip(XY[:-1], XY[1:])]
        edges_toadd.extend([(*uv, data) for uv, data in zip(uv, data_edges)])

        nodes_toadd.extend([(utils.get_unique_number(lon, lat),
                             {"x": lon, "y": lat, "geometry": Point(lon, lat)}) for lon, lat in XY])

    G.add_edges_from(edges_toadd)
    G.add_nodes_from(nodes_toadd)

    G.remove_nodes_from(list(nx.isolates(G)))
    G.interpolation = True
    return G


def _interpolate_geom(geom, dist=1):
    """ Generator that interpolates a geometry created using the ``shapely.geometry.LineString`` method.

    Parameters
    ----------
    geom: shapely.geometry.LineString
        Geometry to be interpolated.
    dist: float, optional, default: 1
        Distance between one node and the next.
    Returns
    ----------
    ret: generator
        Interpolated geometry.
    """
    # TODO: use geospatial interpolation see: npts method in https://pyproj4.github.io/pyproj/stable/api/geod.html
    num_vert = max(round(geod.geometry_length(geom) / dist), 1)
    for n in range(num_vert + 1):
        point = geom.interpolate(n / num_vert, normalized=True)
        yield point.x, point.y


def interpolate_geom(geom, dist=1):
    """ Method that interpolates a geometry created using the ``shapely.geometry.LineString`` method.

    Parameters
    ----------
    geom: shapely.geometry.LineString
        Geometry to be interpolated.
    dist: float, optional, default: 1
        Distance between one node and the next.
    Returns
    ----------
    geom: shapely.geometry
        Interpolated geometry.
    """
    if isinstance(geom, LineString):
        return LineString([xy for xy in _interpolate_geom(geom, dist)])
