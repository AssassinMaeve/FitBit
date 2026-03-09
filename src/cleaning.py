import pandas as pd
import logging


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Standardizes column names to snake_case."""
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )
    return df


def standardize_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Detects and converts date/time columns, removes timezones.
    
    Fix #5: Expanded keyword list to catch columns named 'start', 'end',
    'log', 'day' etc. that contain date values but don't have 'date'/'time'
    in the column name.
    """
    date_keywords = ("date", "time", "start", "end", "log", "day")
    for col in df.columns:
        if any(kw in col for kw in date_keywords):
            df[col] = pd.to_datetime(df[col], errors="coerce", format="mixed")

            # Remove timezone information if present (for Excel compatibility)
            if isinstance(df[col].dtype, pd.DatetimeTZDtype):
                df[col] = df[col].dt.tz_localize(None)
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Applies the full cleaning logic.
    
    Fix #1: Uses median imputation instead of fillna(0). 
    A heart rate of 0 or SpO2 of 0% is biologically impossible —
    median preserves the distribution without introducing impossible values.
    """
    df = normalize_columns(df)
    df = standardize_dates(df)

    # Drop completely empty rows and duplicates
    df.dropna(how="all", inplace=True)
    df.drop_duplicates(inplace=True)

    # Statistical Cleaning: Drop rows where ALL numeric values are missing
    numeric_cols = df.select_dtypes(include="number").columns
    if len(numeric_cols) > 0:
        df.dropna(subset=numeric_cols, how="all", inplace=True)

        # Median imputation: fill NaN with per-column median
        for col in numeric_cols:
            median_val = df[col].median()
            if pd.notna(median_val):
                df[col] = df[col].fillna(median_val)
            else:
                logging.warning(f"Column '{col}' has no non-null values — cannot impute.")

    return df