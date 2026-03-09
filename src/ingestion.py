import os
import math
import pandas as pd
import logging
from src.cleaning import clean_data
from src.utils import safe_filename


def process_subject(subject_name, config):
    """Ingest and clean data for a single subject.

    Fix #12: Process all directory levels, not just one level deep.
    Fix #13: force_rerun now defaults to True in config for data correction.
    """
    root_dir = config['paths']['root_dir']
    output_dir = config['paths']['output_dir']
    keywords = config['keywords']
    max_rows = config['settings']['max_rows_per_sheet']

    # Get the force_rerun setting (defaults to False if not set)
    force_rerun = config['settings'].get('force_rerun', False)

    person_path = os.path.join(root_dir, subject_name)
    person_out_dir = os.path.join(output_dir, f"{subject_name}_cleaned")
    os.makedirs(person_out_dir, exist_ok=True)

    if not os.path.isdir(person_path):
        logging.error(f"Folder not found: {person_path}")
        return

    logging.info(f" Processing subject: {subject_name}")

    # Fix #12: Walk ALL directory levels, use the deepest folder name as category
    for root, dirs, files in os.walk(person_path):
        # Skip the root directory itself (no category)
        if root == person_path:
            # But still process files AT root level if they match keywords
            # by checking filenames instead of directory names
            root_files = [f for f in files if f.lower().endswith((".csv", ".xlsx"))
                          and "readme" not in f.lower()]
            if root_files:
                for f in root_files:
                    file_lower = f.lower()
                    if any(k in file_lower for k in keywords):
                        _process_single_file(
                            os.path.join(root, f), subject_name, file_lower,
                            person_out_dir, max_rows, force_rerun
                        )
            continue

        # Use the immediate directory name as the category
        category = os.path.basename(root)

        # Filter by keywords
        if not any(k in category.lower() for k in keywords):
            continue

        # Define the output path
        output_filename = f"{subject_name}_{safe_filename(category)}.xlsx"
        output_file_path = os.path.join(person_out_dir, output_filename)

        # CHECK: If file exists and we are NOT forcing a rerun, SKIP IT
        if os.path.exists(output_file_path) and not force_rerun:
            logging.info(f"   ⏭  Skipping {category} (File exists. Set force_rerun: true to regenerate)")
            continue

        logging.info(f"   ➤ Processing category: {category}")

        dfs = []
        for file in files:
            if not file.lower().endswith((".csv", ".xlsx")) or "readme" in file.lower():
                continue

            file_path = os.path.join(root, file)
            try:
                if file.lower().endswith(".csv"):
                    df = pd.read_csv(file_path)
                else:
                    df = pd.read_excel(file_path)

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


def _process_single_file(file_path, subject_name, file_lower, out_dir, max_rows, force_rerun):
    """Process a single data file found at root level."""
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    output_filename = f"{subject_name}_{safe_filename(base_name)}.xlsx"
    output_file_path = os.path.join(out_dir, output_filename)

    if os.path.exists(output_file_path) and not force_rerun:
        return

    try:
        if file_path.lower().endswith(".csv"):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        df = clean_data(df)

        if not df.empty:
            df["source_file"] = os.path.basename(file_path)
            save_to_excel(df, output_file_path, max_rows)
    except Exception as e:
        logging.warning(f"      Failed to read {file_path}: {e}")


def save_to_excel(df, path, max_rows):
    """Handles logic for splitting large datasets into multiple Excel sheets.

    Fix #19: Uses math.ceil to avoid creating an empty trailing sheet
    when total_rows is an exact multiple of max_rows.
    """
    try:
        with pd.ExcelWriter(path, engine="openpyxl") as writer:
            total_rows = len(df)
            if total_rows <= max_rows:
                df.to_excel(writer, sheet_name="data", index=False)
            else:
                num_sheets = math.ceil(total_rows / max_rows)
                for i in range(num_sheets):
                    start = i * max_rows
                    end = start + max_rows
                    chunk = df.iloc[start:end]
                    if not chunk.empty:
                        chunk.to_excel(writer, sheet_name=f"data_{i+1}", index=False)
        logging.info(f"     ✅ Saved: {path}")
    except Exception as e:
        logging.error(f"      Failed to save {path}: {e}")