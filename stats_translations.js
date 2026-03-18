
const i18n = {
    "it": {
        "title": "Statistiche - Sviluppo Ferroviario Italiano (1839-1913)",
        "nav_infra": "Infrastruttura",
        "nav_access": "Accessibilità",
        "lbl_reg": "REGIONE",
        "lbl_prov": "PROVINCIA",
        "lbl_year": "ANNO:",
        "opt_all_it": "Tutta Italia",
        "opt_all_prov": "Tutte le Province",
        "btn_map": "Mappa",
        "title_infra": "Sviluppo Rete Ferroviaria",
        "kpi_tot": "Totale Costruito",
        "kpi_new": "nell'anno",
        "kpi_type": "Tipologia",
        "kpi_prim": "Primaria",
        "kpi_sec": "Secondaria",
        "kpi_dens": "Densità",
        "title_access": "Accessibilità Territoriale",
        "desc_access": "Evoluzione della distanza media (in linea d'aria) dalla stazione ferroviaria più vicina.",
        "kpi_dist_avg": "Distanza Media Territorio",
        "kpi_dist_cap": "Distanza Capoluogo",
        "lbl_italy": "Italia",
        "chart_y_axis": "Km dalla stazione",
        "dyn_avg_it": "Media Italia",
        "dyn_avg_reg": "Media",
        "dyn_avg_com_it": "Media Comuni (Italia)",
        "dyn_avg_com": "Media Comuni",
        "dyn_avg_prov": "Media Prov.",
        "dyn_cap_reg": "Capoluogo Regionale",
        "dyn_cap_prov": "Capoluogo Provinciale",
        "dyn_cap": "Capoluogo",
        "footer_curated": "A cura di",
        "footer_data": "Dati:",
        "modals": {
            "area": {
                "title": "ℹ️ Calcolo Distanza Media Territoriale",
                "body": `
                    <p>Questo indicatore misura il grado di penetrazione della ferrovia nel territorio selezionato (Regione o Provincia).</p>
                    <strong>Metodologia:</strong>
                    <ul>
                        <li>Vengono considerati <b>tutti i Comuni</b> appartenenti all'area selezionata.</li>
                        <li>Per ogni Comune, si calcola il <b>centroide geometrico</b>.</li>
                        <li>Si misura la distanza in linea d'aria tra il centroide e il punto più vicino della rete ferroviaria.</li>
                        <li>Si calcola la media aritmetica di queste distanze.</li>
                    </ul>
                    <div class="formula-box">D_media = (Σ dist(Centroide_i, Rete)) / N_comuni</div>
                `
            },
            "cap": {
                "title": "ℹ️ Calcolo Distanza Capoluogo",
                "body": `
                    <p>Misura l'isolamento del centro amministrativo principale.</p>
                    <strong>Metodologia:</strong>
                    <ul>
                        <li>Si considera il <b>Capoluogo</b> (Regionale o Provinciale).</li>
                        <li>Si misura la distanza minima in linea d'aria tra il centroide della città e la ferrovia.</li>
                    </ul>
                    <div class="formula-box">D_cap = min(dist(Punto_Capoluogo, Rete))</div>
                `
            }
        }
    },
    "en": {
        "title": "Statistics - Italian Railway Development (1839-1913)",
        "nav_infra": "Infrastructure",
        "nav_access": "Accessibility",
        "lbl_reg": "REGION",
        "lbl_prov": "PROVINCE",
        "lbl_year": "YEAR:",
        "opt_all_it": "All Italy",
        "opt_all_prov": "All Provinces",
        "btn_map": "Map",
        "title_infra": "Railway Network Development",
        "kpi_tot": "Total Built",
        "kpi_new": "in the year",
        "kpi_type": "Typology",
        "kpi_prim": "Primary",
        "kpi_sec": "Secondary",
        "kpi_dens": "Density",
        "title_access": "Territorial Accessibility",
        "desc_access": "Evolution of the average distance (straight line) from the nearest railway station.",
        "kpi_dist_avg": "Average Territory Distance",
        "kpi_dist_cap": "Capital Distance",
        "lbl_italy": "Italy",
        "chart_y_axis": "Km from station",
        "dyn_avg_it": "Italy Average",
        "dyn_avg_reg": "Average",
        "dyn_avg_com_it": "Municipalities Average (Italy)",
        "dyn_avg_com": "Municipalities Average",
        "dyn_avg_prov": "Prov. Average",
        "dyn_cap_reg": "Regional Capital",
        "dyn_cap_prov": "Provincial Capital",
        "dyn_cap": "Capital",
        "footer_curated": "Curated by",
        "footer_data": "Data:",
        "modals": {
            "area": {
                "title": "ℹ️ Territorial Average Distance Calculation",
                "body": `
                    <p>This indicator measures the degree of railway penetration in the selected territory (Region or Province).</p>
                    <strong>Methodology:</strong>
                    <ul>
                        <li><b>All Municipalities</b> belonging to the selected area are considered.</li>
                        <li>For each Municipality, the <b>geometric centroid</b> is calculated.</li>
                        <li>The straight-line distance between the centroid and the closest point of the railway network is measured.</li>
                        <li>The arithmetic mean of these distances is calculated.</li>
                    </ul>
                    <div class="formula-box">D_avg = (Σ dist(Centroid_i, Network)) / N_municipalities</div>
                `
            },
            "cap": {
                "title": "ℹ️ Capital Distance Calculation",
                "body": `
                    <p>Measures the isolation of the main administrative center.</p>
                    <strong>Methodology:</strong>
                    <ul>
                        <li>The <b>Capital</b> (Regional or Provincial) is considered.</li>
                        <li>The minimum straight-line distance between the city's centroid and the railway is measured.</li>
                    </ul>
                    <div class="formula-box">D_cap = min(dist(Capital_Point, Network))</div>
                `
            }
        }
    }
};

let currentLang = "it";

function setLanguage(lang) {
    currentLang = lang;
    
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if(i18n[lang][key]) {
            el.innerHTML = i18n[lang][key];
        }
    });
    
    document.title = i18n[lang]["title"];
    
    // Update dynamically created texts in DOM
    if (document.getElementById('opt-all-reg')) {
        document.getElementById('opt-all-reg').innerText = i18n[lang].opt_all_it;
    }
    
    if (typeof updateDashboard === "function") {
        updateDashboard();
    }
}
