# Analysis of Behavioural and Physiological Trends in Type 2 Diabetes Using Fitbit Data

A modular, production-ready MLOps pipeline designed to ingest, clean, and analyze physiological data from Fitbit devices. This project transforms raw Fitbit exports into clean, structured, analysis-ready datasets, enabling reliable study of physiological trends such as glucose levels, sleep quality, heart rate, and stress metrics.



> **Note:** This repository contains the **code and methodology only**. Raw Fitbit data is intentionally excluded for privacy, ethics, and storage constraints.

---

## Objectives

* **Build a Reproducible Pipeline:** Move from manual notebooks to a scalable Python package.
* **Participant-Wise Processing:** Ingest and clean data for specific subjects (e.g., `Fitbit_ba`, `Fitbit_lo`).
* **Signal Separation:** Automatically separate distinct physiological signals (Heart Rate, SpO2, Sleep) into dedicated datasets.
* **Automated Analysis:** Generate time-series trends, distributions, and correlation maps automatically.
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
│   └── pipeline.log         # Execution logs for debugging
├── reports/                 # (Ignored) Generated graphs and CSV stats
├── src/
│   ├── __init__.py
│   ├── ingestion.py         # Logic for reading and merging files (Stage 1)
│   ├── cleaning.py          # Logic for standardization & validation (Stage 2)
│   ├── analysis.py          # Logic for visualization & reporting
│   └── utils.py             # Helpers for logging and config loading
├── run_pipeline.py          # Main execution script
├── requirements.txt         # Project dependencies
└── README.md

```

---

## Data Processing Pipeline

The pipeline operates in three distinct stages, fully automated via `run_pipeline.py`.

### Stage 1: Ingestion & Structural Preprocessing

* **Participant-wise crawling:** Recursively searches `data/raw/` for specific subject folders.
* **Idempotency Check:** Smartly skips files that have already been processed to save time.
* **Merging:** Combines multiple export files for the same category into a single DataFrame.

### Stage 2: Analytical Cleaning

* **Standardization:** Normalizes column names (`snake_case`) and fixes mixed date formats.
* **Sanitization:** Removes null-only rows, duplicates, and non-numeric signal errors.
* **Output:** Saves clean, compressed Excel files to `data/processed/`.

### Stage 3: Automated Analysis

* **Trend Analysis:** Generates line charts for time-series data (e.g., Glucose over time).
* **Distribution:** Creates histograms to visualize data spread (e.g., Daily Step Counts).
* **Correlations:** Produces heatmaps to identify relationships between metrics (e.g., Sleep Score vs. Activity).

---

## How to Use (Locally)

### 1. Setup Environment

```bash
# Clone the repo
git clone [https://github.com/AssassinMaeve/Fitbit.git](https://github.com/your-username/Fitbit.git)
cd Fitbit

# Install dependencies
pip install -r requirements.txt

# Install package in editable mode
pip install -e .

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

### 5. View Results

* **Clean Data:** `data/processed/{subject}_cleaned/`
* **Visual Reports:** `reports/{subject}/`
* **Logs:** `logs/pipeline.log`

---

## Ethics & Privacy

* **No Personal Data:** No raw or processed participant data is committed to this repository.
* **Local Processing:** All cleaning and analysis happen locally on your machine.
* **Compliance:** The pipeline design adheres to standard ethical research guidelines for health data handling.

---
graph TD
    %% Nodes
    Config[config/config.yaml]:::config
    Raw[data/raw/]:::data
    
    Orch(run_pipeline.py):::script
    
    subgraph "src/ Module"
        Ingest[ingestion.py]:::script
        Clean[cleaning.py]:::script
        Analyze[analysis.py]:::script
    end
    
    Processed[data/processed/]:::data
    Reports[reports/]:::data
    Log[logs/pipeline.log]:::logs

    %% Flows
    Config --> Orch
    Raw --> Ingest
    Orch --> Ingest
    Ingest --> Clean
    Clean --> Processed
    Processed --> Analyze
    Orch --> Analyze
    Analyze --> Reports
    
    %% Logging (Dashed)
    Orch -.-> Log
    Ingest -.-> Log
    Clean -.-> Log
    Analyze -.-> Log

    %% Styling
    classDef config fill:#fff2cc,stroke:#d6b656,stroke-width:2px;
    classDef data fill:#dae8fc,stroke:#6c8ebf,stroke-width:2px;
    classDef script fill:#d5e8d4,stroke:#82b366,stroke-width:2px;
    classDef logs fill:#f5f5f5,stroke:#666666,stroke-width:2px,stroke-dasharray: 5 5;
## Technologies Used

* **Python 3.10+**
* **Pandas** (Data Manipulation)
* **Seaborn & Matplotlib** (Visualization)
* **PyYAML** (Configuration Management)
* **OpenPyXL** (Excel I/O)

---

## Author

**Maeve Fernandes**
MSc Software Technology
Research focus: Health Data Analysis & Applied Data Science

```

```