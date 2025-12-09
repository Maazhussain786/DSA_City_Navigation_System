# traffic_model.py

import math
import random
from typing import Tuple

from config import TRAFFIC_SCHEDULE, MODE_CONFIG


def get_congestion_factor(minutes_from_midnight: float) -> float:
    """
    Given minutes from midnight, return a congestion factor from TRAFFIC_SCHEDULE.
    Lower = more congestion, higher = freer flow. 0.1–1.0 bounded.
    """
    hour = (minutes_from_midnight / 60) % 24
    for start, end, factor in TRAFFIC_SCHEDULE:
        if start <= end:
            if start <= hour < end:
                return factor
        else:
            # schedule that wraps past midnight
            if start <= hour or hour < end:
                return factor
    return 1.0


def get_dynamic_edge_data(edge, mode: str, current_time_min: float) -> Tuple[float, str, bool]:
    """
    Compute time cost and color for a given edge at a particular time and mode.

    Returns:
        (time_cost_minutes, color_hex, is_valid_edge)
    """
    hw_type = edge["type"]
    length = edge["length"]
    config = MODE_CONFIG[mode]

    # some modes can't use certain road types
    if hw_type in config["forbidden"]:
        return float("inf"), "#000000", False

    base_speed = config["speeds"].get(hw_type, 30)
    traffic_level = get_congestion_factor(current_time_min)
    impact = config["traffic_impact"]

    # combine traffic with mode impact
    effective_factor = traffic_level + (1 - traffic_level) * (1 - impact)
    effective_factor = max(0.1, min(1.0, effective_factor))

    # deterministic-ish randomization per edge + time
    random.seed(int(length) + int(current_time_min))
    effective_factor *= random.uniform(0.9, 1.1)
    effective_factor = max(0.1, min(1.0, effective_factor))

    final_speed = base_speed * effective_factor  # km/h
    time_cost = (length / 1000) / final_speed * 60  # minutes

    # color scale for traffic visualization
    color = "#20c997"  # green-ish
    if effective_factor < 0.4:
        color = "#dc3545"  # red
    elif effective_factor < 0.7:
        color = "#fd7e14"  # orange

    return time_cost, color, True
