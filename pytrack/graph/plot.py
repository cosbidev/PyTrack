import folium

from . import utils


def plot_graph_folium(G, plot_nodes=False, edge_color="#3388ff", edge_width=3,
                      edge_opacity=1, radius=1.7, node_color="red", fill=True, fill_color=None,
                      fill_opacity=1):
    edge_attr = dict()
    edge_attr["color"] = edge_color
    edge_attr["weight"] = edge_width
    edge_attr["opacity"] = edge_opacity

    node_attr = dict()
    node_attr["color"] = node_color
    node_attr["fill"] = fill
    if not fill_color:
        node_attr["fill_color"] = node_color
    else:
        node_attr["fill_color"] = node_color
    node_attr["fill_opacity"] = fill_opacity

    nodes, edges = utils.graph_to_gdfs(G)
    edges = utils.graph_to_gdfs(G, nodes=False)

    graph_map = folium.Map([nodes.y.mean(), nodes.x.mean()], tiles='CartoDB positron', zoom_start=16)
    folium.LatLngPopup().add_to(graph_map)

    for geom in edges.geometry:
        edge = [(lat, lng) for lng, lat in geom.coords]
        folium.PolyLine(locations=edge, **edge_attr, ).add_to(graph_map)

    if plot_nodes:
        for point, osmid in zip(nodes.geometry, nodes.osmid):
            folium.Circle(location=(point.y, point.x), popup=f"osmid: {osmid}", radius=radius, **node_attr).add_to(
                graph_map)

    return graph_map
