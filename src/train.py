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
from sklearn.model_selection import train_test_split
from sklearn.metrics         import mean_squared_error, r2_score

# ─── CONFIG ────────────────────────────────────────────────────────────────
DATA_DIR    = Path(__file__).parent.parent / "data"
MODELS_DIR  = Path(__file__).parent.parent / "models"
MODELS_DIR.mkdir(exist_ok=True)
LOG_TARGETS = {"viscosity"}   # only apply log→exp for the 'viscosity' model
DEGREE      = 3
BUBBLEPOINT_DEGREE = 2  # lower degree for bubble point to reduce overfitting

def make_pipeline(log_tf: bool, degree: int = DEGREE):
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
        else:
            # Other datasets use X1 (concentration) and X2 (temperature)
            x_cols = ["X1", "X2"]
            y_cols = [c for c in df.columns if c not in ("X1", "X2")]
        
        if len(y_cols) != 1:
            raise ValueError(f"{csv_path.name} must have exactly one Y column, got {y_cols}")
        y_col = y_cols[0]

        X = df[x_cols]
        y = df[y_col]
        X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)

        # Use lower degree for bubble point to reduce overfitting
        if "bubblepoint" in stem:
            pipe = make_pipeline(log_tf=(stem in LOG_TARGETS), degree=BUBBLEPOINT_DEGREE)
        else:
            pipe = make_pipeline(log_tf=(stem in LOG_TARGETS))
        pipe.fit(X_tr, y_tr)

        # evaluate
        y_pred = pipe.predict(X_te)
        rmse   = np.sqrt(mean_squared_error(y_te, y_pred))
        r2     = r2_score(y_te, y_pred)
        print(f"{stem:15s} → RMSE: {rmse:.4f},  R²: {r2:.4f}")

        models[stem] = {"model": pipe, "features": x_cols}

    # persist all pipelines in one file
    out_path = MODELS_DIR / "pipelines_by_target.pkl"
    joblib.dump(models, out_path)
    print(f"\nSaved {len(models)} models to {out_path}")

if __name__ == "__main__":
    main()
