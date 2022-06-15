import ipyleaflet
from ipyleaflet import basemaps
from ipyleaflet import Popup, Polyline, LayerGroup, LayersControl
from folium.plugins import MarkerCluster
from ipywidgets import HTML

class FoliumMap2(ipyleaflet.Map):

    def __init__(self, center=(43.7602, 11.2856), zoom=16, basemap=basemaps.CartoDB.Positron, crs="EPSG3857"):
        super(FoliumMap2, self).__init__(center=center, zoom=zoom, basemap=basemap)
        self.on_interaction(self.handle_click)
        self.num_click = 0
        self.control = LayersControl(position='topright')
        self.add_control(self.control)

    def handle_click(self, **kwargs):
        mes = HTML()

        if kwargs.get('type') == 'click':
            if self.num_click == 0:
                lat = kwargs.get('coordinates')[0]
                lon = kwargs.get('coordinates')[1]
                mes.value = f"Latitude: {lat:.4f} <br> Longitude: {lon:.4f}"

                self.add_layer(Popup(location=kwargs.get('coordinates'), child=mes, close_button=True, control=False, keep_in_view=True))
                self.num_click += 1
            else:
                self.num_click = 0


    def add_graph(self, G, plot_nodes=False, edge_color="#3388ff", edge_width=3,
                          edge_opacity=1, radius=1.7, node_color="red", fill=True, fill_color=None,
                          fill_opacity=1):

        edge_attr = dict()
        edge_attr["color"] = edge_color
        edge_attr["weight"] = edge_width
        edge_attr["opacity"] = edge_opacity
        edge_attr["fill"] = False

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

        fg_graph=LayerGroup(name='Graph edges')
        self.add_layer(fg_graph)
        #self.add_child(fg_point)
        #marker_cluster = MarkerCluster().add_to(fg)


        for geom in edges.geometry:
            edge = [(lat, lng) for lng, lat in geom.coords]
            LayerGroup.add_layer(Polyline(locations=edge, **edge_attr, ))

        if plot_nodes:
            for point, osmid in zip(nodes.geometry, nodes.osmid):
                folium.Circle(location=(point.y, point.x), popup=f"osmid: {osmid}", radius=radius, **node_attr).add_to(fg_point)

        folium.LayerControl().add_to(self)
        #self.lc = folium.LayerControl()
        #self.add_child(folium.LayerControl())
