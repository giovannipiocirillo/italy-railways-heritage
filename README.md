# Italian Railway Development Dashboard (1839-1913) 🚂

An interactive visualization and analytics platform tracking the historical development of the Italian railway network. This project provides a geographical and economic analysis, overlaying infrastructure growth with physical constraints (**Terrain Ruggedness**) and agricultural potential (**Wheat Suitability**).

## 🚀 Live Demo
View the live dashboard here:  
👉 **[https://giovannipiocirillo.github.io/italy-railways-heritage/](https://giovannipiocirillo.github.io/italy-railways-heritage/)**

## 🗺️ Key Features

### 1. Interactive Historical Map
* **Time-Travel Slider:** Visualize the network expansion year by year from 1839 to 1913.
* **Data Inspection:** Click on any railway segment to view precise details:
    * **Length:** Precise segment length in meters.
    * **Type:** Primary vs. Secondary lines (based on historical legislation like *Legge Baccarini*).
    * **Gauge:** Standard (1435mm) vs. Narrow (950mm).

### 2. Geographical & Economic Context Layers
Exogenous layers help explain *why* railways were built where they were:
* **🏔️ Terrain Ruggedness Index (TRI):** Based on Nunn & Puga (2012). Highlights engineering challenges (tunnels, viaducts) and the necessity of narrow gauge in mountainous areas.
* **🌾 Wheat Suitability (FAO GAEZ):** Shows historical agricultural potential. Highlights the economic drive to connect the "granaries of Italy" to ports and major cities.

### 3. 📊 Statistics Dashboard
A dedicated Business Intelligence view for quantitative analysis:
* **Territorial Breakdown:** Filter statistics at National, Regional, or Provincial levels.
* **Precise Kilometers:** Track lengths are calculated using exact geometric intersections with administrative borders.
* **Accessibility Analysis:**
    * **Average Territorial Distance:** Measures the mean distance of all municipalities in an area from the nearest station.
    * **Capital Distance:** Tracks how far administrative capitals were from the network over time.

## 🗂️ Data sources

### 🚂 Railways Data
* **Reference:** Ciccarelli, C., & Groote, P. (2017). Railway endowment in Italy's provinces, 1839-1913. *Rivista di storia economica*, (1), 45-88.
* **Dataset:** [Download via ArcGIS](https://www.arcgis.com/home/item.html?id=d4fe94faf2e54518b3f421f19a137d4c)

### 🏔️ Orography (Ruggedness)
* **Reference:** Nunn, N., & Puga, D. (2012). Ruggedness: The blessing of bad geography in Africa. *The Review of Economics and Statistics*, 94(1), 20–36.
* **Dataset:** [Download via diegopuga.org](https://diegopuga.org/data/rugged/)

### 🌾 Agriculture (Wheat)
* **Reference:** FAO & IIASA. Global Agro-Ecological Zones (GAEZ v4).
* **Dataset:** [Data Portal (gaez.fao.org)](https://gaez.fao.org)

### 🏛️ Administrative Boundaries
* **Source:** OpenPolis. Used for precise spatial joins and accessibility metrics.
* **Dataset:** [OpenPolis GeoJSONs](https://github.com/openpolis/geojson-italy)

## 🛠️ Technical Pipeline

The data visualization is the result of a custom **Python** processing pipeline:

1. **Data Processing (Python/Pandas/GeoPandas):**
    * Cleaning and standardizing historical shapefiles.
    * Clipping global raster files (TRI and GAEZ) exactly to the Italian borders using `rasterio`.
    * Performing exact geometric cuts (overlay intersection) to assign track lengths to specific provinces.
    * Calculating distances from ~7,900 municipality centroids to the evolving railway network.
3. **Web Implementation:**
    * **Leaflet.js:** For high-performance rendering of vector datasets and interactive mapping.
    * **Chart.js:** For dynamic rendering of infrastructure growth and accessibility trends.
    * **HTML5/CSS3:** Responsive "Glassmorphism" UI design.

## 📄 License
This project is open for educational and research purposes. Please credit the original data authors (Ciccarelli & Groote, Nunn & Puga, FAO, OpenPolis) when using the datasets derived from this dashboard.
