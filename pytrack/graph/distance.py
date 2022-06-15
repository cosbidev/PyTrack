import networkx as nx
import numpy as np
from pyproj import Geod
from shapely.geometry import Point, LineString

from pytrack.graph import utils

geod = Geod(ellps="WGS84")
EARTH_RADIUS_M = 6_371_009  # distance in meters


def haversine_dist(lat1, lon1, lat2, lon2, earth_radius=EARTH_RADIUS_M):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(np.deg2rad, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    # haversine formula 
    h = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    h = np.minimum(1, h)  # protect against floating point errors
    arc = 2 * np.arcsin(np.sqrt(h))

    # return distance in units of earth_radius
    return arc * earth_radius


def enlarge_bbox(north, south, west, east, dist):
    delta_lat = (dist / EARTH_RADIUS_M) * (180 / np.pi)
    lat_mean = np.mean([north, south])
    delta_lng = (dist / EARTH_RADIUS_M) * (180 / np.pi) / np.cos(lat_mean * np.pi / 180)
    north = north + delta_lat
    south = south - delta_lat
    east = east + delta_lng
    west = west - delta_lng

    return north, south, west, east


def add_edge_lengths(G, precision=3):
    uvk = tuple(G.edges)

    lat = G.nodes(data='y')
    lon = G.nodes(data='x')

    lat_u, lon_u, lat_v, lon_v = list(zip(*[(lat[u], lon[u], lat[v], lon[v]) for u, v, _ in uvk]))

    dists = haversine_dist(lat_u, lon_u, lat_v, lon_v).round(precision)
    dists[np.isnan(dists)] = 0
    nx.set_edge_attributes(G, values=dict(zip(uvk, dists)), name='length')
    return G


def interpolate_graph(G, dist=1):
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
    # TODO: use geospatial interpolation see: npts method in https://pyproj4.github.io/pyproj/stable/api/geod.html
    num_vert = max(round(geod.geometry_length(geom) / dist), 1)
    for n in range(num_vert + 1):
        point = geom.interpolate(n / num_vert, normalized=True)
        yield point.x, point.y


def interpolate_geom(geom, dist=1):
    if isinstance(geom, LineString):
        return LineString([xy for xy in _interpolate_geom(geom, dist)])
