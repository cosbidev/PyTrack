import itertools
from decimal import Decimal

import folium
import networkx as nx
import numpy as np
import pandas as pd
from pyproj import Geod
from shapely.geometry import Point, LineString
from sklearn.neighbors import BallTree

from pytrack.graph import distance, plot, utils

geod = Geod(ellps="WGS84")


def get_unique_number(lon, lat):
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


def interpolate_graph(G, dist=1):
    G = G.copy()

    edges_toadd = []
    nodes_toadd = []

    for edge in list(G.edges(data=True)):
        u, v, data = edge
        # oneway = data["oneway"]
        geom = data["geometry"]
        data["length"] = dist

        G.remove_edge(u, v)

        XY = [xy for xy in _interpolate_geom(geom, dist=dist)]

        # generate nodes id
        uv = [(get_unique_number(*u), get_unique_number(*v)) for u, v in zip(XY[:-1], XY[1:])]
        # edges_interp = [LineString([u, v]) for u, v in zip(XY[:-1], XY[1:])]
        data_edges = [(lambda d: d.update({"geometry": LineString([u, v])}) or d)(data.copy()) for u, v in
                      zip(XY[:-1], XY[1:])]
        edges_toadd.extend([(*uv, data) for uv, data in zip(uv, data_edges)])

        nodes_toadd.extend([(get_unique_number(lon, lat),
                             {"x": lon, "y": lat, "geometry": Point(lon, lat)}) for lon, lat in XY])

        """
        # if not oneway:
        #  G.remove_edge(v, u)
        # uv_inv = [(get_unique_number(*u), get_unique_number(*v)) for u, v in zip(XY[:-len(XY):-1], XY[-2::-1])]
        #  uv_inv = [(v, u) for u, v in uv[::-1]]
        # edges_interp_inv = [LineString([u, v]) for u, v in zip(XY[:-len(XY):-1], XY[-2::-1])] 
        #  data_inv_edges = [(lambda d: d.update({"geometry": LineString([u, v])}) or d)(data.copy()) \
        #  for u, v in zip(XY[:-len(XY):-1], XY[-2::-1])]
        #  edges_toadd.extend([(*uv, data) for uv, data in zip(uv_inv, data_inv_edges)])
        """
    G.add_edges_from(edges_toadd)
    G.add_nodes_from(nodes_toadd)

    G.remove_nodes_from(list(nx.isolates(G)))
    G.interpolation = True
    return G


def _interpolate_geom(geom, dist=1):
    # TODO: use geospatial interpolation see: npts method in https://pyproj4.github.io/pyproj/stable/api/geod.html
    num_vert = max(round(geod.geometry_length(geom) / dist), 1)
    for n in range(num_vert + 1):
        point = geom.interpolate(n / num_vert, normalized=True)
        yield point.x, point.y


def interpolate_geom(geom, dist=1):
    if isinstance(geom, LineString):
        return LineString([xy for xy in _interpolate_geom(geom, dist)])


def get_candidates(G, points, interp_dist=1, closest=True, radius=10):
    """
    G: graph
    x: longitude
    y: latitude
    distance: distance of interpolation
    radius: radius of research
    """

    G = G.copy()

    if interp_dist:
        G = interpolate_graph(G, dist=interp_dist)

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


def get_candidates_old(G, points, interp_dist=1, closest=True, radius=10):
    """
    G: graph
    x: longitude
    y: latitude
    distance: distance of interpolation
    radius: radius of research
    """
    geoms = utils.graph_to_gdfs(G, nodes=False).set_index(["u", "v", "key"])[["osmid", "geometry"]]

    uvk_xy = [[uvk, osmid, np.deg2rad(xy)] for uvk, geom, osmid in
              zip(geoms.index, geoms.geometry.values, geoms.osmid.values)
              for xy in _interpolate_geom(geom, dist=interp_dist)]
    index, osmid, xy = zip(*uvk_xy)

    nodes = pd.DataFrame(xy, index=osmid, columns=["x", "y"])[["y", "x"]]

    ball = BallTree(nodes, metric='haversine')

    idxs, dists = ball.query_radius(np.deg2rad(points), radius / distance.EARTH_RADIUS_M, return_distance=True)
    dists = dists * distance.EARTH_RADIUS_M  # radians to meters

    if closest:
        results = dict()
        for i, (point, idx, dist) in enumerate(zip(points, idxs, dists)):
            df = pd.DataFrame({"edge_osmid": list(nodes.index[idx]),
                               "coords": tuple(map(tuple, np.rad2deg(nodes.values[idx]))),
                               "dist": dist})

            df = df.loc[df.groupby('edge_osmid')['dist'].idxmin()].reset_index(drop=True)

            results[i] = {"observation": point,
                          "edge_osmid": list(df["edge_osmid"]),
                          "candidates": list(df["coords"]),
                          "dists": list(df["dist"])}

    else:
        results = {i: {"observation": point,
                       "edge_osmid": list(nodes.index[idx]),
                       "candidates": list(map(tuple, np.rad2deg(nodes.values[idx]))),
                       "dists": list(dist)} for i, (point, idx, dist) in enumerate(zip(points, idxs, dists))}
    return results


def plot_candidates(G, candidates, radius):
    graph_map = plot.plot_graph_folium(G)

    for i, obs in enumerate(candidates.keys()):
        folium.Circle(location=candidates[obs]["observation"], radius=radius, weight=1, color="black", fill=True,
                      fill_opacity=0.2).add_to(graph_map)
        popup = f'{i}-th point \n Latitude: {candidates[obs]["observation"][0]}\n Longitude: ' \
                f'{candidates[obs]["observation"][1]}'
        folium.Circle(location=candidates[obs]["observation"], popup=popup, radius=1, color="black",
                      fill=True, fill_opacity=1).add_to(graph_map)

        # plot candidates
        for cand, label, cand_type in zip(candidates[obs]["candidates"], candidates[obs]["edge_osmid"],
                                          candidates[obs]["candidate_type"]):
            popup = f"coord: {cand} \n edge_osmid: {label}"
            if cand_type:
                folium.Circle(location=cand, popup=popup, radius=2, color="yellow", fill=True, fill_opacity=1).add_to(
                    graph_map)
            else:
                folium.Circle(location=cand, popup=popup, radius=1, color="red", fill=True, fill_opacity=1).add_to(
                    graph_map)

    folium.LatLngPopup().add_to(graph_map)

    return graph_map


def elab_candidate_results(results, predecessor):
    results = results.copy()
    for key in list(results.keys())[:-1]:
        win_cand_idx = int(predecessor[str(key + 1)].split("_")[1])
        results[key]["candidate_type"][win_cand_idx] = True

    win_cand_idx = int(predecessor["target"].split("_")[1])
    results[list(results.keys())[-1]]["candidate_type"][win_cand_idx] = True
    return results


def create_path(G, trellis, predecessor):
    u, v = list(zip(*[(u, v) for v, u in predecessor.items()][2:]))
    path = [(u, v) for u, v in zip(u, u[1:])]

    path_elab = [node for u, v in path for node in nx.shortest_path(G, trellis.nodes[u]["candidate"].node_id,
                                                                    trellis.nodes[v]["candidate"].node_id,
                                                                    weight='length')]
    path_elab = [k for k, g in itertools.groupby(path_elab)]
    return path_elab


def plot_path(G: object, results: object, trellis: object, predecessor: object, radius: object) -> object:
    # TODO: non ricreare altra mappa ma utilizza quella esistente oppure utinizzane una semplificata
    path_map = plot_candidates(G, results, radius)

    path_elab = create_path(G, trellis, predecessor)

    edge_attr = dict()
    edge_attr["color"] = "green"
    edge_attr["weight"] = 4
    edge_attr["opacity"] = 1

    edge = [(lat, lng) for lng, lat in LineString([G.nodes[node]["geometry"] for node in path_elab]).coords]
    folium.PolyLine(locations=edge, **edge_attr, ).add_to(path_map)

    return path_map
