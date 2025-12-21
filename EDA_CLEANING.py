# EDA_CLEANING.py
# Implements the exact cleaning steps from the mentor doc.
import pandas as pd
import numpy as np
import os

INPUT = "rawdata.xlsx"
OUT_DIR = "outputs"
OUT_FILE = os.path.join(OUT_DIR, "cleaned_data.xlsx")

def load_data(path=INPUT):
    df = pd.read_excel(path, engine="openpyxl")
    print("✅ Data Loaded. Shape:", df.shape)
    print("Columns:", df.columns.tolist())
    return df

def clean_data(df):
    print("\n🔹 Step A: Drop completely empty columns")
    df = df.dropna(axis=1, how="all")
    print("Columns after dropping empty cols:", df.columns.tolist())

    print("\n🔹 Step B: Remove duplicated columns (keep first occurrence)")
    df = df.loc[:, ~df.columns.duplicated()]
    print("Columns after removing duplicated-named cols:", df.columns.tolist())

    print("\n🔹 Step C: Drop unnecessary columns (mentor doc list)")
    unnecessary = ['Random Notes', 'Extra_Column', 'Empty1', 'Empty2']  # include Empty2 too, safe to drop if exists
    to_drop = [c for c in unnecessary if c in df.columns]
    if to_drop:
        print("Dropping:", to_drop)
        df = df.drop(columns=to_drop)
    else:
        print("No unnecessary columns found to drop.")

    print("\n🔹 Step D: Remove duplicate rows")
    before = df.shape[0]
    df = df.drop_duplicates()
    after = df.shape[0]
    print(f"Removed {before - after} duplicate rows")

    print("\n🔹 Step E: Fill numeric NaNs with mean (numeric columns only)")
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if numeric_cols:
        means = df[numeric_cols].mean(numeric_only=True)
        df[numeric_cols] = df[numeric_cols].fillna(means)
        print("Filled numeric NaNs for:", numeric_cols)
    else:
        print("No numeric columns detected.")

    print("\n🔹 Step F: Rename columns to simpler names (as doc)")
    rename_map = {
        'Study Hours/Day': 'StudyHours',
        'Sleep Hours': 'SleepHours',
        'Social Media Hours': 'SocialMedia',
        'Exercise Hours': 'Exercise',
        'Attention Level (1-10)': 'AttentionLevel',
        # keep Student Name as-is
    }
    intersect = {k: v for k, v in rename_map.items() if k in df.columns}
    if intersect:
        df = df.rename(columns=intersect)
        print("Renamed columns:", intersect)
    else:
        print("No columns to rename from map (check exact names).")

    # Trim whitespace in string columns
    for c in df.select_dtypes(include=['object']).columns:
        df[c] = df[c].astype(str).str.strip()

    # Final check: reorder columns if possible for neatness
    cols = df.columns.tolist()
    preferred_order = ['Student Name', 'StudyHours', 'SleepHours', 'SocialMedia', 'Exercise', 'AttentionLevel']
    final_order = [c for c in preferred_order if c in cols] + [c for c in cols if c not in preferred_order]
    df = df[final_order]

    print("\n🔹 Final columns and shape:", df.shape, df.columns.tolist())
    return df

def save_df(df, path=OUT_FILE):
    os.makedirs(OUT_DIR, exist_ok=True)
    df.to_excel(path, index=False, engine="openpyxl")
    print("\n✅ Cleaned data saved to:", path)

def main():
    df = load_data()
    df_clean = clean_data(df)
    save_df(df_clean)

    print("\n-- Quick stats after cleaning --")
    print(df_clean.info())
    print("\nMissing counts:\n", df_clean.isna().sum())
    print("\nSample rows:\n", df_clean.head().to_string(index=False))

if __name__ == "__main__":
    main()
