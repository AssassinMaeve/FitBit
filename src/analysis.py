import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import logging

sns.set_theme(style="whitegrid", context="notebook")


def get_date_col(df):
    date_cols = [c for c in df.columns if 'date' in c or 'time' in c]
    return date_cols[0] if date_cols else None

def plot_periodic_summary(df, date_col, metric_key, output_dir, freq='W'):
    try:
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        # Filter: Only keep columns with actual data
        valid_cols = [col for col in numeric_cols if (df[col] != 0).sum() > 0]
        
        if not valid_cols: return

        summary = df.resample(freq, on=date_col)[valid_cols].mean().dropna(how='all')
        if summary.empty: return

        freq_label = "weekly" if freq == 'W' else "monthly"
        # Save CSV for the table
        summary.to_csv(os.path.join(output_dir, f"summary_{freq_label}_{metric_key}.csv"))

        # Save Plot for the PDF
        for col in valid_cols[:1]: # Take the primary metric
            plt.figure(figsize=(10, 5))
            x_data = summary.index.strftime('%Y-%m-%d')
            sns.barplot(x=x_data, y=summary[col], color="#3498db")
            plt.title(f"{freq_label.capitalize()} {metric_key.replace('_', ' ').title()}")
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # CRITICAL: Save with a clean name the reporter expects
            plt.savefig(os.path.join(output_dir, f"{freq_label}_{metric_key}.png"))
            plt.close()
    except Exception as e:
        logging.warning(f"Analysis error for {metric_key}: {e}")

def analyze_subject(subject_name, config):
    processed_dir = os.path.join(config['paths']['output_dir'], f"{subject_name}_cleaned")
    reports_dir = os.path.join("reports", subject_name)
    os.makedirs(reports_dir, exist_ok=True)
    
    # Smarter Keyword Mapping
    # If the filename contains 'heart', we map it to 'heart_rate'
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

    logging.info(f"📊 Scanning for data in: {processed_dir}")

    for file in os.listdir(processed_dir):
        if not file.endswith(".xlsx"):
            continue
            
        file_lower = file.lower()
        # Find which metric this file belongs to by checking keywords
        metric_key = None
        for key, value in keywords.items():
            if key in file_lower:
                metric_key = value
                break
        
        if metric_key:
            logging.info(f"     Found {metric_key} data in: {file}")
            df = pd.read_excel(os.path.join(processed_dir, file))
            date_col = get_date_col(df)
            
            if date_col:
                plot_periodic_summary(df, date_col, metric_key, reports_dir, freq='W')
                plot_periodic_summary(df, date_col, metric_key, reports_dir, freq='M')