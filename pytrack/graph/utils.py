from shapely.geometry import LineString, Point
import pandas as pd

'''
ISSUE: geopandas ha problemi con osx el captain
def graph_to_gdfs(G, nodes=True, edges=True, node_geometry=True, edge_geometry=True):
    #TODO: gestisci il fatto che grafo sia semplificato e quindi geometrie esistono
    crs = G.graph["crs"]

    if nodes:
        nodes, data = zip(*G.nodes(data=True))

        if node_geometry:
            # convert node x/y attributes to Points for geometry column
            geom = [Point(d["x"], d["y"]) for d in data]
            gdf_nodes = gpd.GeoDataFrame(data, crs=crs, geometry=geom)
            gdf_nodes.insert(loc=0, column='osmid', value=nodes)
        else:
            gdf_nodes = gpd.GeoDataFrame(data)
            gdf_nodes.insert(loc=0, column='osmid', value=nodes)

    if edges:
        u, v, k, data = zip(*G.edges(keys=True, data=True))
        if edge_geometry:
            longs = G.nodes(data="x")
            lats = G.nodes(data="y")

            if G.graph["simplified"]:
                return
            else:
                geoms = [LineString((Point((longs[src], lats[src])),
                                     Point((longs[tgt], lats[tgt])))) for src, tgt in zip(u, v)]
            
            gdf_edges = gpd.GeoDataFrame(data, crs=crs, geometry=geoms)

        else:
            gdf_edges = gpd.GeoDataFrame(data)
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
'''


def graph_to_gdfs(G, nodes=True, edges=True, node_geometry=True, edge_geometry=True):
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
