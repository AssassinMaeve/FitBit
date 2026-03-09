import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import os
import logging
import warnings
import math

# Suppress matplotlib categorical-string warnings (Fix #4 — log spam)
warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")

sns.set_theme(style="whitegrid", context="notebook")

# Maximum number of metric columns to plot per chart
MAX_PLOT_COLS = 4


def get_date_col(df):
    """Find the first date/time column in a DataFrame."""
    date_keywords = ("date", "time", "start", "end", "log", "day")
    date_cols = [c for c in df.columns if any(kw in c for kw in date_keywords)]
    return date_cols[0] if date_cols else None


def plot_periodic_summary(df, date_col, metric_key, output_dir, freq='W'):
    """Generate periodic (weekly/monthly) summary CSVs and charts.

    Fix #3: Plots up to MAX_PLOT_COLS columns in a subplot grid.
    Fix #4: Uses native datetime axis via matplotlib.dates instead of strftime strings.
    """
    try:
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        # Filter: Only keep columns with actual non-zero data
        valid_cols = [col for col in numeric_cols if (df[col] != 0).sum() > 0]

        if not valid_cols:
            return

        # Ensure the date column is proper datetime
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        df = df.dropna(subset=[date_col])

        summary = df.resample(freq, on=date_col)[valid_cols].mean().dropna(how='all')
        if summary.empty:
            return

        freq_label = "weekly" if freq == 'W' else "monthly"

        # Save CSV for the table
        summary.to_csv(os.path.join(output_dir, f"summary_{freq_label}_{metric_key}.csv"))

        # --- Fix #3: Plot up to MAX_PLOT_COLS columns in subplots ---
        cols_to_plot = valid_cols[:MAX_PLOT_COLS]
        n_cols = len(cols_to_plot)

        if n_cols == 1:
            fig, axes = plt.subplots(1, 1, figsize=(10, 5))
            axes = [axes]  # Normalize to list
        else:
            n_rows_grid = math.ceil(n_cols / 2)
            fig, axes_grid = plt.subplots(n_rows_grid, 2, figsize=(14, 5 * n_rows_grid))
            axes = axes_grid.flatten() if n_cols > 1 else [axes_grid]

        for idx, col in enumerate(cols_to_plot):
            ax = axes[idx]
            # Fix #4: Use native datetime x-axis
            ax.bar(summary.index, summary[col], width=5 if freq == 'W' else 20,
                   color="#3498db", alpha=0.8)
            ax.set_title(f"{col.replace('_', ' ').title()}")
            ax.set_ylabel(col.replace('_', ' ').title())

            # Proper time-axis formatting
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            ax.xaxis.set_major_locator(mdates.AutoDateLocator())
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

        # Hide any unused subplot axes
        for idx in range(n_cols, len(axes)):
            axes[idx].set_visible(False)

        fig.suptitle(f"{freq_label.capitalize()} {metric_key.replace('_', ' ').title()}",
                     fontsize=14, fontweight='bold')
        fig.tight_layout()

        plt.savefig(os.path.join(output_dir, f"{freq_label}_{metric_key}.png"), dpi=150)
        plt.close(fig)

    except Exception as e:
        logging.warning(f"Analysis error for {metric_key} ({freq}): {e}")


def generate_eda(df, metric_key, output_dir):
    """Generate Exploratory Data Analysis (EDA) stats and plots."""
    try:
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        valid_cols = [col for col in numeric_cols if (df[col] != 0).sum() > 0]
        if not valid_cols:
            return

        # 1. Descriptive Stats
        stats = []
        for col in valid_cols:
            series = df[col].dropna()
            if len(series) < 2:
                continue
            stats.append({
                'Metric': col.replace('_', ' ').title(),
                'Mean': series.mean(),
                'Min': series.min(),
                '25%': series.quantile(0.25),
                'Median': series.median(),
                '75%': series.quantile(0.75),
                'Max': series.max(),
                'Skewness': series.skew()
            })
        
        if stats:
            stats_df = pd.DataFrame(stats)
            stats_df.to_csv(os.path.join(output_dir, f"eda_stats_{metric_key}.csv"), index=False)

        # 2. Distribution Plots
        cols_to_plot = valid_cols[:MAX_PLOT_COLS]
        n_cols = len(cols_to_plot)
        if n_cols > 0:
            if n_cols == 1:
                fig, axes = plt.subplots(1, 1, figsize=(10, 5))
                axes = [axes]
            else:
                n_rows_grid = math.ceil(n_cols / 2)
                fig, axes_grid = plt.subplots(n_rows_grid, 2, figsize=(14, 5 * n_rows_grid))
                axes = axes_grid.flatten() if n_cols > 1 else [axes_grid]

            for idx, col in enumerate(cols_to_plot):
                ax = axes[idx]
                sns.histplot(df[col].dropna(), kde=True, ax=ax, color="#2ecc71")
                ax.set_title(f"Distribution of {col.replace('_', ' ').title()}")
                ax.set_xlabel("Value")
                ax.set_ylabel("Frequency")

            for idx in range(n_cols, len(axes)):
                axes[idx].set_visible(False)

            fig.suptitle(f"Exploratory Data Analysis: {metric_key.replace('_', ' ').title()}",
                         fontsize=14, fontweight='bold')
            fig.tight_layout()
            plt.savefig(os.path.join(output_dir, f"eda_dist_{metric_key}.png"), dpi=150)
            plt.close(fig)

        # 3. Correlation Heatmap
        corr_cols = [c for c in valid_cols if 'id' not in c.lower() and 'log' not in c.lower()]
        if len(corr_cols) > 1:
            fig, ax = plt.subplots(figsize=(10, 8))
            corr = df[corr_cols].corr()
            sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax, fmt=".2f",
                        annot_kws={"size": 8})
            ax.set_title(f"Correlation Matrix: {metric_key.replace('_', ' ').title()}")
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right', rotation_mode='anchor')
            fig.tight_layout()
            plt.savefig(os.path.join(output_dir, f"eda_corr_{metric_key}.png"), dpi=150)
            plt.close(fig)

    except Exception as e:
        logging.warning(f"EDA error for {metric_key}: {e}")


def analyze_subject(subject_name, config):
    """Run analysis for a single subject.

    Fix #2: Distinguishes HRV (Heart Rate Variability) files from Heart Rate.
    Fix #14: Reads ALL sheets from multi-sheet Excel files.
    """
    processed_dir = os.path.join(config['paths']['output_dir'], f"{subject_name}_cleaned")
    reports_dir = os.path.join(
        config['paths'].get('reports_dir', 'reports'), subject_name
    )
    os.makedirs(reports_dir, exist_ok=True)

    # Skip if already processed and force_rerun is not enabled
    force_rerun = config['settings'].get('force_rerun', False)
    if not force_rerun and os.path.isdir(reports_dir):
        existing_csvs = [f for f in os.listdir(reports_dir) if f.startswith('summary_weekly_') and f.endswith('.csv')]
        if existing_csvs:
            logging.info(f"   ⏭  Skipping analysis for {subject_name} (results already exist. Set force_rerun: true to regenerate)")
            return

    # Keyword → metric mapping
    keywords = {
        "heart": "heart_rate",
        "glucose": "glucose",
        "sleep": "sleep_score",
        "stress": "stress_score",
        "oxygen": "oxygen",
        "spo2": "oxygen",
        "activity": "activity",
        "steps": "activity"
    }

    # Fix #2: Exclusion keywords — if filename contains these, override the metric
    hrv_exclusion_keywords = ("variability", "hrv")

    logging.info(f"📊 Scanning for data in: {processed_dir}")

    if not os.path.isdir(processed_dir):
        logging.warning(f"   Processed directory not found: {processed_dir}")
        return

    for file in os.listdir(processed_dir):
        if not file.endswith(".parquet"):
            continue

        file_lower = file.lower()

        # Find which metric this file belongs to
        metric_key = None
        for key, value in keywords.items():
            if key in file_lower:
                metric_key = value
                break

        # Fix #2: If it's a heart_rate match but contains HRV indicators, reclassify
        if metric_key == "heart_rate" and any(ex in file_lower for ex in hrv_exclusion_keywords):
            metric_key = "hrv"
            logging.info(f"     Reclassified as HRV (not HR): {file}")

        if metric_key:
            logging.info(f"     Found {metric_key} data in: {file}")

            # Fix #14: Read parquet file directly
            filepath = os.path.join(processed_dir, file)
            try:
                df = pd.read_parquet(filepath)
            except Exception as e:
                logging.warning(f"     Failed to read {file}: {e}")
                continue

            date_col = get_date_col(df)

            if date_col:
                plot_periodic_summary(df, date_col, metric_key, reports_dir, freq='W')
                plot_periodic_summary(df, date_col, metric_key, reports_dir, freq='ME')
                generate_eda(df, metric_key, reports_dir)
            else:
                logging.warning(f"     No date column found in {file} — skipping analysis")