
Depolyed Link : https://web-production-c8bc6.up.railway.app/

# **Islamabad Smart Navigation System**

*A multi-route, traffic-aware, fuel-optimized navigation engine built with Flask, Leaflet, and OpenStreetMap.*

---

## **Overview**

Islamabad Smart Navigation System is a complete navigation engine that provides:

* **Shortest distance routing (Dijkstra)**
* **Fastest time routing (A*) with dynamic traffic simulation**
* **Multi-stop route planning**
* **Live traffic heat overlay (time-dependent)**
* **Fuel-aware routing (auto-insert nearest gas station when fuel is low)**
* **Nearest Points-of-Interest finder (Restaurants, ATMs, Hotels, Gas Stations)**
* **Map click support** → set **Start**, **End**, and **Stops** by clicking on the map
* Clean & modern **Leaflet.js UI** with Bootstrap styling

This project is designed to simulate a **real navigation system** similar to Google Maps but fully customized for Islamabad.

---

## **Tech Stack**

| Component    | Technology                       |
| ------------ | -------------------------------- |
| Backend      | Flask, Python                    |
| Graph Engine | OSMnx, Dijkstra, A*              |
| Frontend     | Leaflet.js, Bootstrap 5          |
| Database     | SQLite (POIs), Pickle (Graph)    |
| Traffic      | Time-based congestion simulation |
| Deployment   | Render / Heroku supported        |

---

## 📁 **Project Structure**

```
City-Navigation-System/
│
├── app.py                    # Main Flask app
├── route_manager.py          # Multi-stop routing + fuel logic
├── graph_search.py           # Dijkstra / A* implementation
├── traffic_model.py          # Dynamic congestion + traffic colors
├── fuel_manager.py           # Fuel range + gas-station insertion logic
├── graph_utils.py            # Graph loading, adjacency lists, helpers
├── db_utils.py               # SQLite POI database utilities
│
├── data_points.py            # Static POI / gas-station definitions
├── config.py                 # Speeds, traffic schedule, mode settings
├── points.db                 # SQLite database for POIs
├── islamabad_full_v9.pkl     # Preprocessed OSM Graph (adj list)
│
├── templates/
│   └── index.html            # Complete frontend UI (Leaflet)
│
├── cache/                    # Route/traffic cache
└── requirements.txt          # Python dependencies
```

---

##  **Key Features (In Depth)**

### 🔹 **1. Two Routing Algorithms**

* **Dijkstra (Shortest Distance)**
  Pure distance-based, no traffic.

* **A* (Fastest Time)**
  Uses speed limits + dynamic congestion to compute fastest route.

---

### 🔹 **2. Multi-Stop Route Planning**

Users can:

* Add unlimited intermediate stops
* Pick stops via datalist or clicking directly on the map
* Route is calculated segment-by-segment with updated arrival time

---

### 🔹 **3. Dynamic Traffic Heatmap**

Traffic changes throughout the day:

* Morning rush
* Evening congestion
* Late-night clear roads

Edges are colored:

* **🟥 Red** = Heavy congestion
* **🟧 Orange** = Medium congestion
* **🟩 Green** = Free flow

Route calculations also use these dynamic traffic multipliers.

---

### 🔹 **4. Fuel-Aware Routing**

If estimated travel distance exceeds available fuel:

* Nearest gas station is automatically inserted into the route
* User is notified with a **"Low Fuel! Station Added"** warning

---

### 🔹 **5. Nearest POI Search**

From the current location, the system can find:

* Restaurants
* ATMs 
* Hotels 
* Gas Stations 

Uses Haversine distance + database query.

---

### 🔹 **6. Modern UI with Leaflet**

* Map markers for start/end/stops
* Custom icons for gas stations
* Click map to set new points
* Sidebar for routing options and trip summary
* Beautiful responsive UI

---

## **Installation & Setup**

### **1. Clone the Repository**

```bash
git clone https://github.com/<your-username>/City-Navigation-system-.git
cd City-Navigation-system-
```

---

### **2. Install Dependencies**

```bash
pip install -r requirements.txt
```

---

### **3. Run the Server**

```bash
python app.py
```

---

### **4. Open in Browser**

Go to:

```
http://localhost:5000
```

You will now see the full navigation UI with maps, controls, and routing.

---

## **How Routing Works Internally**

### **Graph Engine**

* Graph loaded from processed **OSMnx graph → pickle file**
* Converted to adjacency list for fast routing

### **Edge Cost Computation**

For A*:

```
edge_time = distance / (speed_limit × traffic_factor)
```

For Dijkstra:

```
edge_cost = distance
```

### **Traffic Factor**

Time-based multiplier defined in `config.py`.

### **Fuel Logic**

```python
range = avg_km_per_liter × current_liters
if total_estimated_distance > range:
    insert_nearest_gas_station()
```
## 🤝 Contributors

* **Muhammad Bilal Atif**
* **Maaz Hussain**
* **Muhammad Abdul Daym**
* **Muhammad Hamza Iqbal**
---

## 📜 License

This project is open-source for academic and research purposes.

---

## ⭐ Support the Project

If this helps your assignment or project:

🔹 Star the repository ❤️
🔹 Share with classmates
🔹 Contribute improvements

Just tell me!
