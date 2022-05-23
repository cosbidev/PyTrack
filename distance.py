import numpy as np
import networkx as nx

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
