import pandas as pd
from pathlib import Path

# Define input and output paths
input_files = {
    "KG_PlantConnectome_20250421.csv": "/home/shanchun123/newplantconnectome/connectome_files/KG_PlantConnectome_20250421.csv",
    "connectome_agi_pairs_pmid_edge_all_columns_TF.csv": "/home/shanchun123/newplantconnectome/connectome_files/connectome_agi_pairs_pmid_edge_all_columns_TF.csv"
}

preview_dir = Path("/home/shanchun123/newplantconnectome/connectome_files/previews")
preview_dir.mkdir(parents=True, exist_ok=True)

# Generate preview CSVs (first 10 rows)
for name, path in input_files.items():
    df = pd.read_csv(path)
    preview_path = preview_dir / f"{name}.preview.csv"
    df.head(10).to_csv(preview_path, index=False)
    print(f"✅ Saved preview: {preview_path}")