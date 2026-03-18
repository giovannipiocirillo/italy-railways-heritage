
const i18n = {
    "it": {
        "title": "Mappa - Sviluppo Ferroviario Italiano (1839-1913)",
        "panel_title": "Sviluppo Ferroviario",
        "single_year": "Solo tratti aperti nell'anno selezionato",
        "line_type": "Tipologia Linee",
        "primary": "Primaria",
        "secondary": "Secondaria",
        "gauge": "Scartamento",
        "standard_gauge": "Normale (1435mm)",
        "narrow_gauge": "Ridotto (950mm)",
        "low": "Bassa",
        "medium": "Media",
        "high": "Alta",
        "extreme": "Estrema",
        "map_bg": "Sfondo Mappa",
        "light_map": "Mappa Chiara",
        "satellite": "Satellite",
        "layers": "Livelli",
        "rail_network": "Rete Ferroviaria",
        "rail_filters": "Filtri Ferroviari",
        "stats_btn": "📊 Vai alle Statistiche",
        "footer_curated": "A cura di",
        "footer_data": "Dati:",
        "popup_year": "Anno",
        "popup_length": "Lunghezza",
        "popup_type": "Tipo",
        "popup_gauge": "Scartamento",
        "modals": {
            "tri": {
                "title": "ℹ️ Terrain Ruggedness Index (TRI)",
                "body": `
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
                    </div>`
            },
            "wheat": {
                "title": "ℹ️ Wheat Suitability (FAO GAEZ v4)",
                "body": `
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
                    Nel XIX secolo l’Italia era un Paese prevalentemente agricolo e il grano rappresentava la coltivazione più diffusa e strategica per l’alimentazione della popolazione. Le zone ad alta idoneità (verde scuro) corrispondono ai principali distretti cerealicoli – i “granai d’Italia”, come il Tavoliere delle Puglie o la Sicilia interna – che necessitavano prioritariamente di collegamenti ferroviari verso i porti e i centri urbani per l’integrazione nei mercati nazionali ed esteri.
                    </p>
                    <div style="font-size:11px; color:#7f8c8d; margin-top:15px; border-top:1px solid #ddd; padding-top:5px;">
                        <b>Fonte:</b> FAO Global Agro-Ecological Zones (GAEZ v4).
                    </div>`
            },
            "rail-type": {
                "title": "ℹ️ Linee Primarie e Secondarie",
                "body": `
                    <p style="margin-bottom:10px;">
                        La distinzione deriva principalmente dalla <a href="https://www.normattiva.it/atto/caricaDettaglioAtto?atto.dataPubblicazioneGazzetta=1879-07-30&atto.codiceRedazionale=079U5002&tipoDettaglio=originario&qId=" target="_blank"><b>Legge Baccarini (L. 5002/1879)</b></a>, che definì le linee "complementari" (o secondarie) necessarie per completare la rete nazionale principale già esistente.
                    </p>
                    <hr style="border:0; border-top:1px solid #eee; margin:10px 0;">
                    <ul style="padding-left:20px; font-size:13px; margin-top:5px;">
                        <li style="margin-bottom:8px;"><b>Linee Primarie (Rosso):</b> La grande dorsale nazionale. Costruite dallo Stato o grandi concessionarie per collegare le metropoli e i confini.</li>
                        <li><b>Linee Secondarie (Blu):</b> Linee di interesse locale, nate per rompere l'isolamento dei centri rurali minori e collegarli alla rete principale.</li>
                    </ul>`
            },
            "gauge": {
                "title": "ℹ️ Scartamento normale e Scartamento ridotto",
                "body": `
                    <p style="margin-bottom:10px;">
                        Lo scartamento è la distanza tra le facce interne delle due rotaie.
                    </p>
                    <hr style="border:0; border-top:1px solid #eee; margin:10px 0;">
                    <ul style="padding-left:20px; font-size:13px; margin-top:5px;">
                        <li style="margin-bottom:8px;"><b>Normale (1435mm):</b> Lo standard internazionale ("Stephenson"). Garantisce maggiore stabilità, velocità e capacità di carico, ma richiede curve ad ampio raggio.</li>
                        <li><b>Ridotto (950mm):</b> Lo standard italiano per le linee secondarie. Permette curve molto strette, consentendo al treno di "arrampicarsi" sulle montagne (alta Ruggedness) riducendo drasticamente i costi di costruzione della linea.</li>
                    </ul>`
            }
        }
    },
    "en": {
        "title": "Map - Italian Railway Development (1839-1913)",
        "panel_title": "Railway Development",
        "single_year": "Only sections opened in the selected year",
        "line_type": "Line Typology",
        "primary": "Primary",
        "secondary": "Secondary",
        "gauge": "Track Gauge",
        "standard_gauge": "Standard (1435mm)",
        "narrow_gauge": "Narrow (950mm)",
        "low": "Low",
        "medium": "Medium",
        "high": "High",
        "extreme": "Extreme",
        "map_bg": "Map Background",
        "light_map": "Light Map",
        "satellite": "Satellite",
        "layers": "Layers",
        "rail_network": "Railway Network",
        "rail_filters": "Railway Filters",
        "stats_btn": "📊 Go to Statistics",
        "footer_curated": "Curated by",
        "footer_data": "Data:",
        "popup_year": "Year",
        "popup_length": "Length",
        "popup_type": "Type",
        "popup_gauge": "Gauge",
        "modals": {
            "tri": {
                "title": "ℹ️ Terrain Ruggedness Index (TRI)",
                "body": `
                    <p style="margin-bottom:10px;">
                        The <b>TRI (Terrain Ruggedness Index)</b> measures terrain heterogeneity by calculating the sum of elevation differences (in millimeters, converted to meters for simplicity) between a central cell and its 8 adjacent cells.
                    </p>
                    <hr style="border:0; border-top:1px solid #eee; margin:10px 0;">
                    <strong style="color:#2c3e50">Impact on Railways:</strong>
                    <p style="font-size:13px; margin-top:5px;">
                        In the years of analysis, steam technology tolerated minimal slopes. A high TRI, and therefore a more rugged terrain, entailed:
                    </p>
                    <ul style="padding-left:20px; font-size:13px;">
                        <li>Exponential construction costs (tunnels, viaducts, excavations).</li>
                        <li>Tortuous routes to avoid the harshest areas (increased travel times).</li>
                        <li>Convenience of narrow-gauge tracks to set tighter curves.</li>
                        <li>Need for more powerful locomotives.</li>
                    </ul>
                    <hr style="border:0; border-top:1px solid #eee; margin:10px 0;">
                    <strong style="color:#2c3e50">Class Legend (in meters):</strong>
                    <ul style="padding-left:20px; font-size:13px; list-style:none; margin-top:5px;">
                        <li>⚪ <b>< 80 (Low):</b> Plain/Gentle hill.</li>
                        <li>🟡 <b>80 - 150 (Medium):</b> Uneven terrain.</li>
                        <li>🟠 <b>150 - 350 (High):</b> Mountain.</li>
                        <li>⚫ <b>> 350 (Extreme):</b> Peaks.</li>
                    </ul>
                    <div style="font-size:11px; color:#7f8c8d; margin-top:15px; border-top:1px solid #ddd; padding-top:5px;">
                        <b>Source:</b> Nunn & Puga (2012), "Ruggedness: The Blessing of Bad Geography in Africa".
                    </div>`
            },
            "wheat": {
                "title": "ℹ️ Wheat Suitability (FAO GAEZ v4)",
                "body": `
                    <p style="margin-bottom:10px;">
                        Agro-climatic suitability index for <b>wheat</b> cultivation, calculated on a 1961-1990 basis.
                    </p>
                    <hr style="border:0; border-top:1px solid #eee; margin:10px 0;">
                    <strong style="color:#2c3e50">Historical Parameters:</strong>
                    <ul style="padding-left:20px; font-size:13px; margin-top:5px;">
                        <li><b>Low Input:</b> Simulates pre-industrial agriculture (manual labor, no chemical fertilizers).</li>
                        <li><b>Rain-fed:</b> Cultivation dependent on rainfall (without modern artificial irrigation).</li>
                    </ul>
                    <strong style="color:#2c3e50">Economic Relevance:</strong>
                    <p style="font-size:13px; margin-top:5px;">
                    In the 19th century, Italy was a predominantly agricultural country and wheat was the most widespread and strategic crop for feeding the population. Highly suitable areas (dark green) correspond to the main cereal districts – the "granaries of Italy", such as the Tavoliere delle Puglie or inland Sicily – which urgently needed railway connections to ports and urban centers for integration into national and foreign markets.
                    </p>
                    <div style="font-size:11px; color:#7f8c8d; margin-top:15px; border-top:1px solid #ddd; padding-top:5px;">
                        <b>Source:</b> FAO Global Agro-Ecological Zones (GAEZ v4).
                    </div>`
            },
            "rail-type": {
                "title": "ℹ️ Primary and Secondary Lines",
                "body": `
                    <p style="margin-bottom:10px;">
                        The distinction stems mainly from the <a href="https://www.normattiva.it/atto/caricaDettaglioAtto?atto.dataPubblicazioneGazzetta=1879-07-30&atto.codiceRedazionale=079U5002&tipoDettaglio=originario&qId=" target="_blank"><b>Baccarini Law (L. 5002/1879)</b></a>, which defined the "complementary" (or secondary) lines necessary to complete the already existing main national network.
                    </p>
                    <hr style="border:0; border-top:1px solid #eee; margin:10px 0;">
                    <ul style="padding-left:20px; font-size:13px; margin-top:5px;">
                        <li style="margin-bottom:8px;"><b>Primary Lines (Red):</b> The great national backbone. Built by the State or large concessionaires to connect metropolises and borders.</li>
                        <li><b>Secondary Lines (Blue):</b> Local interest lines, created to break the isolation of minor rural centers and connect them to the main network.</li>
                    </ul>`
            },
            "gauge": {
                "title": "ℹ️ Standard and Narrow Gauge",
                "body": `
                    <p style="margin-bottom:10px;">
                        The track gauge is the distance between the inner faces of the two rails.
                    </p>
                    <hr style="border:0; border-top:1px solid #eee; margin:10px 0;">
                    <ul style="padding-left:20px; font-size:13px; margin-top:5px;">
                        <li style="margin-bottom:8px;"><b>Standard (1435mm):</b> The international standard ("Stephenson"). It guarantees greater stability, speed, and load capacity, but requires wide-radius curves.</li>
                        <li><b>Narrow (950mm):</b> The Italian standard for secondary lines. It allows very tight curves, enabling the train to "climb" mountains (high Ruggedness), drastically reducing line construction costs.</li>
                    </ul>`
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
    
    if (typeof update === "function") {
        update();
    }
}
