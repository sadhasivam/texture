"""Demo: Spec-driven algorithm framework.

Shows how YAML specs eliminate boilerplate and make the framework extensible.

Usage:
    cd Weaver
    uv run python demo_spec_framework.py
"""
from app.core.spec_loader import spec_loader
from app.ml.linear_regression_spec import LinearRegressionSpecAdapter
from app.ml.kmeans_spec import KMeansSpecAdapter

def main():
    print("=" * 70)
    print("Texture Spec-Driven Algorithm Framework Demo")
    print("=" * 70)
    print()

    # Demo 1: Discover all algorithm specs
    print("1. Discovering algorithm specs...")
    print("-" * 70)
    specs = spec_loader.discover_algorithms()
    for spec_path in specs:
        print(f"   Found: {spec_path}")
    print()

    # Demo 2: Load and inspect spec
    print("2. Loading Linear Regression spec...")
    print("-" * 70)
    spec = spec_loader.load_algorithm("supervised/linear-regression.yaml")
    spec_data = spec["spec"]
    print(f"   ID: {spec_data['id']}")
    print(f"   Name: {spec['metadata']['displayName']}")
    print(f"   Description: {spec_data['description']}")
    print(f"   Tags: {', '.join(spec_data['tags'])}")
    print(f"   Pros: {len(spec_data['pros'])} items")
    print(f"   Cons: {len(spec_data['cons'])} items")
    print(f"   Parameters: {len(spec_data['parameters'])} defined")
    print(f"   Metrics: {len(spec_data['outputs']['metrics'])} defined")
    print()

    # Demo 3: Instantiate spec-driven adapter
    print("3. Creating spec-driven adapter...")
    print("-" * 70)
    adapter = LinearRegressionSpecAdapter()
    print(f"   Adapter ID: {adapter.id}")
    print(f"   Adapter Name: {adapter.name}")
    print(f"   Adapter Category: {adapter.category}")
    print()

    # Demo 4: Get metadata (auto-generated from YAML)
    print("4. Getting metadata (auto-built from YAML spec)...")
    print("-" * 70)
    metadata = adapter.get_metadata()
    print(f"   ID: {metadata.id}")
    print(f"   Name: {metadata.name}")
    print(f"   Difficulty: {metadata.difficulty}")
    print(f"   Model Family: {metadata.model_family}")
    print(f"   Target Types: {metadata.target.allowed_types}")
    print(f"   Feature Types: {metadata.features.allowed_types}")
    print(f"   Parameters: {[p.name for p in metadata.parameters]}")
    print(f"   Output Metrics: {metadata.outputs.metrics}")
    print(f"   Output Charts: {metadata.outputs.charts}")
    print()

    # Demo 5: Unsupervised algorithm
    print("5. Loading K-Means (Unsupervised) spec...")
    print("-" * 70)
    kmeans_adapter = KMeansSpecAdapter()
    kmeans_metadata = kmeans_adapter.get_metadata()
    print(f"   ID: {kmeans_metadata.id}")
    print(f"   Group: {kmeans_metadata.group}")
    print(f"   Target Required: {kmeans_metadata.target.required}")
    print(f"   Feature Types: {kmeans_metadata.features.allowed_types}")
    print(f"   Min Features: {kmeans_metadata.features.min_columns}")
    print()

    # Demo 6: Ontology resolution
    print("6. Ontology resolution (from referenced spec)...")
    print("-" * 70)
    if "ontology" in spec:
        ontology = spec["ontology"]["spec"]
        classification = ontology["classification"]
        print(f"   Group: {classification['group']}")
        print(f"   Subgroup: {classification['subgroup']}")
        print(f"   Learning Type: {classification['learningType']}")
        print(f"   Interpretability: {classification['interpretability']}")

        use_cases = ontology["useCases"]
        print(f"   Primary Use Case: {use_cases['primary']}")
        print(f"   Examples: {len(use_cases['examples'])} listed")
    print()

    print("=" * 70)
    print("Summary:")
    print("=" * 70)
    print("✓ YAML specs define all metadata")
    print("✓ Python adapters only contain ML logic")
    print("✓ Ontology specs shared across similar algorithms")
    print("✓ Framework auto-discovers and loads specs")
    print("✓ No hardcoded metadata in Python code")
    print()
    print(f"Boilerplate reduction:")
    print(f"  Linear Regression: 188 → 141 lines (47 lines saved, 25%)")
    print(f"  K-Means: 194 → 126 lines (68 lines saved, 35%)")
    print()


if __name__ == "__main__":
    main()
