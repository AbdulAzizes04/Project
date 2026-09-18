"""
Tests for Data Preprocessing and Feature Engineering
"""
import os
import pytest
import pandas as pd
import numpy as np
from ml.preprocess import clean_data, build_preprocessor, NUMERICAL_COLS, CATEGORICAL_COLS

def test_clean_data_handles_blood_pressure():
    sample_df = pd.DataFrame({
        "Person ID": [1],
        "Gender": ["Male"],
        "Age": [30],
        "Occupation": ["Doctor"],
        "Sleep Duration": [7.0],
        "Quality of Sleep": [7],
        "Physical Activity Level": [60],
        "Stress Level": [5],
        "BMI Category": ["Normal Weight"],
        "Blood Pressure": ["125/80"],
        "Heart Rate": [72],
        "Daily Steps": [8000],
        "Sleep Disorder": [np.nan]
    })
    cleaned = clean_data(sample_df)
    assert "Person ID" not in cleaned.columns
    assert cleaned["BMI Category"].iloc[0] == "Normal"
    assert cleaned["Sleep Disorder"].iloc[0] == "None"
    assert cleaned["Systolic_BP"].iloc[0] == 125.0
    assert cleaned["Diastolic_BP"].iloc[0] == 80.0

def test_preprocessor_transformation():
    sample_df = pd.DataFrame({
        "Gender": ["Female"],
        "Age": [40],
        "Occupation": ["Nurse"],
        "Sleep Duration": [6.5],
        "Quality of Sleep": [6],
        "Physical Activity Level": [45],
        "Stress Level": [7],
        "BMI Category": ["Overweight"],
        "Heart Rate": [78],
        "Daily Steps": [5000],
        "Systolic_BP": [130.0],
        "Diastolic_BP": [85.0]
    })
    preprocessor = build_preprocessor()
    preprocessor.fit(sample_df)
    transformed = preprocessor.transform(sample_df)
    assert transformed.shape[0] == 1
    assert transformed.shape[1] >= len(NUMERICAL_COLS)
