#!/bin/bash

# Download Boston Housing dataset from Kaggle
# Usage: ./scripts/download_boston_housing.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR/.."
DATASET_DIR="$PROJECT_DIR/data-set"

# Activate virtual environment
source "$PROJECT_DIR/.venv/bin/activate"

# Create data-set directory if it doesn't exist
mkdir -p "$DATASET_DIR"

# Change to data-set directory
cd "$DATASET_DIR"

echo "Downloading Boston Housing dataset from Kaggle..."
kaggle kernels pull prasadperera/the-boston-housing-dataset

echo "Dataset downloaded to: $DATASET_DIR"
echo "Files in directory:"
ls -lh
