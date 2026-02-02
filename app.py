import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ---------------- FIX STREAMLIT SCALING ----------------
plt.rcParams["figure.dpi"] = 100
plt.rcParams["savefig.dpi"] = 100

SMALL_FIG = (4, 2.5)

st.set_page_config(
    page_title="Fitbit Health Analytics",
    layout="wide"
)

st.title("Fitbit Behavioural & Physiological Analysis")

# ---------------- Participant Selector ----------------
person = st.selectbox(
    "Select Participant",
    ["Fitbit_Ir", "Fitbit_ba", "Fitbit_lo", "Fitbit_su", "Fitbit_vi"]
)

BASE_DIR = f"cleaned_output/{person}_cleaned"

# ---------------- Load Data Safely ----------------
def load_excel(filename):
    try:
        return pd.read_excel(f"{BASE_DIR}/{filename}")
    except:
        return None

sleep_df = load_excel(f"{person}_sleep_score_cleaned.xlsx")
stress_df = load_excel(f"{person}_stress_score_cleaned.xlsx")
activity_df = load_excel(f"{person}_active_zone_minutes_(azm)_cleaned.xlsx")
biometric_df = load_excel(f"{person}_biometrics_cleaned.xlsx")

# ---------------- PREPARE GLUCOSE (ONLY IF EXISTS) ----------------
glucose_daily = None

if biometric_df is not None and "value" in biometric_df.columns:
    biometric_df["time"] = pd.to_datetime(biometric_df["time"], errors="coerce")
    biometric_df = biometric_df[biometric_df["value"] > 0]

    glucose_daily = (
        biometric_df
        .groupby(biometric_df["time"].dt.date)["value"]
        .mean()
        .reset_index(name="avg_glucose")
        .rename(columns={"time": "date"})
    )

# ---------------- OVERVIEW ----------------
st.header("Overview")

cols = st.columns(4 if glucose_daily is not None else 3)

if sleep_df is not None:
    cols[0].metric("Avg Sleep Score", round(sleep_df["overall_score"].mean(), 1))

if stress_df is not None:
    cols[1].metric("Avg Stress Score", round(stress_df["stress_score"].mean(), 1))

if activity_df is not None:
    activity_df["date"] = pd.to_datetime(activity_df["date_time"], errors="coerce").dt.date
    daily_activity = (
        activity_df.groupby("date")["total_minutes"]
        .sum()
        .reset_index()
    )
    cols[2].metric("Avg Active Minutes", int(daily_activity["total_minutes"].mean()))

if glucose_daily is not None:
    cols[3].metric("Avg Glucose (mg/dL)", round(glucose_daily["avg_glucose"].mean(), 1))

st.divider()

# ====================== TRENDS (SIDE BY SIDE) ======================
st.header("Trends")

col1, col2 = st.columns(2)

# ---- Sleep Trend ----
if sleep_df is not None:
    sleep_df["date"] = pd.to_datetime(
        sleep_df["timestamp"], errors="coerce"
    ).dt.date

    fig, ax = plt.subplots(figsize=SMALL_FIG)
    ax.plot(sleep_df["date"], sleep_df["overall_score"], marker="o")
    ax.set_ylabel("Sleep Score")
    ax.set_xlabel("Date")
    ax.tick_params(axis="x", rotation=45)
    plt.tight_layout()

    col1.subheader("Sleep Score")
    col1.pyplot(fig, use_container_width=False)

# ---- Stress Trend ----
if stress_df is not None:
    stress_df["date"] = pd.to_datetime(
        stress_df["date"], errors="coerce"
    ).dt.date

    fig, ax = plt.subplots(figsize=SMALL_FIG)
    ax.plot(
        stress_df["date"],
        stress_df["stress_score"],
        marker="s",
        color="red"
    )
    ax.set_ylabel("Stress Score")
    ax.set_xlabel("Date")
    ax.tick_params(axis="x", rotation=45)
    plt.tight_layout()

    col2.subheader("Stress Score")
    col2.pyplot(fig, use_container_width=False)

st.divider()

col3, col4 = st.columns(2)

# ---- Activity Trend ----
if activity_df is not None:
    fig, ax = plt.subplots(figsize=SMALL_FIG)
    ax.bar(daily_activity["date"], daily_activity["total_minutes"])
    ax.set_ylabel("Active Minutes")
    ax.set_xlabel("Date")
    ax.tick_params(axis="x", rotation=45)
    plt.tight_layout()

    col3.subheader("Physical Activity")
    col3.pyplot(fig, use_container_width=False)

# ---- Glucose Trend ----
if glucose_daily is not None:
    fig, ax = plt.subplots(figsize=SMALL_FIG)
    ax.plot(glucose_daily["date"], glucose_daily["avg_glucose"], marker="o")
    ax.set_ylabel("Avg Glucose (mg/dL)")
    ax.set_xlabel("Date")
    ax.tick_params(axis="x", rotation=45)
    plt.tight_layout()

    col4.subheader("Glucose")
    col4.pyplot(fig, use_container_width=False)

st.divider()

# ====================== CORRELATION ======================
st.header("Multi-Metric Correlation")

dfs = []

if sleep_df is not None:
    dfs.append(
        sleep_df[["date", "overall_score"]]
        .rename(columns={"overall_score": "sleep_score"})
    )

if stress_df is not None:
    dfs.append(stress_df[["date", "stress_score"]])

if activity_df is not None:
    dfs.append(
        daily_activity.rename(columns={"total_minutes": "active_minutes"})
    )

if glucose_daily is not None:
    dfs.append(glucose_daily)

if len(dfs) >= 2:
    merged = dfs[0]
    for df in dfs[1:]:
        merged = pd.merge(merged, df, on="date", how="inner")

    corr = merged.select_dtypes("number").corr()

    fig, ax = plt.subplots(figsize=SMALL_FIG)
    sns.heatmap(
        corr,
        annot=True,
        cmap="coolwarm",
        fmt=".2f",
        annot_kws={"size": 7},
        cbar=False,
        ax=ax
    )
    plt.tight_layout()
    st.pyplot(fig, use_container_width=False)
else:
    st.info("Insufficient aligned data for correlation analysis.")
