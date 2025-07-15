#!/usr/bin/env python3
import pandas as pd
import joblib
from pathlib import Path

def main():
    models_path = Path(__file__).parent.parent / "models" / "pipelines_by_target.pkl"
    models = joblib.load(models_path)

    # prompt once for X1, X2
    X1 = float(input("Enter concentration (X1): "))
    X2 = float(input("Enter temperature (°C): "))

    sample = pd.DataFrame({"X1":[X1], "X2":[X2]})

    print("\nPredictions:")
    for stem, pipe in models.items():
        val   = pipe.predict(sample)[0]
        label = stem.replace("_", " ").title()
        print(f"  {label:15s}: {val:.4f}")

if __name__ == "__main__":
    main()

