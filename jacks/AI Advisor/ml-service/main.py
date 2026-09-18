import os
import json
import joblib
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

# Machine Learning imports
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier, XGBRegressor
from sklearn.metrics import (
    accuracy_score, f1_score, precision_score, recall_score,
    mean_absolute_error, mean_squared_error, r2_score
)

app = FastAPI(title="AI Business Advisor ML Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FilePathRequest(BaseModel):
    filepath: str

class QuerySpecRequest(BaseModel):
    filepath: str
    query_spec: Dict[str, Any]

class TrainRequest(BaseModel):
    filepath: str
    target_col: str
    features: Optional[List[str]] = None
    task_type: Optional[str] = "auto" # auto, classification, regression, forecast
    date_col: Optional[str] = None
    model_id: str

class PredictRequest(BaseModel):
    model_path: str
    input_data: List[Dict[str, Any]]

class GenerateChartsRequest(BaseModel):
    filepath: str
    dataset_id: str
    date_col: Optional[str] = None
    target_col: Optional[str] = None
    output_dir: str

def clean_for_json(val: Any) -> Any:
    """Helper to convert numpy types and NaNs to standard JSON serializable types."""
    if isinstance(val, dict):
        return {k: clean_for_json(v) for k, v in val.items()}
    elif isinstance(val, list):
        return [clean_for_json(x) for x in val]
    elif isinstance(val, tuple):
        return tuple(clean_for_json(x) for x in val)
    elif pd.isna(val) or val is None:
        return None
    elif isinstance(val, (np.integer, np.int64, np.int32)):
        return int(val)
    elif isinstance(val, (np.floating, np.float64, np.float32)):
        return float(val)
    elif isinstance(val, np.ndarray):
        return [clean_for_json(x) for x in val.tolist()]
    elif isinstance(val, pd.Series):
        return [clean_for_json(x) for x in val.tolist()]
    else:
        return val

def load_dataframe(filepath: str) -> pd.DataFrame:
    """Load CSV or Excel dataset, auto-detecting CSV separators."""
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail=f"File not found: {filepath}")
    
    _, ext = os.path.splitext(filepath)
    ext = ext.lower()
    
    try:
        if ext in ['.xlsx', '.xls']:
            return pd.read_excel(filepath)
        else:
            # Attempt to auto-detect delimiter using engine='python'
            try:
                return pd.read_csv(filepath, sep=None, engine='python')
            except Exception:
                return pd.read_csv(filepath, encoding='latin1')
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse dataset: {str(e)}")

@app.post("/process")
def process_dataset(req: FilePathRequest):
    df = load_dataframe(req.filepath)
    
    row_count, col_count = df.shape
    duplicates = int(df.duplicated().sum())
    
    columns_info = []
    numeric_cols = []
    date_cols = []
    categorical_cols = []
    
    # Analyze columns
    for col in df.columns:
        col_series = df[col]
        null_count = int(col_series.isna().sum())
        unique_count = int(col_series.nunique())
        
        # Determine basic type
        detected_type = "string"
        if pd.api.types.is_numeric_dtype(col_series):
            detected_type = "numeric"
            numeric_cols.append(col)
        else:
            # Try to see if it's a date
            try:
                parsed_dates = pd.to_datetime(col_series.dropna().head(10), errors='raise')
                if len(parsed_dates) > 0:
                    detected_type = "datetime"
                    date_cols.append(col)
            except Exception:
                pass
            
            if detected_type != "datetime":
                categorical_cols.append(col)
                detected_type = "categorical"
                
        # Sample values
        sample_vals = col_series.dropna().head(5).tolist()
        
        # Stats summary
        stats = {}
        if detected_type == "numeric":
            stats = {
                "mean": float(col_series.mean()) if not col_series.empty else 0,
                "median": float(col_series.median()) if not col_series.empty else 0,
                "min": float(col_series.min()) if not col_series.empty else 0,
                "max": float(col_series.max()) if not col_series.empty else 0,
                "std": float(col_series.std()) if not col_series.empty else 0,
                "q25": float(col_series.quantile(0.25)) if not col_series.empty else 0,
                "q75": float(col_series.quantile(0.75)) if not col_series.empty else 0,
            }
        elif detected_type == "categorical":
            top_vals = col_series.value_counts().head(5).to_dict()
            stats = {
                "top_values": {str(k): int(v) for k, v in top_vals.items()}
            }
            
        columns_info.append({
            "name": col,
            "type": detected_type,
            "nullCount": null_count,
            "uniqueCount": unique_count,
            "sampleValues": clean_for_json(sample_vals),
            "stats": clean_for_json(stats)
        })
        
    # Calculate Correlation Matrix
    corr_matrix = {}
    if len(numeric_cols) > 1:
        corr_df = df[numeric_cols].corr()
        for idx in corr_df.index:
            corr_matrix[idx] = {col: float(val) if not pd.isna(val) else 0.0 for col, val in corr_df.loc[idx].items()}
            
    # Simple outlier detection (IQR method for numeric columns)
    outliers_info = {}
    for col in numeric_cols:
        col_series = df[col].dropna()
        if not col_series.empty:
            q25 = col_series.quantile(0.25)
            q75 = col_series.quantile(0.75)
            iqr = q75 - q25
            lower_bound = q25 - 1.5 * iqr
            upper_bound = q75 + 1.5 * iqr
            outlier_count = int(((col_series < lower_bound) | (col_series > upper_bound)).sum())
            outliers_info[col] = {
                "outlierCount": outlier_count,
                "percentage": float((outlier_count / row_count) * 100) if row_count > 0 else 0
            }
            
    # Generate automatic KPI suggestions (e.g. Sales, Profit columns)
    suggested_kpis = []
    for col in numeric_cols:
        col_lower = col.lower()
        if any(keyword in col_lower for keyword in ["sales", "revenue", "profit", "amount", "total", "cost", "margin"]):
            suggested_kpis.append({
                "column": col,
                "sum": float(df[col].sum()),
                "avg": float(df[col].mean())
            })
            
    summary = {
        "rowCount": row_count,
        "columnCount": col_count,
        "duplicates": duplicates,
        "columns": columns_info,
        "correlationMatrix": corr_matrix,
        "outliers": outliers_info,
        "suggestedKPIs": suggested_kpis
    }
    
    return clean_for_json(summary)

@app.post("/query")
def query_dataset(req: QuerySpecRequest):
    df = load_dataframe(req.filepath)
    spec = req.query_spec
    
    action = spec.get("action")
    if not action:
        raise HTTPException(status_code=400, detail="Action not specified in query spec")
        
    try:
        # 1. Filters
        filters = spec.get("filters", [])
        for f in filters:
            col = f.get("col")
            op = f.get("op")
            val = f.get("val")
            if col in df.columns:
                if op == "==":
                    df = df[df[col] == val]
                elif op == "!=":
                    df = df[df[col] != val]
                elif op == ">":
                    df = df[df[col] > float(val)]
                elif op == "<":
                    df = df[df[col] < float(val)]
                elif op == ">=":
                    df = df[df[col] >= float(val)]
                elif op == "<=":
                    df = df[df[col] <= float(val)]
                elif op == "contains":
                    df = df[df[col].astype(str).str.contains(str(val), case=False, na=False)]

        # 2. Perform actions
        if action == "groupby":
            groupby_col = spec.get("groupby_col")
            target_col = spec.get("target_col")
            agg = spec.get("agg", "sum")
            
            if groupby_col not in df.columns or target_col not in df.columns:
                raise HTTPException(status_code=400, detail=f"Columns {groupby_col} or {target_col} not found")
                
            grouped = df.groupby(groupby_col)[target_col].agg(agg).reset_index()
            # Sort descending for summaries
            grouped = grouped.sort_values(by=target_col, ascending=False)
            result = grouped.to_dict(orient="records")
            
        elif action == "trend":
            date_col = spec.get("date_col")
            target_col = spec.get("target_col")
            freq = spec.get("freq", "ME") # M, W, D, Q, Y. Standard pandas is ME for month end.
            
            if date_col not in df.columns or target_col not in df.columns:
                raise HTTPException(status_code=400, detail=f"Columns {date_col} or {target_col} not found")
                
            temp_df = df.copy()
            temp_df[date_col] = pd.to_datetime(temp_df[date_col])
            
            # Set index to datetime and resample
            temp_df = temp_df.set_index(date_col)
            trend = temp_df[target_col].resample(freq).sum().reset_index()
            trend[date_col] = trend[date_col].dt.strftime('%Y-%m-%d')
            result = trend.to_dict(orient="records")
            
        elif action == "correlation":
            col1 = spec.get("col1")
            col2 = spec.get("col2")
            if col1 not in df.columns or col2 not in df.columns:
                raise HTTPException(status_code=400, detail="Columns not found")
            corr = float(df[col1].corr(df[col2]))
            result = {"correlation": corr}
            
        elif action == "top_records":
            sort_by = spec.get("sort_by")
            limit = int(spec.get("limit", 10))
            ascending = spec.get("ascending", False)
            
            if sort_by not in df.columns:
                raise HTTPException(status_code=400, detail=f"Column {sort_by} not found")
                
            sorted_df = df.sort_values(by=sort_by, ascending=ascending).head(limit)
            result = sorted_df.to_dict(orient="records")
            
        elif action == "stats":
            target_col = spec.get("target_col")
            if target_col not in df.columns:
                raise HTTPException(status_code=400, detail=f"Column {target_col} not found")
            
            col_series = df[target_col]
            if pd.api.types.is_numeric_dtype(col_series):
                result = {
                    "sum": float(col_series.sum()),
                    "mean": float(col_series.mean()),
                    "min": float(col_series.min()),
                    "max": float(col_series.max()),
                    "count": int(col_series.count())
                }
            else:
                top_vals = col_series.value_counts().head(5).to_dict()
                result = {
                    "count": int(col_series.count()),
                    "unique": int(col_series.nunique()),
                    "top_values": {str(k): int(v) for k, v in top_vals.items()}
                }
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported action: {action}")
            
        return clean_for_json(result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

@app.post("/train")
def train_model(req: TrainRequest):
    df = load_dataframe(req.filepath)
    target = req.target_col
    
    if target not in df.columns:
        raise HTTPException(status_code=400, detail=f"Target column '{target}' not found in dataset")
        
    # Determine or validate ML Task
    task_type = req.task_type
    if task_type == "auto":
        target_series = df[target].dropna()
        if pd.api.types.is_numeric_dtype(target_series):
            # Check cardinality
            if target_series.nunique() <= 10:
                task_type = "classification"
            else:
                task_type = "regression"
        else:
            task_type = "classification"
            
    # Drop rows where target is missing
    df = df.dropna(subset=[target])
    
    # Separate features and target
    X = df.drop(columns=[target])
    y = df[target]
    
    # If date_col is specified and it is forecasting
    is_forecast = (task_type == "forecast")
    if is_forecast:
        date_col = req.date_col
        if not date_col or date_col not in df.columns:
            raise HTTPException(status_code=400, detail="Forecasting requires a valid 'date_col'")
        
        # Force sort by date
        df[date_col] = pd.to_datetime(df[date_col])
        df = df.sort_values(by=date_col)
        X = df.drop(columns=[target])
        y = df[target]
        
    # Filter features if specified
    if req.features:
        # Keep features that actually exist in the dataframe
        valid_features = [f for f in req.features if f in X.columns]
        X = X[valid_features]
        
    # Separate numeric and categorical features
    numeric_features = X.select_dtypes(include=['int64', 'float64', 'int32', 'float32']).columns.tolist()
    categorical_features = X.select_dtypes(include=['object', 'category', 'bool']).columns.tolist()
    
    # Clean datetime fields out of standard features if present and not forecasting
    # If forecasting, we might extract date components
    if is_forecast:
        # Extract features from date_col
        df_time = pd.DataFrame()
        df_time['year'] = df[date_col].dt.year
        df_time['month'] = df[date_col].dt.month
        df_time['day'] = df[date_col].dt.day
        df_time['dayofweek'] = df[date_col].dt.dayofweek
        
        # Let's add lag features of the target
        df_time['lag_1'] = y.shift(1)
        df_time['lag_2'] = y.shift(2)
        df_time['lag_3'] = y.shift(3)
        df_time['rolling_mean_3'] = y.shift(1).rolling(3).mean()
        
        # Combine with other numeric features if available
        for col in numeric_features:
            if col != date_col and col != target:
                df_time[col] = X[col]
                
        # Drop rows with NaNs caused by shift
        df_time[target] = y
        df_time = df_time.dropna()
        
        X = df_time.drop(columns=[target])
        y = df_time[target]
        
        numeric_features = X.columns.tolist()
        categorical_features = []
        
    # Preprocessing pipelines
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ],
        remainder='drop'
    )
    
    # Train / Test split
    if is_forecast:
        # Time series split: preserve order
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    else:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
    # Select Model
    metrics = {}
    model = None
    
    if task_type == "classification":
        # Check class balance
        model = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('classifier', XGBClassifier(random_state=42, use_label_encoder=False, eval_metric='logloss'))
        ])
        
        # Fit model
        model.fit(X_train, y_train)
        
        # Predict
        preds = model.predict(X_test)
        
        metrics = {
            "accuracy": float(accuracy_score(y_test, preds)),
            "f1_score": float(f1_score(y_test, preds, average='weighted', zero_division=0)),
            "precision": float(precision_score(y_test, preds, average='weighted', zero_division=0)),
            "recall": float(recall_score(y_test, preds, average='weighted', zero_division=0))
        }
        
    elif task_type in ["regression", "forecast"]:
        model = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('regressor', XGBRegressor(random_state=42))
        ])
        
        # Fit model
        model.fit(X_train, y_train)
        
        # Predict
        preds = model.predict(X_test)
        
        mae = mean_absolute_error(y_test, preds)
        rmse = np.sqrt(mean_squared_error(y_test, preds))
        r2 = r2_score(y_test, preds)
        
        metrics = {
            "mae": float(mae),
            "rmse": float(rmse),
            "r2_score": float(r2)
        }
        
    # Calculate Feature Importances
    feature_importances = {}
    try:
        # Get feature names after preprocessing
        # Extract preprocessor fitted model
        fitted_preprocessor = model.named_steps['preprocessor']
        
        # Numerical feature names
        num_cols = numeric_features
        
        # Categorical feature names after OneHot
        cat_cols = []
        if len(categorical_features) > 0:
            try:
                cat_encoder = fitted_preprocessor.named_transformers_['cat'].named_steps['onehot']
                cat_cols = list(cat_encoder.get_feature_names_out(categorical_features))
            except Exception:
                # Fallback if cat encoding fails
                cat_cols = [f"{col}_encoded" for col in categorical_features]
                
        all_features = num_cols + cat_cols
        
        # Extract estimator
        estimator = model.steps[-1][1]
        importances = estimator.feature_importances_
        
        # Match features with importances
        for name, imp in zip(all_features, importances):
            feature_importances[name] = float(imp)
            
        # Sort feature importances
        feature_importances = dict(sorted(feature_importances.items(), key=lambda item: item[1], reverse=True))
    except Exception as e:
        # Fallback if feature importance extraction fails
        feature_importances = {"features_processed": 1.0}
        print("Feature importance extraction error:", str(e))
        
    # Save Model Binary
    model_dir = os.path.join("..", "models")
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, f"{req.model_id}.joblib")
    joblib.dump(model, model_path)
    
    # Store metadata alongside in JSON
    metadata = {
        "model_id": req.model_id,
        "task_type": task_type,
        "target": target,
        "features": list(X.columns),
        "numeric_features": numeric_features,
        "categorical_features": categorical_features,
        "metrics": metrics,
        "feature_importances": feature_importances,
        "is_forecast": is_forecast,
        "date_col": req.date_col if is_forecast else None
    }
    
    meta_path = os.path.join(model_dir, f"{req.model_id}.json")
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)
        
    return clean_for_json(metadata)

@app.post("/predict")
def predict_model(req: PredictRequest):
    if not os.path.exists(req.model_path):
        raise HTTPException(status_code=404, detail="Model binary not found")
        
    try:
        model = joblib.load(req.model_path)
        
        # Load metadata to get features
        meta_path = req.model_path.replace(".joblib", ".json")
        features = None
        if os.path.exists(meta_path):
            with open(meta_path, "r") as f:
                meta = json.load(f)
                features = meta.get("features")
                is_forecast = meta.get("is_forecast", False)
                
        # Convert input data list of dicts to DataFrame
        input_df = pd.DataFrame(req.input_data)
        
        # Filter columns to only what the model expects
        if features:
            for col in features:
                if col not in input_df.columns:
                    # Provide dummy value/nan if missing
                    input_df[col] = np.nan
            input_df = input_df[features]
            
        preds = model.predict(input_df)
        
        return {"predictions": clean_for_json(preds)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.post("/generate-charts")
def generate_charts(req: GenerateChartsRequest):
    df = load_dataframe(req.filepath)
    os.makedirs(req.output_dir, exist_ok=True)
    
    dataset_id = req.dataset_id
    
    # 1. Correlation Matrix Heatmap
    corr_path = None
    numeric_cols = df.select_dtypes(include=['int64', 'float64', 'int32', 'float32']).columns.tolist()
    if len(numeric_cols) > 1:
        try:
            plt.figure(figsize=(10, 8))
            # Limit to top 15 columns if there are too many, to avoid cluttered heatmaps
            subset_cols = numeric_cols[:15]
            corr = df[subset_cols].corr()
            sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5, cbar=True)
            plt.title("Correlation Matrix Heatmap", fontsize=16, fontweight='bold', pad=15)
            plt.tight_layout()
            corr_path = os.path.join(req.output_dir, f"{dataset_id}_correlation.png")
            plt.savefig(corr_path, dpi=150)
            plt.close()
        except Exception as e:
            print(f"Failed to generate correlation chart: {e}")
            plt.close()
            
    # 2. Target Variable Distribution
    dist_path = None
    if req.target_col and req.target_col in df.columns:
        try:
            plt.figure(figsize=(10, 6))
            target_series = df[req.target_col].dropna()
            
            if pd.api.types.is_numeric_dtype(target_series):
                sns.histplot(target_series, kde=True, color="#4F46E5", bins=30)
                plt.title(f"Distribution of {req.target_col}", fontsize=16, fontweight='bold', pad=15)
                plt.xlabel(req.target_col)
                plt.ylabel("Frequency")
            else:
                # Categorical countplot
                top_classes = target_series.value_counts().head(10)
                sns.barplot(x=top_classes.index, y=top_classes.values, palette="viridis")
                plt.title(f"Top 10 Classes of {req.target_col}", fontsize=16, fontweight='bold', pad=15)
                plt.xlabel(req.target_col)
                plt.ylabel("Count")
                plt.xticks(rotation=45, ha='right')
                
            plt.tight_layout()
            dist_path = os.path.join(req.output_dir, f"{dataset_id}_distribution.png")
            plt.savefig(dist_path, dpi=150)
            plt.close()
        except Exception as e:
            print(f"Failed to generate distribution chart: {e}")
            plt.close()
            
    # 3. Trend Plot / Forecast Plot
    trend_path = None
    if req.date_col and req.date_col in df.columns and req.target_col and req.target_col in df.columns:
        try:
            plt.figure(figsize=(12, 6))
            temp_df = df.copy()
            temp_df[req.date_col] = pd.to_datetime(temp_df[req.date_col])
            temp_df = temp_df.sort_values(by=req.date_col)
            
            # Resample by month to get clean trend lines
            temp_df = temp_df.set_index(req.date_col)
            numeric_target = pd.api.types.is_numeric_dtype(temp_df[req.target_col])
            
            if numeric_target:
                monthly_trend = temp_df[req.target_col].resample('ME').sum()
                plt.plot(monthly_trend.index, monthly_trend.values, marker='o', color="#10B981", linewidth=2.5)
                plt.title(f"Monthly Trend: {req.target_col} over Time", fontsize=16, fontweight='bold', pad=15)
                plt.xlabel("Date")
                plt.ylabel(f"Total {req.target_col}")
                plt.grid(True, linestyle="--", alpha=0.5)
            else:
                # Frequency count trend
                monthly_trend = temp_df[req.target_col].resample('ME').count()
                plt.plot(monthly_trend.index, monthly_trend.values, marker='o', color="#3B82F6", linewidth=2.5)
                plt.title(f"Monthly Event Frequencies over Time", fontsize=16, fontweight='bold', pad=15)
                plt.xlabel("Date")
                plt.ylabel("Count")
                plt.grid(True, linestyle="--", alpha=0.5)
                
            plt.tight_layout()
            trend_path = os.path.join(req.output_dir, f"{dataset_id}_trend.png")
            plt.savefig(trend_path, dpi=150)
            plt.close()
        except Exception as e:
            print(f"Failed to generate trend chart: {e}")
            plt.close()
            
    return {
        "correlationChart": os.path.abspath(corr_path) if corr_path else None,
        "distributionChart": os.path.abspath(dist_path) if dist_path else None,
        "trendChart": os.path.abspath(trend_path) if trend_path else None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
