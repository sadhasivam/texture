Below is a build-ready specification you can hand to Claude, Codex, or Gemini.

# Texture Specification

## 1. Product Identity

**Product name:** Texture
**Frontend app name:** Kolam
**Backend app name:** Weaver

**Product type:**
A minimal, algorithm-first machine learning learning studio for tabular CSV data.

**Primary purpose:**
Let a user pick one ML algorithm, upload one CSV dataset, inspect the discovered schema, map the required columns, run the algorithm, and view clean visual output with metrics and plain-language explanations.

**Non-goals:**
Texture is not an AutoML platform, notebook system, workflow canvas, feature store, deployment platform, or enterprise MLops suite.

---

## 2. Product Vision

Texture should feel like a focused learning dashboard, not a generic data science platform.

A user should be able to:

1. select an algorithm from a right-side panel
2. fetch algorithm metadata from the server
3. upload a CSV
4. see the discovered schema and preview rows
5. select target and feature columns based on algorithm rules
6. run the algorithm
7. see charts, metrics, and simple explanations

The experience should be minimal, fast, and visually clean.

---

## 3. Design Principles

Kolam should follow a minimal visual language inspired by Uber Base. Uber Base describes itself as the design system that defines the foundations of UI across Uber’s ecosystem, and its design tokens are meant to represent reusable foundational decisions across platforms. ([base.uber.com][1])

### UI principles

- minimal chrome
- strong spacing and hierarchy
- restrained typography
- token-driven styling
- no decorative clutter
- fast interaction
- clear labels and plain language
- educational but not verbose

### UX principles

- algorithm-first
- schema-aware
- guided mapping
- instant validation
- strong feedback after each step
- every output should help the user learn

---

## 4. Primary User Story

A learner opens Texture, sees a right-side list of algorithms, selects one, uploads a CSV, reviews the discovered columns, picks target and features according to the selected algorithm’s requirements, runs the model, and learns from charts and metrics.

---

## 5. Scope for V1

### Included

- right-side algorithm catalog
- algorithm metadata API
- CSV upload
- schema discovery
- preview rows
- column mapping UI
- run model action
- result metrics
- chart rendering
- plain-language explanation panel
- warning/validation messages

### Excluded

- authentication
- collaboration
- saved workspaces
- user accounts
- notebooks
- drag-and-drop workflow builder
- background jobs
- model deployment
- experiment versioning
- testcase generation
- README generation

---

## 6. Supported Algorithms for V1

Start with only these:

1. Linear Regression
2. Logistic Regression
3. Decision Tree
4. Random Forest

These four are enough to teach regression, classification, interpretability, and ensemble basics.

---

## 7. Functional Requirements

## 7.1 Algorithm Discovery

The frontend must fetch the list of available algorithms from the backend.

Each algorithm entry must include:

- id
- name
- category
- short description

When the user selects an algorithm, Kolam must call a detail endpoint to fetch full metadata.

---

## 7.2 Algorithm Metadata Contract

Each algorithm must expose metadata that drives the UI.

Required fields:

```json
{
  "id": "linear_regression",
  "name": "Linear Regression",
  "category": "regression",
  "description": "Predicts a continuous numeric target from one or more features.",
  "target": {
    "required": true,
    "allowed_types": ["numeric"],
    "cardinality": "single"
  },
  "features": {
    "required": true,
    "min_columns": 1,
    "max_columns": null,
    "allowed_types": ["numeric", "categorical_encoded"]
  },
  "parameters": [
    {
      "name": "test_size",
      "type": "float",
      "default": 0.2,
      "label": "Test size"
    }
  ],
  "outputs": {
    "metrics": ["r2", "mae", "rmse"],
    "charts": ["predicted_vs_actual", "residual_plot"],
    "tables": ["coefficients"]
  },
  "validation_rules": [
    "Target must be numeric",
    "At least one feature column is required"
  ]
}
```

The frontend must render forms from this metadata rather than hardcoding per-algorithm screens.

---

## 7.3 Dataset Upload

The user must be able to upload a CSV file.

The backend must:

- parse the CSV
- infer schema
- compute row count and column count
- generate sample rows
- identify missing values and simple type inference

The frontend must display:

- dataset filename
- row count
- column count
- preview rows
- discovered schema table

---

## 7.4 Schema Discovery

For each column, the backend should return:

- column name
- inferred type
- missing count
- unique count
- sample values
- optional role suggestion

Example inferred types:

- numeric
- categorical
- boolean
- datetime
- text
- identifier

---

## 7.5 Column Mapping

Based on the selected algorithm metadata, Kolam must ask the user to provide:

- target column
- feature columns
- optional parameters

The UI must enforce algorithm constraints before allowing run.

Examples:

- Linear Regression requires one numeric target
- Logistic Regression requires a categorical or binary target
- Linear Regression requires at least one feature
- Target column cannot also be selected as a feature

---

## 7.6 Model Run

The user clicks a single Run button.

Kolam sends:

- algorithm id
- dataset id
- target column
- feature columns
- parameters

Weaver validates the mapping, runs preprocessing as needed, trains the model, computes evaluation output, and returns a presentation-ready response.

---

## 7.7 Result Rendering

The backend must return:

- summary
- metrics
- chart-friendly data
- optional tables
- explanations
- warnings

Kolam must render:

- metric cards
- chart panels
- explanation panel
- warning messages

Charts must be interactive when practical.

---

## 8. Technical Stack Requirements

## 8.1 Root Structure

```text
Texture/
├─ Kolam/
└─ Weaver/
```

---

## 8.2 Frontend Requirements: Kolam

Kolam must be built with:

- React
- TypeScript
- Rsbuild
- pnpm

Rsbuild is a modern build tool powered by Rspack, designed to keep configuration simple while providing fast builds and optimized production output. Current docs state Rsbuild supports React and requires Node.js 18.12.0 or higher for current versions. ([Rsbuild][2])

### Frontend design requirements

- dashboard layout
- right sidebar for algorithms
- main workspace for upload, schema, mapping, and results
- design tokens inspired by Uber Base
- minimalist component surface
- no heavy global state unless necessary

### Frontend recommended libraries

- React
- TypeScript
- Rsbuild
- pnpm
- TanStack Query for server state
- Zustand only if local cross-component state becomes necessary
- Recharts for charts
- TanStack Table for schema/data preview

### Frontend architectural requirements

- metadata-driven rendering
- component composition over abstraction-heavy patterns
- keep files small and obvious
- avoid over-engineering
- no test setup in V1

### Frontend folder layout

```text
Texture/
└─ Kolam/
   ├─ package.json
   ├─ pnpm-lock.yaml
   ├─ rsbuild.config.ts
   ├─ tsconfig.json
   └─ src/
      ├─ main.tsx
      ├─ app/
      │  ├─ App.tsx
      │  └─ providers.tsx
      ├─ pages/
      │  └─ DashboardPage.tsx
      ├─ features/
      │  ├─ algorithms/
      │  │  ├─ AlgorithmSidebar.tsx
      │  │  ├─ AlgorithmCard.tsx
      │  │  └─ useAlgorithms.ts
      │  ├─ dataset/
      │  │  ├─ DatasetUpload.tsx
      │  │  ├─ DatasetPreview.tsx
      │  │  ├─ SchemaTable.tsx
      │  │  └─ useDatasetUpload.ts
      │  ├─ mapping/
      │  │  ├─ MappingForm.tsx
      │  │  ├─ TargetSelector.tsx
      │  │  ├─ FeatureSelector.tsx
      │  │  └─ ParameterForm.tsx
      │  └─ results/
      │     ├─ ResultsPanel.tsx
      │     ├─ MetricsCards.tsx
      │     ├─ ChartRenderer.tsx
      │     ├─ ExplanationPanel.tsx
      │     └─ WarningsPanel.tsx
      ├─ services/
      │  └─ api.ts
      ├─ types/
      │  ├─ algorithm.ts
      │  ├─ dataset.ts
      │  └─ run.ts
      └─ styles/
         └─ tokens.css
```

---

## 8.3 Backend Requirements: Weaver

Weaver must be built with:

- Python
- uv
- FastAPI
- pyproject.toml
- Ruff

FastAPI describes itself as a modern, high-performance web framework based on Python type hints, and it automatically generates OpenAPI schema and docs. FastAPI also documents a recommended multi-file structure for larger apps. ([FastAPI][3])

uv is Astral’s Python project and package tool, with official docs recommending it for installation and workflow use. Ruff is Astral’s fast linter and formatter and can be configured in `pyproject.toml`. ([Astral Docs][4])

### Backend responsibilities

- serve algorithm metadata
- accept dataset upload
- infer schema
- validate column selection
- run ML algorithms
- compute metrics
- emit chart-friendly result payloads
- support frontend CORS for local dev

### Backend recommended libraries

- FastAPI
- Uvicorn
- pandas
- numpy
- scikit-learn
- python-multipart
- pydantic
- uv
- ruff

### Backend architectural requirements

- thin routes
- service layer for business logic
- algorithm registry
- adapters per algorithm
- schemas defined in Pydantic
- no database in V1
- uploaded files may be stored temporarily on local disk
- no auth in V1
- no tests in V1

### Backend folder layout

```text
Texture/
└─ Weaver/
   ├─ pyproject.toml
   ├─ .python-version
   └─ app/
      ├─ main.py
      ├─ api/
      │  └─ v1/
      │     ├─ algorithms.py
      │     ├─ datasets.py
      │     ├─ runs.py
      │     └─ health.py
      ├─ core/
      │  ├─ config.py
      │  └─ cors.py
      ├─ schemas/
      │  ├─ algorithm.py
      │  ├─ dataset.py
      │  └─ run.py
      ├─ services/
      │  ├─ algorithm_registry.py
      │  ├─ dataset_service.py
      │  ├─ schema_service.py
      │  ├─ run_service.py
      │  └─ explanation_service.py
      ├─ ml/
      │  ├─ base.py
      │  ├─ linear_regression.py
      │  ├─ logistic_regression.py
      │  ├─ decision_tree.py
      │  └─ random_forest.py
      └─ storage/
         └─ uploads/
```

---

## 9. API Requirements

## 9.1 Health

`GET /api/v1/health`

Response:

```json
{
  "status": "ok"
}
```

---

## 9.2 List Algorithms

`GET /api/v1/algorithms`

Response:

```json
[
  {
    "id": "linear_regression",
    "name": "Linear Regression",
    "category": "regression",
    "description": "Predict a continuous numeric value."
  }
]
```

---

## 9.3 Get Algorithm Metadata

`GET /api/v1/algorithms/{algorithm_id}`

Returns full metadata contract.

---

## 9.4 Upload Dataset

`POST /api/v1/datasets/upload`

Form-data:

- file

Response:

```json
{
  "dataset_id": "ds_001",
  "filename": "housing.csv",
  "row_count": 506,
  "column_count": 6,
  "columns": [
    {
      "name": "area",
      "inferred_type": "numeric",
      "missing_count": 0,
      "unique_count": 320,
      "sample_values": [1200, 1500, 1800]
    }
  ],
  "preview_rows": [
    {
      "area": 1200,
      "price": 220000
    }
  ]
}
```

---

## 9.5 Get Dataset Details

`GET /api/v1/datasets/{dataset_id}`

Returns upload metadata, schema, and preview.

---

## 9.6 Run Algorithm

`POST /api/v1/runs`

Request:

```json
{
  "algorithm_id": "linear_regression",
  "dataset_id": "ds_001",
  "target_column": "price",
  "feature_columns": ["area", "bedrooms"],
  "parameters": {
    "test_size": 0.2
  }
}
```

Response:

```json
{
  "run_id": "run_001",
  "status": "success",
  "summary": {
    "target_column": "price",
    "feature_columns": ["area", "bedrooms"],
    "train_rows": 404,
    "test_rows": 102
  },
  "metrics": {
    "r2": 0.82,
    "mae": 18000.5,
    "rmse": 24500.3
  },
  "charts": [
    {
      "type": "predicted_vs_actual",
      "title": "Predicted vs Actual",
      "data": [{ "actual": 220000, "predicted": 228000 }]
    }
  ],
  "tables": [
    {
      "type": "coefficients",
      "rows": [{ "feature": "area", "coefficient": 145.2 }]
    }
  ],
  "explanations": [
    "The model explains about 82% of the variation in the target."
  ],
  "warnings": []
}
```

---

## 10. Internal Backend Design

## 10.1 Algorithm Registry

Weaver must use a registry pattern.

Each algorithm adapter must implement a consistent contract.

Example interface:

```python
class AlgorithmAdapter:
    id: str
    name: str
    category: str

    def get_metadata(self) -> dict: ...
    def validate_mapping(self, schema, target, features, parameters) -> list[str]: ...
    def run(self, dataframe, target, features, parameters) -> dict: ...
```

This keeps the UI metadata-driven and allows easy extension.

---

## 10.2 Data Validation Rules

Validation must happen before model execution.

Examples:

- target exists
- features exist
- target not duplicated in features
- allowed types match metadata
- minimum feature count met
- enough usable rows remain after cleaning
- binary target required for binary logistic regression in V1

Errors should be returned in clean frontend-friendly JSON.

---

## 10.3 Preprocessing

Preprocessing should stay minimal in V1.

Allowed:

- drop rows with invalid target
- numeric coercion when obvious
- optional categorical encoding only when algorithm metadata says it is supported

Avoid advanced preprocessing in V1.

---

## 11. Frontend UX Requirements

## 11.1 Layout

Single-page dashboard layout.

### Right sidebar

- algorithm list
- selected state
- short labels

### Main workspace

- algorithm details
- dataset upload
- schema preview
- column mapping
- run button
- results

---

## 11.2 Interaction Flow

### Step 1

User selects algorithm.

### Step 2

Kolam fetches algorithm metadata.

### Step 3

User uploads CSV.

### Step 4

Kolam shows schema and preview.

### Step 5

Kolam asks for target and features according to metadata.

### Step 6

User clicks Run.

### Step 7

Kolam renders results.

---

## 11.3 States

Kolam must handle these states clearly:

- idle
- loading algorithms
- algorithm selected
- uploading dataset
- schema ready
- mapping incomplete
- ready to run
- running
- success
- error

---

## 11.4 Error Handling

Must show clear messages for:

- invalid CSV
- unsupported types
- missing target
- insufficient columns
- backend validation errors
- model execution failures

Do not expose Python tracebacks to the UI.

---

## 12. Charting Requirements

Use **Recharts** in V1.

Required chart support by algorithm:

### Linear Regression

- predicted vs actual scatter
- residual plot
- optional best-fit line when only one feature is selected

### Logistic Regression

- confusion matrix view
- class distribution bar chart
- probability output display

### Decision Tree

- feature importance bar chart
- class distribution or regression summary

### Random Forest

- feature importance bar chart
- predicted vs actual or confusion summary

The backend should return chart-ready JSON, not only static images.

---

## 13. Minimal Visual Style Requirements

Kolam should visually reflect the spirit of Uber Base:

- token-driven spacing
- bold but sparse headings
- neutral palette
- clean cards
- subtle borders
- minimal shadows
- motion only where useful

Uber Base documents typography, motion, and token systems as foundational UI elements, so Kolam should borrow the design philosophy rather than copy product-specific visuals. ([base.uber.com][5])

---

## 14. Development Requirements

## 14.1 Kolam

- package manager: pnpm
- build tool: Rsbuild
- language: TypeScript
- framework: React

## 14.2 Weaver

- package manager / env: uv
- app framework: FastAPI
- config via `pyproject.toml`
- lint and format via Ruff

---

## 15. Simplicity Constraints

The implementation must stay minimalist.

### Must avoid

- over-abstracted frontend patterns
- Redux unless clearly necessary
- plugin systems in V1
- database in V1
- container orchestration
- microservices
- async job queues
- excessive config files
- tests and README files

### Must prefer

- direct file structure
- small components
- thin API routes
- single-purpose services
- obvious naming
- JSON contracts
- fast local development

---

## 16. Success Criteria for V1

Texture V1 is successful if:

- a user can launch Kolam and Weaver locally
- the algorithm list loads from the server
- a CSV can be uploaded
- schema is discovered automatically
- the UI asks for valid columns based on algorithm metadata
- Linear Regression can run end-to-end
- at least one other algorithm can run end-to-end
- charts and metrics render cleanly
- the UI feels minimal and coherent

---

## 17. Implementation Order

Recommended build order:

1. Weaver health endpoint
2. algorithm registry and metadata endpoints
3. Kolam dashboard shell and sidebar
4. CSV upload endpoint
5. schema inference endpoint
6. dataset preview UI
7. mapping form from metadata
8. Linear Regression adapter
9. run endpoint
10. result rendering with Recharts
11. Logistic Regression adapter
12. Decision Tree adapter
13. Random Forest adapter

---

## 18. Final Build Directive

Build **Texture** as a minimal two-project workspace:

- **Kolam**: React + TypeScript + Rsbuild + pnpm, with a dashboard UI inspired by Uber Base design principles
- **Weaver**: Python + uv + FastAPI + pyproject.toml + Ruff, exposing clean metadata-first APIs for algorithm discovery, dataset upload, schema inference, model execution, and result delivery

The system must be **algorithm-first, metadata-driven, schema-aware, visually minimal, and focused on learning**.

If you want, I can turn this next into a stricter `SPEC.md` format with headings, acceptance criteria, JSON contracts, and exact folder trees only.

[1]: https://base.uber.com/?utm_source=chatgpt.com "Base design system - Uber"
[2]: https://v2.rsbuild.dev/guide/start/?utm_source=chatgpt.com "Introduction"
[3]: https://fastapi.tiangolo.com/?utm_source=chatgpt.com "FastAPI"
[4]: https://docs.astral.sh/uv/?utm_source=chatgpt.com "uv - Astral Docs"
[5]: https://base.uber.com/6d2425e9f/p/976582-typography?utm_source=chatgpt.com "Typography - Base design system - Uber"
