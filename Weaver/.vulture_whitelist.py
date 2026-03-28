# Vulture whitelist for false positives in Weaver
# These items are used but cannot be detected by static analysis

# Algorithm adapters - loaded dynamically via importlib in spec_registry.py
_.AdaBoostAdapter
_.DecisionTreeAdapter
_.GradientBoostingAdapter
_.KNNAdapter
_.LinearRegressionAdapter
_.LogisticRegressionAdapter
_.NaiveBayesAdapter
_.RandomForestAdapter
_.SVMAdapter
_.XGBoostAdapter
_.DBSCANAdapter
_.IsolationForestAdapter
_.KMeansAdapter
_.PCAAdapter
_.TSNEAdapter

# proto generted files


# gRPC service methods - called by gRPC framework via protobuf bindings
_.HealthCheck
_.InferSchema
_.ValidateRun
_.ExecuteRun

# Pydantic model fields - accessed dynamically by Pydantic
_.label
_.cardinality
