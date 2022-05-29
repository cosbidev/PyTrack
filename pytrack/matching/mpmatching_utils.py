import math

import matplotlib.pyplot as plt
import networkx as nx
from pytrack.graph import distance

SIGMA_Z = 4.07
BETA = 20


# A gaussian distribution
def emission_prob(u):
    if u.great_dist:
        c = 1 / (SIGMA_Z * math.sqrt(2 * math.pi))
        return c * math.exp(-(u.great_dist / SIGMA_Z) ** 2)
    else:
        return 1


# A empirical distribution
def transition_prob(G, u, v):   
    c = 1 / BETA

    if u.great_dist and v.great_dist:
        delta = abs(
            nx.shortest_path_length(G, u.node_id, v.node_id, weight="length", method='dijkstra')
            - distance.haversine_dist(*u.coord, *v.coord))
        return c * math.exp(-delta / BETA) * 1e5
    else:
        return 1


class Candidate:
    __slots__ = ["node_id", "edge_osmid", "obs", "great_dist", "coord"]

    def __init__(self, node_id, edge_osmid, obs, great_dist, coord):
        self.node_id = node_id
        self.edge_osmid = edge_osmid
        self.obs = obs
        self.great_dist = great_dist
        self.coord = coord


def create_trellis(results):
    G = nx.DiGraph()

    prev_nodes = ["start"]
    G.add_node("start", candidate=Candidate("start", None, None, None, None))
    G.add_node("target", candidate=Candidate("start", None, None, None, None))

    for idx, item in results.items():
        obs = item["observation"]
        nodes, data_node = zip(*[(f"{idx}_{j}", {"candidate": Candidate(node_id, edge_osmid, obs, dist, cand)})
                                 for j, (node_id, edge_osmid, dist, cand) in
                                 enumerate(zip(item["osmid"], item["edge_osmid"], item["dists"], item["candidates"]))])
        edges = [(u, v) for u in prev_nodes for v in nodes]

        G.add_nodes_from(zip(nodes, data_node))
        G.add_edges_from(edges)
        prev_nodes = nodes

    edges = [(u, "target") for u in prev_nodes]
    G.add_edges_from(edges)
    return G


def draw_trellis(T, figsize=(15, 12), dpi=300, node_size=500, font_size=8):
    plt.figure(1, figsize=figsize, dpi=dpi)

    pos = nx.drawing.nx_pydot.graphviz_layout(T, prog='dot', root='start')
    trellis_diag = nx.draw_networkx(T, pos, node_size=node_size, font_size=font_size)

    return trellis_diag
