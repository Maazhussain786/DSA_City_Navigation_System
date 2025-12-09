# route_manager.py

from typing import Any, Dict, List, Optional, Tuple

import osmnx as ox

import graph_utils
from fuel_manager import get_lat_lon, choose_fuel_stop, StopType
from graph_search import run_search


def find_nearest_node(lat: Optional[float], lon: Optional[float]):
    """
    Use osmnx's nearest_nodes to find the closest graph node for given coords.
    """
    if lat is None or lon is None:
        return None
    return ox.distance.nearest_nodes(graph_utils.G, lon, lat)


def calculate_route_manager(
    stops: List[StopType],
    algo: str,
    fuel_params: Optional[Dict[str, Any]],
    mode: str,
    start_time_str: str,
) -> Dict[str, Any]:
    """
    Main entry point used by the Flask API.

    Handles:
      - optional fuel stop insertion
      - alternative route (primary + penalized) for 2-stop trips
      - full multi-stop routing with accumulated time & distance
    """
    h, m = map(int, start_time_str.split(":"))
    current_time_min = h * 60 + m
    metric = "dist" if algo == "dijkstra" else "time"

    # ---- FUEL LOGIC (may modify stops) ----
    stops, fuel_alert, stop_added = choose_fuel_stop(stops, fuel_params)

    # ---- SIMPLE 2-STOP CASE (start -> end) ----
    if len(stops) == 2:
        s_n = find_nearest_node(*get_lat_lon(stops[0]))
        e_n = find_nearest_node(*get_lat_lon(stops[1]))

        res1 = run_search(s_n, e_n, mode, algo, current_time_min, metric=metric)
        if not res1:
            return {"error": "No path found"}

        # build penalty edges for alternative route
        path_edges = [
            (res1["simple_path"][i], res1["simple_path"][i + 1])
            for i in range(len(res1["simple_path"]) - 1)
        ]
        res2 = run_search(
            s_n,
            e_n,
            mode,
            algo,
            current_time_min,
            penalty_edges=path_edges,
            metric=metric,
        )

        routes = [{**res1, "type": "Primary"}]
        if res2 and res2["simple_path"] != res1["simple_path"]:
            routes.append({**res2, "type": "Alternative"})

        return {
            "mode": "alternatives",
            "routes": routes,
            "fuel_alert": fuel_alert,
            "fuel_stop": stop_added,
        }

    # ---- MULTI-STOP CASE ----
    all_segs: List[Dict[str, Any]] = []
    total_time = 0
    total_dist = 0.0

    # normalize stop objects for frontend: always have name/lat/lon
    final_stops_list: List[Dict[str, Any]] = []
    for s in stops:
        if isinstance(s, str):
            lat, lon = get_lat_lon(s)
            final_stops_list.append({"name": s, "lat": lat, "lon": lon})
        else:
            final_stops_list.append(s)

    for i in range(len(stops) - 1):
        coords1 = get_lat_lon(stops[i])
        coords2 = get_lat_lon(stops[i + 1])
        s_n = find_nearest_node(*coords1)
        e_n = find_nearest_node(*coords2)

        res = run_search(s_n, e_n, mode, algo, current_time_min, metric=metric)
        if res:
            all_segs.extend(res["segments"])
            total_time += res["time"]
            total_dist += res["dist"]
            # small dwell time at each intermediate stop
            current_time_min = res["arrival_clock"] + 5

    return {
        "mode": "multistop",
        "segments": all_segs,
        "ordered_stops": final_stops_list,
        "time": total_time,
        "dist": round(total_dist, 1),
        "fuel_alert": fuel_alert,
        "fuel_stop": stop_added,
    }
