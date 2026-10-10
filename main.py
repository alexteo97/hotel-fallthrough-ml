from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from sklearn.metrics import confusion_matrix

from src.data import (
    load_and_prepare_source_data,
)

from src.features import (
    prepare_modeling_data,
)

from src.modeling import (
    TARGET_COLUMN,
    build_random_forest_pipeline,
    calculate_top_risk_metrics,
    evaluate_probabilities,
    get_xy,
    temporal_split,
)


# ---------------------------------------------------------------------
# Final model configuration
# ---------------------------------------------------------------------
#
# These values were selected using validation data only.
# They are frozen before final test evaluation.
#

FINAL_RF_CONFIG = {
    "n_estimators": 300,
    "max_depth": 20,
    "min_samples_leaf": 2,
}

FINAL_THRESHOLD = 0.13


def evaluate_subtypes(
    test_data: pd.DataFrame,
    predictions,
) -> dict[str, dict[str, float | int]]:
    """
    Check whether the combined fall-through model identifies
    cancellations and no-shows separately.

    This is a diagnostic because cancellations dominate the
    positive class.
    """

    results = test_data[
        [
            "reservation_status",
            TARGET_COLUMN,
        ]
    ].copy()

    results = results.reset_index(
        drop=True
    )

    results["prediction"] = predictions

    normalised_status = (
        results["reservation_status"]
        .astype("string")
        .str.strip()
        .str.lower()
        .str.replace(
            "-",
            "",
            regex=False,
        )
        .str.replace(
            " ",
            "",
            regex=False,
        )
    )

    cancellation_mask = (
        normalised_status.isin(
            [
                "canceled",
                "cancelled",
            ]
        )
    )

    no_show_mask = (
        normalised_status
        == "noshow"
    )

    subtype_metrics = {}

    for (
        subtype_name,
        subtype_mask,
    ) in [
        (
            "Canceled",
            cancellation_mask,
        ),
        (
            "No-Show",
            no_show_mask,
        ),
    ]:
        subtype_rows = results.loc[
            subtype_mask
        ]

        count = len(
            subtype_rows
        )

        if count == 0:
            recall = float("nan")
        else:
            recall = (
                subtype_rows[
                    "prediction"
                ].mean()
            )

        subtype_metrics[
            subtype_name
        ] = {
            "count": count,
            "recall": recall,
        }

    return subtype_metrics


def run_pipeline() -> dict:
    """
    Run the complete modelling workflow.

    Steps:
        1. Load raw SQLite booking data.
        2. Remove exact duplicates.
        3. Apply deterministic feature preparation.
        4. Split chronologically.
        5. Fit the frozen model using training data.
        6. Evaluate once on the final test period.
        7. Produce business and subtype diagnostics.
    """

    print(
        "=" * 60
    )

    print(
        "Travelers' Inn Fall-Through "
        "Prediction Pipeline"
    )

    print(
        "=" * 60
    )

    # -------------------------------------------------------------
    # Load source data
    # -------------------------------------------------------------

    bookings = (
        load_and_prepare_source_data()
    )

    # -------------------------------------------------------------
    # Feature preparation
    # -------------------------------------------------------------

    modeling_data = (
        prepare_modeling_data(
            bookings
        )
    )

    # -------------------------------------------------------------
    # Temporal split
    # -------------------------------------------------------------

    splits = temporal_split(
        modeling_data
    )

    print()
    print(
        "Chronological split:"
    )

    for (
        name,
        dataframe,
    ) in [
        (
            "Train",
            splits.train,
        ),
        (
            "Validation",
            splits.validation,
        ),
        (
            "Test",
            splits.test,
        ),
    ]:
        print(
            f"{name}: "
            f"{len(dataframe):,} rows, "
            f"{dataframe[TARGET_COLUMN].mean():.2%} "
            "fall-through"
        )

    # -------------------------------------------------------------
    # Build frozen final model
    # -------------------------------------------------------------

    print()
    print(
        "Final model configuration:"
    )

    print(
        FINAL_RF_CONFIG
    )

    print(
        "Frozen classification threshold:",
        FINAL_THRESHOLD,
    )

    final_model = (
        build_random_forest_pipeline(
            n_estimators=(
                FINAL_RF_CONFIG[
                    "n_estimators"
                ]
            ),
            max_depth=(
                FINAL_RF_CONFIG[
                    "max_depth"
                ]
            ),
            min_samples_leaf=(
                FINAL_RF_CONFIG[
                    "min_samples_leaf"
                ]
            ),
        )
    )

    # -------------------------------------------------------------
    # Training
    # -------------------------------------------------------------

    X_train, y_train = get_xy(
        splits.train
    )

    print()
    print(
        "Training final Random Forest..."
    )

    final_model.fit(
        X_train,
        y_train,
    )

    print(
        "Training completed."
    )

    # -------------------------------------------------------------
    # FINAL TEST EVALUATION
    # -------------------------------------------------------------

    X_test, y_test = get_xy(
        splits.test
    )

    print()
    print(
        "=" * 60
    )

    print(
        "FINAL TEMPORAL TEST EVALUATION"
    )

    print(
        "=" * 60
    )

    test_probabilities = (
        final_model.predict_proba(
            X_test
        )[:, 1]
    )

    test_metrics = (
        evaluate_probabilities(
            y_test,
            test_probabilities,
            threshold=(
                FINAL_THRESHOLD
            ),
        )
    )

    test_predictions = (
        test_probabilities
        >= FINAL_THRESHOLD
    ).astype(int)

    print()
    print(
        "Test fall-through prevalence:",
        f"{y_test.mean():.2%}",
    )

    print(
        "Average Precision:",
        f"{test_metrics['average_precision']:.4f}",
    )

    print(
        "ROC-AUC:",
        f"{test_metrics['roc_auc']:.4f}",
    )

    print(
        "Brier score:",
        f"{test_metrics['brier_score']:.4f}",
    )

    print(
        "Precision:",
        f"{test_metrics['precision']:.4f}",
    )

    print(
        "Recall:",
        f"{test_metrics['recall']:.4f}",
    )

    print(
        "F1:",
        f"{test_metrics['f1']:.4f}",
    )

    print(
        "F2:",
        f"{test_metrics['f2']:.4f}",
    )

    # -------------------------------------------------------------
    # Confusion matrix
    # -------------------------------------------------------------

    (
        true_negative,
        false_positive,
        false_negative,
        true_positive,
    ) = confusion_matrix(
        y_test,
        test_predictions,
        labels=[
            0,
            1,
        ],
    ).ravel()

    print()
    print(
        "Confusion matrix counts:"
    )

    print(
        "True negatives:",
        f"{true_negative:,}",
    )

    print(
        "False positives:",
        f"{false_positive:,}",
    )

    print(
        "False negatives:",
        f"{false_negative:,}",
    )

    print(
        "True positives:",
        f"{true_positive:,}",
    )

    # -------------------------------------------------------------
    # Business-facing Top-20% diagnostic
    # -------------------------------------------------------------

    top_risk_metrics = (
        calculate_top_risk_metrics(
            y_test,
            test_probabilities,
            top_fraction=0.20,
        )
    )

    print()
    print(
        "Test Top-20% risk diagnostic:"
    )

    print(
        "Share of actual fall-throughs captured:",
        (
            f"{top_risk_metrics['recall_at_top']:.2%}"
        ),
    )

    print(
        "Fall-through rate among top-risk reservations:",
        (
            f"{top_risk_metrics['precision_at_top']:.2%}"
        ),
    )

    print(
        "Lift versus test baseline:",
        (
            f"{top_risk_metrics['lift_at_top']:.2f}x"
        ),
    )

    # -------------------------------------------------------------
    # Cancellation vs No-Show diagnostic
    # -------------------------------------------------------------

    subtype_metrics = (
        evaluate_subtypes(
            splits.test,
            test_predictions,
        )
    )

    print()
    print(
        "Positive-class subtype diagnostic:"
    )

    for (
        subtype,
        values,
    ) in subtype_metrics.items():
        print(
            f"{subtype}: "
            f"{values['count']:,} cases, "
            f"recall = "
            f"{values['recall']:.2%}"
        )

    # -------------------------------------------------------------
    # Collect final metrics
    # -------------------------------------------------------------

    final_results = {
        "model": (
            "RandomForestClassifier"
        ),
        "model_configuration": (
            FINAL_RF_CONFIG
        ),
        "threshold": (
            FINAL_THRESHOLD
        ),
        "test_rows": (
            len(splits.test)
        ),
        "test_prevalence": (
            float(
                y_test.mean()
            )
        ),
        "test_metrics": {
            key: float(value)
            for (
                key,
                value,
            ) in test_metrics.items()
        },
        "confusion_matrix": {
            "true_negative": (
                int(
                    true_negative
                )
            ),
            "false_positive": (
                int(
                    false_positive
                )
            ),
            "false_negative": (
                int(
                    false_negative
                )
            ),
            "true_positive": (
                int(
                    true_positive
                )
            ),
        },
        "top_20_percent": {
            key: float(value)
            for (
                key,
                value,
            ) in (
                top_risk_metrics.items()
            )
        },
        "subtype_metrics": (
            subtype_metrics
        ),
    }

    # -------------------------------------------------------------
    # Save final metrics
    # -------------------------------------------------------------

    output_directory = Path(
        "outputs"
    )

    output_directory.mkdir(
        exist_ok=True
    )

    metrics_path = (
        output_directory
        / "metrics.json"
    )

    with metrics_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            final_results,
            file,
            indent=2,
        )

    print()
    print(
        "Final metrics saved to:",
        metrics_path,
    )

    print()
    print(
        "=" * 60
    )

    print(
        "Pipeline completed successfully."
    )

    print(
        "=" * 60
    )

    return final_results


if __name__ == "__main__":
    run_pipeline()