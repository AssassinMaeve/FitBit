# Analysis of Behavioural and Physiological Trends in Type 2 Diabetes Using Fitbit Data

A modular, production-ready MLOps pipeline designed to ingest, clean, and analyze physiological data from Fitbit devices. This project transforms raw Fitbit exports into clean, structured, analysis-ready datasets, enabling reliable study of physiological trends such as glucose levels, sleep quality, heart rate, and stress metrics.



> **Note:** This repository contains the **code and methodology only**. Raw Fitbit data is intentionally excluded for privacy, ethics, and storage constraints.

---

## Objectives

* **Build a Reproducible Pipeline:** Move from manual notebooks to a scalable Python package.
* **Participant-Wise Processing:** Ingest and clean data for specific subjects (e.g., `Fitbit_ba`, `Fitbit_lo`).
* **Signal Separation:** Automatically separate distinct physiological signals (Heart Rate, HRV, SpO2, Sleep, Glucose) into dedicated datasets.
* **Automated Analysis:** Generate time-series trends and periodic summaries (weekly & monthly) automatically.
* **PDF Reporting:** Generate comprehensive PDF health reports with executive summaries, data quality assessments, and visualizations.
* **Explore Relationships:** Enable research into Glucose vs. Sleep, Activity vs. Stress, and more.

---

## Repository Structure

The project has been refactored from a notebook-based workflow into a professional MLOps structure:

```text
FitBit/
├── config/
│   └── config.yaml          # Control center: subjects, paths, settings
├── data/
│   ├── raw/                 # (Ignored) Place your raw 'Fitbit_xx' folders here
│   └── processed/           # (Ignored) Cleaned Excel files appear here
├── logs/
│   └── pipeline.log         # Rotating execution logs (max 1MB, 3 backups)
├── reports/                 # (Ignored) Generated PDFs, graphs, and CSV stats
├── src/
│   ├── __init__.py
│   ├── ingestion.py         # Logic for reading and merging files (Stage 1)
│   ├── cleaning.py          # Logic for standardization & validation (Stage 2)
│   ├── analysis.py          # Logic for visualization & time-series analysis
│   ├── reporting.py         # PDF report generation
│   └── utils.py             # Helpers for logging, config, and filename sanitization
├── run_pipeline.py          # Main execution script
├── requirements.txt         # Project dependencies
└── README.md
```

---

## Data Processing Pipeline

The pipeline operates in three distinct stages, fully automated via `run_pipeline.py`.

### Stage 1: Ingestion & Structural Preprocessing

* **Participant-wise crawling:** Recursively searches `data/raw/` for specific subject folders at all directory depths.
* **Idempotency Check:** Skips files that have already been processed (set `force_rerun: true` in `config.yaml` to regenerate all outputs).
* **Merging:** Combines multiple export files for the same category into a single DataFrame.
* **Sheet Splitting:** Large datasets (>1M rows) are split across multiple Excel sheets automatically.

### Stage 2: Analytical Cleaning

* **Standardization:** Normalizes column names (`snake_case`) and fixes mixed date formats. Detects date columns named `start`, `end`, `log`, `day`, etc.
* **Sanitization:** Removes null-only rows, duplicates, and non-numeric signal errors.
* **Missing Value Handling:** Uses **median imputation** instead of zero-filling — preserves statistical validity for health metrics (HR, SpO2, glucose).
* **Output:** Saves clean Excel files to `data/processed/`.

### Stage 3: Analysis & Reporting

* **Signal Separation:** Distinguishes Heart Rate from Heart Rate Variability (HRV) data automatically.
* **Multi-Column Analysis:** Plots up to 4 key metrics per dataset with proper datetime axes.
* **Periodic Summaries:** Generates both weekly and monthly aggregations (CSVs + charts).
* **PDF Reports:** Comprehensive reports with executive summary, data quality assessment, trend charts, and data tables.

---

## Configuration

All pipeline settings are controlled via `config/config.yaml`:

| Setting | Description | Default |
| --- | --- | --- |
| `paths.root_dir` | Directory containing raw Fitbit export folders | `data/raw` |
| `paths.output_dir` | Directory for cleaned Excel files | `data/processed` |
| `paths.reports_dir` | Directory for generated reports and PDFs | `reports` |
| `settings.subjects` | List of subject folder names to process | — |
| `settings.max_rows_per_sheet` | Max rows per Excel sheet before splitting | `1000000` |
| `settings.force_rerun` | Regenerate outputs even if they already exist | `true` |
| `keywords` | List of keywords for matching data categories | See config file |

---

## How to Use (Locally)

### 1. Setup Environment

```bash
# Clone the repo
git clone https://github.com/AssassinMaeve/Fitbit.git
cd Fitbit

# Install dependencies
pip install -r requirements.txt
```

### 2. Prepare Data

Place your raw Fitbit export folders inside the `data/raw/` directory.

* Example: `data/raw/Fitbit_ba/`

### 3. Configure Pipeline

Edit `config/config.yaml` to list the subjects you want to process:

```yaml
subjects:
  - "Fitbit_ba"
  - "Fitbit_lo"
```

### 4. Run Pipeline

```bash
python run_pipeline.py
```

The pipeline will print a summary at the end showing how many subjects succeeded/failed.

### 5. View Results

* **Clean Data:** `data/processed/{subject}_cleaned/`
* **Visual Reports:** `reports/{subject}/`
* **PDF Reports:** `reports/{subject}/{subject}_Detailed_Report.pdf`
* **Logs:** `logs/pipeline.log`

---

## Ethics & Privacy

* **No Personal Data:** No raw or processed participant data is committed to this repository.
* **Local Processing:** All cleaning and analysis happen locally on your machine.
* **Compliance:** The pipeline design adheres to standard ethical research guidelines for health data handling.

---

## Technologies Used

* **Python 3.10+**
* **Pandas** (Data Manipulation)
* **Seaborn & Matplotlib** (Visualization)
* **FPDF** (PDF Report Generation)
* **PyYAML** (Configuration Management)
* **OpenPyXL** (Excel I/O)

---

## Author

**Maeve Fernandes**
MSc Software Technology
Research focus: Health Data Analysis & Applied Data Science