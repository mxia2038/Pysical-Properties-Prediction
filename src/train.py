#!/usr/bin/env python3
import os
from pathlib import Path

import numpy as np
import pandas as pd
import joblib

from sklearn.pipeline        import Pipeline
from sklearn.impute          import SimpleImputer
from sklearn.preprocessing   import StandardScaler, PolynomialFeatures
from sklearn.compose         import TransformedTargetRegressor
from sklearn.linear_model    import RidgeCV
from sklearn.ensemble        import RandomForestRegressor
from sklearn.neural_network  import MLPRegressor
from sklearn.base            import BaseEstimator, TransformerMixin
from sklearn.model_selection import train_test_split
from sklearn.metrics         import mean_squared_error, r2_score

# ─── CONFIG ────────────────────────────────────────────────────────────────
DATA_DIR    = Path(__file__).parent.parent / "data"
MODELS_DIR  = Path(__file__).parent.parent / "models"
MODELS_DIR.mkdir(exist_ok=True)
LOG_TARGETS = {"viscosity"}   # apply log→exp for viscosity only (HCl uses polynomial without log)
DEGREE      = 3
BUBBLEPOINT_DEGREE = 2  # lower degree for bubble point to reduce overfitting

class AdvancedFeatureEngineer(BaseEstimator, TransformerMixin):
    """Advanced feature engineering for HCl vapor pressure"""
    
    def __init__(self):
        pass
    
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        X_new = X.copy()
        
        # Temperature in Kelvin
        T_K = X_new['X2'] + 273.15
        
        # Basic physics-based features
        X_new['inv_T'] = 1 / T_K
        X_new['log_T'] = np.log(T_K)
        X_new['sqrt_T'] = np.sqrt(T_K)
        
        # Concentration-based features
        X_new['log_X1'] = np.log(X_new['X1'] + 1)
        X_new['sqrt_X1'] = np.sqrt(X_new['X1'])
        X_new['X1_squared'] = X_new['X1'] ** 2
        
        # Interaction terms
        X_new['X1_inv_T'] = X_new['X1'] * X_new['inv_T']
        X_new['X1_log_T'] = X_new['X1'] * X_new['log_T']
        X_new['X1_sqrt_T'] = X_new['X1'] * X_new['sqrt_T']
        
        # Advanced interactions
        X_new['X1_X2'] = X_new['X1'] * X_new['X2']
        X_new['X1_X2_inv_T'] = X_new['X1'] * X_new['X2'] * X_new['inv_T']
        
        # Exponential/logarithmic combinations
        X_new['exp_inv_T'] = np.exp(X_new['inv_T'])
        X_new['X1_exp_inv_T'] = X_new['X1'] * np.exp(X_new['inv_T'])
        
        return X_new

def make_pipeline(log_tf: bool, degree: int = DEGREE, use_rf: bool = False, use_nn: bool = False):
    if use_nn:
        # Neural Network for HCl vapor pressure (best performance)
        nn_reg = MLPRegressor(
            hidden_layer_sizes=(200, 100, 50, 25),
            activation='relu',
            solver='adam',
            alpha=0.001,
            batch_size=32,
            learning_rate='adaptive',
            max_iter=2000,
            random_state=42,
            early_stopping=True,
            validation_fraction=0.1
        )
        
        if log_tf:
            reg = TransformedTargetRegressor(
                regressor=nn_reg,
                func=np.log,
                inverse_func=np.exp
            )
        else:
            reg = nn_reg
        
        return Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler",  StandardScaler()),
            ("reg",     reg)
        ])
    elif use_rf:
        # Random Forest for HCl vapor pressure
        base_reg = RandomForestRegressor(n_estimators=100, random_state=42)
        if log_tf:
            reg = TransformedTargetRegressor(
                regressor=base_reg,
                func=np.log,
                inverse_func=np.exp
            )
        else:
            reg = base_reg
        
        return Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("reg",     reg)
        ])
    else:
        # Ridge regression for other properties
        ridge = RidgeCV(alphas=np.logspace(-6,6,13), cv=5)
        if log_tf:
            reg = TransformedTargetRegressor(
                regressor=ridge,
                func=np.log,
                inverse_func=np.exp
            )
        else:
            reg = ridge

        return Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scale",   StandardScaler()),
            ("poly",    PolynomialFeatures(degree=degree, include_bias=False)),
            ("reg",     reg)
        ])

def main():
    models = {}

    for csv_path in DATA_DIR.glob("*.csv"):
        stem = csv_path.stem  # e.g. "viscosity" or "vapor_pressure"
        df   = pd.read_csv(csv_path)

        # Determine input features based on dataset
        if "bubblepoint" in stem:
            # Bubble point uses X1 (concentration) and X3 (pressure)
            x_cols = ["X1", "X3"]
            y_cols = [c for c in df.columns if c not in ("X1", "X3")]
        elif "concentration" in stem:
            # NaCl concentration uses X2 (temperature) and X4 (density)
            x_cols = ["X2", "X4"]
            y_cols = [c for c in df.columns if c not in ("X2", "X4")]
        else:
            # Other datasets use X1 (concentration) and X2 (temperature)
            x_cols = ["X1", "X2"]
            y_cols = [c for c in df.columns if c not in ("X1", "X2")]
        
        if len(y_cols) != 1:
            raise ValueError(f"{csv_path.name} must have exactly one Y column, got {y_cols}")
        y_col = y_cols[0]

        X = df[x_cols]
        y = df[y_col]
        
        # Feature engineering for HCl vapor pressure
        if "HCl" in stem and "vapor_pressure" in stem:
            # Use advanced feature engineering for Neural Network
            feature_eng = AdvancedFeatureEngineer()
            X = feature_eng.fit_transform(X)
        
        X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)

        # Use Neural Network with log transform for HCl vapor pressure (best performance)
        if "HCl" in stem and "vapor_pressure" in stem:
            pipe = make_pipeline(log_tf=True, use_nn=True)  # Neural Network with log transform
        elif "bubblepoint" in stem:
            pipe = make_pipeline(log_tf=any(target in stem for target in LOG_TARGETS), degree=BUBBLEPOINT_DEGREE)
        elif "NaOH_density" in stem:
            pipe = make_pipeline(log_tf=any(target in stem for target in LOG_TARGETS), degree=2)  # Lower degree to prevent unphysical behavior
        else:
            pipe = make_pipeline(log_tf=any(target in stem for target in LOG_TARGETS))
        pipe.fit(X_tr, y_tr)

        # evaluate
        y_pred = pipe.predict(X_te)
        rmse   = np.sqrt(mean_squared_error(y_te, y_pred))
        r2     = r2_score(y_te, y_pred)
        print(f"{stem:15s} -> RMSE: {rmse:.4f},  R2: {r2:.4f}")

        # Store the actual features used (including engineered features)
        actual_features = list(X.columns)
        models[stem] = {"model": pipe, "features": actual_features}

    # persist all pipelines in one file
    out_path = MODELS_DIR / "pipelines_by_target.pkl"
    joblib.dump(models, out_path)
    print(f"\nSaved {len(models)} models to {out_path}")

if __name__ == "__main__":
    main()
