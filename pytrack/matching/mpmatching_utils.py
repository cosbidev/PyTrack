import itertools
import math

import networkx as nx
from shapely.geometry import LineString

from pytrack.graph import distance
from pytrack.matching import candidate

SIGMA_Z = 4.07
BETA = 20


# A gaussian distribution
def emission_prob(u, sigma=SIGMA_Z):
    """ Compute emission probability of a node

    Parameters
    ----------
    u: dict
        Node of the graph.
    sigma: float
        It is an estimate of the magnitude of the GPS error. See https://www.ismll.uni-hildesheim.de/lehre/semSpatial-10s/script/6.pdf
        for a more detailed description of its calculation.

    Returns
    -------
    ret: float
        Emission probability of a node.
    """
    if u.great_dist:
        c = 1 / (sigma * math.sqrt(2 * math.pi))
        return c * math.exp(-(u.great_dist / sigma) ** 2)
    else:
        return 1


# A empirical distribution
def transition_prob(G, u, v, beta=BETA):
    """ Compute transition probability between node u and v.

    Parameters
    ----------
    G: networkx.MultiDiGraph
        Road network graph.
    u: dict
        Starting node of the graph.
    v: dict
        Target node of the graph.
    beta: float
        This describes the difference between route distances and great circle distances. See https://www.ismll.uni-hildesheim.de/lehre/semSpatial-10s/script/6.pdf
        for a more detailed description of its calculation.

    Returns
    -------
    ret: float
        Transition probability between node u and v.
    """
    c = 1 / BETA

    if u.great_dist and v.great_dist:
        delta = abs(
            nx.shortest_path_length(G, u.node_id, v.node_id, weight="length", method='dijkstra')
            - distance.haversine_dist(*u.coord, *v.coord))
        return c * math.exp(-delta / BETA) * 1e5
    else:
        return 1


def create_trellis(results):
    """ Create a Trellis graph.

    Parameters
    ----------
    results: dict
        Output of ``candidate.get_candidates`` method.
    Returns
    -------
    G: networkx.DiGraph
        A directed acyclic Trellis graph.
    """

    G = nx.DiGraph()

    prev_nodes = ["start"]
    G.add_node("start", candidate=candidate.Candidate("start", None, None, None, None))
    G.add_node("target", candidate=candidate.Candidate("start", None, None, None, None))

    for idx, item in results.items():
        obs = item["observation"]
        nodes, data_node = zip(
            *[(f"{idx}_{j}", {"candidate": candidate.Candidate(node_id, edge_osmid, obs, dist, cand)})
              for j, (node_id, edge_osmid, dist, cand) in
              enumerate(zip(item["osmid"], item["edge_osmid"], item["dists"], item["candidates"]))])
        edges = [(u, v) for u in prev_nodes for v in nodes]

        G.add_nodes_from(zip(nodes, data_node))
        G.add_edges_from(edges)
        prev_nodes = nodes

    edges = [(u, "target") for u in prev_nodes]
    G.add_edges_from(edges)
    return G


def create_path(G, trellis, predecessor):
    """ Create the path that best matches the actual GPS data.

    Parameters
    ----------
    G: networkx.MultiDiGraph
        Road network graph.
    trellis: networkx.DiGraph
        A directed acyclic graph.
    predecessor: dict
        Predecessor for each node.
    Returns
    -------
    path_elab: list
        list of node IDs.
    """
    u, v = list(zip(*[(u, v) for v, u in predecessor.items()][2:]))
    path = [(u, v) for u, v in zip(u, u[1:])]

    path_elab = [node for u, v in path for node in nx.shortest_path(G, trellis.nodes[u]["candidate"].node_id,
                                                                    trellis.nodes[v]["candidate"].node_id,
                                                                    weight='length')]
    path_elab = [k for k, g in itertools.groupby(path_elab)]
    return path_elab


def create_matched_path(G, trellis, predecessor):
    """ Create the path that best matches the actual GPS points. Route created based on results obtained from ``pmatching_utils.viterbi_search`` and ``mpmatching_utils.create_trellis`` methods.

    Parameters
    ----------
    G: networkx.MultiDiGraph
        Street network graph used to create trellis graph.
    trellis: networkx.DiGraph
        A directed acyclic Trellis graph.
    predecessor: dict
        Predecessor for each node.

    Returns
    -------
    node_ids: list
        List of ids of the nodes that compose the path.
    path_coords: list
        List of nodes' coordinates, in the form of tuple (lat, lon), composing the path.
    """
    node_ids = create_path(G, trellis, predecessor)
    path_coords = [(lat, lng) for lng, lat in LineString([G.nodes[node]["geometry"] for node in node_ids]).coords]
    return node_ids, path_coords
