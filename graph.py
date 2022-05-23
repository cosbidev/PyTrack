import datetime as dt
from itertools import groupby

import networkx as nx
from shapely.geometry import Point, LineString

from PyTrack import distance
from PyTrack import download


def graph_from_bbox(north, south, west, east, simplify=True, network_type='drive', buffer_dist=0):
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
    if len(segment) > 2:
        return True
    else:
        return False


def _simplification(G, response_json):
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
    attribute = segment_attributes.copy()

    attribute["geometry"] = LineString([Point((G.nodes[node]["x"],
                                               G.nodes[node]["y"])) for node in segment])
    attribute["oneway"] = is_oneway

    lat, lon = zip(*[(G.nodes[node]["y"], G.nodes[node]["x"]) for node in segment])
    edge_lengths = sum(distance.haversine_dist(lat[:-1], lon[:-1], lat[1:], lon[1:])).round(3)

    attribute["length"] = edge_lengths

    return attribute


def _build_edge(G, segment, segment_attributes, is_oneway, reverse=False):
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
    indices = [i for i, x in enumerate(nodes) if junction[i]]
    for start, end in zip([0, *indices], [*indices, len(nodes)]):
        yield nodes[start:end + 1]


def create_graph(response_json):
    # TODO: nella creazione del grafo rimuovi intersezioni multiple, in modo tale che c'è un solo nodo intersezione
    #  per grafo create the graph as a MultiDiGraph and set its meta-attributes
    metadata = {
        'created_date': "{:%Y-%m-%d %H:%M:%S}".format(dt.datetime.now()),
        'created_with': f"PyTrack {1.00}",
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
    return {path[key] for key in path.keys() if key.startswith("oneway") and path[key] == "no"}


def _is_oneway(path, bidirectional):
    no_oneway_values = {"no", "false", "0", "reversible", "alternating"}

    oneway_path_values = _oneway_path_values(path)
    is_oneway = oneway_path_values.isdisjoint(no_oneway_values) and (
        not not oneway_path_values) and not bidirectional

    return is_oneway


def _is_reversed(path):
    reversed_values = {"-1", "reverse", "T"}

    oneway_path_values = _oneway_path_values(path)
    is_reversed = not oneway_path_values.isdisjoint(reversed_values)

    return is_reversed


def add_edges(G, paths, bidirectional=False, all_oneway=False):
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
    # add OSM path id and remove consecutive duplicate nodes in the list of path's nodes
    path = {'osmid': element['id'], 'nodes': [group for group, _ in groupby(element['nodes'])]}

    # add tags
    path.update(element['tags'])

    return path


def convert_node(element):
    # add node's GPS coordinates
    node = {'y': element['lat'], 'x': element['lon']}

    # add tags
    node.update(element['tags']) if "tags" in element else None

    return node


def get_nodes_edges(response_json):
    nodes = dict()
    paths = dict()

    for element in response_json['elements']:
        if element['type'] == "node":
            nodes[element['id']] = convert_node(element)
        elif element['type'] == "way":
            paths[element['id']] = convert_edge(element)

    return nodes, paths


# %%
#grafo = graph_from_bbox(41.86722, 41.86660, 12.41930, 12.42239, simplify=True, network_type='drive')
