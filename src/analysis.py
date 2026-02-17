import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import logging

# Set a professional plotting style
sns.set_theme(style="whitegrid", context="notebook")

def plot_trends(df, file_name, output_dir):
    """
    Detects date columns and plots numeric trends over time.
    """
    # 1. Find the date column
    date_cols = [c for c in df.columns if 'date' in c or 'time' in c]
    if not date_cols:
        return
    
    date_col = date_cols[0]
    df = df.sort_values(by=date_col)
    
    # 2. Identify numeric columns to plot (skip IDs or constant values)
    numeric_cols = df.select_dtypes(include=['number']).columns
    numeric_cols = [c for c in numeric_cols if df[c].nunique() > 1]
    
    # 3. Generate a plot for each key metric (limit to top 5 to avoid clutter)
    for col in numeric_cols[:5]:
        plt.figure(figsize=(12, 6))
        sns.lineplot(data=df, x=date_col, y=col, linewidth=2, color="#2c3e50")
        
        # Formatting
        plt.title(f"Trend over Time: {col.replace('_', ' ').title()}", fontsize=14)
        plt.xlabel("Date", fontsize=12)
        plt.ylabel(col.replace('_', ' ').title(), fontsize=12)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Save
        save_path = os.path.join(output_dir, f"trend_{file_name}_{col}.png")
        plt.savefig(save_path)
        plt.close()

def plot_distributions(df, file_name, output_dir):
    """
    Creates histograms/KDE plots to show data distribution.
    """
    numeric_cols = df.select_dtypes(include=['number']).columns
    numeric_cols = [c for c in numeric_cols if df[c].nunique() > 1]
    
    for col in numeric_cols[:5]:
        plt.figure(figsize=(10, 6))
        sns.histplot(data=df, x=col, kde=True, color="#e74c3c", bins=20)
        
        plt.title(f"Distribution of {col.replace('_', ' ').title()}", fontsize=14)
        plt.xlabel(col.replace('_', ' ').title())
        plt.tight_layout()
        
        save_path = os.path.join(output_dir, f"dist_{file_name}_{col}.png")
        plt.savefig(save_path)
        plt.close()

def plot_correlations(df, file_name, output_dir):
    """
    Generates a heatmap to show relationships between variables.
    """
    numeric_df = df.select_dtypes(include=['number'])
    
    # Need at least 2 columns to correlate
    if numeric_df.shape[1] < 2:
        return

    plt.figure(figsize=(10, 8))
    corr = numeric_df.corr()
    
    # Draw heatmap
    sns.heatmap(
        corr, 
        annot=True, 
        fmt=".2f", 
        cmap='RdBu_r', 
        vmin=-1, 
        vmax=1, 
        linewidths=0.5
    )
    plt.title(f"Correlation Matrix: {file_name}", fontsize=14)
    plt.tight_layout()
    
    save_path = os.path.join(output_dir, f"corr_{file_name}.png")
    plt.savefig(save_path)
    plt.close()

def analyze_subject(subject_name, config):
    """
    Main function to orchestrate analysis for a subject.
    """
    processed_dir = os.path.join(config['paths']['output_dir'], f"{subject_name}_cleaned")
    reports_dir = os.path.join("reports", subject_name)
    os.makedirs(reports_dir, exist_ok=True)
    
    logging.info(f" Generating advanced visuals for: {subject_name}")

    if not os.path.exists(processed_dir):
        logging.warning(f"      No cleaned data found for {subject_name}")
        return

    # Loop through each cleaned Excel file
    for file in os.listdir(processed_dir):
        if not file.endswith(".xlsx"):
            continue
            
        file_path = os.path.join(processed_dir, file)
        # Create a clean name for file (e.g., "sleep_score" instead of "Fitbit_ba_sleep_score")
        short_name = file.replace(".xlsx", "").replace(f"{subject_name}_", "")
        
        try:
            df = pd.read_excel(file_path)
            
            if df.empty:
                continue

            # 1. Generate Statistical Summary
            stats_file = os.path.join(reports_dir, f"stats_{short_name}.csv")
            df.describe().to_csv(stats_file)
            
            # 2. Generate Visualizations
            plot_trends(df, short_name, reports_dir)
            plot_distributions(df, short_name, reports_dir)
            plot_correlations(df, short_name, reports_dir)
                
        except Exception as e:
            logging.error(f"      Analysis failed for {file}: {e}")

    logging.info(f"     ✅ Reports ready in: {reports_dir}")