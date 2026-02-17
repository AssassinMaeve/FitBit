import os
import pandas as pd
import logging
from src.cleaning import clean_data
from src.utils import safe_filename

def process_subject(subject_name, config):
    root_dir = config['paths']['root_dir']
    output_dir = config['paths']['output_dir']
    keywords = config['keywords']
    max_rows = config['settings']['max_rows_per_sheet']
    
    # 1. Get the force_rerun setting (defaults to False if not set)
    force_rerun = config['settings'].get('force_rerun', False)
    
    person_path = os.path.join(root_dir, subject_name)
    person_out_dir = os.path.join(output_dir, f"{subject_name}_cleaned")
    os.makedirs(person_out_dir, exist_ok=True)

    if not os.path.isdir(person_path):
        logging.error(f"Folder not found: {person_path}")
        return

    logging.info(f" Processing subject: {subject_name}")

    # Walk through folders
    for root, dirs, files in os.walk(person_path):
        if root == person_path:
            continue

        category = os.path.basename(root)
        
        # Filter by keywords
        if not any(k in category.lower() for k in keywords):
            continue

        # 2. Define the output path early
        output_filename = f"{subject_name}_{safe_filename(category)}.xlsx"
        output_file_path = os.path.join(person_out_dir, output_filename)

        # 3. CHECK: If file exists and we are NOT forcing a rerun, SKIP IT
        if os.path.exists(output_file_path) and not force_rerun:
            logging.info(f"   ⏭  Skipping {category} (File exists)")
            continue

        logging.info(f"   ➤ Processing category: {category}")
        
        dfs = []
        for file in files:
            if not file.lower().endswith((".csv", ".xlsx")) or "readme" in file.lower():
                continue

            file_path = os.path.join(root, file)
            try:
                # Read Data
                if file.lower().endswith(".csv"):
                    df = pd.read_csv(file_path)
                else:
                    df = pd.read_excel(file_path)
                
                # Clean Data
                df = clean_data(df)
                
                if not df.empty:
                    df["source_file"] = file
                    dfs.append(df)
            except Exception as e:
                logging.warning(f"      Failed to read {file}: {e}")

        if not dfs:
            logging.info(f"      No usable data in {category}")
            continue

        # Merge all files for this category
        final_df = pd.concat(dfs, ignore_index=True)
        
        # Save to Excel
        save_to_excel(final_df, output_file_path, max_rows)

def save_to_excel(df, path, max_rows):
    """Handles logic for splitting large datasets into multiple Excel sheets."""
    try:
        with pd.ExcelWriter(path, engine="openpyxl") as writer:
            total_rows = len(df)
            if total_rows <= max_rows:
                df.to_excel(writer, sheet_name="data", index=False)
            else:
                for i in range((total_rows // max_rows) + 1):
                    start = i * max_rows
                    end = start + max_rows
                    chunk = df.iloc[start:end]
                    chunk.to_excel(writer, sheet_name=f"data_{i+1}", index=False)
        logging.info(f"     ✅ Saved: {path}")
    except Exception as e:
        logging.error(f"      Failed to save {path}: {e}")