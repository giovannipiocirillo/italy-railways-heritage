Italian Railway Development Dashboard (1839-1913) 🇮🇹🚂
An interactive visualization dashboard tracking the historical development of the Italian railway network. This project provides a unique geographical and economic analysis, overlaying infrastructure growth with physical constraints (Terrain Ruggedness) and agricultural potential (Wheat Suitability).

🚀 Live Demo
View the live dashboard here:
https://giovannipiocirillo.github.io/italy-railways-heritage/

🗺️ Key Features
1. Interactive Historical Map
Time-Travel Slider: Visualize the network expansion year by year from 1839 (Napoli-Portici) to 1913.

Data Inspection: Click on any railway segment to view precise details:

Type: Primary vs. Secondary lines (Legge Baccarini).

Gauge: Standard (1435mm) vs. Narrow (950mm).

Length: Precise segment length in meters.

2. Advanced Filtering & Control
Dual-Panel Interface:

Left Panel: Narrative controls (Time slider) and detailed legends.

Right Panel: Operational filters to toggle Primary/Secondary lines and Gauge types independently.

Smart Basemaps: Switch seamlessly between a clean Topographic view and Satellite imagery.

3. Geographical & Economic Context Layers
Unlike standard maps, this dashboard offers deep context layers to understand why railways were built where they were:

🏔️ Terrain Ruggedness Index (TRI): Visualizes land unevenness based on Nunn & Puga (2012). Helps explain the engineering challenges (tunnels, viaducts) and the choice of narrow gauge in mountainous areas.

🌾 Wheat Suitability (FAO GAEZ): Shows historical agricultural potential (Low Input/Rain-fed). Highlights the economic drive to connect the "granaries of Italy" (e.g., Puglia, Sicily) to ports and cities.

4. Educational Context
Info Modals: Integrated pop-ups explaining historical context (e.g., the difference between Primary and Secondary networks) and technical concepts (TRI calculation, Gauge implications).

📚 Data Sources & References
This project aggregates and processes data from high-quality economic history research and geographical institutes:

Railways Data:

Ciccarelli, C., & Groote, P. (2017). Railway endowment in Italy's provinces, 1839-1913. Rivista di storia economica. DOI: 10.1410/86763

Orography (Ruggedness):

Nunn, N., & Puga, D. (2012). Ruggedness: The blessing of bad geography in Africa. The Review of Economics and Statistics. DOI: 10.1162/REST_a_00161

Agriculture (Wheat):

FAO & IIASA. Global Agro-Ecological Zones (GAEZ v4). Data Portal. gaez.fao.org

🛠️ Technical Pipeline
The data visualization is the result of a Python processing pipeline:

Python (GeoPandas & Rasterio): Used to clip global raster files (TRI and GAEZ) exactly to the Italian borders and vectorize them into simplified GeoJSONs for web performance.

Leaflet.js: Front-end mapping library.

HTML5/CSS3: Modern "Glassmorphism" UI design.

📄 License
This project is open for educational and research purposes. Please credit the original data authors (Ciccarelli & Groote, Nunn & Puga, FAO) when using the datasets derived from this dashboard.
