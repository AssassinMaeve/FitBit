# FitBit Data Processing & Analysis Pipeline

A modular, production-ready Python pipeline designed to ingest, clean, and analyze physiological data from Fitbit devices.

This project transforms messy raw Fitbit data exports into structured, analysis-ready binary datasets. It provides fully automated time-series analysis, statistical summaries, Exploratory Data Analysis (EDA), and compiles these insights into comprehensive and easy-to-read PDF reports.

> **Note:** This repository contains the **code and methodology only**. Raw Fitbit data is intentionally excluded for privacy, ethics, and storage constraints.

---

## Key Features

* **High-Performance Parquet Caching:** Uses Apache Parquet (`.parquet`) for intermediate data storage, offering massive I/O speedups over traditional CSV/Excel caching.
* **Massively Parallel Processing:** Leverages multi-core CPUs via `ProcessPoolExecutor` to process multiple patients/subjects simultaneously.
* **Biologically Accurate Cleaning:** Uses time-aware linear interpolation rather than flat median imputation to accurately bridge missing data gaps without destroying your natural physiological variance.
* **Exploratory Data Analysis (EDA):** Automatically generates statistical summaries, distribution histograms, and correlation matrix heatmaps to understand data shape and relationships.
* **Automated PDF Reporting:** Compiles everything into a layman-friendly PDF health report containing executive summaries, data quality assessments, and readable, paginated metrics.
* **Signal Separation:** Automatically isolates distinct physiological signals (Heart Rate, HRV, SpO2, Sleep, Glucose, Stress, Activity) into dedicated datasets.

---

## Pipeline Architecture

The pipeline operates in three fully automated stages orchestrated by `run_pipeline.py`.

### Stage 1: Ingestion & Aggregation (`src/ingestion.py`)

- **Participant-wise Indexing:** Recursively searches `data/raw/` for specific subject folders at all directory depths.
- **Intelligent Merging:** Combines scattered daily/weekly export files for the same health category into unified datasets.
- **Fast Archiving:** Saves the merged categories directly to lightning-fast Apache Parquet files in `data/processed/`.

### Stage 2: Analytical Cleaning (`src/cleaning.py`)

- **Standardization:** Normalizes column names to `snake_case` and enforces standard ISO datetime formats.
- **Sanitization:** Strips out completely empty rows, duplicates, and faulty/erroneous sensor errors.
- **Time-Series Interpolation:** Sorts chronological data and bridges `NaN` (missing) gaps using linear interpolation.

### Stage 3: Analysis & Reporting (`src/analysis.py` & `src/reporting.py`)

- **Time-Series Analysis:** Generates weekly and monthly aggregation plots across all valid datasets.
- **Exploratory Data Analysis (EDA):** Produces distribution charts, correlation heatmaps, and statistical matrices (Mean, Median, Skewness, percentiles).
- **Executive PDF Generation:** Bundles visualizations and data tables into a final layman-friendly, multi-page PDF document.

---

## Configuration (`config.yaml`)

Your pipeline settings are strictly controlled via `config/config.yaml`.

| Setting                  | Description                                                      | Default            |
| ------------------------ | ---------------------------------------------------------------- | ------------------ |
| `paths.root_dir`       | Directory containing raw Fitbit export folders                   | `data/raw`       |
| `paths.output_dir`     | Directory for the lightning-fast `.parquet` caches             | `data/processed` |
| `paths.reports_dir`    | Directory for the generated PDFs, graphs, and CSVs               | `reports`        |
| `settings.subjects`    | List of subject folder names to process                          | —                 |
| `settings.force_rerun` | Set to `true` to regenerate outputs even if they already exist | `false`          |
| `keywords`             | Internal regex keywords for mapping export files                 | See config file    |

---

## How to Use (Locally)

### 1. Setup Environment

Clone the repository and install the dependencies:

```bash
git clone https://github.com/AssassinMaeve/Fitbit.git
cd Fitbit

pip install -r requirements.txt
```

### 2. Prepare Data

Place your raw Fitbit export folders inside the `data/raw/` directory. Each subject should have their own folder.

* Example: `data/raw/Fitbit_test_subject_1/`

### 3. Configure Pipeline

Edit `config/config.yaml` to specify which subjects you want the pipeline to run on:

```yaml
settings:
  subjects:
    - "Fitbit_test_subject_1"
    - "Fitbit_test_subject_2"
```

### 4. Run Pipeline

Execute the main orchestrator script:

```bash
python run_pipeline.py
```

*The pipeline will leverage your CPU's multiple cores to process patients concurrently and print a summary when finished.*

### 5. View Results

All results are cleanly organized by subject:

* **Cleaned Data:** `data/processed/{subject}_cleaned/`
* **Visual Plots & EDA:** `reports/{subject}/`
* **Final PDF Reports:** `reports/{subject}/{subject}_Detailed_Report.pdf`
* **Diagnostic Logs:** `logs/pipeline.log`

---

## Ethics & Privacy

* **No Personal Data:** No raw, identified, or processed participant data is committed to this repository.
* **Local Processing:** All data cleaning and analysis operations occur 100% locally on your machine. No cloud API calls are made.
* **Compliance:** The pipeline design adheres to standard ethical research guidelines for health data handling.

---

## Technologies Used

* **Language:** Python 3.10+
* **Data Processing:** Pandas, FastParquet / PyArrow
* **Visualization:** Seaborn, Matplotlib
* **Reporting:** FPDF
* **Concurrency:** `concurrent.futures.ProcessPoolExecutor`

---

## Author

**Maeve Fernandes**
MSc Software Technology
Research focus: Health Data Analysis & Applied Data Science
