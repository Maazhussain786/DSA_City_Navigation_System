# graph_search.py

import heapq
import math
from typing import Any, Dict, List, Tuple, Optional

import graph_utils
from traffic_model import get_dynamic_edge_data


class PriorityQueue:
    """Simple min-heap priority queue used by A* / Dijkstra."""

    def __init__(self):
        self.heap: List[Tuple[float, Any]] = []

    def push(self, item: Any, priority: float) -> None:
        heapq.heappush(self.heap, (priority, item))

    def pop(self) -> Any:
        return heapq.heappop(self.heap)[1]

    def empty(self) -> bool:
        return len(self.heap) == 0


def heuristic(u, v, mode: str, metric: str = "time") -> float:
    """
    Heuristic for A* search.

    - If metric == 'time', uses a simple distance / max speed estimate.
    - If metric == 'dist', returns straight-line distance in meters.
    """
    y1, x1 = graph_utils.node_coords[u]
    y2, x2 = graph_utils.node_coords[v]
    dist_km = math.sqrt((y1 - y2) ** 2 + (x1 - x2) ** 2) * 111  # rough

    if metric == "dist":
        return dist_km * 1000.0  # meters

    # optimistic time (assuming 100km/h car, 60km/h bike)
    max_speed = 100 if mode == "car" else 60
    return (dist_km / max_speed) * 60.0  # minutes


def run_search(
    start,
    end,
    mode: str,
    algo: str,
    start_time_min: float,
    penalty_edges: Optional[List[Tuple[int, int]]] = None,
    metric: str = "time",
):
    """
    Run A* or Dijkstra search between two nodes.

    - algo: 'astar' or 'dijkstra'
    - metric: 'time' (minutes) or 'dist' (meters)
    """
    if penalty_edges is None:
        penalty_edges = []

    pq = PriorityQueue()
    pq.push(start, 0.0)

    came_from: Dict[Any, Optional[Any]] = {start: None}
    cost_so_far: Dict[Any, float] = {start: 0.0}
    time_so_far: Dict[Any, float] = {start: 0.0}

    while not pq.empty():
        current = pq.pop()
        if current == end:
            break

        current_clock = start_time_min + time_so_far.get(current, 0.0)

        if current in graph_utils.adj_list:
            for edge in graph_utils.adj_list[current]:
                neighbor = edge["neighbor"]
                edge_time, _, valid = get_dynamic_edge_data(
                    edge, mode, current_clock
                )
                if not valid:
                    continue

                edge_cost = edge["length"] if metric == "dist" else edge_time
                if (current, neighbor) in penalty_edges:
                    edge_cost *= 5.0  # penalize edges from primary path

                new_cost = cost_so_far[current] + edge_cost
                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    time_so_far[neighbor] = time_so_far[current] + edge_time

                    priority = new_cost
                    if algo == "astar":
                        priority += heuristic(neighbor, end, mode, metric)
                    pq.push(neighbor, priority)
                    came_from[neighbor] = current

    return reconstruct_path(came_from, start, end, mode, start_time_min)


def reconstruct_path(
    came_from: Dict[Any, Optional[Any]],
    start,
    end,
    mode: str,
    start_time: float,
):
    """
    Backtrack from end to start and build segment list, total time & distance.
    """
    if end not in came_from:
        return None

    # rebuild node list from end -> start
    nodes: List[Any] = []
    curr = end
    while curr is not None:
        nodes.append(curr)
        curr = came_from[curr]
    nodes.reverse()

    segments: List[Dict[str, Any]] = []
    total_dist = 0.0  # meters
    total_time = 0.0  # minutes
    curr_clock = start_time

    for i in range(len(nodes) - 1):
        u, v = nodes[i], nodes[i + 1]
        for e in graph_utils.adj_list[u]:
            if e["neighbor"] == v:
                time_cost, color, _ = get_dynamic_edge_data(
                    e, mode, curr_clock
                )
                total_dist += e["length"]
                total_time += time_cost
                curr_clock += time_cost

                segments.append(
                    {
                        "coords": [
                            graph_utils.node_coords[u],
                            graph_utils.node_coords[v],
                        ],
                        "color": color,
                    }
                )
                break

    return {
        "segments": segments,
        "simple_path": nodes,
        "time": math.ceil(total_time),
        "dist": round(total_dist / 1000.0, 1),  # km
        "arrival_clock": curr_clock,
    }
