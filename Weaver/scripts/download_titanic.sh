#!/bin/bash

# Download Titanic dataset from Kaggle
echo "Downloading Titanic dataset from Kaggle..."

# Get the script directory and project root
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DATASET_DIR="$PROJECT_ROOT/data-set"

# Create data-set directory if it doesn't exist
mkdir -p "$DATASET_DIR"

# Set Kaggle config directory
export KAGGLE_CONFIG_DIR="$SCRIPT_DIR"

# Change to project root to use uv
cd "$PROJECT_ROOT"

# Download the dataset using uv run
uv run kaggle competitions download -c titanic -p "$DATASET_DIR"

# Unzip the dataset
cd "$DATASET_DIR"
unzip -o titanic.zip
rm titanic.zip

echo "Dataset downloaded to: $DATASET_DIR"
echo "Files in directory:"
ls -lh
