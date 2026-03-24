Below is the specification for Texture, the algorithm-first ML learning studio.

# Texture Specification

## 1. Product Identity

**Product name:** Texture

**Service Architecture:**
- **Kolam** - React frontend (user interface)
- **Loom** - Go HTTP gateway (API layer, authentication, orchestration)
- **Weaver** - Python gRPC server (ML compute engine)

**Product type:**
A minimal, algorithm-first machine learning learning studio for tabular CSV data.

**Primary purpose:**
Let a user pick one ML algorithm, upload one CSV dataset, inspect the discovered schema, map the required columns, run the algorithm, and view clean visual output with metrics and plain-language explanations.

**Non-goals:**
Texture is not an AutoML platform, notebook system, workflow canvas, feature store, deployment platform, or enterprise MLops suite.

---

## 1.1 System Architecture

Texture is built as a three-tier microservices architecture:

```
Browser (Kolam)
     ↓ HTTP/REST + JWT
Loom (API Gateway)
     ↓ gRPC + Protocol Buffers
Weaver (ML Compute)
```

### Kolam - Frontend
- React 19 + TypeScript + Rsbuild
- Clerk authentication integration
- TanStack Query for server state
- Recharts for visualizations
- Runs on port 3000 (dev)

### Loom - API Gateway
- Go 1.26.1 + Chi router + Huma v2
- REST API endpoints (`/api/v1/*`)
- Clerk JWT authentication
- CSV file upload handling
- Algorithm metadata serving (from YAML specs)
- gRPC client to Weaver
- Runs on port 8080

### Weaver - ML Compute Engine
- Python 3.14 + gRPC server
- Schema inference from CSV
- Algorithm execution (scikit-learn, XGBoost)
- Auto-discovery of algorithms from YAML specs
- Metric calculation and chart data generation
- Runs on port 50051

### Service Contracts
- Protocol Buffers for gRPC (`/proto` directory)
- YAML specifications for algorithms (`/algorithms` directory)
- REST/JSON for frontend communication

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

## 5. Current Feature Scope

### Included

- User authentication (Clerk JWT-based)
- Algorithm catalog (14 algorithms)
- Algorithm metadata API
- CSV upload (via Loom gateway)
- Schema discovery (via Weaver gRPC)
- Preview rows
- Column mapping UI
- Algorithm execution
- Result metrics
- Interactive chart rendering (Recharts)
- Plain-language explanation panel
- Warning/validation messages
- YAML-based algorithm specifications
- Auto-discovery of algorithms

### Excluded

- Collaboration features
- Persistent workspaces
- Notebooks
- Drag-and-drop workflow builder
- Background jobs
- Model deployment
- Experiment versioning
- Automated test generation
- Multi-file uploads
- Dataset versioning

---

## 6. Supported Algorithms

Texture supports 15 machine learning algorithms across supervised learning, unsupervised learning, and anomaly detection.

### Supervised Learning (10 algorithms)

1. Linear Regression
2. Logistic Regression
3. Decision Tree
4. Random Forest
5. Support Vector Machine (SVM)
6. K-Nearest Neighbors (KNN)
7. Naive Bayes
8. Gradient Boosting
9. AdaBoost
10. XGBoost

### Unsupervised Learning (4 algorithms)

**Clustering:**
11. K-Means
12. DBSCAN

**Dimensionality Reduction:**
13. Principal Component Analysis (PCA)
14. t-SNE

### Anomaly Detection (1 algorithm)

15. Isolation Forest

All algorithms are defined via YAML specifications in the `/algorithms` directory and auto-discovered at runtime by both Loom and Weaver.

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

Each algorithm is defined via a YAML specification in the `/algorithms` directory using a Kubernetes-style manifest format.

**Example YAML specification** (`algorithms/supervised/linear-regression.yaml`):

```yaml
apiVersion: texture.ml/v1
kind: Algorithm
metadata:
  name: linear-regression
  displayName: Linear Regression
  namespace: supervised-learning
  labels:
    difficulty: beginner
    model-family: linear
    category: regression
spec:
  ontologyRef: base/ontology-supervised-regression.yaml
  dependencyRef: base/dependencies-sklearn-base.yaml
  id: linear_regression
  description: Predicts a continuous numeric target from one or more features.
  tags:
    - interpretable
    - beginner-friendly
  difficulty: beginner
  modelFamily: linear
  target:
    required: true
    types: [numeric]
    cardinality: single
  features:
    required: true
    types: [numeric]
    min: 1
  parameters:
    - name: test_size
      type: float
      default: 0.2
      label: Test size
  outputs:
    metrics:
      - name: r2
        displayName: R² Score
      - name: mae
        displayName: Mean Absolute Error
    visualizations:
      - name: predicted_vs_actual
        defaultChart: scatter
  validationRules:
    - Target must be numeric
    - At least one feature column is required
  handler:
    module: app.ml.supervised.linear_regression
    class: LinearRegressionAdapter
```

**Ontology reference** (`algorithms/base/ontology-supervised-regression.yaml`):

```yaml
apiVersion: texture.ml/v1
kind: Ontology
metadata:
  name: supervised-regression
spec:
  classification:
    group: supervised
    subgroup: regression
    category: regression
```

**Auto-discovery process:**
1. Both Loom and Weaver scan `/algorithms` directory at startup
2. Load all YAML files with `kind: Algorithm`
3. Resolve ontology and dependency references
4. Register algorithms in memory
5. Serve metadata to frontend

The frontend renders forms dynamically from this metadata rather than hardcoding per-algorithm screens.

---

## 7.3 Dataset Upload

The user uploads a CSV file via the Kolam frontend.

**Upload flow:**
1. Kolam sends multipart form data to Loom (`POST /api/v1/datasets/upload`)
2. Loom receives file and validates size (max 50MB)
3. Loom sends CSV bytes to Weaver via gRPC (`InferSchema`)
4. Weaver parses CSV, infers schema, generates preview
5. Loom caches dataset metadata and file bytes
6. Loom returns schema information to Kolam

**Weaver must:**
- Parse CSV with pandas
- Infer column types (numeric, categorical, boolean, datetime, text, identifier)
- Compute row count and column count
- Generate sample preview rows
- Identify missing values and unique counts per column

**Kolam must display:**

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
├─ algorithms/           # YAML algorithm specifications
│  ├─ base/             # Ontologies and dependencies
│  ├─ supervised/       # Supervised algorithm specs
│  └─ unsupervised/     # Unsupervised algorithm specs
├─ proto/               # Protocol Buffer definitions
│  ├─ common.proto
│  └─ weaver.proto
├─ Kolam/               # React frontend
├─ Loom/                # Go API gateway
└─ Weaver/              # Python ML compute engine
```

---

## 8.2 Frontend Requirements: Kolam

**Core stack:**
- React 19.2.3
- TypeScript 5.9.3
- Rsbuild 1.7.1 (build tool powered by Rspack)
- pnpm (package manager)
- Node.js >= 24.13.1

**Key libraries:**
- `@clerk/react` 6.1.2 - Authentication
- `@tanstack/react-query` 5.90.21 - Server state management
- `@tanstack/react-table` 8.21.3 - Data tables
- `recharts` 3.8.0 - Charts and visualizations

### Design requirements

- Dashboard layout with right sidebar for algorithms
- Main workspace for upload, schema, mapping, and results
- Design tokens inspired by Uber Base
- Minimalist component surface
- Fast, responsive interactions

### Architectural requirements

- Metadata-driven rendering (from YAML specs via API)
- Component composition over abstraction-heavy patterns
- Keep files small and obvious
- Avoid over-engineering
- No global state management (TanStack Query handles server state)
- No automated tests yet (manual testing for now)

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

## 8.3 API Gateway Requirements: Loom

**Core stack:**
- Go 1.26.1
- Chi v5.2.5 (HTTP router)
- Huma v2.37.2 (OpenAPI framework)
- Cobra v1.10.2 (CLI)
- Viper v1.21.0 (configuration)

**Key libraries:**
- `github.com/clerk/clerk-sdk-go/v2` v2.5.1 - Authentication
- `google.golang.org/grpc` v1.79.3 - gRPC client
- `google.golang.org/protobuf` v1.36.11 - Protocol Buffers
- `github.com/go-chi/cors` v1.2.2 - CORS middleware
- `gopkg.in/yaml.v3` - YAML parsing for algorithm specs

### Gateway responsibilities

- Serve REST API endpoints (`/api/v1/*`)
- JWT authentication and authorization (Clerk)
- HTTP file upload handling (CSV files)
- Load and serve algorithm metadata from YAML specs
- Route computation requests to Weaver via gRPC
- Cache dataset metadata and file bytes
- CORS configuration for frontend

### Architectural requirements

- Clean HTTP handlers using Chi router
- OpenAPI documentation via Huma
- gRPC client connection pool to Weaver
- Middleware for auth, CORS, logging
- No database (stateless gateway)
- Configuration via environment variables

### Folder layout

```text
Loom/
├─ cmd/loom/             # CLI entry point
│  ├─ main.go
│  ├─ serve.go
│  └─ version.go
├─ internal/
│  ├─ api/               # HTTP handlers
│  │  ├─ algorithms.go
│  │  ├─ datasets.go
│  │  ├─ runs.go
│  │  ├─ auth.go
│  │  └─ health.go
│  ├─ config/            # Configuration
│  │  └─ config.go
│  ├─ grpc/              # gRPC client
│  │  └─ client.go
│  ├─ middleware/        # HTTP middleware
│  │  ├─ clerk.go
│  │  └─ cors.go
│  ├─ server/            # Server setup
│  │  └─ server.go
│  └─ services/          # Business logic
│     ├─ algorithm_service.go
│     └─ dataset_service.go
├─ pb/                   # Generated protobuf code
│  ├─ common_pb2.go
│  └─ weaver_pb2.go
├─ go.mod
└─ go.sum
```

---

## 8.4 Compute Engine Requirements: Weaver

**Core stack:**
- Python 3.14
- gRPC 1.78.0 (server)
- grpcio-tools 1.78.0 (protobuf compiler)
- uv (package manager)
- Ruff (linting and formatting via `pyproject.toml`)

**Key libraries:**
- pandas 2.2.0 - Data manipulation
- numpy 2.0.0 - Numerical computing
- scikit-learn 1.5.0 - ML algorithms
- xgboost 2.0.0 - Gradient boosting
- pydantic 2.9.0 - Data validation
- pyyaml 6.0.3 - YAML parsing

### Compute engine responsibilities

- Serve gRPC API (`WeaverService`)
- Auto-discover algorithms from YAML specs
- Infer schema from CSV data
- Validate run requests
- Execute ML algorithms
- Calculate evaluation metrics
- Generate chart-ready data
- Return structured results via Protocol Buffers

### Architectural requirements

- gRPC server with Protocol Buffers
- Spec-driven algorithm adapters
- Auto-discovery and registration
- Minimal adapter boilerplate (YAML drives metadata)
- Pydantic schemas for validation
- No database
- No authentication (protected by Loom gateway)
- No automated tests yet

### Folder layout

```text
Weaver/
├─ pyproject.toml
├─ .python-version
└─ app/
   ├─ grpc_server/          # gRPC server
   │  ├─ server.py
   │  └─ handlers.py
   ├─ core/                 # Core utilities
   │  └─ spec_loader.py     # YAML spec loader
   ├─ schemas/              # Pydantic schemas
   │  ├─ algorithm.py
   │  ├─ dataset.py
   │  └─ run.py
   ├─ services/             # Business logic
   │  ├─ algorithm_registry.py
   │  ├─ spec_registry.py   # Auto-discovery
   │  └─ schema_service.py
   ├─ ml/                   # Algorithm adapters
   │  ├─ base.py            # Base adapter
   │  ├─ base_validator.py
   │  ├─ spec_adapter.py    # Spec-driven base
   │  ├─ supervised/
   │  │  ├─ linear_regression.py
   │  │  ├─ logistic_regression.py
   │  │  ├─ decision_tree.py
   │  │  ├─ random_forest.py
   │  │  ├─ svm.py
   │  │  ├─ knn.py
   │  │  ├─ naive_bayes.py
   │  │  ├─ gradient_boosting.py
   │  │  ├─ adaboost.py
   │  │  └─ xgboost.py
   │  └─ unsupervised/
   │     ├─ kmeans.py
   │     ├─ dbscan.py
   │     ├─ pca.py
   │     ├─ tsne.py
   │     └─ isolation_forest.py
   └─ pb/                   # Generated protobuf code
      ├─ common_pb2.py
      ├─ weaver_pb2.py
      └─ weaver_pb2_grpc.py
```

---

## 9. API Requirements

Texture has two API layers:
1. **Loom REST API** - Public HTTP/JSON API for frontend
2. **Weaver gRPC API** - Internal gRPC API for ML computation

---

## 9.1 Loom REST API

All REST endpoints are under `/api/v1/` and require Clerk JWT authentication (except health).

### Health Check

`GET /api/v1/health`

**Response:**
```json
{
  "status": "ok",
  "environment": "development"
}
```

### List Algorithms

`GET /api/v1/algorithms`

Returns summary list of all available algorithms (loaded from YAML specs).

**Response:**
```json
[
  {
    "id": "linear_regression",
    "name": "Linear Regression",
    "category": "regression",
    "group": "supervised",
    "subgroup": "regression",
    "description": "Predicts a continuous numeric target",
    "tags": ["interpretable", "beginner-friendly"],
    "difficulty": "beginner",
    "model_family": "linear"
  }
]
```

### Get Algorithm Metadata

`GET /api/v1/algorithms/{algorithm_id}`

Returns full metadata for a specific algorithm (from YAML spec).

### Upload Dataset

`POST /api/v1/datasets/upload`

**Request:** `multipart/form-data` with file field

**Flow:**
1. Loom receives file
2. Loom calls Weaver gRPC `InferSchema`
3. Loom caches dataset
4. Loom returns schema to frontend

**Response:**
```json
{
  "dataset_id": "uuid-here",
  "filename": "housing.csv",
  "row_count": 506,
  "column_count": 6,
  "columns": [
    {
      "name": "area",
      "inferred_type": "numeric",
      "missing_count": 0,
      "unique_count": 320,
      "sample_values": ["1200", "1500", "1800"]
    }
  ],
  "preview_rows": [
    {"area": "1200", "price": "220000"}
  ]
}
```

### Get Dataset Details

`GET /api/v1/datasets/{dataset_id}`

Returns cached dataset metadata, schema, and preview.

### Execute Algorithm Run

`POST /api/v1/runs`

**Request:**
```json
{
  "algorithm_id": "linear_regression",
  "dataset_id": "uuid-here",
  "target_column": "price",
  "feature_columns": ["area", "bedrooms"],
  "parameters": {
    "test_size": "0.2"
  }
}
```

**Flow:**
1. Loom receives run request
2. Loom loads cached CSV bytes
3. Loom calls Weaver gRPC `ExecuteRun`
4. Weaver executes algorithm and returns results
5. Loom forwards results to frontend

**Response:**
```json
{
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
      "data": [
        {"actual": 220000, "predicted": 228000, "best_fit": 225000}
      ]
    }
  ],
  "tables": [
    {
      "type": "coefficients",
      "rows": [
        {"feature": "intercept", "coefficient": 50000.0},
        {"feature": "area", "coefficient": 145.2}
      ]
    }
  ],
  "explanations": [
    "The model explains about 82.0% of the variation in the target.",
    "On average, predictions are off by 18000.50 units (MAE)."
  ],
  "warnings": []
}
```

---

## 9.2 Weaver gRPC API

Weaver exposes a gRPC service (`WeaverService`) for internal communication with Loom.

**Protocol Buffers:** Defined in `/proto/weaver.proto`

### Health Check

`rpc HealthCheck(Empty) returns (HealthResponse)`

Returns service status, Python version, and available algorithms count.

### Infer Schema

`rpc InferSchema(InferSchemaRequest) returns (InferSchemaResponse)`

**Request:**
- `bytes dataset_csv` - Raw CSV data
- `string dataset_id` - Optional tracking ID

**Response:**
- Dataset ID, filename, row/column counts
- Column schemas (name, type, missing count, unique count, sample values)
- Preview rows

### Validate Run

`rpc ValidateRun(ValidateRunRequest) returns (ValidateRunResponse)`

Validates if a run can be executed based on algorithm requirements.

### Execute Run

`rpc ExecuteRun(ExecuteRunRequest) returns (ExecuteRunResponse)`

**Request:**
- `string algorithm_id`
- `bytes dataset_csv` - Raw CSV data
- `string target_column`
- `repeated string feature_columns`
- `map<string, string> parameters`
- `string request_id` - For tracing

**Response:**
- Status (success/error)
- Run summary
- Metrics (map of metric name to value)
- Charts (array of chart objects with data)
- Tables (array of table objects with rows)
- Explanations (array of strings)
- Warnings (array of strings)
- Error message (if failed)

---

## 10. Internal Design Patterns

## 10.1 Spec-Driven Algorithm Registry

Both Loom and Weaver use auto-discovery to load algorithms from YAML specifications at startup.

**Weaver implementation:**

```python
class SpecDrivenAdapter:
    """Base adapter that loads metadata from YAML spec."""
    spec_path: str  # e.g., "supervised/linear-regression.yaml"

    def get_metadata(self) -> dict:
        # Load from YAML spec
        spec = spec_loader.load_algorithm(self.spec_path)
        return spec

    def run(self, dataframe, target, features, parameters) -> dict:
        # Implemented by subclass
        pass
```

**Algorithm adapter example:**

```python
from app.ml.spec_adapter import SpecDrivenAdapter

class LinearRegressionAdapter(SpecDrivenAdapter):
    spec_path = "supervised/linear-regression.yaml"

    def run(self, dataframe, target, features, parameters):
        # Implementation only - metadata comes from YAML
        model = LinearRegression()
        # ... train and return results
```

**Auto-discovery process:**

1. `spec_loader.discover_algorithms()` scans `/algorithms` directory
2. Finds all YAML files with `kind: Algorithm`
3. Reads `handler.module` and `handler.class` from spec
4. Dynamically imports and instantiates adapter class
5. Registers in `spec_registry`

This pattern eliminates boilerplate and makes adding new algorithms trivial (YAML spec + minimal Python implementation).

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

## 18. Architecture Summary

Texture is built as a **three-tier microservices architecture**:

### Kolam (Frontend)
- React 19 + TypeScript + Rsbuild + pnpm
- Clerk authentication
- Dashboard UI inspired by Uber Base design principles
- Metadata-driven rendering from YAML specs

### Loom (API Gateway)
- Go 1.26.1 + Chi + Huma + gRPC client
- REST API layer (`/api/v1/*`)
- JWT authentication (Clerk)
- File upload handling
- Algorithm metadata serving
- Request orchestration to Weaver

### Weaver (ML Compute Engine)
- Python 3.14 + gRPC server + scikit-learn + XGBoost
- Auto-discovery of algorithms from YAML specs
- Schema inference
- ML execution and evaluation
- Chart data generation

The system is **algorithm-first, spec-driven, metadata-driven, schema-aware, visually minimal, and focused on learning**.

---

## 19. Development Guardrails

### Core Principles

1. **Simplicity First**
   - No over-engineering
   - Add features only when explicitly needed
   - Avoid abstractions for one-time use
   - Keep files small and obvious

2. **Spec-Driven Development**
   - Algorithms defined in YAML specs (`/algorithms`)
   - Auto-discovery eliminates manual registration
   - Metadata drives UI rendering
   - Single source of truth for algorithm contracts

3. **Security**
   - All API endpoints protected by Clerk JWT (except health)
   - Input validation on both Loom and Weaver
   - No Python tracebacks exposed to frontend
   - CSV parsing with pandas (safe)
   - File size limits enforced

4. **Error Handling**
   - User-friendly error messages
   - Graceful degradation
   - Clear validation feedback
   - Structured logging

5. **Code Quality**
   - **TypeScript:** Strict mode, no `any` types
   - **Go:** `gofmt`, proper error handling, no panics
   - **Python:** Ruff linting, type hints, PEP 8
   - Consistent naming conventions

### Constraints

- **No Database:** Stateless services, in-memory caching only
- **No Persistent Storage:** CSV files cached temporarily
- **No Automated Tests Yet:** Manual testing for now (add in future)
- **No Deployment Automation:** Focus on local development first

### Environment Configuration

```bash
# Kolam
LOOM_API_URL=http://localhost:8080/api/v1
VITE_CLERK_PUBLISHABLE_KEY=pk_test_...

# Loom
PORT=8080
CLERK_SECRET_KEY=sk_test_...
WEAVER_GRPC_URL=localhost:50051
ALGORITHM_SPECS_PATH=../algorithms
ALLOWED_ORIGINS=http://localhost:3000

# Weaver
GRPC_PORT=50051
ALGORITHM_SPECS_PATH=../algorithms
```

### Future Considerations

- Add automated testing (unit + integration)
- Add database for persistent workspaces
- Add background job processing for long-running algorithms
- Add dataset versioning
- Add experiment tracking
- Add deployment automation

[1]: https://base.uber.com/?utm_source=chatgpt.com "Base design system - Uber"
[2]: https://v2.rsbuild.dev/guide/start/?utm_source=chatgpt.com "Introduction"
[3]: https://fastapi.tiangolo.com/?utm_source=chatgpt.com "FastAPI"
[4]: https://docs.astral.sh/uv/?utm_source=chatgpt.com "uv - Astral Docs"
[5]: https://base.uber.com/6d2425e9f/p/976582-typography?utm_source=chatgpt.com "Typography - Base design system - Uber"
