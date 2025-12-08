# app.py

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS

from db_utils import init_db, get_points_by_category
import graph_utils
from route_manager import calculate_route_manager
from traffic_model import get_dynamic_edge_data


app = Flask(__name__)
CORS(app)


def ensure_initialized():
    """Ensure database and graph are loaded."""
    init_db()
    if not graph_utils.adj_list:
        graph_utils.load_graph()


@app.route("/traffic", methods=["GET"])
def traffic():
    ensure_initialized()
    time_str = request.args.get("time", "08:00")
    h, m = map(int, time_str.split(":"))
    mins = h * 60 + m
    traffic_lines = []
    count = 0
    for u in graph_utils.adj_list:
        count += 1
        if count % 3 != 0:
            continue
        for e in graph_utils.adj_list[u]:
            if e["type"] in ["motorway", "trunk", "primary", "secondary"]:
                _, color, _ = get_dynamic_edge_data(e, "car", mins)
                traffic_lines.append(
                    {
                        "coords": [
                            graph_utils.node_coords[u],
                            graph_utils.node_coords[e["neighbor"]],
                        ],
                        "color": color,
                    }
                )
    return jsonify(traffic_lines)


@app.route("/route", methods=["POST"])
def route():
    ensure_initialized()
    data = request.json
    result = calculate_route_manager(
        data.get("stops", []),
        data.get("algo", "astar"),
        data.get("fuel_params"),
        data.get("mode", "car"),
        data.get("time", "08:00"),
    )
    return jsonify(result)


@app.route("/nearest", methods=["POST"])
def nearest():
    ensure_initialized()
    import math

    data = request.json
    lat = float(data["lat"])
    lon = float(data["lon"])
    category = data["category"]

    rows = get_points_by_category(category)
    results = []
    for row in rows:
        plat = row["lat"]
        plon = row["lon"]
        dist = math.sqrt((lat - plat) ** 2 + (lon - plon) ** 2)
        results.append(
            {
                "name": row["name"],
                "lat": plat,
                "lon": plon,
                "dist": dist,
            }
        )

    results.sort(key=lambda x: x["dist"])
    return jsonify(results[:5])


@app.route("/pois", methods=["GET"])
def pois_api():
    """Return all POIs/gas/hotels/restaurants as JSON for frontend."""
    poi_rows = get_points_by_category("poi")
    gas_rows = get_points_by_category("gas")
    hotel_rows = get_points_by_category("hotel")
    rest_rows = get_points_by_category("restaurant")

    combined = {}
    for r in poi_rows + gas_rows + hotel_rows + rest_rows:
        combined[r["name"]] = (r["lat"], r["lon"])

    return jsonify(combined)


@app.route("/")
def home():
    ensure_initialized()
    
    if not graph_utils.adj_list:
        return "<h3>⏳ Downloading Map... Refresh in 30s.</h3>"
    
    # Build pois dict for the template
    poi_rows = get_points_by_category("poi")
    gas_rows = get_points_by_category("gas")
    hotel_rows = get_points_by_category("hotel")
    rest_rows = get_points_by_category("restaurant")
    atm_rows = get_points_by_category("atm")

    pois = {}
    for r in poi_rows + gas_rows + hotel_rows + rest_rows + atm_rows:
        pois[r["name"]] = [r["lat"], r["lon"]]

    return render_template("index.html", pois=pois)


if __name__ == "__main__":
    print("🚀 App running at http://localhost:5000")
    app.run(port=5000, debug=True)
