# AIAP Batch 25 Technical Assessment

## Travelers' Inn Reservation Fall-Through Prediction

**Name:** Alex Teo

**Email:** alexteo97@hotmail.com

---

## 1. Project Overview

Travelers' Inn operates two properties:

- City Hotel
- Airport Hotel

Management highlighted several profitability concerns, including reservation cancellations and no-shows, as well as room pricing that is currently influenced heavily by intuition.

The objective of this project was first to use exploratory data analysis (EDA) to determine which business problem could be addressed most defensibly using the available data, and then to build a reproducible machine-learning pipeline for the selected problem.

The final selected problem is:

> **Predict the risk that a confirmed reservation will fall through because of cancellation or no-show rather than result in a completed stay, using only information available before the final reservation outcome is known.**

The intended use is to provide the Revenue & Reservations team with earlier visibility of future inventory and revenue exposure so that higher-risk bookings can be prioritised for review and operational planning.

The model is intended as a **decision-support and risk-ranking tool**, not as an automated instruction to cancel, resell or overbook rooms.

---

## 2. Repository Structure

```text
.
├── .github/
│   └── workflows/
│       └── github-actions.yml
│
├── data/
│   └── hotel.db                  # Local only; excluded from Git
│
├── src/
│   ├── __init__.py
│   ├── data.py                   # Data loading and source deduplication
│   ├── features.py               # Cleaning and feature engineering
│   ├── modeling.py               # Splitting, preprocessing, models and validation
│   └── main.py                   # Final end-to-end pipeline
│
├── outputs/
│   └── metrics.json              # Generated after pipeline execution
│
├── eda.ipynb
├── decision_log.md
├── prompt_chat_history.md
├── requirements.txt
├── run.sh
└── README.md


---

## 3. How to Run the Project

### 3.1 Install dependencies

From the repository root:

```bash
pip install -r requirements.txt
```

The main dependencies are:

```text
numpy==2.5.2
pandas==3.0.5
scikit-learn==1.9.0
matplotlib==3.11.1
```

### 3.2 Run the complete pipeline

```bash
bash ./run.sh
```

`run.sh` executes:

```bash
python -m src.main
```

The pipeline will:

1. locate or retrieve `hotel.db`;
2. load the booking records;
3. remove exact duplicate source rows;
4. apply deterministic data-cleaning rules;
5. create the modelling target and predictors;
6. split the data chronologically;
7. fit the frozen preprocessing and Random Forest model;
8. evaluate the model on the final temporal test period;
9. calculate business-facing diagnostics; and
10. save final metrics to:

```text
outputs/metrics.json
```

The pipeline has also been successfully executed through the supplied GitHub Actions workflow.

---

## 4. Exploratory Data Analysis Summary

The detailed EDA is available in:

```text
eda.ipynb
```

The notebook was executed from a restarted kernel through to completion before final modelling.

### 4.1 Source Records

The bookings table initially contained:

```text
118,549 rows
36 columns
```

There were:

```text
353 exact duplicate booking records
```

After removing those exact duplicates:

```text
118,196 reservations remained
```

The cleaned reservation outcomes were:

| Outcome | Count |
|---|---:|
| Check-Out | 75,168 |
| Canceled | 41,849 |
| No-Show | 1,179 |
| **Total** | **118,196** |

A combined reservation fall-through outcome therefore occurred for:

```text
43,028 reservations
```

or:

```text
36.40%
```

of the deduplicated booking population.

### 4.2 Cancellation Timing Changed the Original Problem Framing

The stakeholder concern suggested that cancellations were predominantly last-minute.

The EDA did not fully support this assumption.

Among cancellations:

- median cancellation notice was approximately **56 days before arrival**;
- only **12.04%** occurred within seven days of arrival;
- approximately **19.92%** occurred within 14 days;
- approximately **33.27%** occurred within 30 days; and
- almost half occurred more than 60 days before arrival.

The business problem was therefore reframed from primarily:

> last-minute room recovery

towards:

> **earlier visibility of future reservation fall-through risk.**

This allows the analysis to remain aligned with what the data supports instead of forcing the original assumption onto the dataset.

### 4.3 Fall-Through Is Persistent but Varies by Property

Historical fall-through rates differed substantially between the properties:

| Hotel | Fall-Through Rate |
|---|---:|
| Airport Hotel | 27.59% |
| City Hotel | 40.78% |

Monthly EDA also showed that fall-through remained material across the observed period rather than being caused by one isolated month.

This suggested both:

- a persistent business issue; and
- variation that booking-time information may help explain.

### 4.4 Booking-Time Variables Contain Predictive Signal

Several characteristics available before the reservation outcome showed substantial differences in historical fall-through rate.

Examples include lead time, deposit type, market segment, distribution channel and customer type.

#### Lead Time

| Lead-Time Band | Fall-Through Rate |
|---|---:|
| 0–7 days | 9.53% |
| 8–30 days | 26.38% |
| 31–60 days | 36.46% |
| 61–90 days | 39.53% |
| 91–180 days | 44.62% |
| 181–365 days | 54.77% |
| 366+ days | 66.87% |

The raw data contained 300 negative lead-time values. These were treated as logically invalid rather than silently interpreted as genuine lead times.

Other booking characteristics also showed material differences in historical fall-through rates, including:

- deposit type;
- market segment;
- distribution channel;
- customer type;
- hotel; and
- other reservation characteristics.

These relationships are interpreted as **predictive associations**, not causal effects.

---

## 5. Why Fall-Through Prediction Was Selected

Two major machine-learning opportunities were considered:

1. reservation fall-through prediction; and
2. room pricing.

Pricing is clearly relevant to the business, and ADR varies substantially across properties and time.

However, the available dataset contains historical prices rather than an observed **optimal price**.

Important information required for genuine price optimisation is unavailable, including:

- competitor pricing;
- rejected demand;
- unconstrained demand;
- experimentally observed price elasticity;
- real-time inventory conditions; and
- the counterfactual outcome had a different price been offered.

A model predicting historical ADR would therefore risk reproducing historical pricing decisions rather than demonstrating that the predicted price is better.

Reservation fall-through was selected because it has:

- a directly observed outcome;
- substantial historical prevalence;
- clear business relevance;
- meaningful pre-outcome predictive signals; and
- a defensible operational prediction point.

---

## 6. Target Definition

The binary modelling target is:

```text
fall_through_flag
```

defined as:

```text
0 = Check-Out
1 = Canceled or No-Show
```

Cancellations account for the large majority of the positive class, while no-shows are comparatively uncommon.

The two outcomes were combined because both represent the same high-level operational outcome:

> a confirmed reservation does not become a completed stay.

Because cancellations dominate the positive class, cancellation and no-show performance are also reviewed separately during final evaluation.

---

## 7. Prediction Point and Leakage Control

The intended prediction point is after a reservation has been confirmed but before the eventual cancellation, no-show or completed stay is known.

Only information reasonably available before that final outcome is eligible as a predictor.

Several fields are intentionally excluded.

| Field | Decision | Reason |
|---|---|---|
| `reservation_status` | Excluded from predictors | Directly describes the final outcome |
| `reservation_status_date` | Excluded | Outcome-related information |
| `assigned_room_type` | Excluded | Actual room assignment occurs later |
| `booking_changes` | Excluded | Final value may include post-confirmation amendments |
| Review rating | Excluded | Post-stay information |
| Review comments | Excluded | Post-stay information |
| Review existence | Excluded | Availability depends on later customer behaviour |
| `booking_id` | Excluded | Identifier rather than generalisable signal |
| `client_email` | Excluded | High-cardinality personal identifier |
| `Unnamed: 0` | Excluded | Source export/index artefact |

`reservation_status` is used to construct the modelling target but is never supplied to the model as a predictor.

---

## 8. Data Cleaning and Feature Engineering

The production pipeline reproduces the cleaning requirements discovered during EDA directly from the raw SQLite source.

Deterministic cleaning is performed before the temporal split because these rules do not learn statistical information from future observations.

Learned preprocessing such as median imputation, scaling and categorical encoding is fitted using training data only.

### Feature Processing Summary

| Feature / Group | Processing |
|---|---|
| Exact duplicate rows | Removed |
| `lead_time` | Numeric value extracted; negative values treated as missing |
| `adr` | Currency symbols and decimal-format inconsistencies normalised |
| Arrival date | Constructed from validated year, month and day fields |
| Arrival month | Derived from arrival date |
| Arrival weekday | Derived from arrival date |
| Total nights | Weekend nights + weekday nights |
| Binary fields | Normalised into numeric binary values |
| Deposit type | Category spelling/case normalisation |
| Market segment | Category spelling/case normalisation |
| Distribution channel | Category spelling/case normalisation |
| Customer type | Category spelling/case normalisation |
| Agent | Converted to `has_agent` presence indicator |
| Company | Converted to `has_company` presence indicator |
| Promo code | Converted to `has_promo_code` presence indicator |
| Missing numeric values | Median imputation fitted on training data |
| Numeric predictors | Standardised |
| Missing categorical values | Most-frequent imputation fitted on training data |
| Categorical predictors | One-hot encoded |
| Previously unseen future categories | Safely ignored by encoder |

`OneHotEncoder(handle_unknown="ignore")` is used so that a category appearing in a later period does not cause the production pipeline to fail.

---

## 9. Final Candidate Predictors

The final modelling dataset contains:

```text
28 predictors
```

comprising:

```text
20 numeric predictors
8 categorical predictors
```

### Numeric Predictors

```text
lead_time_clean
arrival_year
arrival_month
arrival_weekday
stays_in_weekend_nights
stays_in_week_nights
total_nights
adults
children
babies
adr_clean
is_repeated_guest
previous_cancellations
previous_bookings_not_canceled
days_in_waiting_list
required_car_parking_spaces
total_of_special_requests
has_agent
has_company
has_promo_code
```

### Categorical Predictors

```text
hotel_clean
meal_clean
country_clean
reserved_room_type_clean
deposit_type_clean
customer_type_clean
market_segment_clean
distribution_channel_clean
```

---

## 10. Temporal Train / Validation / Test Design

A chronological split was used instead of a random split.

This better approximates the intended deployment scenario:

> learn from historical reservations and predict reservations from later periods.

The final split was:

| Split | Arrival Period | Rows | Fall-Through Rate |
|---|---|---:|---:|
| Train | Aug 2023–Dec 2024 | 77,577 | 35.18% |
| Validation | Jan 2025–Apr 2025 | 18,442 | 36.53% |
| Test | May 2025–Aug 2025 | 22,177 | 40.57% |

The later test period has a higher underlying fall-through rate, providing a useful test of temporal generalisation.

The roles of the splits were deliberately separated.

### Train

Used to:

- fit preprocessing; and
- fit model parameters.

### Validation

Used to:

- compare candidate models;
- perform limited Random Forest tuning; and
- choose the operating threshold.

### Test

Used only after development decisions were frozen to evaluate the final system on a later time period.

The final model was not modified in response to test-set performance.

---

## 11. Models Considered

Three models were initially evaluated.

### 11.1 DummyClassifier

The `DummyClassifier` provides a no-skill probability baseline.

It establishes whether the real models are learning meaningful predictive structure rather than only benefiting from the target distribution.

### 11.2 Logistic Regression

Logistic Regression was included as a relatively simple and interpretable classification baseline.

It provides a useful comparison against a more flexible nonlinear model.

### 11.3 Random Forest

Random Forest was included because the EDA suggested that fall-through risk may depend on nonlinear relationships and interactions across variables such as:

- lead time;
- deposit type;
- booking channel;
- customer type; and
- hotel.

Random Forest can model these relationships without requiring them to be explicitly specified in advance.

---

## 12. Model Evaluation Metrics

Accuracy was not used as the main metric because it can be misleading when one class occurs more frequently than another.

For example, predicting that every booking will complete could still achieve superficially reasonable accuracy while identifying no fall-throughs.

The main evaluation metrics are:

| Metric | Interpretation |
|---|---|
| Average Precision | Primary model-selection metric; assesses how effectively fall-through cases are prioritised across precision/recall trade-offs |
| ROC-AUC | Measures overall discrimination/ranking between completed and fall-through bookings |
| Brier Score | Measures risk-score error; lower is better |
| Precision | Among bookings flagged as risky, how many actually fall through |
| Recall | Among all actual fall-throughs, how many are identified |
| F1 | Balances precision and recall approximately equally |
| F2 | Places greater emphasis on recall |
| Top-risk capture | Measures how many fall-throughs are concentrated among highest-risk bookings |
| Lift | Compares the high-risk group's fall-through rate against the overall population |

---

## 13. Initial Validation Results

The first model comparison produced:

| Model | ROC-AUC | Average Precision | Brier Score | Precision @ 0.50 | Recall @ 0.50 | F1 @ 0.50 |
|---|---:|---:|---:|---:|---:|---:|
| Dummy | 0.5000 | 0.3653 | 0.2320 | 0.0000 | 0.0000 | 0.0000 |
| Logistic Regression | 0.8565 | 0.8044 | 0.1468 | 0.7054 | 0.7001 | 0.7027 |
| Random Forest | **0.8868** | **0.8413** | **0.1323** | **0.8314** | 0.5710 | 0.6770 |

Random Forest achieved the strongest threshold-independent ranking performance.

Logistic Regression had better F1 at the default 0.50 threshold, but the threshold is an operating decision rather than an appropriate basis for model architecture selection.

Random Forest was therefore carried forward for limited optimisation.

---

## 14. Lightweight Random Forest Optimisation

Hyperparameter optimisation was deliberately kept small to avoid excessive searching against the same validation period.

Three configurations were compared:

| Configuration | Trees | Max Depth | Min Samples Leaf | Average Precision | ROC-AUC | Brier |
|---|---:|---:|---:|---:|---:|---:|
| RF base | 300 | None | 2 | 0.8413 | 0.8868 | 0.1323 |
| **RF depth20** | **300** | **20** | **2** | **0.8434** | **0.8892** | 0.1323 |
| RF leaf5 | 300 | None | 5 | 0.8430 | 0.8883 | **0.1322** |

The selected configuration was:

```text
RandomForestClassifier
n_estimators = 300
max_depth = 20
min_samples_leaf = 2
random_state = 42
```

The improvement over the original Random Forest was modest.

Further hyperparameter searching was therefore not considered justified.

---

## 15. Threshold Selection

Model selection and alert-threshold selection were treated as separate decisions.

There was no supplied business cost matrix or operational requirement such as a minimum acceptable precision.

The validation threshold was therefore selected using **F2**, which places greater weight on recall than precision.

This matches the proposed use as a screening and risk-identification system, where missing a genuine fall-through is considered more undesirable than generating some additional review alerts.

The selected validation risk-score threshold was:

```text
0.13
```

Validation performance at this threshold:

| Metric | Result |
|---|---:|
| Precision | 52.70% |
| Recall | 96.30% |
| F1 | 0.6812 |
| F2 | 0.8263 |

This is intentionally a **high-recall screening threshold**.

It should not be interpreted as a rule for automatic cancellation, overbooking or room resale.

The raw Random Forest score is treated primarily as a **risk score** rather than assuming that a score such as `0.13` represents a perfectly calibrated 13% real-world probability.

---

## 16. Validation Business Diagnostic

The model's ranking was also evaluated independently of the hard alert threshold.

Among the highest-risk 20% of validation reservations:

- **48.56%** of all eventual fall-throughs were captured;
- **88.69%** of those selected reservations actually fell through; and
- the group achieved **2.43x lift** over the validation population.

The 20% cutoff is used only as a business-facing diagnostic.

It does not assume that Travelers' Inn has capacity to review exactly 20% of bookings.

---

## 17. Final Untouched Temporal Test Results

After all development decisions were frozen, the final model was evaluated on reservations arriving from May to August 2025.

The test period contained:

```text
22,177 reservations
40.57% fall-through prevalence
```

Final test performance:

| Metric | Test Result |
|---|---:|
| Average Precision | **0.8051** |
| ROC-AUC | **0.8510** |
| Brier Score | **0.1600** |
| Precision @ 0.13 | **52.71%** |
| Recall @ 0.13 | **97.87%** |
| F1 @ 0.13 | **0.6852** |
| F2 @ 0.13 | **0.8355** |

Performance declined moderately from validation on Average Precision, ROC-AUC and Brier score.

This indicates some temporal generalisation degradation in the later period.

However, discrimination remained meaningful and the predefined high-recall screening behaviour remained relatively stable.

The model was not retuned after viewing these results.

---

## 18. Final Confusion Matrix

At the frozen `0.13` threshold:

| Actual / Prediction | Predicted Completed | Predicted Fall-Through |
|---|---:|---:|
| Completed Stay | **5,278** true negatives | **7,901** false positives |
| Fall-Through | **192** false negatives | **8,806** true positives |

The threshold successfully captures nearly all fall-throughs but generates a substantial number of false-positive alerts.

Approximately 75% of test reservations are therefore classified into the high-recall screening group.

This is the major limitation of the `0.13` operating threshold.

It should be interpreted as a broad screening mechanism rather than a small operational watchlist.

---

## 19. Top-Risk Test Performance

The model ranking itself provides a more capacity-oriented interpretation.

Among the highest-risk 20% of test reservations:

| Metric | Result |
|---|---:|
| Share of all fall-throughs captured | **41.13%** |
| Fall-through rate within group | **83.45%** |
| Lift versus overall test population | **2.06x** |

Therefore:

> By reviewing only the highest-risk 20% of reservations, approximately 41% of all eventual fall-throughs are concentrated in a group where more than 83% of reservations historically fall through.

This demonstrates that the risk ranking may be useful for prioritisation even when acting on every reservation above the broad `0.13` screening threshold would be operationally impractical.

---

## 20. Cancellation and No-Show Diagnostic

Because cancellations dominate the positive class, final recall was checked separately.

| Positive Outcome | Test Cases | Recall |
|---|---:|---:|
| Canceled | 8,833 | **97.97%** |
| No-Show | 165 | **92.12%** |

The combined model therefore did not achieve its high aggregate recall solely by identifying cancellations while completely missing no-shows.

However, no-shows remain a much smaller subgroup, so conclusions about no-show performance are less statistically robust than conclusions about cancellation performance.

---

## 21. Final Model Interpretation

The final model demonstrates that reservation information available before the final outcome contains useful predictive signal.

The model should be interpreted as:

> a system for ranking upcoming reservations by historical fall-through risk.

It should **not** be interpreted as:

- proof that any individual feature causes cancellation;
- an instruction to automatically cancel bookings;
- an automatic overbooking system;
- proof of guaranteed recovered revenue; or
- a replacement for Revenue & Reservations judgement.

The model predicts reservation fall-through, but the dataset does not establish:

- whether cancelled inventory is later resold;
- what cancellation fees are retained;
- the cost of staff reviewing alerts;
- the cost of false-positive interventions; or
- the incremental revenue that an intervention would create.

The appropriate business benefit is therefore described as:

> **earlier visibility of future inventory and revenue exposure**

rather than guaranteed lost-revenue prevention.

---

## 22. Key Limitations

### Temporal Drift

Validation and test performance differ, and the test fall-through prevalence is higher than the earlier periods.

Model performance should therefore be monitored if deployed.

### High-Recall Threshold Creates Many Alerts

The F2-selected `0.13` threshold identifies almost all fall-throughs but flags a large share of all reservations.

The production threshold should ultimately be chosen using:

- operational review capacity;
- cost of false positives;
- cost of missed fall-throughs; and
- the actual business intervention.

### Risk Score Calibration

Brier score was used as a lightweight probability-quality diagnostic.

The Random Forest output is nevertheless described primarily as a **risk score**, because a Brier score alone does not demonstrate perfect probability calibration.

### Combined Target

The fall-through target combines cancellations and no-shows, but cancellations dominate the positive class.

Separate subgroup monitoring should therefore continue if deployed.

### Predictive, Not Causal

Strong associations between variables such as lead time, deposit type or booking channel and historical fall-through should not be interpreted as proof that changing those variables would cause fall-through to change.

### Pricing Is Not Solved by This Model

The model addresses reservation risk only.

The available data does not provide sufficient evidence for genuine price optimisation.

---

## 23. Deployment Considerations and Next Steps

If this model were taken beyond the assessment, recommended next steps would include:

1. integrate risk scoring into the reservation workflow at the defined prediction point;
2. determine the operational action associated with different risk levels;
3. obtain business estimates for:
   - alert-review cost;
   - missed fall-through cost;
   - potential recovered revenue;
4. use those estimates to choose a production operating threshold;
5. monitor:
   - fall-through prevalence;
   - feature distributions;
   - Average Precision;
   - ROC-AUC;
   - precision and recall;
   - risk-score calibration;
6. monitor cancellations and no-shows separately;
7. retrain when performance materially deteriorates or booking behaviour changes; and
8. evaluate whether prioritised intervention actually improves realised commercial outcomes.

A useful operational design may be to use the model primarily as a **ranking system**, allowing staff to focus on the highest-risk portion of upcoming reservations based on available capacity.

---

## 24. Reproducibility

The complete pipeline is executable through:

```bash
bash ./run.sh
```

The supplied GitHub Actions workflow has successfully executed the same end-to-end pipeline on a fresh runner.

This verifies that the submission is not dependent only on the local development environment.

Final pipeline output is written to:

```text
outputs/metrics.json
```

The assessment database itself is intentionally excluded from Git.