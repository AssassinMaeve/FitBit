import pandas as pd

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Standardizes column names."""
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )
    return df

def standardize_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Detects and converts date/time columns, removes timezones."""
    for col in df.columns:
        if "date" in col or "time" in col:
            # FIX: Added format="mixed" to handle varying date formats without warnings
            df[col] = pd.to_datetime(df[col], errors="coerce", format="mixed")
            
            # Remove timezone information if present (for Excel compatibility)
            if isinstance(df[col].dtype, pd.DatetimeTZDtype):
                df[col] = df[col].dt.tz_localize(None)
    return df

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Applies the full cleaning logic."""
    df = normalize_columns(df)
    df = standardize_dates(df)
    
    # Drop completely empty rows and duplicates
    df.dropna(how="all", inplace=True)
    df.drop_duplicates(inplace=True)

    # Statistical Cleaning: Drop rows where ALL numeric values are missing
    numeric_cols = df.select_dtypes(include="number").columns
    if len(numeric_cols) > 0:
        df.dropna(subset=numeric_cols, how="all", inplace=True)
        df[numeric_cols] = df[numeric_cols].fillna(0)
        
    return df