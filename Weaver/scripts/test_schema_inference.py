#!/usr/bin/env python3
"""Test schema inference on downloaded datasets."""

import sys
from pathlib import Path

import pandas as pd

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.schema_service import infer_schema


def test_dataset(csv_path: Path, expected_target: str, expected_type: str):
    """Test schema inference for a dataset."""
    print(f"\n{'=' * 70}")
    print(f"Testing: {csv_path.name}")
    print(f"Expected target: {expected_target} ({expected_type})")
    print("=" * 70)

    df = pd.read_csv(csv_path)
    schema = infer_schema(df)

    # Find the target column
    target_schema = next((col for col in schema if col.name == expected_target), None)

    if target_schema:
        if target_schema.inferred_type == expected_type:
            print(f"✅ PASS - Target '{expected_target}' correctly inferred as '{expected_type}'")
        else:
            print(
                f"❌ FAIL - Target '{expected_target}' inferred as '{target_schema.inferred_type}', "
                f"expected '{expected_type}'"
            )
    else:
        print(f"❌ FAIL - Target column '{expected_target}' not found")

    # Show numeric columns count
    numeric_cols = [col for col in schema if col.inferred_type == "numeric"]
    print(f"Numeric features available: {len(numeric_cols)}")
    if numeric_cols:
        print(f"  - {', '.join([col.name for col in numeric_cols[:5]])}")


def main():
    data_dir = Path(__file__).parent.parent / "data-set"

    # Test datasets
    tests = [
        ("california_housing.csv", "MedHouseVal", "numeric"),
        ("iris.csv", "target", "categorical"),
        ("breast_cancer.csv", "target", "categorical"),
        ("wine.csv", "target", "categorical"),
        ("train.csv", "Survived", "categorical"),
    ]

    for csv_file, target, expected_type in tests:
        csv_path = data_dir / csv_file
        if csv_path.exists():
            test_dataset(csv_path, target, expected_type)
        else:
            print(f"\n⚠️  Skipping {csv_file} - file not found")

    print("\n" + "=" * 70)
    print("Schema inference test complete")
    print("=" * 70)


if __name__ == "__main__":
    main()
