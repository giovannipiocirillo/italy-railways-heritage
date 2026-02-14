import rasterio
from rasterio.mask import mask
import geopandas as gpd
import numpy as np

# --- CONFIGURAZIONE ---
INPUT_WHEAT = "wheat-suitability/sxLr0_whe.tif" # The file downloaded from FAO GAEZ
OUTPUT_TIF = "wheat-suitability/italy_wheat_clipped.tif"
# ISTAT Italy's borders
URL_CONFINI = "https://raw.githubusercontent.com/openpolis/geojson-italy/master/geojson/limits_IT_regions.geojson"

def process_wheat():
    print("--- SCRIPT 2: WHEAT SUITABILITY ---")
    
    # 1. Loading Italy's borders
    print("📥 Downloading Italy's borders...")
    try:
        gdf = gpd.read_file(URL_CONFINI)
        # Since the geojson contains the borders of the individual regions,
        # we join the borders to obtain a single "Italy" polygon with the relative borders
        italy_geom = [gdf.dissolve().geometry.values[0]]
    except Exception as e:
        print(f"Error downloading Italy's geojson: {e}")
        return

    # 2. Raster processing
    print(f"📖 Reading {INPUT_WHEAT} (it may take a while)...")
    try:
        with rasterio.open(INPUT_WHEAT) as src:
            print("✂️  Exact mask clipping for wheat suitability in Italy...")
            out_image, out_transform = mask(src, italy_geom, crop=True)
            out_meta = src.meta.copy()

            # Updating metadata and lossless compression
            out_meta.update({
                "driver": "GTiff",
                "height": out_image.shape[1],
                "width": out_image.shape[2],
                "transform": out_transform,
                "compress": "lzw"
            })

            # Writing new clipped file
            with rasterio.open(OUTPUT_TIF, "w", **out_meta) as dest:
                dest.write(out_image)

            print(f"✅ Created: {OUTPUT_TIF}")
            
    except Exception as e:
        print(f"Error during raster processing: {e}")

if __name__ == "__main__":
    process_wheat()
