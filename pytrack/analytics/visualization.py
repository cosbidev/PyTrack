from inspect import signature

import folium
import matplotlib.pyplot as plt
import networkx as nx
from shapely.geometry import LineString

from pytrack.graph import utils
from pytrack.matching import mpmatching_utils


class Map(folium.Map):
    """ This class extends the ``folium.Map`` to add functionality useful to represent graphs and road paths.

    Parameters
    ----------
    location: tuple or list, optional, default: None
        Latitude and Longitude of Map (Northing, Easting).
    width: int or percentage string, optional, default: '100%')
        Width of the map.
    height: int or percentage string, optional, default: '100%'
        Height of the map.
    tiles: str, optional, default: 'OpenStreetMap'
        Map tileset to use. Can choose from a list of built-in tiles,
        pass a custom URL or pass `None` to create a map without tiles.
        For more advanced tile layer options, use the `TileLayer` class.
    min_zoom: int, optional, default: 0
        Minimum allowed zoom level for the tile layer that is created.
    max_zoom: int, optional, default: 18
        Maximum allowed zoom level for the tile layer that is created.
    zoom_start: int, optional, default 10
        Initial zoom level for the map.
    attr: string, optional, default: None
        Map tile attribution; only required if passing custom tile URL.
    crs : str, optional, default: 'EPSG3857'
        Defines coordinate reference systems for projecting geographical points
        into pixel (screen) coordinates and back.
        You can use Leaflet's values :
        * EPSG3857 : The most common CRS for online maps, used by almost all
        free and commercial tile providers. Uses Spherical Mercator projection.
        Set in by default in Map's crs option.
        * EPSG4326 : A common CRS among GIS enthusiasts.
        Uses simple Equirectangular projection.
        * EPSG3395 : Rarely used by some commercial tile providers.
        Uses Elliptical Mercator projection.
        * Simple : A simple CRS that maps longitude and latitude into
        x and y directly. May be used for maps of flat surfaces
        (e.g. game maps). Note that the y axis should still be inverted
        (going from bottom to top).
    control_scale : bool, optional, default: False
        Whether to add a control scale on the map.
    prefer_canvas : bool, optional, default: False
        Forces Leaflet to use the Canvas back-end (if available) for
        vector layers instead of SVG. This can increase performance
        considerably in some cases (e.g. many thousands of circle
        markers on the map).
    no_touch : bool, optional, default: False
        Forces Leaflet to not use touch events even if it detects them.
    disable_3d : bool, optional, default: False
        Forces Leaflet to not use hardware-accelerated CSS 3D
        transforms for positioning (which may cause glitches in some
        rare environments) even if they're supported.
    zoom_control : bool, optional, default: True
        Display zoom controls on the map.
    **kwargs : keyword arguments, optional, default: no attributes
        Additional keyword arguments are passed to Leaflets Map class:
        https://leafletjs.com/reference-1.6.0.html#map

    Returns
    -------
    Folium Map Object

    Notes
    -----
    See https://github.com/python-visualization/folium/blob/551b2420150ab56b71dcf14c62e5f4b118caae32/folium/folium.py#L69
    for a more detailed description

    """

    def __init__(
            self,
            location=None,
            width='100%',
            height='100%',
            left='0%',
            top='0%',
            position='relative',
            tiles='CartoDB positron',
            attr=None,
            min_zoom=0,
            max_zoom=18,
            zoom_start=15,
            min_lat=-90,
            max_lat=90,
            min_lon=-180,
            max_lon=180,
            max_bounds=False,
            crs='EPSG3857',
            control_scale=False,
            prefer_canvas=False,
            no_touch=False,
            disable_3d=False,
            png_enabled=False,
            zoom_control=True,
            **kwargs
    ):
        super().__init__(location, width, height, left, top, position, tiles, attr, min_zoom, max_zoom, zoom_start,
                         min_lat, max_lat, min_lon, max_lon, max_bounds, crs, control_scale, prefer_canvas, no_touch,
                         disable_3d, png_enabled, zoom_control, **kwargs)
        self.tiles = tiles
        folium.LatLngPopup().add_to(self)

    def _render_reset(self):
        for key in list(self._children.keys()):
            if key.startswith('cartodbpositron') or key.startswith('lat_lng_popup'):
                self._children.pop(key)
        children = self._children
        self.__init__(self.location, tiles=self.tiles)
        self.options = self.options
        for k, v in children.items():
            self.add_child(v)

    def add_graph(self, G, plot_nodes=False, edge_color="#3388ff", edge_width=3,
                  edge_opacity=1, radius=1.7, node_color="red", fill=True, fill_color=None,
                  fill_opacity=1):
        """ Add the road network graph created with ``pytrack.graph.graph.graph_from_bbox`` method

        Parameters
        ----------
        G: networkx.MultiDiGraph
            Road network graph.
        plot_nodes: bool, optional, default: False
            If true, it will show the vertices of the graph.
        edge_color: str, optional, default: "#3388ff"
            Colour of graph edges
        edge_width: float, optional, default: 3
            Width of graph edges
        edge_opacity: float, optional, default: 1
            Opacity of graph edges
        radius: float, optional, default: 1.7
            Radius of graph vertices
        node_color: str, optional, default: "red"
            Colour of graph vertices
        fill: bool, optional, default: True
            Whether to fill the nodes with color. Set it to false to disable filling on the nodes.
        fill_color: str or NoneType, default: None
            Fill color. Defaults to the value of the color option.
        fill_opacity: float, optional, default: 1
            Fill opacity
        """
        edge_attr = dict()
        edge_attr["color"] = edge_color
        edge_attr["weight"] = edge_width
        edge_attr["opacity"] = edge_opacity

        node_attr = dict()
        node_attr["color"] = node_color
        node_attr["fill"] = fill

        if not fill_color:
            node_attr["fill_color"] = fill_color
        else:
            node_attr["fill_color"] = fill_color
        node_attr["fill_opacity"] = fill_opacity

        nodes, edges = utils.graph_to_gdfs(G)
        edges = utils.graph_to_gdfs(G, nodes=False)

        fg_graph = folium.FeatureGroup(name='Graph edges', show=True)
        self.add_child(fg_graph)

        for geom in edges.geometry:
            edge = [(lat, lng) for lng, lat in geom.coords]
            folium.PolyLine(locations=edge, **edge_attr, ).add_to(fg_graph)

        if plot_nodes:
            fg_point = folium.FeatureGroup(name='Graph vertices', show=True)
            self.add_child(fg_point)
            for point, osmid in zip(nodes.geometry, nodes.osmid):
                folium.Circle(location=(point.y, point.x), popup=f"osmid: {osmid}", radius=radius, **node_attr).add_to(
                    fg_point)

        folium.LayerControl().add_to(self)

    def draw_candidates(self, candidates, radius):
        """ Draw the candidate nodes of the HMM matcher

        Parameters
        ----------
        candidates: dict
            Candidates' dictionary computed via ``pytrack.matching.candidate.get_candidates`` method
        radius: float
            Candidate search radius
        """
        fg_cands = folium.FeatureGroup(name='Candidates', show=True, control=True)
        fg_gps = folium.FeatureGroup(name="Actual GPS points", show=True, control=True)
        self.add_child(fg_cands)
        self.add_child(fg_gps)

        for i, obs in enumerate(candidates.keys()):
            folium.Circle(location=candidates[obs]["observation"], radius=radius, weight=1, color="black", fill=True,
                          fill_opacity=0.2).add_to(fg_gps)
            popup = f'{i}-th point \n Latitude: {candidates[obs]["observation"][0]}\n Longitude: ' \
                    f'{candidates[obs]["observation"][1]}'
            folium.Circle(location=candidates[obs]["observation"], popup=popup, radius=1, color="black",
                          fill=True, fill_opacity=1).add_to(fg_gps)

            # plot candidates
            for cand, label, cand_type in zip(candidates[obs]["candidates"], candidates[obs]["edge_osmid"],
                                              candidates[obs]["candidate_type"]):
                popup = f"coord: {cand} \n edge_osmid: {label}"
                if cand_type:
                    folium.Circle(location=cand, popup=popup, radius=2, color="yellow", fill=True,
                                  fill_opacity=1).add_to(
                        fg_cands)
                else:
                    folium.Circle(location=cand, popup=popup, radius=1, color="red", fill=True, fill_opacity=1).add_to(
                        fg_cands)

        del self._children[next(k for k in self._children.keys() if k.startswith('layer_control'))]
        self.add_child(folium.LayerControl())
        self._render_reset()

    def draw_path(self, G, trellis, predecessor, path_name="Matched path"):
        """ Draw the map-matched path

        Parameters
        ----------
        G: networkx.MultiDiGraph
            Road network graph.
        trellis: nx.DiGraph
            Trellis DAG graph created with ``pytrack.matching.mpmatching_utils.create_trellis`` method
        predecessor: dict
            Predecessors' dictionary computed with ``pytrack.matching.mpmatching.viterbi_search`` method
        path_name: str
            Name of the path to be drawn
        """

        fg_matched = folium.FeatureGroup(name=path_name, show=True, control=True)
        self.add_child(fg_matched)

        path_elab = mpmatching_utils.create_path(G, trellis, predecessor)

        edge_attr = dict()
        edge_attr["color"] = "green"
        edge_attr["weight"] = 4
        edge_attr["opacity"] = 1

        edge = [(lat, lng) for lng, lat in LineString([G.nodes[node]["geometry"] for node in path_elab]).coords]
        folium.PolyLine(locations=edge, **edge_attr, ).add_to(fg_matched)

        del self._children[next(k for k in self._children.keys() if k.startswith('layer_control'))]
        self.add_child(folium.LayerControl())
        self._render_reset()


def draw_trellis(T, figsize=None, dpi=None, node_size=500, font_size=8, **kwargs):
    """ Draw a trellis graph

    Parameters
    ----------
    T: networkx.DiGraph
        A directed acyclic graph
    figsize: (float, float), optional, default: [15.0, 12.0]
        Width, height figure size tuple in inches, optional
    dpi: float, optional, default: 300.0
        The resolution of the figure in dots-per-inch
    node_size: scalar or array, optional, default: 500
        Size of nodes.  If an array is specified it must be the same length as nodelist.
    font_size: int, optional, default: 8
        Font size for text labels
    kwargs: keyword arguments, optional, default: no attributes
        See networkx.draw_networkx_nodes(), networkx.draw_networkx_edges(),
        networkx.draw_networkx_labels() and matplotlib.pyplot.figure() for a description of optional keywords.

    Returns
    -------
    trellis_diag: matplotlib.pyplot.Figure
        Graphical illustration of the Trellis diagram used in the Hidden Markov Model process to find the path that best
        matches the actual GPS data
    """

    valid_node_kwargs = signature(nx.draw_networkx_nodes).parameters.keys()
    valid_edge_kwargs = signature(nx.draw_networkx_edges).parameters.keys()
    valid_label_kwargs = signature(nx.draw_networkx_labels).parameters.keys()
    valid_plt_kwargs = signature(plt.figure).parameters.keys()

    valid_nx_kwargs = (valid_node_kwargs | valid_edge_kwargs | valid_label_kwargs)

    # Create a set with all valid keywords across the three functions and
    # remove the arguments of this function (draw_networkx)
    valid_kwargs = (valid_nx_kwargs | valid_plt_kwargs) - {
        "G",
        "figsize",
        "dpi",
        "pos",
        "node_size",
        "font_size",
    }

    if any([k not in valid_kwargs for k in kwargs]):
        invalid_args = ", ".join([k for k in kwargs if k not in valid_kwargs])
        raise ValueError(f"Received invalid argument(s): {invalid_args}")

    nx_kwargs = {k: v for k, v in kwargs.items() if k in valid_nx_kwargs}
    plt_kwargs = {k: v for k, v in kwargs.items() if k in valid_plt_kwargs}

    if figsize is None:
        figsize = (15, 12)
    if dpi is None:
        dpi = 300

    plt.figure(figsize=figsize, dpi=dpi, **plt_kwargs)

    pos = nx.drawing.nx_pydot.graphviz_layout(T, prog='dot', root='start')
    trellis_diag = nx.draw_networkx(T, pos, node_size=node_size, font_size=font_size, **nx_kwargs)

    return trellis_diag
