"""
Sleep Disorder AI - Data Preprocessing & EDA Pipeline
"""
import os
import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

TARGET_COLUMN = "Sleep Disorder"
TARGET_MAPPING = {"None": 0, "Insomnia": 1, "Sleep Apnea": 2}
REVERSE_TARGET_MAPPING = {0: "None", 1: "Insomnia", 2: "Sleep Apnea"}

NUMERICAL_COLS = [
    "Age",
    "Sleep Duration",
    "Quality of Sleep",
    "Physical Activity Level",
    "Stress Level",
    "Heart Rate",
    "Daily Steps",
    "Systolic_BP",
    "Diastolic_BP"
]

CATEGORICAL_COLS = [
    "Gender",
    "Occupation",
    "BMI Category"
]

def load_and_inspect_dataset(filepath="data/dataset.csv"):
    """
    Loads raw dataset, prints full EDA metrics, and returns raw DataFrame.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Dataset not found at {filepath}")
    
    df = pd.read_csv(filepath)
    print("=" * 60)
    print("EXPLORATORY DATA ANALYSIS (EDA)")
    print("=" * 60)
    print(f"1. Dataset Shape: {df.shape[0]} rows, {df.shape[1]} columns")
    print(f"2. Raw Columns: {list(df.columns)}")
    print("\n3. Missing Values per Column:")
    print(df.isnull().sum())
    print(f"\n4. Duplicate Records: {df.duplicated().sum()}")
    print("\n5. Raw Target Distribution ('Sleep Disorder'):")
    print(df[TARGET_COLUMN].value_counts(dropna=False))
    print("=" * 60)
    return df

def clean_data(df):
    """
    Cleans raw DataFrame:
    - Drops Person ID identifier
    - Imputes missing Sleep Disorder with 'None'
    - Standardizes BMI Category ('Normal Weight' -> 'Normal')
    - Parses 'Blood Pressure' into Systolic_BP and Diastolic_BP
    """
    cleaned = df.copy()
    
    if "Person ID" in cleaned.columns:
        cleaned = cleaned.drop(columns=["Person ID"])
    
    # 1. Impute missing target as 'None' (dataset standard for healthy controls)
    cleaned[TARGET_COLUMN] = cleaned[TARGET_COLUMN].fillna("None").astype(str).str.strip()
    
    # 2. Standardize BMI Category
    cleaned["BMI Category"] = cleaned["BMI Category"].replace({"Normal Weight": "Normal"}).str.strip()
    
    # 3. Parse Blood Pressure
    if "Blood Pressure" in cleaned.columns:
        bp_split = cleaned["Blood Pressure"].astype(str).str.split("/", expand=True)
        cleaned["Systolic_BP"] = pd.to_numeric(bp_split[0], errors="coerce")
        cleaned["Diastolic_BP"] = pd.to_numeric(bp_split[1], errors="coerce")
        cleaned = cleaned.drop(columns=["Blood Pressure"])
        
    return cleaned

def build_preprocessor():
    """
    Builds a Scikit-Learn ColumnTransformer for numerical scaling and categorical encoding.
    """
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERICAL_COLS),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL_COLS)
        ]
    )
    return preprocessor

def prepare_data(filepath="data/dataset.csv", output_dir="models"):
    """
    Complete data preparation pipeline:
    - Loads raw dataset and runs EDA
    - Cleans data
    - Fits preprocessor on X
    - Returns X_raw, y, preprocessor, feature_names
    """
    os.makedirs(output_dir, exist_ok=True)
    df_raw = load_and_inspect_dataset(filepath)
    df_clean = clean_data(df_raw)
    
    X = df_clean.drop(columns=[TARGET_COLUMN])
    y_raw = df_clean[TARGET_COLUMN]
    
    # Map target classes to numeric codes
    y = y_raw.map(TARGET_MAPPING).values
    
    preprocessor = build_preprocessor()
    preprocessor.fit(X)
    
    # Extract feature names after OneHotEncoding
    ohe = preprocessor.named_transformers_["cat"]
    cat_feature_names = list(ohe.get_feature_names_out(CATEGORICAL_COLS))
    all_feature_names = NUMERICAL_COLS + cat_feature_names
    
    # Save preprocessor and feature names
    joblib.dump(preprocessor, os.path.join(output_dir, "preprocessor.pkl"))
    joblib.dump(all_feature_names, os.path.join(output_dir, "feature_names.pkl"))
    
    print(f"\n[OK] Preprocessor saved to {os.path.join(output_dir, 'preprocessor.pkl')}")
    print(f"[OK] Total processed features ({len(all_feature_names)}): {all_feature_names}")
    
    return X, y, preprocessor, all_feature_names

if __name__ == "__main__":
    prepare_data()
