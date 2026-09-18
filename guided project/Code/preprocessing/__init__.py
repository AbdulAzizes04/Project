"""
Preprocessing Package.

Provides data validation, cleaning, missing value imputation, duplicate removal,
dtype conversion, categorical encoding, numerical scaling, outlier capping,
and domain feature engineering pipelines.
"""

from preprocessing.preprocessing import (
    validate_dataset,
    handle_missing_values,
    remove_duplicates,
    convert_dtypes,
    encode_features,
    scale_features,
    handle_outliers,
    remove_constant_and_id_features,
    save_processed_dataset,
    load_processed_dataset,
    preprocess_dataset_pipeline,
)

from preprocessing.feature_engineering import (
    create_transaction_features,
    create_temporal_features,
    create_velocity_features,
    create_balance_features,
    create_recipient_features,
    create_device_features,
    create_location_features,
    create_customer_features,
    create_risk_features,
    create_interaction_features,
    validate_engineered_features,
    feature_engineering_pipeline,
)

__all__ = [
    "validate_dataset",
    "handle_missing_values",
    "remove_duplicates",
    "convert_dtypes",
    "encode_features",
    "scale_features",
    "handle_outliers",
    "remove_constant_and_id_features",
    "save_processed_dataset",
    "load_processed_dataset",
    "preprocess_dataset_pipeline",
    "create_transaction_features",
    "create_temporal_features",
    "create_velocity_features",
    "create_balance_features",
    "create_recipient_features",
    "create_device_features",
    "create_location_features",
    "create_customer_features",
    "create_risk_features",
    "create_interaction_features",
    "validate_engineered_features",
    "feature_engineering_pipeline",
]
