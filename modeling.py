from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    f1_score,
    fbeta_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import (
    OneHotEncoder,
    StandardScaler,
)


# ---------------------------------------------------------------------
# Temporal split configuration
# ---------------------------------------------------------------------

TRAIN_END = pd.Timestamp("2024-12-31")
VALIDATION_END = pd.Timestamp("2025-04-30")


@dataclass
class DataSplits:
    """
    Container for chronological train, validation and test datasets.
    """

    train: pd.DataFrame
    validation: pd.DataFrame
    test: pd.DataFrame


def temporal_split(
    modeling_data: pd.DataFrame,
) -> DataSplits:
    """
    Split reservations chronologically.

    Train:
        arrival_date <= 2024-12-31

    Validation:
        2025-01-01 to 2025-04-30

    Test:
        2025-05-01 onwards

    This approximates deployment, where historical
    reservations are used to predict later reservations.
    """

    data = (
        modeling_data
        .sort_values("arrival_date")
        .reset_index(drop=True)
    )

    train = data.loc[
        data["arrival_date"] <= TRAIN_END
    ].copy()

    validation = data.loc[
        (
            data["arrival_date"]
            > TRAIN_END
        )
        & (
            data["arrival_date"]
            <= VALIDATION_END
        )
    ].copy()

    test = data.loc[
        data["arrival_date"]
        > VALIDATION_END
    ].copy()

    if any(
        len(split) == 0
        for split in [
            train,
            validation,
            test,
        ]
    ):
        raise ValueError(
            "Temporal split produced an empty dataset."
        )

    if (
        len(train)
        + len(validation)
        + len(test)
        != len(data)
    ):
        raise ValueError(
            "Temporal split lost or duplicated rows."
        )

    if not (
        train["arrival_date"].max()
        < validation["arrival_date"].min()
        < test["arrival_date"].min()
    ):
        raise ValueError(
            "Temporal split periods overlap."
        )

    return DataSplits(
        train=train,
        validation=validation,
        test=test,
    )


# ---------------------------------------------------------------------
# Predictor definitions
# ---------------------------------------------------------------------

NUMERIC_FEATURES = [
    "lead_time_clean",
    "arrival_year",
    "arrival_month",
    "arrival_weekday",
    "stays_in_weekend_nights",
    "stays_in_week_nights",
    "total_nights",
    "adults",
    "children",
    "babies",
    "adr_clean",
    "is_repeated_guest",
    "previous_cancellations",
    "previous_bookings_not_canceled",
    "days_in_waiting_list",
    "required_car_parking_spaces",
    "total_of_special_requests",
    "has_agent",
    "has_company",
    "has_promo_code",
]


CATEGORICAL_FEATURES = [
    "hotel_clean",
    "meal_clean",
    "country_clean",
    "reserved_room_type_clean",
    "deposit_type_clean",
    "customer_type_clean",
    "market_segment_clean",
    "distribution_channel_clean",
]


TARGET_COLUMN = "fall_through_flag"


def get_xy(
    dataframe: pd.DataFrame,
):
    """
    Separate candidate predictors from the modelling target.
    """

    feature_columns = (
        NUMERIC_FEATURES
        + CATEGORICAL_FEATURES
    )

    X = dataframe[
        feature_columns
    ].copy()

    y = dataframe[
        TARGET_COLUMN
    ].copy()

    return X, y


# ---------------------------------------------------------------------
# Preprocessing
# ---------------------------------------------------------------------

def build_preprocessor() -> ColumnTransformer:
    """
    Build preprocessing that is fitted using training data only.

    Numeric:
        median imputation + standardisation

    Categorical:
        most-frequent imputation + one-hot encoding
    """

    numeric_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(
                    strategy="median"
                ),
            ),
            (
                "scaler",
                StandardScaler(),
            ),
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(
                    strategy="most_frequent"
                ),
            ),
            (
                "encoder",
                OneHotEncoder(
                    handle_unknown="ignore"
                ),
            ),
        ]
    )

    return ColumnTransformer(
        transformers=[
            (
                "numeric",
                numeric_pipeline,
                NUMERIC_FEATURES,
            ),
            (
                "categorical",
                categorical_pipeline,
                CATEGORICAL_FEATURES,
            ),
        ]
    )


# ---------------------------------------------------------------------
# Candidate models
# ---------------------------------------------------------------------

def build_dummy_pipeline() -> Pipeline:
    """
    Naive probability baseline.
    """

    return Pipeline(
        steps=[
            (
                "preprocessor",
                build_preprocessor(),
            ),
            (
                "model",
                DummyClassifier(
                    strategy="prior"
                ),
            ),
        ]
    )


def build_logistic_pipeline() -> Pipeline:
    """
    Interpretable linear baseline.
    """

    return Pipeline(
        steps=[
            (
                "preprocessor",
                build_preprocessor(),
            ),
            (
                "model",
                LogisticRegression(
                    max_iter=1000,
                    random_state=42,
                ),
            ),
        ]
    )


def build_random_forest_pipeline(
    n_estimators: int = 300,
    max_depth: int | None = None,
    min_samples_leaf: int = 2,
) -> Pipeline:
    """
    Non-linear Random Forest classifier.
    """

    return Pipeline(
        steps=[
            (
                "preprocessor",
                build_preprocessor(),
            ),
            (
                "model",
                RandomForestClassifier(
                    n_estimators=n_estimators,
                    max_depth=max_depth,
                    min_samples_leaf=min_samples_leaf,
                    random_state=42,
                    n_jobs=-1,
                ),
            ),
        ]
    )


# ---------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------

def evaluate_probabilities(
    y_true: pd.Series,
    probabilities,
    threshold: float = 0.5,
) -> dict[str, float]:
    """
    Calculate probability and threshold-based metrics.
    """

    predictions = (
        probabilities >= threshold
    ).astype(int)

    return {
        "roc_auc": roc_auc_score(
            y_true,
            probabilities,
        ),
        "average_precision": (
            average_precision_score(
                y_true,
                probabilities,
            )
        ),
        "brier_score": (
            brier_score_loss(
                y_true,
                probabilities,
            )
        ),
        "precision": precision_score(
            y_true,
            predictions,
            zero_division=0,
        ),
        "recall": recall_score(
            y_true,
            predictions,
            zero_division=0,
        ),
        "f1": f1_score(
            y_true,
            predictions,
            zero_division=0,
        ),
        "f2": fbeta_score(
            y_true,
            predictions,
            beta=2,
            zero_division=0,
        ),
    }


def compare_models_on_validation(
    splits: DataSplits,
) -> pd.DataFrame:
    """
    Compare initial candidate models on validation data.

    Model architecture is primarily compared using
    Average Precision.
    """

    X_train, y_train = get_xy(
        splits.train
    )

    X_validation, y_validation = get_xy(
        splits.validation
    )

    candidate_models = {
        "Dummy": build_dummy_pipeline(),
        "Logistic Regression": (
            build_logistic_pipeline()
        ),
        "Random Forest": (
            build_random_forest_pipeline()
        ),
    }

    results = []

    for model_name, pipeline in (
        candidate_models.items()
    ):
        print()
        print(
            f"Training {model_name}..."
        )

        pipeline.fit(
            X_train,
            y_train,
        )

        probabilities = (
            pipeline.predict_proba(
                X_validation
            )[:, 1]
        )

        metrics = evaluate_probabilities(
            y_validation,
            probabilities,
        )

        results.append(
            {
                "model": model_name,
                **metrics,
            }
        )

        print(
            "Validation Average Precision: "
            f"{metrics['average_precision']:.4f}"
        )

        print(
            "Validation ROC-AUC: "
            f"{metrics['roc_auc']:.4f}"
        )

        print(
            "Validation Brier score: "
            f"{metrics['brier_score']:.4f}"
        )

    return (
        pd.DataFrame(results)
        .sort_values(
            "average_precision",
            ascending=False,
        )
        .reset_index(drop=True)
    )


# ---------------------------------------------------------------------
# Lightweight Random Forest optimisation
# ---------------------------------------------------------------------

def tune_random_forest(
    splits: DataSplits,
):
    """
    Compare a small, predefined set of Random Forest
    configurations using validation Average Precision.

    This is intentionally limited to avoid excessive
    validation-set tuning.
    """

    X_train, y_train = get_xy(
        splits.train
    )

    X_validation, y_validation = get_xy(
        splits.validation
    )

    configurations = [
        {
            "name": "RF_base",
            "n_estimators": 300,
            "max_depth": None,
            "min_samples_leaf": 2,
        },
        {
            "name": "RF_depth20",
            "n_estimators": 300,
            "max_depth": 20,
            "min_samples_leaf": 2,
        },
        {
            "name": "RF_leaf5",
            "n_estimators": 300,
            "max_depth": None,
            "min_samples_leaf": 5,
        },
    ]

    tuning_results = []

    best_pipeline = None
    best_configuration = None
    best_probabilities = None
    best_ap = -np.inf

    for config in configurations:
        print()
        print(
            f"Training {config['name']}..."
        )

        pipeline = (
            build_random_forest_pipeline(
                n_estimators=(
                    config["n_estimators"]
                ),
                max_depth=(
                    config["max_depth"]
                ),
                min_samples_leaf=(
                    config["min_samples_leaf"]
                ),
            )
        )

        pipeline.fit(
            X_train,
            y_train,
        )

        probabilities = (
            pipeline.predict_proba(
                X_validation
            )[:, 1]
        )

        metrics = evaluate_probabilities(
            y_validation,
            probabilities,
        )

        tuning_results.append(
            {
                "configuration": (
                    config["name"]
                ),
                "n_estimators": (
                    config["n_estimators"]
                ),
                "max_depth": (
                    str(
                        config["max_depth"]
                    )
                ),
                "min_samples_leaf": (
                    config[
                        "min_samples_leaf"
                    ]
                ),
                "average_precision": (
                    metrics[
                        "average_precision"
                    ]
                ),
                "roc_auc": (
                    metrics["roc_auc"]
                ),
                "brier_score": (
                    metrics["brier_score"]
                ),
            }
        )

        print(
            "Average Precision: "
            f"{metrics['average_precision']:.4f}"
        )

        print(
            "ROC-AUC: "
            f"{metrics['roc_auc']:.4f}"
        )

        print(
            "Brier score: "
            f"{metrics['brier_score']:.4f}"
        )

        if (
            metrics["average_precision"]
            > best_ap
        ):
            best_ap = (
                metrics[
                    "average_precision"
                ]
            )

            best_pipeline = pipeline
            best_configuration = config
            best_probabilities = (
                probabilities
            )

    tuning_table = (
        pd.DataFrame(
            tuning_results
        )
        .sort_values(
            "average_precision",
            ascending=False,
        )
        .reset_index(drop=True)
    )

    return (
        best_pipeline,
        best_configuration,
        best_probabilities,
        tuning_table,
    )


# ---------------------------------------------------------------------
# Threshold selection
# ---------------------------------------------------------------------

def select_f2_threshold(
    y_true: pd.Series,
    probabilities,
):
    """
    Select a validation threshold using F2.

    F2 weights recall more heavily than precision,
    which reflects the intended risk-identification use case.

    No quantified business cost matrix is available,
    so F2 is used as a transparent practical rule.
    """

    threshold_values = np.arange(
        0.10,
        0.81,
        0.01,
    )

    rows = []

    for threshold in threshold_values:
        predictions = (
            probabilities >= threshold
        ).astype(int)

        rows.append(
            {
                "threshold": threshold,
                "precision": (
                    precision_score(
                        y_true,
                        predictions,
                        zero_division=0,
                    )
                ),
                "recall": (
                    recall_score(
                        y_true,
                        predictions,
                        zero_division=0,
                    )
                ),
                "f1": (
                    f1_score(
                        y_true,
                        predictions,
                        zero_division=0,
                    )
                ),
                "f2": (
                    fbeta_score(
                        y_true,
                        predictions,
                        beta=2,
                        zero_division=0,
                    )
                ),
            }
        )

    threshold_table = pd.DataFrame(
        rows
    )

    best_row = threshold_table.loc[
        threshold_table[
            "f2"
        ].idxmax()
    ]

    return (
        float(best_row["threshold"]),
        best_row,
        threshold_table,
    )


# ---------------------------------------------------------------------
# Business-facing ranking diagnostic
# ---------------------------------------------------------------------

def calculate_top_risk_metrics(
    y_true: pd.Series,
    probabilities,
    top_fraction: float = 0.20,
) -> dict[str, float]:
    """
    Evaluate concentration of actual fall-throughs
    among the highest-risk reservations.

    The top-20% result is a diagnostic, not an
    assumed operational capacity requirement.
    """

    results = pd.DataFrame(
        {
            "actual": (
                y_true.to_numpy()
            ),
            "risk_score": probabilities,
        }
    )

    results = (
        results
        .sort_values(
            "risk_score",
            ascending=False,
        )
        .reset_index(drop=True)
    )

    top_n = max(
        1,
        int(
            len(results)
            * top_fraction
        ),
    )

    top_risk = results.head(
        top_n
    )

    total_positives = (
        results["actual"].sum()
    )

    captured_positives = (
        top_risk["actual"].sum()
    )

    recall_at_top = (
        captured_positives
        / total_positives
    )

    precision_at_top = (
        top_risk[
            "actual"
        ].mean()
    )

    base_rate = (
        results[
            "actual"
        ].mean()
    )

    lift = (
        precision_at_top
        / base_rate
    )

    return {
        "top_fraction": top_fraction,
        "recall_at_top": (
            recall_at_top
        ),
        "precision_at_top": (
            precision_at_top
        ),
        "lift_at_top": lift,
    }


# ---------------------------------------------------------------------
# Split diagnostics
# ---------------------------------------------------------------------

def print_split_summary(
    splits: DataSplits,
) -> None:
    """
    Print row counts, date ranges and target rates.
    """

    for name, dataframe in [
        ("Train", splits.train),
        (
            "Validation",
            splits.validation,
        ),
        ("Test", splits.test),
    ]:

        positive_rate = (
            dataframe[
                TARGET_COLUMN
            ].mean()
            * 100
        )

        print()
        print(name)
        print("-" * len(name))

        print(
            f"Rows: {len(dataframe):,}"
        )

        print(
            "Arrival range:",
            dataframe[
                "arrival_date"
            ].min().date(),
            "to",
            dataframe[
                "arrival_date"
            ].max().date(),
        )

        print(
            "Fall-through rate:",
            f"{positive_rate:.2f}%"
        )


# ---------------------------------------------------------------------
# Standalone development run
# ---------------------------------------------------------------------

if __name__ == "__main__":
    from src.data import (
        load_and_prepare_source_data,
    )

    from src.features import (
        prepare_modeling_data,
    )

    # -------------------------------------------------------------
    # Data preparation
    # -------------------------------------------------------------

    bookings = (
        load_and_prepare_source_data()
    )

    modeling_data = (
        prepare_modeling_data(
            bookings
        )
    )

    splits = temporal_split(
        modeling_data
    )

    print()
    print(
        "Temporal split completed."
    )

    print_split_summary(
        splits
    )

    X_train, y_train = get_xy(
        splits.train
    )

    print()
    print(
        "Training predictors:",
        X_train.shape[1],
    )

    print(
        "Training target rows:",
        len(y_train),
    )

    print()
    print(
        "Numeric predictors:",
        len(NUMERIC_FEATURES),
    )

    print(
        "Categorical predictors:",
        len(CATEGORICAL_FEATURES),
    )

    # -------------------------------------------------------------
    # Initial model comparison
    # -------------------------------------------------------------

    print()
    print(
        "Initial validation model comparison..."
    )

    validation_results = (
        compare_models_on_validation(
            splits
        )
    )

    print()
    print(
        "Initial validation results:"
    )

    print(
        validation_results.to_string(
            index=False
        )
    )

    # -------------------------------------------------------------
    # Lightweight Random Forest tuning
    # -------------------------------------------------------------

    print()
    print(
        "Lightweight Random Forest tuning..."
    )

    (
        best_rf_pipeline,
        best_rf_configuration,
        best_rf_probabilities,
        tuning_table,
    ) = tune_random_forest(
        splits
    )

    print()
    print(
        "Random Forest tuning results:"
    )

    print(
        tuning_table.to_string(
            index=False
        )
    )

    print()
    print(
        "Selected RF configuration:"
    )

    print(
        best_rf_configuration
    )

    # -------------------------------------------------------------
    # Validation threshold selection
    # -------------------------------------------------------------

    _, y_validation = get_xy(
        splits.validation
    )

    (
        selected_threshold,
        selected_threshold_row,
        _,
    ) = select_f2_threshold(
        y_validation,
        best_rf_probabilities,
    )

    print()
    print(
        "Selected validation threshold "
        "(maximum F2):"
    )

    print(
        f"{selected_threshold:.2f}"
    )

    print()
    print(
        "Metrics at selected threshold:"
    )

    print(
        selected_threshold_row.to_string()
    )

    # -------------------------------------------------------------
    # Top-risk business diagnostic
    # -------------------------------------------------------------

    top_risk_metrics = (
        calculate_top_risk_metrics(
            y_validation,
            best_rf_probabilities,
            top_fraction=0.20,
        )
    )

    print()
    print(
        "Validation Top-20% risk diagnostic:"
    )

    print(
        "Share of actual fall-throughs "
        "captured:",
        f"{top_risk_metrics['recall_at_top']:.2%}",
    )

    print(
        "Fall-through rate among "
        "top-risk reservations:",
        f"{top_risk_metrics['precision_at_top']:.2%}",
    )

    print(
        "Lift versus validation baseline:",
        f"{top_risk_metrics['lift_at_top']:.2f}x",
    )

    # -------------------------------------------------------------
    # Test period intentionally untouched
    # -------------------------------------------------------------

    print()
    print(
        "Development complete."
    )

    print(
        "Final test period has NOT been "
        "evaluated yet."
    )