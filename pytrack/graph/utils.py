from decimal import Decimal

import pandas as pd
from shapely.geometry import LineString, Point


def get_unique_number(lon, lat):
    """ Assigns a unique identifier to a geographical coordinate.
    Parameters
    ----------
    lon: float
        Longitude of the point
    lat: float
        Latitude of the point
    Returns
    -------
    val: float
        Unique identifier.
    """
    if isinstance(lat, str):
        lat_double = float(lat)
    else:
        lat_double = lat
    if isinstance(lon, str):
        lon_double = float(lon)
    else:
        lon_double = lon

    lat_int = int((lat_double * 10 ** abs(Decimal(str(lat_double)).as_tuple().exponent)))
    lon_int = int((lon_double * 10 ** abs(Decimal(str(lon_double)).as_tuple().exponent)))

    val = abs((lat_int << 16 & 0xffff0000) | (lon_int & 0x0000ffff))
    val = val % 2147483647

    # alternative use hash or other
    # return int(str(lat_int)+str(lon_int))
    return val


def graph_to_gdfs(G, nodes=True, edges=True, node_geometry=True, edge_geometry=True):
    """ Convert a networkx.MultiDiGraph to node and/or edge pandas DataFrame.

    Parameters
    ----------
    G: networkx.MultiDiGraph
        Street network graph.
    nodes: bool, optional, default: True
        Whether to extract graph nodes.
    edges: bool, optional, default: True
        Whether to extract graph edges.
    node_geometry: bool, optional, default: True
        Whether to compute graph node geometries.
    edge_geometry: bool, optional, default: True
        Whether to extract graph edge geometries.
    Returns
    -------
    gdf_nodes: pandas.DataFrame
        Dataframe collecting graph nodes.
    gdf_edges: pandas.DataFrame
        Dataframe collecting graph edges
    """
    crs = G.graph["crs"]

    if nodes:
        nodes, data = zip(*G.nodes(data=True))

        if node_geometry:
            # convert node x/y attributes to Points for geometry column
            for d in data:
                d["geometry"] = Point(d["x"], d["y"])
            gdf_nodes = pd.DataFrame(data)
            gdf_nodes.insert(loc=0, column='osmid', value=nodes)
        else:
            gdf_nodes = pd.DataFrame(data)
            gdf_nodes.insert(loc=0, column='osmid', value=nodes)

    if edges:
        u, v, k, data = zip(*G.edges(keys=True, data=True))
        if edge_geometry:
            longs = G.nodes(data="x")
            lats = G.nodes(data="y")

            for d, src, tgt in zip(data, u, v):
                if "geometry" not in d:
                    d["geometry"] = LineString((Point((longs[src], lats[src])),
                                                Point((longs[tgt], lats[tgt]))))
            gdf_edges = pd.DataFrame(data)

        else:
            gdf_edges = pd.DataFrame(data)
            gdf_edges["geometry"] = None
            gdf_edges.crs = crs

        gdf_edges["u"], gdf_edges["v"], gdf_edges["key"] = u, v, k

        gdf_edges = gdf_edges[["u", "v", "key"] + gdf_edges.columns.to_list()[:-3]]

    if nodes and edges:
        return gdf_nodes, gdf_edges
    elif nodes:
        return gdf_nodes
    elif edges:
        return gdf_edges
