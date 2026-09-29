import os
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import TimeSeriesSplit
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from .features import load_data, extract_features

def prepare_train_test(df, test_size=0.2):
    # Sort chronologically
    df = df.sort_values('order_date')
    
    # Split chronologically
    n_samples = len(df)
    train_size = int(n_samples * (1 - test_size))
    
    train_df = df.iloc[:train_size]
    test_df = df.iloc[train_size:]
    
    features = [
        'variant_id', 'base_price', 'days_since_release', 'expected_decay', 'discount_rate', 'is_holiday_or_campaign', 
        'rolling_mean_7d', 'rolling_mean_14d', 'day_of_week', 'month'
    ]
    target = 'daily_sales'
    
    X_train = train_df[features]
    y_train = train_df[target]
    
    X_test = test_df[features]
    y_test = test_df[target]
    
    return X_train, y_train, X_test, y_test

def train_and_evaluate():
    print("Loading data...")
    raw_df = load_data()
    print("Extracting features...")
    df = extract_features(raw_df)
    
    X_train, y_train, X_test, y_test = prepare_train_test(df)
    
    models = {
        "Linear Regression": LinearRegression(),
        "Ridge": Ridge(),
        "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42)
    }
    
    results = []
    best_r2 = -float('inf')
    best_model = None
    best_model_name = ""
    
    print("-" * 60)
    print(f"{'Model':<20} | {'MAE':<10} | {'RMSE':<10} | {'R2 Score':<10}")
    print("-" * 60)
    
    for name, model in models.items():
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        
        mae = mean_absolute_error(y_test, preds)
        rmse = np.sqrt(mean_squared_error(y_test, preds))
        r2 = r2_score(y_test, preds)
        
        print(f"{name:<20} | {mae:<10.4f} | {rmse:<10.4f} | {r2:<10.4f}")
        
        if r2 > best_r2:
            best_r2 = r2
            best_model = model
            best_model_name = name
            
    print("-" * 60)
    print(f"Best model: {best_model_name} with R2 = {best_r2:.4f}")
    
    # Save the model
    artifact_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "artifacts")
    os.makedirs(artifact_dir, exist_ok=True)
    
    model_path = os.path.join(artifact_dir, "demand_model.joblib")
    joblib.dump(best_model, model_path)
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    train_and_evaluate()
