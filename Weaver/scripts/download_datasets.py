#!/usr/bin/env python3
"""
Download gold standard datasets for testing each algorithm.

This script uses sklearn's built-in datasets to create clean CSVs
that are perfect for testing Texture's algorithms.
"""

import os
from pathlib import Path

import pandas as pd
from sklearn.datasets import (
    fetch_california_housing,
    load_breast_cancer,
    load_iris,
    load_wine,
)


def main():
    # Get the data-set directory
    script_dir = Path(__file__).parent
    dataset_dir = script_dir.parent / "data-set"
    dataset_dir.mkdir(exist_ok=True)

    print("Downloading gold standard datasets...\n")

    # 1. California Housing - Regression
    print("1. California Housing (Regression)")
    print("   Target: Median house value")
    print("   Features: 8 numeric features (population, income, etc.)")
    california = fetch_california_housing(as_frame=True)
    california_df = california.frame
    output_path = dataset_dir / "california_housing.csv"
    california_df.to_csv(output_path, index=False)
    print(f"   ✓ Saved to: {output_path}")
    print(f"   Rows: {len(california_df)}, Columns: {len(california_df.columns)}\n")

    # 2. Iris - Classification (3 classes)
    print("2. Iris (Classification - 3 classes)")
    print("   Target: Species (setosa, versicolor, virginica)")
    print("   Features: 4 numeric features (sepal/petal dimensions)")
    iris = load_iris(as_frame=True)
    iris_df = iris.frame
    # Convert numeric target to species names
    iris_df["target"] = iris_df["target"].map(
        {0: "setosa", 1: "versicolor", 2: "virginica"}
    )
    output_path = dataset_dir / "iris.csv"
    iris_df.to_csv(output_path, index=False)
    print(f"   ✓ Saved to: {output_path}")
    print(f"   Rows: {len(iris_df)}, Columns: {len(iris_df.columns)}\n")

    # 3. Breast Cancer - Binary Classification
    print("3. Breast Cancer Wisconsin (Binary Classification)")
    print("   Target: Diagnosis (malignant=1, benign=0)")
    print("   Features: 30 numeric features")
    cancer = load_breast_cancer(as_frame=True)
    cancer_df = cancer.frame
    output_path = dataset_dir / "breast_cancer.csv"
    cancer_df.to_csv(output_path, index=False)
    print(f"   ✓ Saved to: {output_path}")
    print(f"   Rows: {len(cancer_df)}, Columns: {len(cancer_df.columns)}\n")

    # 4. Wine - Classification (3 classes)
    print("4. Wine Recognition (Classification - 3 classes)")
    print("   Target: Wine class (0, 1, 2)")
    print("   Features: 13 numeric features (alcohol, color, etc.)")
    wine = load_wine(as_frame=True)
    wine_df = wine.frame
    output_path = dataset_dir / "wine.csv"
    wine_df.to_csv(output_path, index=False)
    print(f"   ✓ Saved to: {output_path}")
    print(f"   Rows: {len(wine_df)}, Columns: {len(wine_df.columns)}\n")

    print("=" * 60)
    print("DATASET SUMMARY")
    print("=" * 60)
    print("\nREGRESSION DATASETS:")
    print("  • california_housing.csv - Linear Regression, Decision Tree, Random Forest")
    print("\nCLASSIFICATION DATASETS:")
    print("  • iris.csv - Logistic Regression (3 classes), Decision Tree, Random Forest")
    print("  • breast_cancer.csv - Logistic Regression (binary), Decision Tree, Random Forest")
    print("  • wine.csv - Logistic Regression (3 classes), Decision Tree, Random Forest")
    print("  • train.csv (Titanic) - Binary classification")
    print("\nAll datasets saved to:", dataset_dir)


if __name__ == "__main__":
    main()
