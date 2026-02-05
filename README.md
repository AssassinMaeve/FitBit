# Fitbit Health Data Analysis & Preprocessing Pipeline

## Project Overview

This repository contains a **data preprocessing and exploratory analysis pipeline** for Fitbit health data.
The goal of the project is to transform **raw Fitbit exports** into **clean, structured, analysis-ready datasets**, enabling reliable study of physiological trends such as:

* Glucose levels
* Sleep quality
* Heart rate
* Physical activity
* Stress and recovery metrics

⚠️ **Raw Fitbit data is intentionally excluded** from this repository for **privacy, ethics, and storage constraints**.

---

## Objectives

* Build a **reproducible data cleaning pipeline**
* Process Fitbit data **participant-wise**
* Separate and clean **individual physiological signals**
* Prepare datasets for **time-series analysis and visualization**
* Explore relationships such as:

  * Glucose vs sleep quality
  * Glucose vs activity
  * Fasting vs post-meal glucose trends

---

## Repository Structure

```
FitBit/
│
├── ⚙️ .gitignore
├── 📄 DataPreprocessing.ipynb
├── 📄 FitBit_Io.ipynb
├── 📄 FitBit_ba.ipynb
├── 📄 FitBit_lr.ipynb
├── 📄 FitBit_su.ipynb
├── 📄 FitBit_vid.ipynb
├── 📄 Fitbit_vi.ipynb
├── 📝 README.md
├── 📄 Visualisations.ipynb
├── 🐍 app.py
└── 📄 dataprocessingpipeline.codediagram
│
└── (Local only – not tracked)
    ├── DataSet/
    ├── cleaned_output/
```

### Tracked Files

* **`DataPreprocessing.ipynb`**
  Implements the full preprocessing pipeline:

  * Folder filtering
  * Cleaning
  * Deduplication
  * Signal-wise separation

* **`Visualisations.ipynb`**
  Exploratory analysis and plots:

  * Time-series trends
  * Daily averages
  * Glucose–sleep–activity relationships

### Ignored Files

* Raw Fitbit exports
* Cleaned Excel outputs
* Large `.csv` / `.xlsx` files

(Handled via `.gitignore`)

---

## 🔬 Data Processing Pipeline

### Stage 1 — Structural Preprocessing

* Process **one participant at a time**
* Filter **only physiological folders**
* Merge multiple Fitbit exports per signal
* Normalize column names and timestamps
* Export **one Excel file per physiological category**

### Stage 2 — Analytical Cleaning

* Remove null-only rows
* Remove duplicate entries
* Remove rows without numeric signal values
* Produce **analysis-ready datasets**

This two-stage approach ensures:

* Scalability
* Transparency
* Research-grade cleanliness

---

## Analysis Focus

Current analyses explore:

* Glucose trends over time
* Daily average glucose
* Fasting vs post-meal glucose
* Associations with:

  * Sleep score
  * Physical activity
  * Time of day

Plots include:

* Line charts (time-series)
* Daily aggregation trends
* Comparative signal analysis

---

## 🔐 Ethics & Privacy

* **No personal or raw Fitbit data is shared**
* All data processing is performed **locally**
* Repository contains **only code and methodology**
* Designed to comply with ethical research standards

---

## 🛠️ Technologies Used

* **Python**
* **Pandas**
* **Matplotlib / Seaborn**
* **Jupyter Notebook**
* **Git & GitHub**

---

## How to Use (Locally)

1. Place Fitbit export inside a local `DataSet/` folder
2. Run `DataPreprocessing.ipynb`
3. Run cleaning scripts to generate cleaned Excel files
4. Perform analysis using `Visualisations.ipynb`

> ⚠️ Fitbit data files are not provided in this repository.

---

## Author

**Maeve Fernandes**
MSc Software Technology
Research focus: Health Data Analysis & Applied Data Science
