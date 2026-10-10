import calendar

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------

def normalize_text(series: pd.Series) -> pd.Series:
    """
    Standardise basic text formatting while preserving missing values
    as an explicit 'Unknown' category.
    """
    cleaned = (
        series
        .astype("string")
        .fillna("")
        .str.strip()
        .str.lower()
        .str.replace(r"\s+", " ", regex=True)
    )

    missing_like = {
        "",
        "-",
        "unknown",
        "undefined",
        "na",
        "n/a",
        "null",
        "nan",
    }

    return cleaned.where(
        ~cleaned.isin(missing_like),
        "unknown",
    )


def parse_numeric(
    series: pd.Series,
) -> pd.Series:
    """
    Convert ordinary numeric text to numeric values.
    """
    return pd.to_numeric(
        series.astype("string").str.strip(),
        errors="coerce",
    )


def parse_lead_time(
    series: pd.Series,
) -> pd.Series:
    """
    Recover numeric lead-time values from formats such as:
    '14', '14 days', etc.

    Negative lead times are logically invalid and are treated as missing.
    """
    text = (
        series
        .astype("string")
        .str.strip()
    )

    numeric = pd.to_numeric(
        text.str.extract(
            r"(-?\d+(?:\.\d+)?)"
        )[0],
        errors="coerce",
    )

    numeric = numeric.mask(
        numeric < 0,
        np.nan,
    )

    return numeric


def parse_adr(
    series: pd.Series,
) -> pd.Series:
    """
    Recover ADR values from observed formats such as:
    '172.50', '172,50', and 'SGD 172.50'.
    """
    text = (
        series
        .astype("string")
        .str.strip()
        .str.replace(
            "SGD",
            "",
            case=False,
            regex=False,
        )
        .str.replace(
            ",",
            ".",
            regex=False,
        )
        .str.strip()
    )

    return pd.to_numeric(
        text,
        errors="coerce",
    )


def parse_binary(
    series: pd.Series,
) -> pd.Series:
    """
    Standardise common binary representations.
    """
    mapping = {
        "0": 0,
        "no": 0,
        "false": 0,
        "1": 1,
        "yes": 1,
        "true": 1,
    }

    cleaned = (
        series
        .astype("string")
        .str.strip()
        .str.lower()
    )

    return cleaned.map(mapping)


# ---------------------------------------------------------------------
# Category cleaning
# ---------------------------------------------------------------------

def clean_deposit_type(
    series: pd.Series,
) -> pd.Series:
    cleaned = (
        normalize_text(series)
        .str.replace("-", " ", regex=False)
        .str.replace(r"\s+", " ", regex=True)
    )

    mapping = {
        "no deposit": "No Deposit",
        "no depost": "No Deposit",
        "non refund": "Non Refund",
        "refundable": "Refundable",
        "unknown": "Unknown",
    }

    return cleaned.map(
        lambda value: mapping.get(
            value,
            value.title(),
        )
    )


def clean_market_segment(
    series: pd.Series,
) -> pd.Series:
    cleaned = (
        normalize_text(series)
        .str.replace("-", " ", regex=False)
        .str.replace(r"\s+", " ", regex=True)
    )

    def map_value(value: str) -> str:
        compact = value.replace(" ", "")

        if compact in {
            "onlineta",
            "onlinta",
        }:
            return "Online TA"

        if compact in {
            "offlineta/to",
            "offlineta/t0",
        }:
            return "Offline TA/TO"

        mapping = {
            "groups": "Groups",
            "direct": "Direct",
            "corporate": "Corporate",
            "complementary": "Complementary",
            "aviation": "Aviation",
            "unknown": "Unknown",
        }

        return mapping.get(
            value,
            value.title(),
        )

    return cleaned.map(map_value)


def clean_distribution_channel(
    series: pd.Series,
) -> pd.Series:
    cleaned = normalize_text(series)

    mapping = {
        "ta/to": "TA/TO",
        "direct": "Direct",
        "corporate": "Corporate",
        "gds": "GDS",
        "unknown": "Unknown",
    }

    return cleaned.map(
        lambda value: mapping.get(
            value,
            value.title(),
        )
    )


def clean_customer_type(
    series: pd.Series,
) -> pd.Series:
    cleaned = normalize_text(series)

    mapping = {
        "transient": "Transient",
        "transiant": "Transient",
        "transient-party": "Transient-Party",
        "transient party": "Transient-Party",
        "contract": "Contract",
        "group": "Group",
        "unknown": "Unknown",
    }

    return cleaned.map(
        lambda value: mapping.get(
            value,
            value.title(),
        )
    )


# ---------------------------------------------------------------------
# Arrival date
# ---------------------------------------------------------------------

def build_arrival_date(
    dataframe: pd.DataFrame,
) -> pd.Series:
    """
    Construct a proper arrival date from year/month/day fields.
    Supports both full and abbreviated English month names.
    """
    month_mapping = {}

    for month_number in range(1, 13):
        full_name = calendar.month_name[
            month_number
        ].lower()

        abbreviation = calendar.month_abbr[
            month_number
        ].lower()

        month_mapping[full_name] = month_number
        month_mapping[abbreviation] = month_number

    month_clean = (
        dataframe["arrival_date_month"]
        .astype("string")
        .str.strip()
        .str.lower()
    )

    month_number = month_clean.map(
        month_mapping
    )

    year = pd.to_numeric(
        dataframe["arrival_date_year"],
        errors="coerce",
    )

    day = pd.to_numeric(
        dataframe[
            "arrival_date_day_of_month"
        ],
        errors="coerce",
    )

    arrival_date = pd.to_datetime(
        {
            "year": year,
            "month": month_number,
            "day": day,
        },
        errors="coerce",
    )

    return arrival_date


# ---------------------------------------------------------------------
# Target
# ---------------------------------------------------------------------

def create_target(
    dataframe: pd.DataFrame,
) -> pd.Series:
    """
    Create the binary reservation fall-through target.

    0 = Check-Out
    1 = Canceled or No-Show
    """
    status = (
        dataframe["reservation_status"]
        .astype("string")
        .str.strip()
    )

    mapping = {
        "Check-Out": 0,
        "Canceled": 1,
        "No-Show": 1,
    }

    return status.map(mapping)


# ---------------------------------------------------------------------
# Main feature preparation
# ---------------------------------------------------------------------

def prepare_modeling_data(
    bookings: pd.DataFrame,
) -> pd.DataFrame:
    """
    Apply EDA-driven cleaning and feature engineering.

    The returned dataframe contains:
    - leakage-safe candidate predictors
    - fall_through_flag target
    - arrival_date for temporal splitting
    - reservation_status for subtype diagnostics
    """
    df = bookings.copy()

    # -------------------------------------------------------------
    # Target
    # -------------------------------------------------------------

    df["fall_through_flag"] = create_target(
        df
    )

    # -------------------------------------------------------------
    # Dates
    # -------------------------------------------------------------

    df["arrival_date"] = build_arrival_date(
        df
    )

    df["arrival_year"] = (
        df["arrival_date"].dt.year
    )

    df["arrival_month"] = (
        df["arrival_date"]
        .dt.month
        .astype("Int64")
    )

    df["arrival_weekday"] = (
        df["arrival_date"]
        .dt.dayofweek
        .astype("Int64")
    )

    # -------------------------------------------------------------
    # Numeric cleaning
    # -------------------------------------------------------------

    df["lead_time_clean"] = parse_lead_time(
        df["lead_time"]
    )

    df["adr_clean"] = parse_adr(
        df["adr"]
    )

    numeric_columns = [
        "stays_in_weekend_nights",
        "stays_in_week_nights",
        "adults",
        "children",
        "babies",
        "previous_cancellations",
        "previous_bookings_not_canceled",
        "days_in_waiting_list",
        "required_car_parking_spaces",
        "total_of_special_requests",
    ]

    for column in numeric_columns:
        df[column] = parse_numeric(
            df[column]
        )

    df["is_repeated_guest"] = (
        parse_binary(
            df["is_repeated_guest"]
        )
    )

    # -------------------------------------------------------------
    # Derived numeric features
    # -------------------------------------------------------------

    df["total_nights"] = (
        df["stays_in_weekend_nights"]
        + df["stays_in_week_nights"]
    )

    # -------------------------------------------------------------
    # Categorical cleaning
    # -------------------------------------------------------------

    df["deposit_type_clean"] = (
        clean_deposit_type(
            df["deposit_type"]
        )
    )

    df["market_segment_clean"] = (
        clean_market_segment(
            df["market_segment"]
        )
    )

    df[
        "distribution_channel_clean"
    ] = clean_distribution_channel(
        df["distribution_channel"]
    )

    df["customer_type_clean"] = (
        clean_customer_type(
            df["customer_type"]
        )
    )

    # Basic normalization for other categories.
    for column in [
        "hotel",
        "meal",
        "country",
        "reserved_room_type",
    ]:
        df[f"{column}_clean"] = (
            normalize_text(
                df[column]
            )
            .str.title()
        )

    # -------------------------------------------------------------
    # Presence indicators for high-cardinality identifiers
    # -------------------------------------------------------------

    for column in [
        "agent",
        "company",
        "promo_code",
    ]:
        normalized = normalize_text(
            df[column]
        )

        df[f"has_{column}"] = (
            normalized != "unknown"
        ).astype(int)

    # -------------------------------------------------------------
    # Explicit modelling feature set
    # -------------------------------------------------------------

    feature_columns = [
        # Property
        "hotel_clean",

        # Booking horizon / timing
        "lead_time_clean",
        "arrival_year",
        "arrival_month",
        "arrival_weekday",

        # Stay structure
        "stays_in_weekend_nights",
        "stays_in_week_nights",
        "total_nights",
        "adults",
        "children",
        "babies",

        # Booking/product
        "meal_clean",
        "country_clean",
        "reserved_room_type_clean",
        "deposit_type_clean",
        "adr_clean",
        "customer_type_clean",

        # Acquisition channel
        "market_segment_clean",
        "distribution_channel_clean",

        # Customer history
        "is_repeated_guest",
        "previous_cancellations",
        "previous_bookings_not_canceled",

        # Confirmation context
        "days_in_waiting_list",

        # Booking intent / commitment
        "required_car_parking_spaces",
        "total_of_special_requests",

        # Presence indicators
        "has_agent",
        "has_company",
        "has_promo_code",
    ]

    metadata_columns = [
        "arrival_date",
        "reservation_status",
        "fall_through_flag",
    ]

    output_columns = (
        feature_columns
        + metadata_columns
    )

    result = df[
        output_columns
    ].copy()

    # Rows without a valid target or arrival date cannot be
    # used for supervised temporal modelling.
    result = result.dropna(
        subset=[
            "fall_through_flag",
            "arrival_date",
        ]
    )

    result["fall_through_flag"] = (
        result["fall_through_flag"]
        .astype(int)
    )

    return result.reset_index(
        drop=True
    )


if __name__ == "__main__":
    from src.data import (
        load_and_prepare_source_data,
    )

    bookings = (
        load_and_prepare_source_data()
    )

    modeling_data = (
        prepare_modeling_data(
            bookings
        )
    )

    print()
    print("Feature preparation completed.")
    print(
        f"Rows available for modelling: "
        f"{len(modeling_data):,}"
    )
    print(
        f"Candidate predictors: "
        f"{modeling_data.shape[1] - 3}"
    )

    print()
    print("Target distribution:")

    target_summary = (
        modeling_data[
            "fall_through_flag"
        ]
        .value_counts()
        .sort_index()
    )

    print(target_summary)

    print()
    print("Target rates (%):")

    target_rates = (
        modeling_data[
            "fall_through_flag"
        ]
        .value_counts(
            normalize=True
        )
        .sort_index()
        * 100
    ).round(2)

    print(target_rates)

    print()
    print(
        "Arrival date range:",
        modeling_data[
            "arrival_date"
        ].min().date(),
        "to",
        modeling_data[
            "arrival_date"
        ].max().date(),
    )

    print()
    print(
        "Missing cleaned lead_time:",
        modeling_data[
            "lead_time_clean"
        ].isna().sum(),
    )

    print(
        "Missing cleaned ADR:",
        modeling_data[
            "adr_clean"
        ].isna().sum(),
    )