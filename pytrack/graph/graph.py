import datetime as dt
from itertools import groupby

import networkx as nx
from shapely.geometry import Point, LineString

from . import distance
from . import download

useful_tags_way = [
    "bridge",
    "tunnel",
    "oneway",
    "lanes",
    "ref",
    "name",
    "highway",
    "maxspeed",
    "service",
    "access",
    "area",
    "landuse",
    "width",
    "est_width",
    "junction",
]


def graph_from_bbox(north, south, west, east, simplify=True, network_type='drive', buffer_dist=0):
    """ Create a graph from OpenStreetMap within some bounding box.

    Parameters
    ----------
    north: float
        Northern latitude of bounding box.
    south: float
        southern latitude of bounding box.
    west: float
        Western longitude of bounding box.
    east: float
        Eastern longitude of bounding box.
    simplify: bool, optional, default: True
        if True, simplify graph topology with the ``simplify_graph`` method.
    network_type: str, optional, default: 'drive'
        Type of street network to obtain.
    buffer_dist: float, optional, default: 0
        Distance in meters indicating how much to expand the bounding box.
    Returns
    -------
    G: networkx.MultiDiGraph
        Street network graph.
    """
    bbox_buffer = distance.enlarge_bbox(north, south, west, east, buffer_dist)
    response_json = download.osm_download(bbox_buffer, network_type=network_type)
    G = create_graph(response_json)

    if simplify:
        G.graph["simplified"] = True
        G = _simplification(G, response_json)
    else:
        G.graph["simplified"] = False
    return G


def _to_simplify(segment):
    """ Method that determines whether a segment of the graph must be simplified.

    Parameters
    ----------
    segment: list
        Graph segment to be evaluated. A segment is a list of node IDs.
    Returns
    -------
    ret: bool
        Whether or not to simplify a segment.
    """
    if len(segment) > 2:
        return True
    else:
        return False


def _simplification(G, response_json):
    """ Method that simplify a networkx graph.

    Parameters
    ----------
    G: networkx.MultiDiGraph
        Street network graph.
    response_json: json
        Response of OpenStreetMap API service got with``osm_download``method
    Returns
    -------
    G: networkx.MultiDiGraph
        Simplified street network graph.
    """
    _, paths = get_nodes_edges(response_json)
    for path in paths.values():
        is_oneway = _is_oneway(path, False)

        nodes = path.pop("nodes")

        junction = [False, False]
        if is_oneway:
            junction[1:1] = [True if G.degree[node] > 3 else False for node in nodes[1:-1]]
        else:
            junction[1:1] = [True if G.degree[node] > 4 else False for node in nodes[1:-1]]

        all_nodes_to_remove = []
        all_edges_to_add = []

        for segment in _split_at_values(nodes, junction):
            if _to_simplify(segment):
                all_edges_to_add.append(_build_edge(G, segment, path, is_oneway, reverse=False))

                if not is_oneway:
                    all_edges_to_add.append(_build_edge(G, segment, path, is_oneway, reverse=True))

                all_nodes_to_remove.extend(segment[1:-1])

        G.remove_nodes_from(set(all_nodes_to_remove))

        for edge in all_edges_to_add:
            G.add_edge(edge["origin"], edge["destination"], **edge["attr_dict"])

    return G


def _build_edge_attribute(G, segment, segment_attributes, is_oneway):
    """ Method that build the dictionary of attributes of a segment.

    Parameters
    ----------
    G: networkx.MultiDiGraph
        Street network graph.
    segment: list
        Graph segment to be evaluated. A segment is a list of node IDs.
    segment_attributes: dict
        Dictionary of road segment attributes.
    is_oneway: bool
        Indicates whether a street segment is oneway.
    Returns
    -------
    attribute: dict
        Dictionary of road segment attributes.
    """
    attribute = segment_attributes.copy()
    # attribute = {k: segment_attributes[k] for k in useful_tags_way if k in segment_attributes}

    attribute["geometry"] = LineString([Point((G.nodes[node]["x"],
                                               G.nodes[node]["y"])) for node in segment])
    attribute["oneway"] = is_oneway

    lat, lon = zip(*[(G.nodes[node]["y"], G.nodes[node]["x"]) for node in segment])
    edge_lengths = sum(distance.haversine_dist(lat[:-1], lon[:-1], lat[1:], lon[1:])).round(3)

    attribute["length"] = edge_lengths

    return attribute


def _build_edge(G, segment, segment_attributes, is_oneway, reverse=False):
    """ Method that builds an edge of the network street graph.

    Parameters
    ----------
    G: networkx.MultiDiGraph
        Street network graph.
    segment: list
        Graph segment to be evaluated. A segment is a list of node IDs.
    segment_attributes: dict
        Dictionary of road segment attributes.
    is_oneway: bool
        Indicates whether a street segment is oneway.
    reverse: bool, optional, default: False
        Indicates whether invert the direction of the edge.
    Returns
    -------
    edge: dict
        Edges to be added to the street network graph.
    """
    if not reverse:
        segment_attributes = _build_edge_attribute(G, segment, segment_attributes, is_oneway)

        edge = {"origin": segment[0], "destination": segment[-1],
                "attr_dict": segment_attributes}
        return edge
    else:
        segment_attributes = _build_edge_attribute(G, segment[::-1], segment_attributes, is_oneway)
        edge = {"origin": segment[-1], "destination": segment[0],
                "attr_dict": segment_attributes}
        return edge


def _split_at_values(nodes, junction):
    """ Method that creates a networkx.MultiDiGraph representing a network street graph.

    Parameters
    ----------
    nodes: list
        List of node IDs.
    junction: list
        It is a list of boolean conditions. If true, split the segment, otherwise not.
    Returns
    -------
    ret: generator
        Street network graph.
    """
    indices = [i for i, x in enumerate(nodes) if junction[i]]
    for start, end in zip([0, *indices], [*indices, len(nodes)]):
        yield nodes[start:end + 1]


def create_graph(response_json):
    """ Method that creates a networkx.MultiDiGraph representing a network street graph.

    Parameters
    ----------
    response_json: json
        Response of OpenStreetMap API service got with``osm_download``method.
    Returns
    -------
    G: networkx.MultiDiGraph
        Street network graph.
    """
    # TODO: nella creazione del grafo rimuovi intersezioni multiple, in modo tale che c'è un solo nodo intersezione
    #  per grafo create the graph as a MultiDiGraph and set its meta-attributes
    metadata = {
        'created_date': "{:%Y-%m-%d %H:%M:%S}".format(dt.datetime.now()),
        'created_with': f"PyTrack 1.0.0",
        'crs': "epsg:4326",
    }
    G = nx.MultiDiGraph(**metadata)

    nodes, paths = get_nodes_edges(response_json)

    # add each osm node to the graph
    for node, data in nodes.items():
        G.add_node(node, **data)

    add_edges(G, paths, bidirectional=False)

    # add length (haversine distance between nodes) attribute to each edge
    if len(G.edges) > 0:
        G = distance.add_edge_lengths(G)

    return G


def _oneway_path_values(path):
    """ Checks whether an OSM path is oneway.

    Parameters
    ----------
    path: dict
        Dictionary that describes an OSM path.
    Returns
    -------
    ret: dict
        Indicates whether an OSM path is oneway.
    """
    return {path[key] for key in path.keys() if key.startswith("oneway") and path[key] == "no"}


def _is_oneway(path, bidirectional):
    """ Checks whether an OSM path is oneway.

    Parameters
    ----------
    path: dict
        Dictionary that describes an OSM path.
    bidirectional: bool
        Indicates whether an edge is bidirectional.
    Returns
    -------
    is_oneway: bool
        Indicates whether an OSM path is oneway.
    """

    no_oneway_values = {"no", "false", "0", "reversible", "alternating"}

    oneway_path_values = _oneway_path_values(path)
    is_oneway = oneway_path_values.isdisjoint(no_oneway_values) and (
        not not oneway_path_values) and not bidirectional

    return is_oneway


def _is_reversed(path):
    """ Checks whether an OSM path is reversed.

    Parameters
    ----------
    path: dict
        Dictionary that describes an OSM path.
    Returns
    -------
    is_reversed: bool
        Indicates whether an OSM path is reversed.
    """
    reversed_values = {"-1", "reverse", "T"}

    oneway_path_values = _oneway_path_values(path)
    is_reversed = not oneway_path_values.isdisjoint(reversed_values)

    return is_reversed


def add_edges(G, paths, bidirectional=False, all_oneway=False):
    """ Add OSM edges to a ``networkx.MultiDiGraph``.

    Parameters
    ----------
    G: networkx.MultiDiGraph
        Street network graph.
    paths: dict
        Dictionary of OSM paths.
    bidirectional: bool, optional, default: False
        Indicates whether an edge is bidirectional.
    all_oneway: bool, optional, default: False
        Indicates whether an edge is oneway.
    """

    # TODO: "junction": "roundabout" è oneway
    for path in paths.values():
        nodes = path.pop('nodes')

        is_oneway = _is_oneway(path, bidirectional)
        is_reversed = _is_reversed(path)

        if is_oneway and is_reversed:
            nodes.reverse()

        if not all_oneway:
            path['oneway'] = is_oneway

        edges = list(zip(nodes[:-1], nodes[1:]))
        if not is_oneway:
            edges.extend([(v, u) for u, v in edges])

        G.add_edges_from(edges, **path)


def convert_edge(element):
    """ Convert an OSM edge into an edge to construct a street network graph.

    Parameters
    ----------
    element: dict
        An OSM path.
    Returns
    -------
    path: dict
        Dictionary for an OSM path.
    """
    # add OSM path id and remove consecutive duplicate nodes in the list of path's nodes
    path = {'osmid': element['id'], 'nodes': [group for group, _ in groupby(element['nodes'])]}

    # add tags
    path.update(element['tags'])

    return path


def convert_node(element):
    """ Convert an OSM node into a node to construct a street network graph.

    Parameters
    ----------
    element: dict
        An OSM node.
    Returns
    -------
    path: dict
        Dictionary for an OSM node.
    """

    # add node's GPS coordinates
    node = {'y': element['lat'], 'x': element['lon']}

    # add tags
    node.update(element['tags']) if "tags" in element else None

    return node


def get_nodes_edges(response_json):
    """ Extract nodes and paths from the OpenStreetMap query response.

    Parameters
    ----------
    response_json: json
        Response of OpenStreetMap API service got with``osm_download``method
    Returns
    -------
    nodes: dict
        Dictionary of OSM nodes.
    paths: dict
        Dictionary of OSM paths.
    """

    nodes = dict()
    paths = dict()

    for element in response_json['elements']:
        if element['type'] == "node":
            nodes[element['id']] = convert_node(element)
        elif element['type'] == "way":
            paths[element['id']] = convert_edge(element)

    return nodes, paths
