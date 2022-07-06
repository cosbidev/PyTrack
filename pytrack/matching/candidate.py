import copy

import numpy as np
import pandas as pd
from sklearn.neighbors import BallTree

from pytrack.graph import distance, utils


class Candidate:
    """ Class to represent a candidate element.

    Parameters
    ----------
    node_id: str
        OSM node ID.
    edge_osmid: str
        OSM edge ID.
    obs: tuple
        Coordinate of actual GPS points.
    great_dist: float
        Distance between candidate and actual GPS point.
    coord: tuple
        Candidate coordinate.
    Returns
    -------
    Candidate object
    """
    __slots__ = ["node_id", "edge_osmid", "obs", "great_dist", "coord"]

    def __init__(self, node_id, edge_osmid, obs, great_dist, coord):
        self.node_id = node_id
        self.edge_osmid = edge_osmid
        self.obs = obs
        self.great_dist = great_dist
        self.coord = coord


def get_candidates(G, points, interp_dist=1, closest=True, radius=10):
    """ Extract candidate points for Hidden-Markov Model map-matching approach.

    Parameters
    ----------
    G: networkx.MultiDiGraph
        Street network graph.
    points: list
        The actual GPS points.
    interp_dist: float, optional, default: 1
        Step to interpolate the graph. The smaller the interp_dist, the greater the precision and the longer
        the computational time.
    closest: bool, optional, default: True
        If true, only the closest point is considered for each edge.
    radius: float, optional, default: 10
        Radius of the search circle.
    Returns
    -------
    G: networkx.MultiDiGraph
        Street network graph.
    results: dict
        Results to be used for the map-matching algorithm.
    """

    G = G.copy()

    if interp_dist:
        G = distance.interpolate_graph(G, dist=interp_dist)

    geoms = utils.graph_to_gdfs(G, nodes=False).set_index(["u", "v"])[["osmid", "geometry"]]

    uv_xy = [[u, osmid, np.deg2rad(xy)] for uv, geom, osmid in
             zip(geoms.index, geoms.geometry.values, geoms.osmid.values)
             for u, xy in zip(uv, geom.coords[:])]

    index, osmid, xy = zip(*uv_xy)

    nodes = pd.DataFrame(xy, index=osmid, columns=["x", "y"])[["y", "x"]]

    ball = BallTree(nodes, metric='haversine')

    idxs, dists = ball.query_radius(np.deg2rad(points), radius / distance.EARTH_RADIUS_M, return_distance=True)
    dists = dists * distance.EARTH_RADIUS_M  # radians to meters

    if closest:
        results = dict()
        for i, (point, idx, dist) in enumerate(zip(points, idxs, dists)):
            df = pd.DataFrame({"osmid": list(np.array(index)[idx]),
                               "edge_osmid": list(nodes.index[idx]),
                               "coords": tuple(map(tuple, np.rad2deg(nodes.values[idx]))),
                               "dist": dist})

            df = df.loc[df.groupby('edge_osmid')['dist'].idxmin()].reset_index(drop=True)

            results[i] = {"observation": point,
                          "osmid": list(df["osmid"]),
                          "edge_osmid": list(df["edge_osmid"]),
                          "candidates": list(df["coords"]),
                          "candidate_type": np.full(len(df["coords"]), False),
                          "dists": list(df["dist"])}

    else:
        results = {i: {"observation": point,
                       "osmid": list(np.array(index)[idx]),
                       "edge_osmid": list(nodes.index[idx]),
                       "candidates": list(map(tuple, np.rad2deg(nodes.values[idx]))),
                       "candidate_type": np.full(len(nodes.index[idx]), False),
                       "dists": list(dist)} for i, (point, idx, dist) in enumerate(zip(points, idxs, dists))}

    return G, results


def elab_candidate_results(results, predecessor):
    """ Elaborate results of ``candidate.get_candidates`` method. It selects which candidate best matches the actual
    GPS points.

    Parameters
    ----------
    results: dict
        Output of ``candidate.get_candidates`` method.
    predecessor: dict
        Output of ``mpmatching.viterbi_search`` method.
    Returns
    -------
    results: dict
        Elaborated results.
    """
    results = copy.deepcopy(results)
    for key in list(results.keys())[:-1]:
        win_cand_idx = int(predecessor[str(key + 1)].split("_")[1])
        results[key]["candidate_type"][win_cand_idx] = True

    win_cand_idx = int(predecessor["target"].split("_")[1])
    results[list(results.keys())[-1]]["candidate_type"][win_cand_idx] = True
    return results
