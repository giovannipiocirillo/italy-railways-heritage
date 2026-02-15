import geopandas as gpd
import rasterio
from rasterio import features
from shapely.geometry import shape
import json
import numpy as np

# --- INPUT FILE CONFIGURATION ---
FILE_SHP_RAIL = "railways-shapefile/ItalyRailways.shp"
FILE_TRI_CLIPPED = "ruggedness/italy_ruggedness_clipped.tif"
FILE_WHEAT_CLIPPED = "wheat-suitability/italy_wheat_clipped.tif"

# --- OUTPUT FILE CONFIGURATION ---
OUTPUT_HTML = "index.html"
OUTPUT_JS = "db_railways_trunks.js"

def round_floats(o):
    if isinstance(o, float): return round(o, 4)
    if isinstance(o, dict): return {k: round_floats(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)): return [round_floats(x) for x in o]
    return o

def vectorize_raster(tif_path, band_id=1, threshold_filter=None, classify_func=None):
    features_list = []
    try:
        print(f"   Processing {tif_path}...")
        
        # Data variables
        data = None
        transform = None
        nodata = None
        source_crs = None

        # 1. READING RASTER FILE
        with rasterio.open(tif_path) as src:
            # Reading CRS (Coordinate Reference System) from file
            source_crs = src.crs
            
            # If file has not CRS, set default WGS84
            if source_crs is None:
                source_crs = "EPSG:4326"

            data = src.read(band_id)
            transform = src.transform
            nodata = src.nodata

        # 2. PROCESSING RASTER FILE
        
        if nodata is not None:
            mask = data != nodata
        else:
            mask = data > -9999 

        if threshold_filter:
            mask = mask & (data >= threshold_filter)

        # Creating shapes
        shapes_gen = features.shapes(data, mask=mask, transform=transform)

        class_geoms = {} 
        for geom, val in shapes_gen:
            val = float(val)
            cat = classify_func(val)
            if not cat: continue 
            
            if cat not in class_geoms: class_geoms[cat] = []
            class_geoms[cat].append(shape(geom))

        # Creating GeoDataFrame
        for cat, geoms in class_geoms.items():
            if not geoms: continue
            
            gdf = gpd.GeoDataFrame({'geometry': geoms}, crs=source_crs)
            
            if gdf.crs is not None and str(gdf.crs).upper() != "EPSG:4326":
                try:
                    gdf = gdf.to_crs("EPSG:4326")
                except:
                    pass

            dissolved = gdf.dissolve().simplify(0.0001)
            
            geometries_to_save = dissolved.geometry if hasattr(dissolved, 'geometry') else dissolved

            for geom in geometries_to_save:
                features_list.append({
                    "type": "Feature",
                    "geometry": geom.__geo_interface__,
                    "properties": {"class": cat}
                })
        return features_list

    except Exception as e:
        print(f"❌ Error during {tif_path} vectorizing: {e}")
        return []

# --- 1. DATA PROCESSING ---

print("[1/3] Vectorizing RUGGEDNESS...")
def class_tri(val):
    if val > 350000: return 4   # Estremo
    if val > 150000: return 3   # Alto
    if val >= 80000: return 2   # Medio
    return 0 

rugged_data = vectorize_raster(FILE_TRI_CLIPPED, threshold_filter=80000, classify_func=class_tri)

print("[2/3] Vectorizing WHEAT SUITABILITY...")
def class_wheat(val):
    if val >= 7000: return 3   # Alta
    if val >= 3500: return 2   # Media
    if val >= 1000: return 1   # Bassa
    return 0

wheat_data = vectorize_raster(FILE_WHEAT_CLIPPED, threshold_filter=1000, classify_func=class_wheat)

# --- 2. PROCESSING RAILWAYS ---
print("[3/3] Processing RAILWAYS...")

rail_raw = gpd.read_file(FILE_SHP_RAIL)

rail_wgs84 = rail_raw.to_crs(epsg=4326)
print("   ✅ Railways converted to WGS84.")

#Filter only built railways
rail = rail_wgs84[rail_wgs84['YearConstr'] > 0].copy()

rail_json = json.loads(rail.to_json())

# --- 3. WRITING JS ---
print(f"WRITING {OUTPUT_JS}...")
with open(OUTPUT_JS, "w", encoding="utf-8") as f:
    f.write(f"const ruggedData = {json.dumps(round_floats(rugged_data))};\n")
    f.write(f"const wheatData = {json.dumps(round_floats(wheat_data))};\n")
    f.write(f"const railData = {json.dumps(round_floats(rail_json))};\n")

# --- 4. WRITING HTML ---
print(f"WRITING {OUTPUT_HTML}...")
html_content = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <title>Mappa - Sviluppo Ferroviario Italiano (1839-1913)</title>
    <link rel="icon" type="image/png" href="favicon.png">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
    <script src="db_railways_trunks.js"></script>

    <style>
        body { margin:0; padding:0; font-family: 'Roboto', sans-serif; overflow: hidden; background: #f0f0f0; }
        #map { height: 100vh; width: 100vw; }
        
        /* STILE COMUNE PANNELLI */
        .glass-panel {
            background: rgba(255, 255, 255, 0.95); 
            backdrop-filter: blur(10px);
            border-radius: 12px; 
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15); 
            border: 1px solid rgba(255, 255, 255, 0.8);
            font-family: 'Roboto', sans-serif;
            z-index: 1000;
            padding: 15px 20px;
            transition: all 0.3s ease;
        }

        /* PANNELLO SINISTRO (Slider + Legenda) */
        .left-panel {
            position: absolute; 
            bottom: 40px; 
            left: 20px; 
            width: 280px;
            max-height: 85vh; 
            overflow-y: auto;
        }

        /* PANNELLO DESTRO (Filtri + Layer) */
        .right-panel {
            position: absolute;
            top: 20px;
            right: 20px;
            width: 240px;
            max-height: 90vh;
            overflow-y: auto;
        }

        /* Scorrimento personalizzato */
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background-color: #ccc; border-radius: 20px; }

        h2 { margin: 0 0 10px 0; font-weight: 700; font-size: 22px; color: #2c3e50; text-align: center; border-bottom: 2px solid #f0f0f0; padding-bottom: 10px; }
        h4 { margin: 15px 0 8px 0; font-size: 11px; color: #7f8c8d; text-transform: uppercase; letter-spacing: 1px; font-weight: 700; display: flex; align-items: center; justify-content: space-between; }
        
        /* SLIDER ANNO */
        .year-display { text-align: center; font-size: 28px; font-weight: 300; color: #2980b9; margin: 5px 0; display: block; }
        #year-slider { -webkit-appearance: none; width: 100%; height: 6px; background: #e0e0e0; border-radius: 5px; outline: none; margin: 10px 0; }
        #year-slider::-webkit-slider-thumb { -webkit-appearance: none; width: 20px; height: 20px; border-radius: 50%; background: #2980b9; cursor: pointer; border: 3px solid white; box-shadow: 0 2px 6px rgba(0,0,0,0.3); transition: transform 0.1s; }
        #year-slider::-webkit-slider-thumb:hover { transform: scale(1.1); }

        /* SWITCH & CHECKBOXES */
        .switch-container { display: flex; align-items: center; margin-bottom: 5px; font-size: 13px; color: #555; cursor: pointer; }
        .switch { position: relative; display: inline-block; width: 32px; height: 18px; margin-right: 10px; flex-shrink: 0; }
        .switch input { opacity: 0; width: 0; height: 0; }
        .slider-toggle { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #ccc; transition: .4s; border-radius: 34px; }
        .slider-toggle:before { position: absolute; content: ""; height: 12px; width: 12px; left: 3px; bottom: 3px; background-color: white; transition: .4s; border-radius: 50%; }
        input:checked + .slider-toggle { background-color: #3498db; }
        input:checked + .slider-toggle:before { transform: translateX(14px); }

        .checkbox-row { display: flex; align-items: center; margin-bottom: 8px; font-size: 13px; color: #444; }
        .checkbox-row input[type="checkbox"], .checkbox-row input[type="radio"] { accent-color: #2980b9; margin-right: 10px; cursor: pointer; transform: scale(1.1); }

        /* LEGENDA */
        .legend-item { display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px; font-size: 12px; color: #555; }
        .legend-left { display: flex; align-items: center; }
        .box { width: 14px; height: 14px; margin-right: 8px; border-radius: 3px; }
        
        /* PULSANTI INFO */
        .info-btn { background: #3498db; color: #fff; width: 16px; height: 16px; border-radius: 50%; text-align: center; line-height: 16px; font-size: 10px; font-weight: bold; cursor: pointer; transition: 0.2s; }
        .info-btn:hover { transform: scale(1.1); background: #2980b9; }

        /* FOOTER */
        .map-footer {
            position: absolute; bottom: 15px; left: 50%; transform: translateX(-50%);
            z-index: 900; background: rgba(255, 255, 255, 0.8); backdrop-filter: blur(5px);
            padding: 5px 15px; border-radius: 20px; font-size: 10px; color: #666;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1); border: 1px solid rgba(255,255,255,0.4);
            white-space: nowrap; pointer-events: auto;
        }
        .map-footer a { color: #2980b9; text-decoration: none; font-weight: 500; }

        .link-btn {
            position: absolute;
            bottom: 40px; /* Allineato al pannello sinistro */
            right: 20px; 
            z-index: 1000;
            background: #2c3e50;
            color: #fff;
            text-decoration: none;
            padding: 12px 20px;
            border-radius: 30px;
            font-size: 14px;
            font-weight: 500;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 8px;
            border: 1px solid rgba(255,255,255,0.2);
        }
        .link-btn:hover {
            background: #34495e;
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.25);
        }

        /* MODAL */
        .modal-overlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.5); z-index: 2000; backdrop-filter: blur(3px); }
        .modal-content { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; border-radius: 12px; width: 700px; box-shadow: 0 10px 40px rgba(0,0,0,0.3); padding: 25px; animation: fadeIn 0.3s ease-out; }
        .close-btn { position: absolute; top: 10px; right: 15px; font-size: 24px; font-weight: bold; color: #aaa; cursor: pointer; }
        @keyframes fadeIn { from { opacity: 0; transform: translate(-50%, -60%); } to { opacity: 1; transform: translate(-50%, -50%); } }
    </style>
</head>
<body>
    <div id="map"></div>
    
    <div id="left-panel" class="glass-panel left-panel">
        <h2>Sviluppo Ferroviario</h2>
        
        <span id="year-label" class="year-display">1839</span>
        <input type="range" min="1839" max="1913" value="1839" id="year-slider">
        
        <div class="switch-container">
            <label class="switch">
                <input type="checkbox" id="single-year-mode" onchange="update()">
                <span class="slider-toggle"></span>
            </label>
            <span>Solo tratti aperti nell'anno selezionato</span>
        </div>

        <hr style="border: 0; border-top: 1px solid #eee; margin: 15px 0;">

        <h4>Tipologia Linee <div class="info-btn" onclick="openModal('rail-type')">?</div></h4>
        <div class="legend-item"><div class="legend-left"><div class="box" style="background:#e74c3c; height:3px"></div> Primaria</div></div>
        <div class="legend-item"><div class="legend-left"><div class="box" style="background:#1c39bb; height:3px"></div> Secondaria</div></div>

        <h4>Scartamento <div class="info-btn" onclick="openModal('gauge')">?</div></h4>
        <div class="legend-item">
            <div class="legend-left"><div class="box" style="background:#444; height:3px"></div> Normale (1435mm)</div>
        </div>
        <div class="legend-item">
            <div class="legend-left"><div class="box" style="background:transparent; border-bottom: 2px dashed #444; height:0px; width:14px"></div> Ridotto (950mm)</div>
        </div>

        <h4>RUGGEDNESS (TRI) <div class="info-btn" onclick="openModal('tri')">?</div></h4>
        <div class="legend-item"><div class="legend-left"><div class="box" style="background:transparent; border:1px dashed #aaa"></div> Bassa (< 0.8)</div></div>
        <div class="legend-item"><div class="legend-left"><div class="box" style="background:#f1c40f"></div> Media (0.8 - 1.5)</div></div>
        <div class="legend-item"><div class="legend-left"><div class="box" style="background:#e67e22"></div> Alta (1.5 - 3.5)</div></div>
        <div class="legend-item"><div class="legend-left"><div class="box" style="background:#2c3e50"></div> Estrema (> 3.5)</div></div>

        <h4>WHEAT SUITABILITY <div class="info-btn" onclick="openModal('wheat')">?</div></h4>
        <div class="legend-item"><div class="legend-left"><div class="box" style="background:#e8f5e9; border:1px solid #ccc"></div> Bassa</div></div>
        <div class="legend-item"><div class="legend-left"><div class="box" style="background:#66bb6a"></div> Media</div></div>
        <div class="legend-item"><div class="legend-left"><div class="box" style="background:#1b5e20"></div> Alta</div></div>
    </div>

    <div id="right-panel" class="glass-panel right-panel">
        
        <h4 style="margin-top:0">Sfondo Mappa</h4>
        <div class="checkbox-row">
            <input type="radio" name="basemap" id="base-light" checked onchange="updateBasemap()">
            <label for="base-light">Mappa Chiara</label>
        </div>
        <div class="checkbox-row">
            <input type="radio" name="basemap" id="base-sat" onchange="updateBasemap()">
            <label for="base-sat">Satellite</label>
        </div>

        <hr style="border: 0; border-top: 1px solid #eee; margin: 10px 0;">

        <h4>Livelli</h4>
        <div class="checkbox-row">
            <input type="checkbox" id="layer-rugged" onchange="updateLayers()">
            <label for="layer-rugged">Ruggedness (TRI)</label>
        </div>
        <div class="checkbox-row">
            <input type="checkbox" id="layer-wheat" onchange="updateLayers()">
            <label for="layer-wheat">Wheat Suitability</label>
        </div>
        <div class="checkbox-row">
            <input type="checkbox" id="layer-rail" checked onchange="updateLayers()">
            <label for="layer-rail">Rete Ferroviaria</label>
        </div>

        <hr style="border: 0; border-top: 1px solid #eee; margin: 10px 0;">

        <h4>Filtri Ferroviari</h4>
        <div class="checkbox-row">
            <input type="checkbox" id="filter-primary" checked onchange="update()">
            <label for="filter-primary">Primarie</label>
        </div>
        <div class="checkbox-row">
            <input type="checkbox" id="filter-secondary" checked onchange="update()">
            <label for="filter-secondary">Secondarie</label>
        </div>
        <div style="height: 5px;"></div>
        <div class="checkbox-row">
            <input type="checkbox" id="filter-std" checked onchange="update()">
            <label for="filter-std">Scartamento Normale</label>
        </div>
        <div class="checkbox-row">
            <input type="checkbox" id="filter-narrow" checked onchange="update()">
            <label for="filter-narrow">Scartamento Ridotto</label>
        </div>
    </div>

    <a href="railways_stats.html" target="_blank" class="link-btn">
        📊 Vai alle Statistiche
    </a>

    <div class="map-footer">
        A cura di <a href="https://www.linkedin.com/in/giovanni-pio-cirillo" target="_blank">Giovanni Pio Cirillo</a> | 
        Dati: <a href="https://www.rivisteweb.it/doi/10.1410/86763" target="_blank">Ciccarelli & Groote (2017)</a>, <a href="https://direct.mit.edu/rest/article-abstract/94/1/20/57988/Ruggedness-The-Blessing-of-Bad-Geography-in-Africa?redirectedFrom=fulltext" target="_blank">Nunn & Puga (2012)</a>, <a href="https://gaez.fao.org" target="blank">FAO GAEZ v4</a>, <a href="https://github.com/openpolis/geojson-italy" target="blank">OpenPolis</a>
    </div>

    <div id="infoModal" class="modal-overlay" onclick="closeModal()">
        <div class="modal-content" onclick="event.stopPropagation()">
            <span class="close-btn" onclick="closeModal()">&times;</span>
            <div style="padding: 20px; background: #fff; border-radius: 12px;">
                <div style="padding: 20px; background: rgba(236, 240, 241, 0.5); border-radius: 8px; font-size: 15px; line-height: 1.6; color: #444; border-left: 4px solid #3498db;">
                    <strong id="modal-title" style="display:block; margin-bottom: 5px; color: #2c3e50;"></strong>
                    <div id="modal-body"></div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
        // Evita click through
        const pLeft = document.getElementById('left-panel');
        const pRight = document.getElementById('right-panel');
        [pLeft, pRight].forEach(p => {
            L.DomEvent.disableClickPropagation(p);
            L.DomEvent.disableScrollPropagation(p);
        });

        // --- GESTIONE MODAL ---
        function openModal(type) { 
            const title = document.getElementById('modal-title');
            const body = document.getElementById('modal-body');
            
            if(type === 'tri') {
                title.innerText = "ℹ️ Terrain Ruggedness Index (TRI)";
                body.innerHTML = `
                    <p style="margin-bottom:10px;">
                        Il <b>TRI (Terrain Ruggedness Index)</b> misura l'eterogeneità del terreno calcolando la somma delle differenze di elevazione (in millimetri, per semplicità trasformati in metri) tra una cella centrale e le sue 8 celle adiacenti.
                    </p>
                    <hr style="border:0; border-top:1px solid #eee; margin:10px 0;">
                    <strong style="color:#2c3e50">Impatto sulle Ferrovie:</strong>
                    <p style="font-size:13px; margin-top:5px;">
                        Negli anni di analisi, la tecnologia a vapore tollerava pendenze minime. Un TRI elevato, e dunque un terreno più impervio, comportava:
                    </p>
                    <ul style="padding-left:20px; font-size:13px;">
                        <li>Costi di costruzione esponenziali (tunnel, viadotti, scavi).</li>
                        <li>Tracciati tortuosi per evitare le zone più aspre (aumento dei tempi di percorrenza).</li>
                        <li>Convenienza dei binari a scartamento ridotto per impostare curve più strette.</li>
                        <li>Necessità di locomotive più potenti.</li>
                    </ul>
                    <hr style="border:0; border-top:1px solid #eee; margin:10px 0;">
                    <strong style="color:#2c3e50">Legenda Classi (in metri):</strong>
                    <ul style="padding-left:20px; font-size:13px; list-style:none; margin-top:5px;">
                        <li>⚪ <b>< 80 (Bassa):</b> Pianura/Collina dolce.</li>
                        <li>🟡 <b>80 - 150 (Media):</b> Terreno accidentato.</li>
                        <li>🟠 <b>150 - 350 (Alta):</b> Montagna.</li>
                        <li>⚫ <b>> 350 (Estrema):</b> Vette.</li>
                    </ul>
                    <div style="font-size:11px; color:#7f8c8d; margin-top:15px; border-top:1px solid #ddd; padding-top:5px;">
                        <b>Fonte:</b> Nunn & Puga (2012), "Ruggedness: The Blessing of Bad Geography in Africa".
                    </div>`;
            } else if (type === 'wheat') {
                title.innerText = "ℹ️ Wheat Suitability (FAO GAEZ v4)";
                body.innerHTML = `
                    <p style="margin-bottom:10px;">
                        Indice di idoneità agro-climatica per la coltivazione del <b>grano</b> (frumento), calcolato su base 1961-1990.
                    </p>
                    <hr style="border:0; border-top:1px solid #eee; margin:10px 0;">
                    <strong style="color:#2c3e50">Parametri Storici:</strong>
                    <ul style="padding-left:20px; font-size:13px; margin-top:5px;">
                        <li><b>Low Input:</b> Simula l'agricoltura pre-industriale (lavoro manuale, nessun fertilizzante chimico).</li>
                        <li><b>Rain-fed:</b> Coltivazione dipendente dalle piogge (senza irrigazione artificiale moderna).</li>
                    </ul>
                    <strong style="color:#2c3e50">Rilevanza Economica:</strong>
                    <p style="font-size:13px; margin-top:5px;">
                    Nel XIX secolo l’Italia era un Paese prevalentemente agricolo e il grano rappresentava la coltivazione più diffusa e strategica per l’alimentazione della popolazione. Le zone ad alta idoneità (verde scuro) corrispondono ai principali distretti cerealicoli – i “granai d’Italia”, come il Tavoliere delle Puglie o la Sicilia interna – che necessitavano prioritariamente di collegamenti ferroviari verso i porti e i centri urbani per l’integrazione nei mercati nazionali ed esteri.                    </p>
                    <div style="font-size:11px; color:#7f8c8d; margin-top:15px; border-top:1px solid #ddd; padding-top:5px;">
                        <b>Fonte:</b> FAO Global Agro-Ecological Zones (GAEZ v4).
                    </div>`;
            } else if (type === 'rail-type') {
                title.innerText = "ℹ️ Linee Primarie e Secondarie";
                body.innerHTML = `
                    <p style="margin-bottom:10px;">
                        La distinzione deriva principalmente dalla <a href="https://www.normattiva.it/atto/caricaDettaglioAtto?atto.dataPubblicazioneGazzetta=1879-07-30&atto.codiceRedazionale=079U5002&tipoDettaglio=originario&qId=" target="_blak"><b>Legge Baccarini (L. 5002/1879)</b></a>, che definì le linee "complementari" (o secondarie) necessarie per completare la rete nazionale principale già esistente.
                    </p>
                    <hr style="border:0; border-top:1px solid #eee; margin:10px 0;">
                    <ul style="padding-left:20px; font-size:13px; margin-top:5px;">
                        <li style="margin-bottom:8px;"><b>Linee Primarie (Rosso):</b> La grande dorsale nazionale. Costruite dallo Stato o grandi concessionarie per collegare le metropoli e i confini.</li>
                        <li><b>Linee Secondarie (Blu):</b> Linee di interesse locale, nate per rompere l'isolamento dei centri rurali minori e collegarli alla rete principale.</li>
                    </ul>`;
            } else if (type === 'gauge') {
                title.innerText = "ℹ️ Scartamento normale e Scartamento ridotto";
                body.innerHTML = `
                    <p style="margin-bottom:10px;">
                        Lo scartamento è la distanza tra le facce interne delle due rotaie.
                    </p>
                    <hr style="border:0; border-top:1px solid #eee; margin:10px 0;">
                    <ul style="padding-left:20px; font-size:13px; margin-top:5px;">
                        <li style="margin-bottom:8px;"><b>Normale (1435mm):</b> Lo standard internazionale ("Stephenson"). Garantisce maggiore stabilità, velocità e capacità di carico, ma richiede curve ad ampio raggio.</li>
                        <li><b>Ridotto (950mm):</b> Lo standard italiano per le linee secondarie. Permette curve molto strette, consentendo al treno di "arrampicarsi" sulle montagne (alta Ruggedness) riducendo drasticamente i costi di costruzione della linea.</li>
                    </ul>`;
            }
            document.getElementById('infoModal').style.display = 'block'; 
        }
        function closeModal() { document.getElementById('infoModal').style.display = 'none'; }
        document.addEventListener('keydown', (e) => { if (e.key === "Escape") closeModal(); });

        // --- MAPPA ---
        const map = L.map('map', {zoomControl: false}).setView([42.0, 12.5], 6);
        L.control.zoom({ position: 'topleft' }).addTo(map); 
        map.createPane('railwayPane');
        map.getPane('railwayPane').style.zIndex = 650;

        const satelliteMap = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', { attribution: 'Esri' });
        const lightMap = L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', { attribution: 'CartoDB' }).addTo(map);

        // --- LAYER BACKGROUND ---
        const ruggedLayer = L.geoJson(ruggedData, {
            style: (f) => ({ 
                fillColor: f.properties.class === 4 ? '#2c3e50' : f.properties.class === 3 ? '#e67e22' : '#f1c40f', 
                weight: 0, fillOpacity: f.properties.class === 4 ? 0.7 : 0.5 
            }), interactive: false
        });

        const wheatLayer = L.geoJson(wheatData, {
            style: (f) => ({ 
                fillColor: f.properties.class === 3 ? '#1b5e20' : f.properties.class === 2 ? '#66bb6a' : '#e8f5e9', 
                weight: 0, fillOpacity: 0.6 
            }), interactive: false
        });

        let railLayer = L.layerGroup();

        // --- GESTIONE LAYER MANUALI (Nuove Funzioni) ---
        function updateBasemap() {
            const isSat = document.getElementById('base-sat').checked;
            if (isSat) {
                map.addLayer(satelliteMap);
                map.removeLayer(lightMap);
            } else {
                map.addLayer(lightMap);
                map.removeLayer(satelliteMap);
            }
        }

        function updateLayers() {
            // Ruggedness
            if (document.getElementById('layer-rugged').checked) map.addLayer(ruggedLayer);
            else map.removeLayer(ruggedLayer);

            // Wheat
            if (document.getElementById('layer-wheat').checked) map.addLayer(wheatLayer);
            else map.removeLayer(wheatLayer);

            // Rail
            if (document.getElementById('layer-rail').checked) map.addLayer(railLayer);
            else map.removeLayer(railLayer);
        }

        // --- LOGICA FERROVIE ---
        function update() {
            const year = parseInt(document.getElementById('year-slider').value);
            const isSingleYear = document.getElementById('single-year-mode').checked;
            
            const showPrimary = document.getElementById('filter-primary').checked;
            const showSecondary = document.getElementById('filter-secondary').checked;
            const showStd = document.getElementById('filter-std').checked;
            const showNarrow = document.getElementById('filter-narrow').checked;

            document.getElementById('year-label').innerText = year;
            railLayer.clearLayers();
            
            L.geoJson(railData, {
                pane: 'railwayPane',
                filter: (f) => {
                    const p = f.properties;
                    // Filtro Tempo
                    const timeOk = isSingleYear ? p.YearConstr == year : p.YearConstr <= year;
                    if (!timeOk) return false;

                    // Filtro Tipologia
                    const isPrimary = p.MAINLIGHT.toLowerCase().includes('main');
                    if (isPrimary && !showPrimary) return false;
                    if (!isPrimary && !showSecondary) return false;

                    // Filtro Scartamento
                    const isStd = p.STANDNARRO.toLowerCase().includes('stan');
                    if (isStd && !showStd) return false;
                    if (!isStd && !showNarrow) return false;

                    return true;
                },
                style: (f) => {
                    const isPrimary = f.properties.MAINLIGHT.toLowerCase().includes('main');
                    const isStd = f.properties.STANDNARRO.toLowerCase().includes('stan');
                    
                    return {
                        color: isPrimary ? '#e74c3c' : '#1c39bb', 
                        weight: isStd ? 3 : 2.5,                    
                        dashArray: isStd ? '' : '4, 4',             
                        opacity: 1
                    };
                },
                onEachFeature: (f, l) => {
                    const p = f.properties;
                    
                    const tipoIt = p.MAINLIGHT.toLowerCase().includes('main') ? "Primaria" : "Secondaria";
                    const scartIt = p.STANDNARRO.toLowerCase().includes('stan') ? "Normale (1435mm)" : "Ridotto (950mm)";
                    const lenIt = p.Shape_Leng ? Math.round(p.Shape_Leng) : "n.d.";

                    l.bindPopup(`
                        <div style="font-family:'Roboto', sans-serif; font-size:13px; min-width:150px;">
                            <strong style="font-size:15px; color:#2980b9; display:block; margin-bottom:5px;">${p.TRUNK}</strong>
                            <div style="background:#f9f9f9; padding:5px; border-radius:4px; border:1px solid #eee;">
                                <b>Anno:</b> ${p.YearConstr}<br>
                                <b>Lunghezza:</b> ${lenIt} m<br>
                                <b>Tipo:</b> ${tipoIt}<br>
                                <b>Scartamento:</b> ${scartIt}<br>
                            </div>
                        </div>
                    `);
                }
            }).addTo(railLayer);
        }

        // Inizializzazione
        updateBasemap();
        updateLayers();
        document.getElementById('year-slider').addEventListener('input', update);
        update();
    </script>
</body>
</html>
"""

with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
    f.write(html_content)

print("✅ Done! The italian railways heritage dashboard is ready.")
