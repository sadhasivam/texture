from pydantic import BaseModel


class AlgorithmParameter(BaseModel):
    name: str
    type: str
    default: float | int | str | bool
    label: str
    options: list[str] | None = None


class AlgorithmTarget(BaseModel):
    required: bool
    allowed_types: list[str]
    cardinality: str


class AlgorithmFeatures(BaseModel):
    required: bool
    min_columns: int
    max_columns: int | None
    allowed_types: list[str]


class AlgorithmOutputs(BaseModel):
    metrics: list[str]
    charts: list[str]
    tables: list[str]


class AlgorithmMetadata(BaseModel):
    id: str
    name: str
    category: str
    group: str  # supervised, unsupervised, anomaly_detection
    subgroup: str  # regression, classification, both, clustering, dimensionality_reduction
    description: str
    target: AlgorithmTarget
    features: AlgorithmFeatures
    parameters: list[AlgorithmParameter]
    outputs: AlgorithmOutputs
    validation_rules: list[str]


class AlgorithmSummary(BaseModel):
    id: str
    name: str
    category: str
    group: str
    subgroup: str
    description: str
