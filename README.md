# Italian Railway Development Dashboard (1839-1913) 🇮🇹🚂

An interactive visualization dashboard tracking the historical development of the Italian railway network. This project provides a unique geographical and economic analysis, overlaying infrastructure growth with physical constraints (**Terrain Ruggedness**) and agricultural potential (**Wheat Suitability**).

## 🚀 Live Demo
View the live dashboard here:  
👉 **[https://giovannipiocirillo.github.io/italy-railways-heritage/](https://giovannipiocirillo.github.io/italy-railways-heritage/)**

## 🗺️ Key Features

### 1. Interactive Historical Map
* **Time-Travel Slider:** Visualize the network expansion year by year from 1839 (Napoli-Portici) to 1913.
* **Data Inspection:** Click on any railway segment to view precise details:
    * **Type:** Primary vs. Secondary lines (based on *Legge Baccarini*).
    * **Gauge:** Standard (1435mm) vs. Narrow (950mm).
    * **Length:** Precise segment length in meters.

### 2. Advanced Filtering & Control
* **Dual-Panel Interface:** A modern "Glassmorphism" UI with separate panels for narrative controls and operational filters.
* **Smart Filters:** Toggle specific network types independently:
    * Primary vs. Secondary lines.
    * Standard vs. Narrow gauge tracks.
* **Basemap Switcher:** Toggle seamlessly between a clean Topographic view and Satellite imagery.

### 3. Geographical & Economic Context Layers
Unlike standard maps, this dashboard offers deep context layers to understand *why* railways were built where they were:
* **🏔️ Terrain Ruggedness Index (TRI):** Visualizes land unevenness based on Nunn & Puga (2012). Helps explain engineering challenges (tunnels, viaducts) and the adoption of narrow gauge in mountainous areas.
* **🌾 Wheat Suitability (FAO GAEZ):** Shows historical agricultural potential (Low Input/Rain-fed). Highlights the economic drive to connect the "granaries of Italy" (e.g., Puglia, Sicily) to ports and major cities.

### 4. Educational Context
* **Info Modals:** Integrated pop-ups explaining historical context (e.g., the legislation behind Secondary networks) and technical concepts (TRI calculation, Gauge implications).

## 📚 Data Sources & References

This project aggregates and processes data from high-quality economic history research and geographical institutes:

* **Railways Data:** *Ciccarelli, C., & Groote, P.* (2017). Railway endowment in Italy's provinces, 1839-1913. *Rivista di storia economica*. [DOI: 10.1410/86763](https://doi.org/10.1410/86763)

* **Orography (Ruggedness):** *Nunn, N., & Puga, D.* (2012). Ruggedness: The blessing of bad geography in Africa. *The Review of Economics and Statistics*. [DOI: 10.1162/REST_a_00161](https://doi.org/10.1162/REST_a_00161)

* **Agriculture (Wheat):** *FAO & IIASA.* Global Agro-Ecological Zones (GAEZ v4). Data Portal. [gaez.fao.org](https://gaez.fao.org)

## 🛠️ Technical Pipeline

The data visualization is the result of a custom **Python** processing pipeline:

1.  **Data Processing (Python/Pandas/GeoPandas):** * Cleaning and standardizing historical shapefiles.
    * Clipping global raster files (TRI and GAEZ) exactly to the Italian borders using `rasterio`.
    * Vectorizing rasters into simplified GeoJSONs for optimal web performance.
2.  **Frontend (Leaflet.js):** * Rendering heavy vector datasets efficiently.
    * Custom logic for year-by-year filtering and styling.
3.  **UI/UX (HTML5/CSS3):** * Responsive design with floating glass-panels.

## 📄 License
This project is open for educational and research purposes. Please credit the original data authors (Ciccarelli & Groote, Nunn & Puga, FAO) when using the datasets derived from this dashboard.
