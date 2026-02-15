import geopandas as gpd
import pandas as pd
import json
import os
import time

# --- CONFIGURATION ---
FILE_SHP_RAIL = "railways-shapefile/ItalyRailways.shp"

# OpenPolis GeoJSON URLs
URL_REGIONS = "https://raw.githubusercontent.com/openpolis/geojson-italy/master/geojson/limits_IT_regions.geojson"
URL_PROVINCES = "https://raw.githubusercontent.com/openpolis/geojson-italy/master/geojson/limits_IT_provinces.geojson"
URL_MUNICIPALITIES = "https://raw.githubusercontent.com/openpolis/geojson-italy/master/geojson/limits_IT_municipalities.geojson"

# Output filenames
OUTPUT_DB = "db_stats_dashboard.js"
OUTPUT_HTML = "railways_stats.html"

METRIC_CRS = "EPSG:3035" # Metric Coordinate Reference System for Europe

# Regional Capitals (Keys must match Shapefile municipality names)
REGION_CAPITALS = {
    'Torino': 'Piemonte', 'Aosta': "Valle d'Aosta", 'Milano': 'Lombardia', 'Trento': 'Trentino-Alto Adige/Südtirol',
    'Venezia': 'Veneto', 'Trieste': 'Friuli-Venezia Giulia', 'Genova': 'Liguria', 'Bologna': 'Emilia-Romagna',
    'Firenze': 'Toscana', 'Perugia': 'Umbria', 'Ancona': 'Marche', 'Roma': 'Lazio', "L'Aquila": 'Abruzzo',
    'Campobasso': 'Molise', 'Napoli': 'Campania', 'Bari': 'Puglia', 'Potenza': 'Basilicata', 'Catanzaro': 'Calabria',
    'Palermo': 'Sicilia', 'Cagliari': 'Sardegna'
}

def main():
    start_time = time.time()
    print("🚀 STARTING PROCESSING - STATS DASHBOARD (WITH INFO MODALS)")
    
    # 1. LOAD GEOGRAPHIC DATA
    print("[1/5] 🌍 Downloading boundaries...")
    try:
        gdf_regions = gpd.read_file(URL_REGIONS).to_crs(METRIC_CRS)
        gdf_provinces = gpd.read_file(URL_PROVINCES).to_crs(METRIC_CRS)
        print("      ...loading Municipalities...")
        gdf_municipalities = gpd.read_file(URL_MUNICIPALITIES).to_crs(METRIC_CRS)
        
        gdf_municipalities['centroid'] = gdf_municipalities.geometry.centroid
        gdf_municipalities = gdf_municipalities.set_geometry('centroid')
        
        gdf_regions['area_km2'] = gdf_regions.geometry.area / 10**6
        gdf_provinces['area_km2'] = gdf_provinces.geometry.area / 10**6
        
        # Area Map
        meta_areas = {
            "reg": gdf_regions.set_index('reg_name')['area_km2'].to_dict(),
            "prov": gdf_provinces.set_index('prov_name')['area_km2'].to_dict()
        }
        
        # Region -> Province Hierarchy Map
        structure_map = {}
        for _, row in gdf_provinces.iterrows():
            reg = row['reg_name']
            prov = row['prov_name']
            if reg not in structure_map: structure_map[reg] = []
            structure_map[reg].append(prov)
        for r in structure_map: structure_map[r].sort()
            
    except Exception as e:
        print(f"❌ Error loading GeoJSON: {e}")
        return

    # 2. LOAD RAILWAYS
    print("[2/5] 🚂 Processing Railways...")
    if not os.path.exists(FILE_SHP_RAIL): 
        print("❌ SHP File not found.")
        return

    rail = gpd.read_file(FILE_SHP_RAIL).to_crs(METRIC_CRS)
    rail = rail[rail['YearConstr'] > 0] 
    
    # 3. INFRASTRUCTURE STATISTICS (EXACT CUT)
    print("[3/5] ✂️ Exact cut at boundaries (Overlay)...")
    
    # A. Italian Part (Intersection)
    rail_italy = gpd.overlay(rail, gdf_provinces[['prov_name', 'reg_name', 'geometry']], how='intersection', keep_geom_type=True)
    rail_italy['new_length'] = rail_italy.geometry.length / 1000.0
    
    # B. Abroad/Border Part (Difference)
    rail_abroad = gpd.overlay(rail, gdf_regions[['reg_name', 'geometry']], how='difference', keep_geom_type=True)
    rail_abroad['new_length'] = rail_abroad.geometry.length / 1000.0
    rail_abroad['reg_name'] = 'Estero/Confine'
    rail_abroad['prov_name'] = 'Tratte di Confine'

    infra_data = []
    
    def process_rail_df(df):
        for idx, row in df.iterrows():
            if row['new_length'] < 0.01: continue
            is_main = "main" in str(row.get('MAINLIGHT', '')).lower()
            infra_data.append({
                "y": int(row['YearConstr']),
                "l": round(row['new_length'], 3),
                "r": row['reg_name'] if pd.notnull(row['reg_name']) else "Estero",
                "p": row['prov_name'] if pd.notnull(row['prov_name']) else "Estero",
                "t": "Primaria" if is_main else "Secondaria" # Keep Italian tags for UI consistency
            })

    process_rail_df(rail_italy)
    process_rail_df(rail_abroad)

    structure_map['Estero/Confine'] = ['Tratte di Confine']
    meta_areas['reg']['Estero/Confine'] = 1
    meta_areas['prov']['Tratte di Confine'] = 1

    # 4. ACCESSIBILITY STATISTICS
    print("[4/5] ⏱️ Accessibility Analysis (with Provinces)...")
    
    years_to_check = list(range(1839, 1915, 5)) 
    max_rail = int(rail['YearConstr'].max())
    years_to_check = [y for y in years_to_check if y <= max_rail]
    if 1913 not in years_to_check: years_to_check.append(1913)
    years_to_check.sort()

    caps_reg_df = gdf_municipalities[gdf_municipalities['name'].isin(REGION_CAPITALS.keys())].copy()
    caps_prov_df = gdf_municipalities[gdf_municipalities['name'] == gdf_municipalities['prov_name']].copy()
    
    access_data = []
    
    total_steps = len(years_to_check)
    for i, year in enumerate(years_to_check):
        print(f"      ...Year {year} ({i+1}/{total_steps})")
        
        current_rail = rail[rail['YearConstr'] <= year]
        if current_rail.empty: continue
        
        rail_union = current_rail.unary_union
        
        # Municipality Distances
        dists = gdf_municipalities.geometry.distance(rail_union)
        gdf_municipalities['temp_dist'] = dists
        
        # Averages
        for name, val in gdf_municipalities.groupby('reg_name')['temp_dist'].mean().items():
            access_data.append({"y": year, "n": name, "Type": "Regione", "d": round(val/1000, 2)}) # Type: Regione (IT)
        for name, val in gdf_municipalities.groupby('prov_name')['temp_dist'].mean().items():
            access_data.append({"y": year, "n": name, "Type": "Provincia", "d": round(val/1000, 2)}) # Type: Provincia (IT)
            
        # Capitals
        dists_cr = caps_reg_df.geometry.distance(rail_union)
        for idx, val in dists_cr.items():
            city_name = caps_reg_df.loc[idx, 'name']
            access_data.append({"y": year, "n": city_name, "Type": "Cap_Reg", "d": round(val/1000, 2)})

        dists_cp = caps_prov_df.geometry.distance(rail_union)
        for idx, val in dists_cp.items():
            city_name = caps_prov_df.loc[idx, 'name']
            access_data.append({"y": year, "n": city_name, "Type": "Cap_Prov", "d": round(val/1000, 2)})

    # 5. WRITE DATA FILE (JS)
    print(f"[5/5] 💾 Writing {OUTPUT_DB}...")
    final_db = {
        "meta": meta_areas,
        "structure": structure_map,
        "infra": infra_data,
        "access": access_data,
        "capoluoghi_map": REGION_CAPITALS
    }
    
    with open(OUTPUT_DB, "w", encoding="utf-8") as f:
        f.write(f"const DB = {json.dumps(final_db)};")

    # 6. WRITE DASHBOARD FILE (HTML)
    print(f"      💾 Writing {OUTPUT_HTML}...")
    
    # HTML Content (In Italian as requested)
    html_content = r"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Ferrovie v3.0</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    
    <script src="db_stats_dashboard.js"></script>

    <style>
        :root {
            --color-primary: #e74c3c; 
            --color-secondary: #3498db; 
            --bg-sidebar: #2c3e50;
            --text-sidebar: #ecf0f1;
        }
        body { background-color: #f4f6f9; font-family: 'Segoe UI', sans-serif; overflow: hidden; }
        .sidebar {
            position: fixed; top: 0; bottom: 0; left: 0; 
            width: 280px; background-color: var(--bg-sidebar); color: var(--text-sidebar);
            padding: 20px; overflow-y: auto; z-index: 1000;
        }
        .main-content { margin-left: 280px; padding: 25px; height: 100vh; overflow-y: auto; }
        .card-kpi {
            background: white; border: none; border-radius: 10px; padding: 20px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.05); height: 100%; position: relative;
        }
        .chart-container {
            background: white; border-radius: 10px; padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05); margin-bottom: 25px; height: 400px;
        }
        .section-view { display: none; }
        .section-view.active { display: block; animation: fadeIn 0.3s; }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        
        /* Helpers */
        .sidebar .form-select, .sidebar .form-range { background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); color: #fff; }
        .sidebar option { background: var(--bg-sidebar); }
        .nav-pills .nav-link.active { background-color: var(--color-primary); }
        .nav-pills .nav-link { color: #ccc; }

        /* INFO BUTTONS */
        .info-btn {
            color: #95a5a6; cursor: pointer; transition: color 0.2s; font-size: 0.9rem; margin-left: 8px;
        }
        .info-btn:hover { color: var(--color-secondary); }

        /* MODAL STYLING */
        .modal-custom {
            display: none; position: fixed; z-index: 2000; left: 0; top: 0; width: 100%; height: 100%;
            background-color: rgba(0,0,0,0.5); backdrop-filter: blur(4px);
        }
        .modal-custom-content {
            background-color: #fefefe; margin: 10% auto; padding: 30px; border-radius: 15px;
            width: 600px; max-width: 90%; box-shadow: 0 5px 30px rgba(0,0,0,0.3); position: relative;
            animation: slideDown 0.3s ease-out;
        }
        @keyframes slideDown { from { transform: translateY(-50px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
        .close-modal { color: #aaa; float: right; font-size: 28px; font-weight: bold; cursor: pointer; }
        .close-modal:hover { color: #000; }
        .formula-box { background: #f8f9fa; padding: 15px; border-left: 4px solid var(--color-secondary); margin: 15px 0; font-family: 'Courier New', monospace; color: #333; font-size: 0.95rem; }
    </style>
</head>
<body>

<div id="infoModal" class="modal-custom" onclick="closeInfoModal(event)">
    <div class="modal-custom-content">
        <span class="close-modal" onclick="document.getElementById('infoModal').style.display='none'">&times;</span>
        <h4 id="modalTitle" class="fw-bold mb-3"></h4>
        <div id="modalBody"></div>
    </div>
</div>

<div class="sidebar d-flex flex-column">
    <h5 class="mb-4 text-white"><i class="fas fa-train me-2"></i>History Rail BI</h5>
    
    <div class="nav flex-column nav-pills mb-4">
        <a class="nav-link active" href="#" onclick="setView('infra')"><i class="fas fa-chart-bar me-2"></i> Infrastruttura</a>
        <a class="nav-link" href="#" onclick="setView('access')"><i class="fas fa-map-marked-alt me-2"></i> Accessibilità</a>
    </div>

    <div class="mb-3">
        <label class="form-label text-white-50 small">REGIONE</label>
        <select id="sel-reg" class="form-select" onchange="onRegionChange()">
            <option value="ALL">Tutta Italia</option>
        </select>
    </div>

    <div class="mb-4">
        <label class="form-label text-white-50 small">PROVINCIA</label>
        <select id="sel-prov" class="form-select" disabled onchange="updateDashboard()">
            <option value="ALL">Tutte le Province</option>
        </select>
    </div>

    <div class="mb-2">
        <label class="form-label text-white small">ANNO: <span id="lbl-year" class="fw-bold text-warning">1913</span></label>
        <input type="range" class="form-range" id="range-year" min="1839" max="1913" value="1913" oninput="updateDashboard()">
    </div>
</div>

<div class="main-content">
    
    <div id="view-infra" class="section-view active">
        <h3 class="fw-bold mb-4">Sviluppo Rete Ferroviaria</h3>
        
        <div class="row mb-4">
            <div class="col-md-4">
                <div class="card-kpi border-start border-4 border-danger">
                    <small class="text-uppercase text-muted">Totale Costruito</small>
                    <div class="fs-2 fw-bold text-dark"><span id="kpi-tot">0</span> km</div>
                    <small class="text-success"><span id="kpi-new">+0</span> km nell'anno</small>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card-kpi border-start border-4 border-primary">
                    <small class="text-uppercase text-muted">Tipologia</small>
                    <div class="mt-2">
                        <div class="d-flex justify-content-between small fw-bold text-danger"><span>Primaria</span> <span id="kpi-pp">0%</span></div>
                        <div class="progress mb-2" style="height:5px"><div id="bar-p" class="progress-bar bg-danger" style="width:0%"></div></div>
                        <div class="d-flex justify-content-between small fw-bold text-primary"><span>Secondaria</span> <span id="kpi-ps">0%</span></div>
                        <div class="progress" style="height:5px"><div id="bar-s" class="progress-bar bg-primary" style="width:0%"></div></div>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card-kpi">
                    <small class="text-uppercase text-muted">Densità</small>
                    <div class="fs-2 fw-bold text-dark" id="kpi-dens">0</div>
                    <small class="text-muted">m / km²</small>
                </div>
            </div>
        </div>

        <div class="row">
            <div class="col-lg-8"><div class="chart-container"><canvas id="chart-hist"></canvas></div></div>
            <div class="col-lg-4"><div class="chart-container"><canvas id="chart-pie"></canvas></div></div>
        </div>
    </div>

    <div id="view-access" class="section-view">
        <h3 class="fw-bold mb-4">Accessibilità Territoriale</h3>
        <p class="text-muted">Evoluzione della distanza media (in linea d'aria) dalla stazione ferroviaria più vicina.</p>

        <div class="chart-container">
            <canvas id="chart-access"></canvas>
        </div>

        <div class="row">
            <div class="col-md-6">
                <div class="card-kpi border-bottom border-4 border-warning">
                    <div class="d-flex justify-content-between align-items-start">
                        <small class="text-uppercase text-muted">Distanza Media Territorio</small>
                        <i class="fas fa-info-circle info-btn" onclick="showInfo('area')"></i>
                    </div>
                    <div class="fs-2 fw-bold text-dark" id="acc-val-avg">-</div>
                    <small class="text-muted" id="acc-lbl-avg">Italia</small>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card-kpi border-bottom border-4 border-dark">
                    <div class="d-flex justify-content-between align-items-start">
                        <small class="text-uppercase text-muted">Distanza Capoluogo</small>
                        <i class="fas fa-info-circle info-btn" onclick="showInfo('cap')"></i>
                    </div>
                    <div class="fs-2 fw-bold text-dark" id="acc-val-cap">-</div>
                    <small class="text-muted" id="acc-lbl-cap">-</small>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
    let charts = {};
    let currentView = 'infra';

    // --- LOGICA MODAL INFO ---
    function showInfo(type) {
        const modal = document.getElementById('infoModal');
        const title = document.getElementById('modalTitle');
        const body = document.getElementById('modalBody');
        
        if (type === 'area') {
            title.innerHTML = "ℹ️ Calcolo Distanza Media Territoriale";
            body.innerHTML = `
                <p>Questo indicatore misura il grado di penetrazione della ferrovia nel territorio selezionato (Regione o Provincia).</p>
                
                <strong>Metodologia:</strong>
                <ul>
                    <li>Vengono considerati <b>tutti i Comuni</b> appartenenti all'area selezionata.</li>
                    <li>Per ogni Comune, si calcola il <b>centroide geometrico</b> (il centro esatto).</li>
                    <li>Si misura la distanza in linea d'aria (Euclidea) tra il centroide e il punto più vicino della rete ferroviaria esistente in quell'anno.</li>
                    <li>Si calcola la media aritmetica di queste distanze.</li>
                </ul>

                <div class="formula-box">
                    Formula:<br>
                    D_media = (Σ dist(Centroide_i, Rete)) / N_comuni
                </div>

                <p class="text-muted small">Nota: Il calcolo utilizza la proiezione metrica EPSG:3035 (ETRS89-LAEA) per garantire la massima precisione delle distanze in metri.</p>
            `;
        } else {
            title.innerHTML = "ℹ️ Calcolo Distanza Capoluogo";
            body.innerHTML = `
                <p>Questo indicatore misura l'isolamento del centro amministrativo principale rispetto alla rete ferroviaria.</p>
                
                <strong>Metodologia:</strong>
                <ul>
                    <li>Si considera il <b>Capoluogo</b> (di Regione o di Provincia, a seconda della selezione).</li>
                    <li>Si identifica il punto geometrico rappresentativo della città (centroide ISTAT).</li>
                    <li>Si misura la distanza minima in linea d'aria tra questo punto e il segmento ferroviario più vicino attivo nell'anno selezionato.</li>
                </ul>

                <div class="formula-box">
                    Formula:<br>
                    D_cap = min(dist(Punto_Capoluogo, Rete_Ferroviaria))
                </div>

                <p class="text-muted small">Nota: Se la distanza è 0.0 km, significa che la ferrovia attraversa il territorio comunale del capoluogo.</p>
            `;
        }
        modal.style.display = "block";
    }

    function closeInfoModal(e) {
        if (e.target.id === 'infoModal') {
            document.getElementById('infoModal').style.display = 'none';
        }
    }

    window.onload = function() {
        if(typeof DB === 'undefined') { alert("Esegui Python prima per generare db_stats_dashboard.js!"); return; }
        
        // Popola Regioni
        const selReg = document.getElementById('sel-reg');
        Object.keys(DB.structure).sort().forEach(r => {
            selReg.add(new Option(r, r));
        });

        // Set Slider Anno
        const maxYear = Math.max(...DB.infra.map(d=>d.y));
        document.getElementById('range-year').max = maxYear;
        
        updateDashboard();
    };

    function onRegionChange() {
        const reg = document.getElementById('sel-reg').value;
        const selProv = document.getElementById('sel-prov');
        selProv.innerHTML = '<option value="ALL">Tutte le Province</option>';
        
        if(reg === 'ALL') {
            selProv.disabled = true;
        } else {
            selProv.disabled = false;
            if(DB.structure[reg]) {
                DB.structure[reg].forEach(p => selProv.add(new Option(p, p)));
            }
        }
        updateDashboard();
    }

    function setView(view) {
        currentView = view;
        document.querySelectorAll('.section-view').forEach(e => e.classList.remove('active'));
        document.getElementById('view-'+view).classList.add('active');
        document.querySelectorAll('.nav-link').forEach(e => e.classList.remove('active'));
        event.currentTarget.classList.add('active');
        updateDashboard();
    }

    function updateDashboard() {
        const reg = document.getElementById('sel-reg').value;
        const prov = document.getElementById('sel-prov').value;
        const year = parseInt(document.getElementById('range-year').value);
        document.getElementById('lbl-year').innerText = year;

        if(currentView === 'infra') renderInfra(reg, prov, year);
        else renderAccess(reg, prov, year);
    }

    // --- INFRA ---
    function renderInfra(reg, prov, year) {
        const data = DB.infra.filter(d => d.y <= year && (reg==='ALL'||d.r===reg) && (prov==='ALL'||d.p===prov));
        
        let tot=0, yearNew=0, pKm=0, sKm=0;
        const hist = {};

        data.forEach(d => {
            tot += d.l;
            if(d.y === year) yearNew += d.l;
            d.t === 'Primaria' ? pKm += d.l : sKm += d.l;
            
            if(!hist[d.y]) hist[d.y] = {p:0, s:0};
            d.t === 'Primaria' ? hist[d.y].p += d.l : hist[d.y].s += d.l;
        });

        document.getElementById('kpi-tot').innerText = Math.round(tot).toLocaleString();
        document.getElementById('kpi-new').innerText = (yearNew>0?'+':'')+Math.round(yearNew);
        
        const pp = tot ? (pKm/tot*100).toFixed(1) : 0;
        const ps = tot ? (sKm/tot*100).toFixed(1) : 0;
        document.getElementById('kpi-pp').innerText = pp+'%'; document.getElementById('bar-p').style.width = pp+'%';
        document.getElementById('kpi-ps').innerText = ps+'%'; document.getElementById('bar-s').style.width = ps+'%';
        
        let area = reg==='ALL' ? 302000 : (prov==='ALL' ? DB.meta.reg[reg] : DB.meta.prov[prov]);
        document.getElementById('kpi-dens').innerText = ((tot/(area||1))*1000).toFixed(1);

        // Chart History
        const labels = Object.keys(hist).sort();
        if(charts.hist) charts.hist.destroy();
        charts.hist = new Chart(document.getElementById('chart-hist'), {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    { label:'Primarie', data: labels.map(l=>hist[l].p), backgroundColor:'#e74c3c', stack:'0' },
                    { label:'Secondarie', data: labels.map(l=>hist[l].s), backgroundColor:'#3498db', stack:'0' }
                ]
            },
            options: { responsive:true, maintainAspectRatio:false, scales:{x:{stacked:true}, y:{stacked:true}} }
        });

        // Chart Pie
        if(charts.pie) charts.pie.destroy();
        charts.pie = new Chart(document.getElementById('chart-pie'), {
            type: 'doughnut',
            data: { labels:['Primarie','Secondarie'], datasets:[{data:[pKm,sKm], backgroundColor:['#e74c3c','#3498db']}] },
            options: { maintainAspectRatio:false }
        });
    }

    // --- ACCESS ---
    function renderAccess(reg, prov, year) {
        const years = [...new Set(DB.access.map(d=>d.y))].sort();
        
        // --- LOGICA ETICHETTE E FILTRI ---
        let filterTypeArea = 'Regione'; 
        let filterNameArea = reg;
        let filterNameCap = null;
        
        let lblAreaKPI = "Media Italia";
        let lblCapKPI = "Capoluogo";
        let lblAreaChart = "Media Italia";
        let lblCapChart = "Capoluogo";

        if(reg === 'ALL') {
            lblAreaKPI = "Distanza media Comuni (Italia)";
            lblAreaChart = "Media Italia";
            lblCapKPI = "-";
        } else if (prov === 'ALL') {
            lblAreaKPI = "Media Comuni (" + reg + ")";
            lblAreaChart = "Media " + reg;
            for(let [c, r] of Object.entries(DB.capoluoghi_map)) if(r===reg) filterNameCap = c;
            lblCapKPI = "Capoluogo Regionale (" + (filterNameCap || '-') + ")";
            lblCapChart = "Capoluogo (" + (filterNameCap || '-') + ")";
        } else {
            filterTypeArea = 'Provincia';
            filterNameArea = prov;
            filterNameCap = prov; 
            lblAreaKPI = "Media Comuni (Prov. " + prov + ")";
            lblAreaChart = "Media Prov. " + prov;
            lblCapKPI = "Capoluogo Provinciale (" + prov + ")";
            lblCapChart = "Capoluogo (" + prov + ")";
        }

        const dataArea = [];
        const dataCap = [];

        years.forEach(y => {
            if(reg === 'ALL') {
                const vals = DB.access.filter(d => d.y===y && d.Type==='Regione').map(d=>d.d);
                dataArea.push(vals.length ? vals.reduce((a,b)=>a+b)/vals.length : null);
            } else {
                const entry = DB.access.find(d => d.y===y && d.Type===filterTypeArea && d.n===filterNameArea);
                dataArea.push(entry ? entry.d : null);
            }
            if(filterNameCap) {
                const entry = DB.access.find(d => d.y===y && d.n===filterNameCap); 
                dataCap.push(entry ? entry.d : null);
            }
        });

        const idxYear = years.findIndex(y => y > year);
        const limit = idxYear === -1 ? years.length : idxYear;
        
        const viewYears = years.slice(0, limit);
        const viewArea = dataArea.slice(0, limit);
        const viewCap = dataCap.slice(0, limit);

        const lastArea = viewArea.length ? viewArea[viewArea.length-1] : null;
        const lastCap = viewCap.length ? viewCap[viewCap.length-1] : null;
        
        document.getElementById('acc-val-avg').innerText = (lastArea !== null ? lastArea.toFixed(1) : '-') + ' km';
        document.getElementById('acc-lbl-avg').innerText = lblAreaKPI;
        
        document.getElementById('acc-val-cap').innerText = (lastCap !== null ? lastCap.toFixed(1) : '-') + ' km';
        document.getElementById('acc-lbl-cap').innerText = lblCapKPI;

        if(charts.access) charts.access.destroy();
        
        const datasets = [{
            label: lblAreaChart,
            data: viewArea,
            borderColor: '#f39c12',
            backgroundColor: 'rgba(243, 156, 18, 0.1)',
            fill: true, tension: 0.3
        }];
        
        if(filterNameCap) {
            datasets.push({
                label: lblCapChart,
                data: viewCap,
                borderColor: '#2c3e50',
                borderDash: [5,5],
                fill: false
            });
        }

        charts.access = new Chart(document.getElementById('chart-access'), {
            type: 'line',
            data: { labels: viewYears, datasets: datasets },
            options: { 
                responsive: true, 
                maintainAspectRatio: false, 
                scales: { 
                    y: { title: { display: true, text: 'Km dalla stazione' }, beginAtZero: true } 
                },
                plugins: {
                    legend: { position: 'top' }
                }
            }
        });
    }
</script>
</body>
</html>"""
    
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"✅ COMPLETED in {round(time.time() - start_time, 1)}s.")

if __name__ == "__main__":
    main()
