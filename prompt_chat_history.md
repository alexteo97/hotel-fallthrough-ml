# AIAP Technical Assessment — Prompt Chat History

**Candidate name (as in NRIC):** Alex Teo

**Email (as used in your application):** alexteo97@hotmail.com

**AI assistant(s) used:** ChatGPT
---

## How to fill in this document

Your submission has **two parts**:

1. **Share links** — for every chat with the AI that has a share-link feature
   (Claude, ChatGPT, Gemini, etc.), paste the link in the section below.
2. **Transcripts** — produce each chat below, labelling messages as `[User]` or
   `[AI]`. Don't edit, summarise, or rewrite anything afterwards.

**Both parts are required where possible.** The share link is the audit trail
(timestamped on the platform's servers); the transcript is what the assessors
actually read. They will be cross-checked.

For tools without share links (IDE-based assistants like Cursor, GitHub Copilot
Chat, or Claude Code in agent mode), write *"not available"* under share links
for that chat and rely on the transcript.

### What counts as editing

- **Allowed:** removing personal identifiers (real names, emails, API keys);
  redacting any unrelated personal chats accidentally captured in the export;
  fixing copy-paste artefacts (stray HTML tags) into clean text.
- **Not allowed:** deleting messages, summarising responses, rewriting your
  messages afterwards, reordering turns, removing exchanges that look
  embarrassing or off-track.

If you make redactions, note them briefly at the top of the relevant session
(e.g., *"Redacted: two unrelated personal messages between turn 4 and turn 5."*).
That transparency is itself a positive signal.

---

## Part 1 — Share Links

- **Session 1** — EDA, ML development and final evaluation — ChatGPT: https://chatgpt.com/share/6a93d738-b1d4-83ec-8355-908a29262ab6

---

## Part 2 — Transcripts

Produce each chat below using the format:

```
[User] your message here

[AI] assistant's response here

[User] your next message

[AI] next response
```

Use one blank line between turns. Don't edit, summarise, or rewrite anything afterwards.

---

### Session 1 — EDA, ML development and final evaluation — ChatGPT

[User] I am working on the AIAP Batch 25 Technical Assessment. I have attached the full assessment instructions and my current eda.ipynb. I have already completed the project setup, GitHub repository and GitHub Actions setup, Python environment setup, and the initial part of the EDA. I want to continue working through the assessment properly rather than have you generate the whole solution for me. Please first read the assessment requirements and my current EDA notebook carefully before suggesting changes. Some context on the direction I am exploring: the business has issues with cancellations/no-shows as well as pricing. One possible solution I am considering is a layered approach where we first predict bookings at high risk of cancellation/no-show, then use that information to support room recovery/replacement demand and potentially pricing decisions. However, I do not want to lock in the ML problem until the EDA gives enough evidence. For now:
1. Review my existing EDA structure, markdown, code and outputs.
2. Tell me if anything already done is technically incorrect, redundant or weakly explained.
3. Continue the EDA with me step by step from where the notebook currently stops.
4. Explain why each analysis is necessary and what decision it supports.
5. Pay particular attention to data quality, leakage, target definition and whether the booking/review relationship is safe to use.
6. Do not jump straight into modelling yet. We should finish the EDA and use its findings to justify the final ML problem first.
I want the final work to remain coherent across eda.ipynb, the ML pipeline, README, Decision Log and AI chat history.
eda.ipynb
File
AIAP 25 Technical Assessment.pdf
PDF

[AI] I read the assessment instructions and went through your current eda.ipynb cell by cell, including the saved outputs. I agree with your approach: do not choose the final ML problem yet. The assessment deliberately gives a vague business request and expects you to refine it based on your reasoning and EDA, rather than simply assuming “predict cancellations” from the outset.

Your notebook currently stops at the right place conceptually: you have established the dataset structure, investigated data-quality issues, validated the cancellation outcome, and identified the first obvious leakage fields. The assessment specifically expects the EDA to explain the purpose, conclusions, interpretation, and implications of each step, not merely output statistics.

1. Overall assessment of what you have so far

The direction and structure are good. I would not rewrite the notebook from scratch.

Your opening is especially useful because you have deliberately framed six EDA questions rather than prematurely declaring a modelling objective. That keeps cancellation/no-show, pricing, reviews, and the eventual problem-selection decision connected.

There are, however, several things I would fix before moving into the main business EDA.

Area	My assessment	What I would change
Business framing	Good	Keep it. It reflects the assessment rather than prematurely choosing a model.
Dataset overview	Good	Minor wording change around what a review represents after we establish the true grain.
Duplicate investigation	Very useful	You have found the duplicates but have not yet removed them before calculating business statistics. This needs fixing.
Unnamed: 0 investigation	Correct	Conclude explicitly that it is non-business metadata/export index and exclude it.
client_email analysis	Good question, but interpretation needs revision	The apparent duplicates appear to be data duplication, not genuine repeated customers/reviews.
Booking-review join	Important and correctly investigated	Need to test the relationship after deduplication, then separately address temporal leakage.
Missing-value analysis	Technically sound	Add interpretation of structural missingness and missing-like tokens such as unknown and -.
Numeric validation	Strong	Do not simply coerce malformed values to NaN; several are clearly recoverable formatting errors.
Target consistency	Strong	Recalculate the target distribution after deduplication and rename it more accurately if combining cancellations and no-shows.
Leakage analysis	Correct but incomplete	Add assigned_room_type, booking_changes, reviews, and define the model's prediction timestamp.
Notebook presentation	Needs cleanup eventually	Execution counts are out of order and at least one saved output appears stale. Restart + Run All before submission.
Explanations	Uneven	Sections 3.1–3.5 mostly show evidence but do not yet give explicit conclusions/decisions.
Visualisations	None yet	Fine at this stage, but the next business sections need strong visualisations because they are explicitly evaluated.

There are two particularly important technical issues.

2. The biggest correction: deduplicate before calculating business rates

You found:

353 duplicated booking_id groups;
exactly 353 full-row duplicate booking records;
51 exact duplicate review rows.

That is excellent data-quality work.

But your later cancellation figure of 43,151 / 118,549 = 36.40% is still calculated on the raw table containing those duplicate rows.

So I would not present 36.40% as the final business cancellation/fall-through rate yet.

It might barely change after deduplication, but conceptually the denominator should be unique reservation records, not duplicated source rows.

The assessment describes booking_id as the unique reservation identifier, so duplicates violate the expected grain.

Your final notebook should therefore make the logic explicit:

Raw data-quality inspection → detect duplicate ingestion records → remove exact duplicates → establish one-row-per-booking analytical grain → calculate business statistics.

That same cleaning decision later belongs in the pipeline.

3. Your booking-review relationship is actually more interesting than it first appears

Your raw results show:

118,549 booking rows but 118,196 unique emails;
17,583 review rows but 17,532 unique emails;
raw inner join = 17,632 rows, even though there are only 17,532 unique review-linked emails.

At first glance that looks like a many-to-many problem.

But combine that with what you already discovered:

353 booking duplicates are exact full-row duplicates;
51 review duplicates are exact full-row duplicates.

After dropping those duplicates:

bookings should have 118,196 rows and 118,196 unique emails;
reviews should have 17,532 rows and 17,532 unique emails.

So the evidence strongly suggests the raw join inflation is caused by duplicate records, rather than genuine multiple bookings/reviews per email.

This also fits the supplied data dictionary: client_email is specifically the key connecting reviews to bookings, and it is described as the review key.

Therefore I would revise this markdown:

“However, a customer may have more than one booking or review.”

That is currently an assumption. Your actual evidence is pointing in another direction.

A more precise conclusion will probably be:

The apparent duplicate client_email values arise from exact duplicate records. After deduplication, the booking-review relationship should be reassessed to determine whether client_email forms a one-to-one linkage for the reviewed subset.

We'll verify that rather than assume it.

4. Even if the review join is structurally safe, it is not necessarily modelling-safe

This distinction is very important for your assessment.

There are two separate questions:

Structural safety: Does joining on client_email unexpectedly multiply rows?

Temporal/modelling safety: Would the information actually have existed when the prediction was made?

Your notebook has started addressing the first one, but we need to make the second explicit.

The assessment says these are post-stay guest reviews.

Therefore a rating or comment from the same reservation cannot be used to predict whether that reservation will cancel/no-show. The stay has already happened before the review exists.

So if cancellation/fall-through becomes the ML problem:

same-booking rating and comments are leakage and must not be predictors.

There is another likely issue: selection bias.

A guest who canceled or never showed up normally cannot submit a post-stay review. So merely knowing:

has_review = True

may itself almost reveal the outcome.

We should test that explicitly in the EDA.

Reviews can still be extremely useful for:

customer-experience analysis;
perceived-value/pricing investigation;
understanding why completed-stay customers are satisfied/dissatisfied;

but that does not mean they belong in the cancellation feature matrix.

5. Your leakage discussion is correct, but needs to go further

You correctly wrote that reservation_status and reservation_status_date describe the eventual outcome and must not be predictors.

I agree completely.

But there are some additional fields we need to classify.

assigned_room_type

The documentation says this is the room type actually assigned at check-in.

If we want to predict cancellation before arrival, this should almost certainly be excluded.

It is not known at the prediction point for someone who hasn't checked in.

booking_changes

This is trickier.

The assessment defines it as amendments made between:

creation and check-in / cancellation.

If we predict immediately when the booking is confirmed, the final number of future booking changes is unavailable.

So using the final booking_changes count would leak future information.

If the business instead wanted a model that is rescored one day before arrival, booking changes up to that point might be useful—but this dataset doesn't give change timestamps, so we can't reconstruct that safely.

days_in_waiting_list

This depends on our scoring point.

If the booking is scored after confirmation, it may be known.

If scored at original booking creation, it is future information.

Reviews

Definitely unavailable for same-booking pre-arrival prediction.

6. This means we eventually need an explicit prediction timestamp

This is going to become one of the most important reasoning decisions in your whole assessment.

Right now I would not yet lock the problem, but I would use this provisional rule during EDA:

When examining possible predictive features, ask whether the feature would reasonably be known when the reservation is confirmed and before the eventual cancellation/no-show/check-in outcome.

That prevents accidental leakage while we investigate.

If cancellation prediction wins later, I think a booking/confirmation-time risk model will be the safest defensible formulation with this dataset.

That still supports your layered business concept:

booking risk → identify likely fall-through inventory → support recovery/replacement-demand decisions → potentially feed revenue-management decisions.

But we must be careful not to claim that the model predicts last-minute behaviour using last-minute signals when the dataset does not provide historical feature states over time.

7. One terminology change I recommend

Your normalized column is currently:

is_canceled_clean

But the crosstab proves that it contains both:

Canceled
No-Show

as positive outcomes.

That means, semantically, the target is not merely “cancellation”.

I would eventually call the analytical variable something like:

fall_through_flag

where:

0 = Check-Out
1 = Canceled or No-Show

That makes the business interpretation much cleaner.

Do not decide yet that this definitely becomes the ML target—we still need to compare cancellations and no-shows separately—but it is a better EDA variable name.

There are only 1,182 no-shows versus 41,969 cancellations in the raw table, so blindly combining them could hide genuinely different behaviour.

We should investigate that later.

8. Your numeric-data investigation is good, but don't throw away recoverable values

This section is one of the stronger technical parts of your notebook.

You discovered:

lead_time: 50 failed conversions;
arrival_date_week_number: 128 nonblank failed conversions;
adr: 319 failed conversions.

And then correctly inspected the source representations.

For example:

1 days
14 days
99 days

are clearly valid lead times with formatting corruption.

Similarly, week number contains explicit:

unknown
-

rather than numeric values.

And ADR has representations such as:

149,50
172,50
SGD 172.50

which look like formatting inconsistencies rather than genuinely missing prices.

So do not just use pd.to_numeric(..., errors="coerce") and accept the NaNs.

We should repair recoverable formatting first.

There is another useful possibility for arrival_date_week_number: if year + month + day make a valid arrival date, we can derive the ISO week ourselves instead of imputing corrupted values.

That is considerably cleaner.

9. Your missing-value analysis needs interpretation, not more counting

The calculation itself is good.

You found approximately:

company: 70.45% blank;
promo_code: 40.90%;
agent: 13.73%;
everything else is comparatively small.

Reviews have only 1.89% blank comments.

The next thing is not another missingness calculation.

It is deciding what the blanks mean.

For example, the data dictionary explicitly says agent is missing when no agency was involved and company is missing for most bookings.

So blank may encode something useful like:

No agent
No company
No promo

rather than random missingness.

That is materially different from statistical imputation.

This should later feed directly into your feature-processing table in README, which the assessment explicitly requires.

10. There is a notebook execution-state issue

This is not an analytical problem, but fix it before submission.

Your execution counts are currently out of order—for example later duplicate-check cells have counts in the high 20s while following cells have counts around 11–15.

More importantly, one early sampling cell's source prints both bookings and reviews, but its stored output only corresponds to the reviews output. That suggests the cell source was edited after its last execution.

Nothing disastrous, but before the final commit:

Restart Kernel → Run All → confirm every displayed output matches the source → save.

That matters because the notebook itself must work as a presentation and explanations must be clear.

11. What I think we should do next

I would not start plotting feature-vs-cancellation relationships yet.

First close the grain/review/leakage question properly.

Your immediate next section should be something like:

3.7 Establishing the analysis-ready dataset

Add this next.

# Remove exact duplicate source records
bookings_clean = bookings.drop_duplicates().copy()
reviews_clean = reviews.drop_duplicates().copy()

dedup_summary = pd.DataFrame({
    "Dataset": ["bookings", "reviews"],
    "Raw rows": [len(bookings), len(reviews)],
    "Rows after deduplication": [
        len(bookings_clean),
        len(reviews_clean)
    ],
    "Rows removed": [
        len(bookings) - len(bookings_clean),
        len(reviews) - len(reviews_clean)
    ]
})

display(dedup_summary)

grain_check = pd.DataFrame({
    "Check": [
        "booking_id unique after deduplication",
        "booking client_email unique after deduplication",
        "review client_email unique after deduplication"
    ],
    "Result": [
        bookings_clean["booking_id"].is_unique,
        bookings_clean["client_email"].is_unique,
        reviews_clean["client_email"].is_unique
    ]
})

display(grain_check)
Why this analysis is necessary

It answers:

What is the actual observation grain after removing data-quality duplicates?

That determines whether every subsequent cancellation rate, ADR average, revenue estimate and review join is statistically valid.

From your existing numbers, I expect this will produce 118,196 bookings and 17,532 reviews—but let's let your notebook prove it explicitly rather than hard-code the conclusion.

Then immediately run this:

# Validate the booking-review relationship after deduplication

review_link_clean = bookings_clean[
    ["booking_id", "client_email", "reservation_status"]
].merge(
    reviews_clean[
        ["client_email", "rating", "comments"]
    ],
    on="client_email",
    how="inner",
    validate="one_to_one"
)

print("Rows in cleaned booking-review join:", len(review_link_clean))
print(
    "All cleaned reviews matched to a booking:",
    len(review_link_clean) == len(reviews_clean)
)

The key part here is:

validate="one_to_one"

That turns your assumption into an explicit data-integrity check.

And then this is the important leakage/selection-bias test:

review_emails_clean = set(
    reviews_clean["client_email"]
)

review_coverage = (
    bookings_clean
    .assign(
        has_review=lambda df:
            df["client_email"].isin(review_emails_clean)
    )
    .groupby("reservation_status")
    .agg(
        bookings=("booking_id", "size"),
        bookings_with_review=("has_review", "sum")
    )
)

review_coverage["review_coverage_pct"] = (
    review_coverage["bookings_with_review"]
    / review_coverage["bookings"]
    * 100
).round(2)

review_coverage
Why this matters

This answers a completely different question:

Who is actually capable of appearing in the reviews dataset?

If reviews overwhelmingly or exclusively belong to Check-Out reservations, we have strong evidence that review availability itself is determined by the eventual outcome.

That would mean:

reviews remain useful for customer-experience/pricing EDA;
reviews should not be joined into a cancellation model;
absence/presence of a review should not be a cancellation feature either.

That's exactly the type of leakage reasoning I would want an assessor to see.

Finally, recalculate the target on the deduplicated reservation grain:

cancel_mapping = {
    "0": 0,
    "no": 0,
    "false": 0,
    "1": 1,
    "yes": 1,
    "true": 1
}

bookings_clean["fall_through_flag"] = (
    bookings_clean["is_canceled"]
    .astype("string")
    .str.strip()
    .str.lower()
    .map(cancel_mapping)
)

print(
    "Unmapped target values:",
    bookings_clean["fall_through_flag"].isna().sum()
)

display(
    pd.crosstab(
        bookings_clean["fall_through_flag"],
        bookings_clean["reservation_status"],
        margins=True
    )
)

clean_outcome_summary = (
    bookings_clean["reservation_status"]
    .value_counts()
    .rename_axis("Reservation Status")
    .reset_index(name="Bookings")
)

clean_outcome_summary["Percent"] = (
    clean_outcome_summary["Bookings"]
    / len(bookings_clean)
    * 100
).round(2)

clean_outcome_summary

That should become the authoritative outcome distribution used in the rest of the notebook.

12. What comes immediately after this

Once those three outputs are established, I would proceed in this order:

Next analysis	Question it answers	Decision it supports
Arrival-date construction and date validation	Can we trust the temporal fields?	Enables time-based EDA and later temporal validation
Cancellation timing using reservation_status_date	Are cancellations genuinely “last minute,” and how much recovery time exists?	Tests the business's stated pain point and your recovery-layer idea
Outcome magnitude by hotel/year/month	Is the problem persistent and where is it concentrated?	Business impact and potential temporal drift
Cancellation vs no-show comparison	Are they similar enough to combine?	Target definition
Potential room-revenue exposure	Which fall-through bookings carry the most value?	Links classification risk to business action
Feature association analysis	Which booking-time characteristics contain useful signal?	Feature engineering and feasibility
ADR/pricing EDA	Is there enough evidence to justify a pricing ML task?	Competes against cancellation risk as final ML direction
Reviews separately	What do completed-stay guests reveal about perceived value?	Supports or weakens pricing hypothesis
Final problem-selection synthesis	Which opportunity is impactful, measurable, actionable and leakage-safe?	Final Decision Log / ML problem

The cancellation-timing analysis is especially important for your current layered idea. reservation_status_date is forbidden as a predictor, but it is perfectly legitimate during EDA to use it to quantify how many cancellations occur 0–2 days, 3–7 days, 8–14 days, etc. before arrival. The field is explicitly defined as the date the final status was set.

That evidence will tell us whether “room recovery” is actually a meaningful operational opportunity rather than merely a plausible story.

13. One caution on the pricing direction

I would absolutely continue exploring pricing, but I want to protect you from one common trap:

predicting historical adr is not the same thing as optimizing price.

If management historically set prices largely through intuition, a supervised model trained to reproduce those prices could simply learn to imitate their old pricing behaviour.

And this dataset does not obviously provide:

hotel room capacity;
competitor prices;
true unconstrained demand;
explicit room availability;
cancellation fees/refunds;
replacement-booking linkage;
an “optimal price” label.

So the pricing EDA needs to determine what is actually supportable.

Similarly, when we eventually calculate:

ADR × booked nights

for canceled reservations, I would call that potential booked room-revenue exposure, not “revenue lost”.

Some rooms may have been resold, and deposits or cancellation charges might have been retained. The dataset doesn't appear to tell us that.

This kind of careful wording will make the business reasoning much stronger.

14. Where I think you stand right now

I would characterize the current evidence as:

Cancellation/fall-through prediction is a promising candidate, but not yet selected. Pricing remains a competing business opportunity that needs EDA evidence. Reviews are potentially useful for understanding perceived value but are unlikely to be valid same-booking predictors for cancellation.

That is a much stronger position than already declaring:

“We will build a cancellation model.”

It also stays coherent with how the assessment is graded. Your final README is expected to trace pipeline choices and feature engineering back to EDA findings, while the Decision Log is explicitly supposed to capture your own reasoning and is cross-checked against the AI history. The chat-history requirement also explicitly asks for raw, unedited transcripts, so keeping this development genuinely sequential rather than retroactively manufacturing a story is the right approach.

So I suggest we stop here for one iteration: add/run the three cells above—deduplicated grain, cleaned review relationship/coverage, and cleaned target distribution—and send me those outputs. Then we'll interpret them together and move directly into arrival-date validation + cancellation timing, which is the next EDA question that can materially strengthen or weaken your layered room-recovery hypothesis.

[User] I agree with the issues you identified. One thing I want to change though is I don't want to create or save a separate cleaned dataset from the EDA. I would rather use the EDA to identify/document the cleaning needed, then implement those cleaning steps properly in the end-to-end ML pipeline since it needs to ingest the raw SQLite data anyway. For EDA calculations that would be affected by known issues like the exact duplicates or malformed numeric/date values, we can handle them temporarily so the analysis is still accurate, but not treat that as a separate cleaned data deliverable. I think we can close the data quality section with the main findings and pipeline implications, then move into the actual business EDA. Can we start with arrival-date validation and cancellation timing? I want to test the stakeholder's statement that rooms are being lost at the last minute, then look at fall-through by hotel/time and compare cancellations vs no-shows before deciding whether they should become one ML target. Also please continue explaining what each analysis tells us and why it matters, because I want to understand the data and be able to justify the final problem choice myself.

[AI] Yes — that separation is cleaner.

The EDA should diagnose and document the required cleaning; the production cleaning logic belongs in the ML pipeline because the pipeline must ingest the raw SQLite data itself. The assessment explicitly expects the eventual pipeline to fetch/process the data programmatically, while the notebook's role is exploration and explanation.

For EDA, I would use a temporary in-memory working frame only so known duplicate/corruption issues do not distort our conclusions. We are not creating a third dataset or saving anything.

I would now close Section 3 and move to business EDA.

Close Section 3 first

I suggest ending the data-quality section with a concise markdown summary rather than adding much more analysis there.

Markdown cell
### 3.7 Data quality findings and pipeline implications

The initial data-quality assessment identified several issues that must be handled before modelling or business analysis:

- The bookings table contains exact duplicate reservation records despite `booking_id` being defined as a unique reservation identifier.
- The reviews table also contains exact duplicate records.
- Apparent duplicate `client_email` values are therefore partly driven by duplicated source records, and the booking-review relationship should be assessed after duplicate removal before any join is used.
- Missing information is primarily represented by blank strings rather than database null values. Some fields, such as `agent` and `company`, may represent meaningful absence rather than random missingness.
- Several numeric fields contain inconsistent textual formatting. For example, `lead_time` contains values such as `"14 days"`, while `adr` contains currency prefixes and comma decimal separators.
- `is_canceled` uses multiple textual representations of the same binary outcome but is consistent with `reservation_status`.
- `reservation_status` and `reservation_status_date` describe the final booking outcome and would introduce target leakage if used as predictors for a pre-arrival risk model.

These findings will inform the preprocessing logic in the end-to-end ML pipeline. For the remaining EDA, known issues such as exact duplicates and recoverable formatting inconsistencies are handled temporarily in memory so that descriptive statistics are not distorted. No separate cleaned dataset is produced from the EDA.

That is enough. It directly satisfies the requirement to explain conclusions and implications rather than just generating diagnostics.

4. Reservation Outcomes and Timing

This should be the beginning of the actual business investigation.

I would make the section objective explicit:

## 4. Reservation Outcomes and Timing

The stakeholder reported that rooms are frequently lost because bookings are cancelled at the last minute or guests fail to arrive.

This section investigates whether the historical data supports that concern by:

1. validating the arrival-date fields;
2. estimating how far in advance cancellations occur;
3. determining what proportion of cancellations occur close enough to arrival to create a difficult room-recovery problem.

`reservation_status_date` is used here only to analyse historical outcomes. It represents information observed after the booking was made and will not be considered a predictive feature for a pre-arrival model.

That last sentence is worth keeping because it demonstrates leakage awareness while still making legitimate EDA use of the field.

The source describes reservation_status_date as the date on which the most recent reservation status was set.

4.1 Construct and validate the arrival date

Before measuring "days before arrival", we need one trustworthy arrival date.

The source gives us:

arrival year;
month;
week number;
day of month.

I would derive the date from year + month + day rather than trust arrival_date_week_number, because you've already shown the latter contains "unknown" and "-" values.

Temporary analysis frame
# Temporary in-memory frame for EDA only.
# No cleaned dataset is written or exported from the notebook.

bookings_eda = bookings.drop_duplicates().copy()

print("Raw booking rows:", len(bookings))
print("Rows used for EDA after exact duplicate removal:", len(bookings_eda))

This makes your philosophy explicit.

We're not pretending bookings_eda is the final pipeline dataset. We're just ensuring duplicate ingestion records do not inflate the analysis.

First inspect month values rather than assuming them
bookings_eda["arrival_date_month"].value_counts(dropna=False)
Why?

Before writing cleaning logic, we want to know whether months are consistently stored as:

January
February
...

or whether there are abbreviations, numbers, spelling problems, etc.

This is a small but good EDA habit:

inspect → understand → transform

rather than:

assume → transform.

If the output contains the expected 12 English month names, continue with:

month_map = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12
}

bookings_eda["arrival_month_num"] = (
    bookings_eda["arrival_date_month"]
    .astype("string")
    .str.strip()
    .str.lower()
    .map(month_map)
)

print(
    "Unrecognised month values:",
    bookings_eda["arrival_month_num"].isna().sum()
)

Do not automatically proceed if that count isn't zero. Show me what the bad values are first.

Construct the actual date
arrival_year = pd.to_numeric(
    bookings_eda["arrival_date_year"],
    errors="coerce"
)

arrival_day = pd.to_numeric(
    bookings_eda["arrival_date_day_of_month"],
    errors="coerce"
)

bookings_eda["arrival_date"] = pd.to_datetime(
    pd.DataFrame({
        "year": arrival_year,
        "month": bookings_eda["arrival_month_num"],
        "day": arrival_day
    }),
    errors="coerce"
)

arrival_date_summary = pd.Series({
    "Rows analysed": len(bookings_eda),
    "Invalid arrival dates": bookings_eda["arrival_date"].isna().sum(),
    "Earliest arrival": bookings_eda["arrival_date"].min(),
    "Latest arrival": bookings_eda["arrival_date"].max()
})

arrival_date_summary
What this tells us

Three things.

First, whether year/month/day can actually form valid calendar dates.

Second, the real temporal coverage of the dataset rather than merely trusting "three years" from the description.

Third, whether we can safely use calendar-derived features later such as:

month;
weekday;
weekend;
quarter;
ISO week;
season.
4.2 Validate the supplied week number

This is not essential for cancellation timing, but I think it is worth doing because you've already identified corruption in this field.

Rather than just saying:

128 week numbers are malformed,

we can ask the stronger question:

For the apparently valid values, are they actually consistent with the constructed date?

Use:

source_week = pd.to_numeric(
    bookings_eda["arrival_date_week_number"],
    errors="coerce"
)

derived_week = (
    bookings_eda["arrival_date"]
    .dt.isocalendar()
    .week
    .astype("Float64")
)

week_validation = pd.DataFrame({
    "source_week": source_week,
    "derived_week": derived_week
})

valid_comparison = (
    week_validation["source_week"].notna()
    & week_validation["derived_week"].notna()
)

week_mismatch = (
    valid_comparison
    & (
        week_validation["source_week"]
        != week_validation["derived_week"]
    )
)

print("Missing/non-numeric source week numbers:",
      source_week.isna().sum())

print("Comparable week-number records:",
      valid_comparison.sum())

print("Week-number mismatches:",
      week_mismatch.sum())

print(
    "Mismatch rate among comparable records:",
    f"{week_mismatch[valid_comparison].mean():.2%}"
)

Small correction: I'd actually calculate that last one slightly more clearly:

mismatch_rate = (
    week_mismatch.sum()
    / valid_comparison.sum()
)

print(
    "Mismatch rate among comparable records:",
    f"{mismatch_rate:.2%}"
)

If mismatches exist, inspect examples:

bookings_eda.loc[
    week_mismatch,
    [
        "arrival_date_year",
        "arrival_date_month",
        "arrival_date_day_of_month",
        "arrival_date_week_number",
        "arrival_date"
    ]
].head(20)
Why this particular check matters

It supports a future pipeline decision.

If year/month/day produce valid dates and the supplied week field is either corrupt or inconsistent, there is little reason to repair and model the original week field.

The cleaner pipeline decision would be:

derive ISO week from the validated arrival date.

That removes redundant source noise and makes the transformation deterministic.

This is exactly the kind of EDA → pipeline connection that should eventually appear in your README.

4.3 Validate reservation_status_date

Now do the same before using it.

bookings_eda["status_date"] = pd.to_datetime(
    bookings_eda["reservation_status_date"],
    errors="coerce"
)

status_date_summary = pd.Series({
    "Invalid status dates":
        bookings_eda["status_date"].isna().sum(),

    "Earliest status date":
        bookings_eda["status_date"].min(),

    "Latest status date":
        bookings_eda["status_date"].max()
})

status_date_summary
Why?

Because our next variable will be:

$$ \text{days before arrival} = \text{arrival date} - \text{cancellation status date} $$

If either side is malformed, the resulting timing analysis is meaningless.

4.4 Calculate cancellation lead time

Here I would deliberately use Canceled only first.

Do not combine no-shows yet.

cancellations_eda = (
    bookings_eda.loc[
        bookings_eda["reservation_status"].eq("Canceled")
    ]
    .copy()
)

cancellations_eda["days_before_arrival"] = (
    cancellations_eda["arrival_date"]
    - cancellations_eda["status_date"]
).dt.days
Why exclude No-Show here?

Because a cancellation has an observable cancellation date.

A no-show is fundamentally different: you generally only discover that the guest failed to arrive at or around arrival itself.

So if we combine them now, no-shows will mechanically pile up at zero days and make the situation look more "last minute" by definition.

That would muddy the question we're currently testing:

How late are actual cancellations?

We'll compare no-shows separately afterwards.

4.5 Sanity-check the timing variable before analysing it

Do this before a chart:

cancellation_timing_summary = (
    cancellations_eda["days_before_arrival"]
    .describe(
        percentiles=[0.10, 0.25, 0.50, 0.75, 0.90, 0.95]
    )
)

cancellation_timing_summary

And:

print(
    "Cancellations recorded after arrival:",
    (cancellations_eda["days_before_arrival"] < 0).sum()
)

print(
    "Cancellations recorded on arrival date:",
    (cancellations_eda["days_before_arrival"] == 0).sum()
)

If there are negative values, do not silently delete them yet.

Inspect them:

cancellations_eda.loc[
    cancellations_eda["days_before_arrival"] < 0,
    [
        "booking_id",
        "hotel",
        "arrival_date",
        "status_date",
        "days_before_arrival"
    ]
].head(20)

We need to understand whether those are:

genuine data inconsistencies;
date construction issues;
unusual business processes.
4.6 Quantify "last minute"

This is where the EDA starts answering the stakeholder directly.

Rather than arbitrarily declaring one definition of "last minute", show several operational windows.

valid_cancellation_timing = cancellations_eda.loc[
    cancellations_eda["days_before_arrival"] >= 0
].copy()

timing_thresholds = [0, 1, 2, 3, 7, 14, 30]

timing_summary = []

for days in timing_thresholds:
    count = (
        valid_cancellation_timing["days_before_arrival"]
        <= days
    ).sum()

    timing_summary.append({
        "Cancelled within days of arrival": days,
        "Cancellations": count,
        "Percent of cancellations": (
            count / len(valid_cancellation_timing) * 100
        )
    })

timing_summary = pd.DataFrame(timing_summary)

timing_summary["Percent of cancellations"] = (
    timing_summary["Percent of cancellations"]
    .round(2)
)

timing_summary

This gives you something like:

Within arrival	Share
same day	?
1 day	?
2 days	?
3 days	?
7 days	?
14 days	?
30 days	?

We don't know the results yet, and that's important.

Why I prefer this over only making bins

Suppose we eventually find:

5% within 1 day;
10% within 3 days;
20% within 7 days;
40% within 30 days.

Then saying:

“A large number of cancellations are last minute”

would be questionable.

But suppose it's:

20% within 1 day;
35% within 3 days;
50% within 7 days.

Now the stakeholder's complaint has much stronger empirical support.

The cumulative thresholds allow you to define "last minute" from an operational recovery perspective rather than pretending there is one universally correct cutoff.

4.7 Then show a timing distribution

After the numerical table, a visual makes sense.

I'd use buckets that management can interpret:

timing_bins = [-0.1, 0, 2, 7, 14, 30, 60, np.inf]

timing_labels = [
    "Same day",
    "1–2 days",
    "3–7 days",
    "8–14 days",
    "15–30 days",
    "31–60 days",
    "61+ days"
]

valid_cancellation_timing["timing_band"] = pd.cut(
    valid_cancellation_timing["days_before_arrival"],
    bins=timing_bins,
    labels=timing_labels
)

timing_distribution = (
    valid_cancellation_timing["timing_band"]
    .value_counts(sort=False)
    .rename("Cancellations")
    .to_frame()
)

timing_distribution["Percent"] = (
    timing_distribution["Cancellations"]
    / timing_distribution["Cancellations"].sum()
    * 100
)

timing_distribution

Then:

ax = (
    timing_distribution["Percent"]
    .plot(
        kind="bar",
        figsize=(10, 5)
    )
)

ax.set_title("When Do Cancellations Occur Before Arrival?")
ax.set_xlabel("Time Before Scheduled Arrival")
ax.set_ylabel("Share of Cancellations (%)")

plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.show()

This is your first genuinely important business visual.

What decision does this analysis support?

It isn't yet deciding which algorithm to use.

It supports a more fundamental decision:

Is predicting cancellation early enough to act on actually valuable?

There are two extreme outcomes.

Scenario A — many cancellations happen very late

Then your idea strengthens considerably:

Predict risk
    ↓
identify rooms likely to fall through
    ↓
support proactive inventory/recovery decisions

There is a genuine operational need because the business has little natural time to recover those rooms.

Scenario B — most cancellations happen weeks/months in advance

Then the stakeholder's perception of a "last-minute" problem may be overstated.

Cancellation prediction could still have value, but room recovery would be a weaker justification because management already receives substantial notice.

That is why this analysis belongs before model selection.

4.8 One subtle but important limitation

We should be careful about the phrase:

"lost at the last minute."

The data lets us establish when cancellation status was recorded.

It does not tell us whether the room ultimately stayed empty.

A cancelled room could have been rebooked.

Therefore the defensible conclusion is:

“X% of cancellations occur within seven days of arrival, leaving relatively little time for the hotel to replace the booking.”

Not:

“X% of rooms were lost within seven days.”

We don't know replacement occupancy.

This distinction is small in wording but important analytically.

After those outputs, don't jump to feature analysis yet

Once we've run this section, the next logical EDA will be:

4.9 Outcome by hotel and time

We will answer:

Does City Hotel have a materially different fall-through rate from Airport Hotel?
Is the issue stable across 2023–2025 or changing?
Is there seasonality?
Are there particular months where fall-through and demand exposure collide?

Then:

4.10 Cancellation vs No-Show

We will compare them separately on:

frequency;
hotel;
time;
lead time;
booking channel/segment;
possibly ADR/stay characteristics.

That will tell us whether Canceled + No-Show is a defensible single fall-through target, or whether no-shows behave sufficiently differently that collapsing them would obscure the problem.

Given your current raw data, no-shows are only 1,182 records compared with 41,969 cancellations, so this target-definition question is not trivial.

For now, I would run Sections 4.1–4.7 only. The outputs I care most about are the arrival-date validity check, week-number mismatch check, negative cancellation-timing records if any, timing percentiles, and the cumulative 0/1/2/3/7/14/30-day table. Once you have those numbers, we can interpret what they actually say about the stakeholder's “last-minute” claim rather than writing the conclusion in advance.

[User] Yes, let's proceed with Section 4 in that order. One thing I noticed from the earlier data inspection is that arrival_date_month appears to have inconsistent formats such as full month names and abbreviations, so let's inspect the actual unique values first and build the date conversion based on those rather than assuming only the 12 full names.

I'm okay using bookings_eda = bookings.drop_duplicates().copy() as a temporary in-memory frame for accurate EDA, as long as we don't save it as a separate cleaned dataset and the final pipeline later reproduces the required preprocessing from the raw SQLite data.

Let's start with the arrival-date validation and cancellation timing checks.

[AI] Yes. I would keep Section 4 deliberately sequential: first make sure the calendar fields are trustworthy, then calculate cancellation timing, and only then interpret whether “last-minute” is genuinely supported by the data. For EDA we can use a temporary bookings_eda frame in memory, while documenting that the production pipeline must reproduce all preprocessing from the raw SQLite source. That is consistent with the assessment requirement that the ML pipeline itself ingest and process the database.
4. Reservation Outcomes and Timing
I would start the section with this markdown:
## 4. Reservation Outcomes and Timing
The stakeholder reported that confirmed bookings are frequently lost at the last minute through cancellations and no-shows.
This section first validates the reservation date fields before investigating:
1. how far in advance cancellations are recorded;
2. what proportion occur close to the scheduled arrival date;
3. whether the pattern differs by hotel and over time; and
4. whether cancellations and no-shows appear sufficiently similar to represent a single reservation fall-through outcome.
`reservation_status_date` is used only for retrospective EDA because it records the eventual reservation outcome and would not be available as a predictor before that outcome occurs.
The assessment defines the arrival components separately and describes reservation_status_date as the date on which the latest reservation status was set.
4.1 Create the temporary EDA frame
Code cell
# Temporary in-memory frame used only to prevent known exact duplicates
# from distorting EDA statistics. Nothing is written to disk.
bookings_eda = bookings.drop_duplicates().copy()
print(f"Raw booking rows: {len(bookings):,}")
print(f"Rows after exact duplicate removal for EDA: {len(bookings_eda):,}")
print(f"Exact duplicate rows excluded: {len(bookings) - len(bookings_eda):,}")
Why this is necessary
We already established that the booking table contains exact duplicate records even though booking_id is intended to uniquely represent a reservation.
If we left those rows in, cancellation counts, percentages, ADR summaries, monthly volumes, etc. would be slightly inflated.
This does not mean the notebook is producing a cleaned dataset. It is just making the descriptive analysis internally correct.
4.2 Inspect the actual month representations
You are right not to assume twelve full month names.
Let's inspect both the exact values and their frequencies first.
Code cell
month_value_counts = (
    bookings_eda["arrival_date_month"]
    .value_counts(dropna=False)
    .rename_axis("Raw Month Value")
    .reset_index(name="Count")
)
month_value_counts
I'd also inspect trimmed values, because "Jan" and " Jan " would otherwise appear as separate categories:
month_normalized_preview = (
    bookings_eda["arrival_date_month"]
    .astype("string")
    .str.strip()
    .value_counts(dropna=False)
    .rename_axis("Trimmed Month Value")
    .reset_index(name="Count")
)
month_normalized_preview
What this tells us
We want to know whether the inconsistency is merely something like:
January
Jan
February
Feb
...
or whether there are more problematic representations such as:
Sept
09
9
September.
unknown
-
That determines the appropriate cleaning rule.
Decision supported
It tells us whether month parsing can be handled deterministically or whether some values need to be treated as invalid/missing.
Run this cell first.
If the observed values are just full names and standard abbreviations, I would use the following approach.
4.3 Standardise the observed month values
Rather than manually writing 24 separate mappings, we can create mappings for both official full names and abbreviations.
Code cell
import calendar
month_lookup = {}
for month_num in range(1, 13):
    full_name = calendar.month_name[month_num].lower()
    abbreviation = calendar.month_abbr[month_num].lower()
    month_lookup[full_name] = month_num
    month_lookup[abbreviation] = month_num

month_lookup

That produces mappings such as:

"january" -> 1
"jan"     -> 1
"february" -> 2
"feb"      -> 2
...

Then:

month_text = (
    bookings_eda["arrival_date_month"]
    .astype("string")
    .str.strip()
    .str.lower()
)

bookings_eda["arrival_month_num"] = month_text.map(month_lookup)

unmapped_months = (
    bookings_eda.loc[
        bookings_eda["arrival_month_num"].isna(),
        "arrival_date_month"
    ]
    .value_counts(dropna=False)
)

print(
    "Rows with unrecognised month values:",
    bookings_eda["arrival_month_num"].isna().sum()
)

if len(unmapped_months) > 0:
    display(unmapped_months)
Important

If the first inspection reveals other legitimate representations, such as "Sept" rather than "Sep", we should add only the formats actually observed.

For example:

month_lookup["sept"] = 9

But don't add speculative fixes before seeing the data.

That makes your notebook defensible:

I observed the source representations and created deterministic transformations for the formats that actually occurred.

4.4 Validate year and day components

Your earlier numeric conversion check found no failed conversions for arrival_date_year or arrival_date_day_of_month, which is encouraging.

Still, explicitly convert them for the date construction.

arrival_year = pd.to_numeric(
    bookings_eda["arrival_date_year"],
    errors="coerce"
)

arrival_day = pd.to_numeric(
    bookings_eda["arrival_date_day_of_month"],
    errors="coerce"
)

arrival_component_check = pd.DataFrame({
    "Component": [
        "arrival_date_year",
        "arrival_month_num",
        "arrival_date_day_of_month"
    ],
    "Invalid / missing rows": [
        arrival_year.isna().sum(),
        bookings_eda["arrival_month_num"].isna().sum(),
        arrival_day.isna().sum()
    ]
})

arrival_component_check
Why?

A field being numerically parseable does not automatically mean the combination creates a valid calendar date.

For example:

2024 / February / 31

passes numeric conversion but is not a valid date.

So the next check is stronger.

4.5 Construct and validate the arrival date
bookings_eda["arrival_date"] = pd.to_datetime(
    pd.DataFrame({
        "year": arrival_year,
        "month": bookings_eda["arrival_month_num"],
        "day": arrival_day
    }),
    errors="coerce"
)

arrival_date_summary = pd.DataFrame({
    "Metric": [
        "Rows analysed",
        "Invalid arrival dates",
        "Earliest arrival date",
        "Latest arrival date"
    ],
    "Value": [
        len(bookings_eda),
        bookings_eda["arrival_date"].isna().sum(),
        bookings_eda["arrival_date"].min(),
        bookings_eda["arrival_date"].max()
    ]
})

arrival_date_summary

Then, if there are invalid dates:

invalid_arrival_dates = bookings_eda.loc[
    bookings_eda["arrival_date"].isna(),
    [
        "booking_id",
        "arrival_date_year",
        "arrival_date_month",
        "arrival_date_day_of_month"
    ]
]

invalid_arrival_dates.head(20)
What this tells us

This establishes whether we actually have a trustworthy arrival timestamp for each reservation.

It also confirms the real data coverage—for example whether all three stated years are complete or whether the dataset begins/ends partway through a year.

That later matters for monthly/yearly trend analysis.

4.6 Check the supplied week number against the reconstructed date

This is worthwhile because we already know the source field contains malformed values such as "unknown" and "-".

Code cell
source_week = pd.to_numeric(
    bookings_eda["arrival_date_week_number"],
    errors="coerce"
)

derived_week = (
    bookings_eda["arrival_date"]
    .dt.isocalendar()
    .week
    .astype("Float64")
)

week_validation = pd.DataFrame({
    "source_week": source_week,
    "derived_week": derived_week
})

comparable_week = (
    week_validation["source_week"].notna()
    & week_validation["derived_week"].notna()
)

week_mismatch = (
    comparable_week
    & (
        week_validation["source_week"]
        != week_validation["derived_week"]
    )
)

week_validation_summary = pd.DataFrame({
    "Metric": [
        "Rows",
        "Missing / non-numeric source week",
        "Rows available for comparison",
        "Week-number mismatches",
        "Mismatch rate among comparable rows (%)"
    ],
    "Value": [
        len(bookings_eda),
        source_week.isna().sum(),
        comparable_week.sum(),
        week_mismatch.sum(),
        round(
            week_mismatch.sum()
            / comparable_week.sum()
            * 100,
            2
        )
    ]
})

week_validation_summary

If mismatches exist:

bookings_eda.loc[
    week_mismatch,
    [
        "booking_id",
        "arrival_date_year",
        "arrival_date_month",
        "arrival_date_day_of_month",
        "arrival_date_week_number",
        "arrival_date"
    ]
].head(20)
Why this matters

This is not just a data-quality curiosity.

If the reconstructed arrival date is reliable, there is little reason for the future pipeline to struggle with corrupted week values. It can simply derive:

arrival_date.dt.isocalendar().week

from the validated date.

That is a clean example of EDA discovering a preprocessing decision that later belongs in the pipeline.

4.7 Parse and validate reservation_status_date

Now we validate the other half of the cancellation-timing calculation.

bookings_eda["status_date"] = pd.to_datetime(
    bookings_eda["reservation_status_date"]
    .astype("string")
    .str.strip(),
    errors="coerce"
)

status_date_summary = pd.DataFrame({
    "Metric": [
        "Invalid status dates",
        "Earliest status date",
        "Latest status date"
    ],
    "Value": [
        bookings_eda["status_date"].isna().sum(),
        bookings_eda["status_date"].min(),
        bookings_eda["status_date"].max()
    ]
})

status_date_summary

If any fail:

bookings_eda.loc[
    bookings_eda["status_date"].isna(),
    [
        "booking_id",
        "reservation_status",
        "reservation_status_date"
    ]
].head(20)
Why this matters

We are about to calculate:

$$ \text{Cancellation notice} = \text{Arrival date} - \text{Cancellation status date} $$

If either date is wrong, we can manufacture misleading conclusions about "last-minute" cancellations.

4.8 Check reservation-status categories

Before filtering, I would inspect these as well rather than assuming spelling/casing.

bookings_eda["reservation_status"].value_counts(dropna=False)

From your earlier notebook output, we expect the categories:

Canceled
Check-Out
No-Show

but it is still good for this business section to make the outcome states explicit. Your earlier cross-tab showed those three outcome categories and confirmed that both canceled and no-show records map to the positive is_canceled encoding.

4.9 Calculate cancellation notice time — Canceled only

For this first question, keep no-shows out.

cancellations_eda = (
    bookings_eda.loc[
        bookings_eda["reservation_status"].eq("Canceled")
    ]
    .copy()
)

cancellations_eda["days_before_arrival"] = (
    cancellations_eda["arrival_date"]
    - cancellations_eda["status_date"]
).dt.days
Why cancellations only?

Because we are testing:

How much warning does management normally receive when someone cancels?

A no-show is operationally different. By definition, the hotel often only discovers it when the person fails to arrive.

Putting no-shows into this calculation would therefore make the timing distribution look more last-minute almost mechanically.

We'll treat no-shows as their own outcome when we compare the target classes.

4.10 Validate the calculated cancellation timing

Before interpreting averages or drawing charts:

cancellation_timing_quality = pd.DataFrame({
    "Metric": [
        "Canceled reservations",
        "Missing cancellation timing",
        "Cancellation recorded before arrival",
        "Cancellation recorded on arrival date",
        "Cancellation recorded after arrival"
    ],
    "Count": [
        len(cancellations_eda),
        cancellations_eda["days_before_arrival"].isna().sum(),
        (cancellations_eda["days_before_arrival"] > 0).sum(),
        (cancellations_eda["days_before_arrival"] == 0).sum(),
        (cancellations_eda["days_before_arrival"] < 0).sum()
    ]
})

cancellation_timing_quality

If there are negative values:

cancellations_eda.loc[
    cancellations_eda["days_before_arrival"] < 0,
    [
        "booking_id",
        "hotel",
        "arrival_date",
        "reservation_status_date",
        "status_date",
        "days_before_arrival"
    ]
].sort_values("days_before_arrival").head(20)
Do not remove negative values automatically

If they exist, they tell us something.

They could indicate:

data-entry problems;
incorrect arrival-date reconstruction;
delayed administrative updating of cancellation status;
some unusual operational process.

We should understand their magnitude first.

For the actual timing analysis, we can later restrict to logically valid >= 0 observations, but that decision should be documented.

4.11 Distribution of cancellation notice

Once the quality check looks sensible:

valid_cancellations = cancellations_eda.loc[
    cancellations_eda["days_before_arrival"].notna()
    & (cancellations_eda["days_before_arrival"] >= 0)
].copy()

valid_cancellations["days_before_arrival"].describe(
    percentiles=[
        0.10,
        0.25,
        0.50,
        0.75,
        0.90,
        0.95
    ]
)
What I'd pay attention to

Don't focus too much on the mean.

Cancellation timing is very likely right-skewed: some bookings may be cancelled hundreds of days in advance.

The more interpretable statistics will be:

median;
25th percentile;
10th percentile;
75th percentile.

For example, purely hypothetically:

25th percentile = 4 days

would mean one quarter of cancellations provide four days or less notice.

That's a much more useful operational statement than "mean cancellation notice is 38 days."

4.12 Directly test the stakeholder's “last-minute” claim

Now create cumulative thresholds.

timing_thresholds = [0, 1, 2, 3, 7, 14, 30]

timing_summary = []

total_valid_cancellations = len(valid_cancellations)

for threshold in timing_thresholds:
    count = (
        valid_cancellations["days_before_arrival"]
        <= threshold
    ).sum()

    timing_summary.append({
        "Within days of arrival": threshold,
        "Cancellations": count,
        "Percent of cancellations": (
            count / total_valid_cancellations * 100
        )
    })

timing_summary = pd.DataFrame(timing_summary)

timing_summary["Percent of cancellations"] = (
    timing_summary["Percent of cancellations"]
    .round(2)
)

timing_summary

I prefer this table to immediately declaring something like:

"last minute = seven days."

We're testing multiple operational windows:

same day;
within 24 hours;
within 2–3 days;
within a week;
within two weeks;
within one month.

That lets the data tell us how concentrated the problem is.

4.13 Then create the presentation visual

For the notebook presentation, I would convert those individual timing values into mutually exclusive bands.

timing_bins = [
    -0.1,
    0,
    2,
    7,
    14,
    30,
    60,
    np.inf
]

timing_labels = [
    "Same day",
    "1–2 days",
    "3–7 days",
    "8–14 days",
    "15–30 days",
    "31–60 days",
    "61+ days"
]

valid_cancellations["timing_band"] = pd.cut(
    valid_cancellations["days_before_arrival"],
    bins=timing_bins,
    labels=timing_labels
)

timing_distribution = (
    valid_cancellations["timing_band"]
    .value_counts(sort=False)
    .rename_axis("Timing Band")
    .reset_index(name="Cancellations")
)

timing_distribution["Percent"] = (
    timing_distribution["Cancellations"]
    / timing_distribution["Cancellations"].sum()
    * 100
).round(2)

timing_distribution

Then:

fig, ax = plt.subplots(figsize=(10, 5))

ax.bar(
    timing_distribution["Timing Band"].astype(str),
    timing_distribution["Percent"]
)

ax.set_title("Timing of Cancellations Before Scheduled Arrival")
ax.set_xlabel("Time Between Cancellation and Arrival")
ax.set_ylabel("Share of Cancellations (%)")

plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.show()
How we should interpret the result

We should not write the conclusion until you run it.

What we're really testing is this chain of reasoning:

Are many cancellations genuinely close to arrival?

If yes:

Does that leave little time for the hotel to recover the inventory?

If yes:

Would identifying high-risk bookings earlier create a meaningful operational advantage?

That is the business justification for considering cancellation-risk prediction.

It's much stronger than saying:

"Cancellation is 36%, therefore let's build a classifier."

Also notice what we are not claiming

Even if we find 40% of cancellations occur within seven days, the defensible statement is:

40% of observed cancellations were recorded within seven days of scheduled arrival, leaving a relatively short window in which the hotel could attempt to replace the reservation.

We should not say:

40% of rooms were lost.

The dataset doesn't tell us whether a cancelled room was subsequently resold.

That distinction will matter later when we estimate financial exposure too.

What I want you to run now

Run through 4.1–4.12, but don't worry about polishing the markdown or chart yet.

The outputs that matter for our next reasoning step are:

the raw/trimmed arrival_date_month values and counts;
any unrecognised month formats;
invalid constructed arrival dates;
earliest/latest arrival;
source-vs-derived week mismatches;
invalid reservation_status_date values;
counts of cancellations occurring before/on/after arrival;
cancellation timing percentiles;
the 0/1/2/3/7/14/30-day cumulative table.
Once you paste those results, we'll interpret them before proceeding to hotel/time comparisons. In particular, we'll decide whether the stakeholder's phrase “last minute” is strongly, partially, or weakly supported by the actual timing distribution.

[User] I ran the arrival-date and cancellation-timing analysis. I followed the overall approach you suggested, but I made a few changes based on the data and kept the analysis focused.

For the EDA I used bookings_eda = bookings.drop_duplicates().copy() only as a temporary in-memory frame, so the known exact duplicates do not distort the statistics. I am still not creating or saving a separate cleaned dataset; the final ML pipeline will reproduce the required preprocessing directly from the raw SQLite database.

For the target calculation, after excluding the exact duplicate source rows there are 118,196 reservations. Of these, 43,028 (36.40%) are fall-throughs: 41,849 cancellations (35.41%) and 1,179 no-shows (1.00%).

For the arrival date, I found both full and abbreviated month names in the source. I standardised those observed formats and was able to construct all arrival dates successfully with 0 invalid dates. The observed arrival-date coverage is 1 Aug 2023 to 31 Aug 2025.

I did not proceed with the source week-number vs ISO-week comparison. Since we do not know whether the source system uses ISO week numbering, I felt a mismatch could be caused by a different convention rather than necessarily being a data-quality error, and it is not central to the current business question.

I also found multiple formats in reservation_status_date, so instead of applying one generic date conversion I parsed the observed formats deterministically. This resulted in 0 invalid status dates.

The cancellation-timing results are quite important:

41,849 canceled reservations
41,020 were recorded before arrival
829 were recorded on the arrival date
0 were recorded after arrival
median cancellation notice = 56 days
25th percentile = 19 days
10th percentile = 6 days
only 12.04% of cancellations occurred within 7 days of arrival
19.92% occurred within 14 days
33.27% occurred within 30 days
47.76% occurred 61+ days before arrival

So my interpretation is that the data only partially supports the stakeholder's “last-minute” concern. Cancellation/fall-through is clearly a material issue overall, but most cancellations are not happening extremely close to arrival. I therefore don't think we should justify the ML problem mainly as a last-minute room-recovery problem.

I think the cancellation-risk idea can still remain a candidate, but the business framing may need to shift toward earlier visibility of future inventory/revenue risk and proactive planning rather than only last-minute recovery.

For the next EDA steps, I think we should now check:

fall-through rate by hotel and over time to see whether the problem is persistent or concentrated;
cancellations vs no-shows separately to decide whether combining them into one fall_through_flag is defensible;
booking-time characteristics that may contain predictive signal;
a focused pricing/ADR analysis so we can fairly compare the pricing opportunity against cancellation-risk prediction before selecting the final ML problem.

Given the deadline, please keep the next analysis focused on what is necessary to make the final problem-selection decision rather than expanding the EDA unnecessarily.

[AI] Your interpretation is sound, and I would keep it almost exactly as you stated it.

The timing result materially changes the business story: reservation fall-through is large, but “last-minute cancellation” is not the dominant pattern. With a median notice of 56 days and only 12.04% within seven days, the evidence does not support making last-minute room recovery the main justification. The stronger candidate framing is now earlier visibility of future inventory/revenue risk so Revenue & Reservations can plan proactively.

Your decision not to pursue the week-number comparison is also defensible. It would consume time without materially affecting the problem-selection decision, and the assessment rewards purposeful EDA rather than exhaustive diagnostics. The notebook is supposed to explain why steps are taken and what decisions they support.

I would now move directly into the two analyses that can most quickly determine whether fall-through prediction remains a strong ML candidate.

5. Distribution of Reservation Fall-Through

Start with a short markdown transition:

## 5. Distribution of Reservation Fall-Through

Reservation fall-through affects 36.40% of the deduplicated reservation records, but cancellation-timing analysis shows that most cancellations are not concentrated immediately before arrival.

The next analysis therefore examines whether fall-through is:

1. consistently present across both hotels and over time; and
2. sufficiently similar between cancellations and no-shows to justify treating them as a common business outcome.

These analyses help determine whether reservation fall-through represents a persistent and predictable operational problem rather than an issue concentrated in a particular property or period.
5.1 Fall-through by hotel

Use the already validated status rather than recreating complicated target logic.

bookings_eda["fall_through_flag"] = (
    bookings_eda["reservation_status"]
    .isin(["Canceled", "No-Show"])
    .astype(int)
)

hotel_fallthrough = (
    bookings_eda
    .groupby("hotel")
    .agg(
        reservations=("booking_id", "size"),
        fall_throughs=("fall_through_flag", "sum"),
        fall_through_rate=("fall_through_flag", "mean")
    )
    .reset_index()
)

hotel_fallthrough["fall_through_rate_pct"] = (
    hotel_fallthrough["fall_through_rate"] * 100
).round(2)

hotel_fallthrough[
    [
        "hotel",
        "reservations",
        "fall_throughs",
        "fall_through_rate_pct"
    ]
]

Then one simple plot:

fig, ax = plt.subplots(figsize=(7, 4))

ax.bar(
    hotel_fallthrough["hotel"],
    hotel_fallthrough["fall_through_rate_pct"]
)

ax.set_title("Reservation Fall-Through Rate by Hotel")
ax.set_xlabel("Hotel")
ax.set_ylabel("Fall-Through Rate (%)")

plt.tight_layout()
plt.show()
What this tells us

We care about the rate, not just the number of cancellations.

If one hotel has 30,000 cancellations only because it handles many more bookings, that doesn't necessarily mean it has a bigger risk problem.

The useful questions are:

Is fall-through materially high at both hotels?
Is one property clearly more exposed?
Would one common model make sense, or might hotel-specific behaviour be important?
What decision it supports

If both hotels have substantial fall-through rates, that strengthens the case that this is a group-wide operational problem.

If almost all risk is concentrated in one hotel, the eventual solution might need more property-specific framing.

5.2 Fall-through over time

There is an important issue here:

Your observed data covers only:

Aug–Dec 2023;
full 2024;
Jan–Aug 2025.

So do not compare annual cancellation counts as though all three years contain twelve months.

Instead, create an arrival month:

bookings_eda["arrival_year_month"] = (
    bookings_eda["arrival_date"]
    .dt.to_period("M")
    .dt.to_timestamp()
)

Then calculate the monthly rate:

monthly_fallthrough = (
    bookings_eda
    .groupby("arrival_year_month")
    .agg(
        reservations=("booking_id", "size"),
        fall_throughs=("fall_through_flag", "sum"),
        fall_through_rate=("fall_through_flag", "mean")
    )
    .reset_index()
)

monthly_fallthrough["fall_through_rate_pct"] = (
    monthly_fallthrough["fall_through_rate"] * 100
)

Plot:

fig, ax = plt.subplots(figsize=(12, 5))

ax.plot(
    monthly_fallthrough["arrival_year_month"],
    monthly_fallthrough["fall_through_rate_pct"],
    marker="o"
)

ax.set_title("Monthly Reservation Fall-Through Rate")
ax.set_xlabel("Arrival Month")
ax.set_ylabel("Fall-Through Rate (%)")

plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

I would also show the underlying volumes because a rate from a low-volume month can look dramatic:

monthly_fallthrough[
    [
        "arrival_year_month",
        "reservations",
        "fall_throughs",
        "fall_through_rate_pct"
    ]
].round(2)
Why monthly rather than yearly?

Because it answers the real question:

Is this issue repeatedly occurring through the observed period?

A roughly persistent 30–40% rate is much stronger justification for an ML intervention than one isolated spike.

It will also tell us whether there may be:

seasonality;
structural changes;
temporal drift.

That later matters for train/test splitting. If behaviour changes over time, a random split becomes less attractive than a temporal holdout.

Don't make that decision yet—we're just collecting evidence.

5.3 Hotel × time

I would do one additional check, but don't build a huge dashboard.

hotel_monthly = (
    bookings_eda
    .groupby(["arrival_year_month", "hotel"])
    .agg(
        reservations=("booking_id", "size"),
        fall_through_rate=("fall_through_flag", "mean")
    )
    .reset_index()
)

hotel_monthly["fall_through_rate_pct"] = (
    hotel_monthly["fall_through_rate"] * 100
)
fig, ax = plt.subplots(figsize=(12, 5))

for hotel, group in hotel_monthly.groupby("hotel"):
    ax.plot(
        group["arrival_year_month"],
        group["fall_through_rate_pct"],
        marker="o",
        label=hotel
    )

ax.set_title("Monthly Fall-Through Rate by Hotel")
ax.set_xlabel("Arrival Month")
ax.set_ylabel("Fall-Through Rate (%)")
ax.legend()

plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
Why keep this?

Because an overall monthly trend can hide opposing hotel patterns.

But this is enough. I would not start creating weekday, quarter, season, and week-level versions unless something unusual appears here.

5.4 Cancellation versus no-show prevalence

Now separate the outcomes explicitly.

outcome_summary = (
    bookings_eda["reservation_status"]
    .value_counts()
    .rename_axis("reservation_status")
    .reset_index(name="reservations")
)

outcome_summary["percent"] = (
    outcome_summary["reservations"]
    / len(bookings_eda)
    * 100
).round(2)

outcome_summary

Your known deduplicated result should show approximately:

Check-Out: 63.60%
Canceled: 35.41%
No-Show: 1.00%

The important fact isn't merely that no-show is smaller. It is tiny relative to cancellation.

No-shows represent only about:

$$ \frac{1,179}{43,028}\approx2.74\% $$

of the positive fall-through class.

That immediately tells us something about target design:

A combined fall-through model will overwhelmingly learn cancellation behaviour unless no-shows have very distinctive features.

So now we need a focused comparison.

5.5 Cancellation vs no-show by hotel
outcome_by_hotel = pd.crosstab(
    bookings_eda["hotel"],
    bookings_eda["reservation_status"],
    normalize="index"
) * 100

outcome_by_hotel.round(2)

You can optionally keep just:

outcome_by_hotel[
    ["Canceled", "No-Show", "Check-Out"]
].round(2)
Question

Do both hotels show:

cancellation as the dominant fall-through mechanism;
no-show as a small residual problem?

Or is no-show disproportionately concentrated in one property?

5.6 Cancellation vs no-show over time

Don't overdo this.

Calculate monthly rates separately:

monthly_outcomes = (
    bookings_eda
    .groupby(
        ["arrival_year_month", "reservation_status"]
    )
    .size()
    .unstack(fill_value=0)
)

monthly_outcomes["Total"] = monthly_outcomes.sum(axis=1)

monthly_outcomes["Cancellation Rate (%)"] = (
    monthly_outcomes["Canceled"]
    / monthly_outcomes["Total"]
    * 100
)

monthly_outcomes["No-Show Rate (%)"] = (
    monthly_outcomes["No-Show"]
    / monthly_outcomes["Total"]
    * 100
)

monthly_outcomes[
    ["Cancellation Rate (%)", "No-Show Rate (%)"]
].round(2)

A plot is optional here. With the deadline, inspect the table first.

What we're looking for

Not whether the percentages are identical.

We're asking:

Does no-show behave like a stable small extension of the broader fall-through problem, or does it appear to be a genuinely separate phenomenon?

5.7 Compare a small set of booking characteristics

For deciding whether cancellations and no-shows can reasonably share one target, we do not need to compare every column.

Use a focused set of features that are:

available before the outcome;
business-interpretable;
potentially relevant to reservation commitment.

I would use:

lead_time
adr
total nights
market_segment
distribution_channel
deposit_type
customer_type
is_repeated_guest
previous_cancellations
total_of_special_requests

But first, for this outcome-comparison section, I'd use only four or five.

Create total nights
bookings_eda["total_nights"] = (
    pd.to_numeric(
        bookings_eda["stays_in_weekend_nights"],
        errors="coerce"
    )
    +
    pd.to_numeric(
        bookings_eda["stays_in_week_nights"],
        errors="coerce"
    )
)

For lead_time, use the temporary deterministic repair you already identified rather than blindly coercing "14 days" to missing.

For example:

bookings_eda["lead_time_num"] = pd.to_numeric(
    bookings_eda["lead_time"]
    .astype("string")
    .str.strip()
    .str.replace(r"\s*days?$", "", regex=True),
    errors="coerce"
)

Then:

outcome_numeric_profile = (
    bookings_eda
    .groupby("reservation_status")
    .agg(
        reservations=("booking_id", "size"),
        median_lead_time=("lead_time_num", "median"),
        median_total_nights=("total_nights", "median"),
        mean_previous_cancellations=(
            "previous_cancellations",
            lambda x: pd.to_numeric(
                x,
                errors="coerce"
            ).mean()
        ),
        mean_special_requests=(
            "total_of_special_requests",
            lambda x: pd.to_numeric(
                x,
                errors="coerce"
            ).mean()
        )
    )
)

outcome_numeric_profile.round(2)

This is enough for an initial cancellation/no-show comparison.

How I would decide whether to combine them

Don't require cancellation and no-show profiles to be identical.

The relevant question is business + modelling coherence.

A combined fall_through_flag is defensible if:

both outcomes leave the reserved stay unfulfilled;
the operational response is broadly similar;
no-show is too rare to support a robust standalone modelling task;
their observable pre-arrival characteristics are not so radically different that combining them becomes misleading.

A separate no-show target becomes more attractive only if:

the behaviours are clearly distinct;
the business would act differently;
and 1,179 observations are sufficient for credible modelling.

Given the class size, I would currently regard a standalone no-show model as unlikely to be the best use of the assessment, unless the EDA reveals a very strong distinctive pattern.

One nuance about the combined target

If we eventually train:

fall_through_flag
0 = Check-Out
1 = Canceled or No-Show

our evaluation should probably include a small diagnostic showing model performance separately for:

cancellations;
no-shows.

Why?

Because a model could report good overall fall-through recall by detecting cancellations while missing nearly every no-show.

Since no-show is only ~2.7% of the positive class, aggregate metrics could hide that.

We don't need to solve that now, but it's worth remembering.

Then proceed to predictive-signal EDA

Once Sections 5.1–5.7 are done, I would not launch into thirty univariate plots.

We should rank only a compact set of leakage-safe booking-time variables.

Your assessment documentation describes several variables that are naturally available as part of the reservation, such as lead time, market segment, deposit type, previous booking history and special requests.

I would group them conceptually:

Feature group	Examples	Business question
Booking horizon	lead_time	Are long-ahead bookings less committed?
Customer history	repeated guest, previous cancellations	Does prior behaviour predict future reliability?
Booking commitment	deposit type, special requests	Are there signals of guest commitment?
Channel	market segment, distribution channel	Are some acquisition channels riskier?
Stay characteristics	nights, adults/children, room type	Do certain reservation structures fall through more often?
Price	ADR	Does price correlate with fall-through?

That is enough to establish whether usable predictive signal appears to exist.

And then give pricing a fair but focused test

Your instinct to preserve pricing as a competing problem is right.

The original brief explicitly says management believes rooms may be both under- and overpriced and currently sets rates largely through intuition.

But we don't need a huge pricing EDA.

I would test only:

ADR distribution and malformed/outlier values;
ADR by hotel;
ADR over month/time;
ADR by room type;
ADR versus fall-through;
reviews/rating versus ADR for completed stays only, with the selection limitation stated.

Then ask:

Does this dataset actually provide a defensible supervised target for “better pricing”?

That is the key hurdle.

The dataset gives historical ADR but not an explicit optimal price, demand curve, competitor price, capacity/utilisation, or evidence that a different historical price would have produced more revenue.

So cancellation prediction currently has a structural advantage as an ML problem: it has a clearly observed outcome label.

But we should let the focused pricing analysis establish that rather than simply assuming it.

Recommended sequence from here

With the deadline, I would now do only:

Section 5

hotel fall-through rate;
monthly fall-through rate;
monthly rate by hotel;
cancellation vs no-show prevalence;
cancellation vs no-show by hotel/time;
small numerical profile comparison.

Then send me those outputs.

From those results we'll make one explicit target-definition decision before moving to booking-time predictive signal. After that, we can do a compact signal analysis and a compact pricing analysis and finally write a side-by-side problem-selection table.

That should give you enough evidence to choose the ML problem without turning the EDA into an endless exercise.


[User]I went ahead with the focused analyses we discussed and kept them within Section 4 rather than creating another large EDA section, since I want to avoid unnecessary scope expansion before modelling.

The results so far are:

Fall-through remains 36.40% after excluding the known exact duplicate source records.
Airport Hotel has a 27.59% fall-through rate, while City Hotel is substantially higher at 40.78%.
Monthly fall-through remains material across the observed period rather than being driven by one isolated month, so the issue appears persistent although the magnitude varies over property and time.

I also compared cancellations and no-shows. Cancellations make up 97.26% of all fall-throughs, while no-shows are only 2.74%. Their hotel distribution is very similar, although there are some differences across booking channels/segments. This suggests they are not behaviourally identical, but because no-shows are such a small share of the positive class and both outcomes represent a confirmed reservation not becoming a completed stay, I think a combined fall_through_flag may still be the more practical candidate target. I have not fully locked that decision yet.

Before interpreting the categorical variables, I also noticed that the raw data contains inconsistent labels such as variations in casing, spacing and spelling for the same market segment, deposit type, distribution channel and customer type. I therefore standardised those categories temporarily in memory for EDA rather than treating the variants as separate business categories. The final pipeline will need to reproduce this preprocessing from the raw SQLite source.

The booking-time signal analysis produced some strong differences:

Non Refund deposit: 99.35% fall-through
No Deposit: 27.71%
Groups market segment: 59.87%
Online TA: 36.02%
Offline TA/TO: 34.63%
TA/TO distribution channel: 40.33%
Direct distribution channel: 17.26%
Transient customer type: 40.29%

Lead time also shows a strong gradient. I found 300 logically invalid negative lead-time records, so I documented them and excluded them only from the lead-time relationship analysis rather than silently treating them as valid. For the valid records, fall-through rises from 9.53% for bookings made 0–7 days ahead to 66.87% for bookings made more than 365 days ahead.

Taken together, I think this gives reasonable evidence that information available before the eventual outcome contains predictive signal, although this still does not prove model performance.

I also completed a focused ADR/pricing feasibility check. All ADR values could be recovered after handling the observed formatting inconsistencies. City Hotel has a higher historical median ADR (230.00) than Airport Hotel (172.50), and median ADR also varies substantially by arrival month.

However, I don't think historical ADR alone gives us a defensible supervised target for “optimal pricing”. We do not have an observed optimal price, competitor rates, rejected bookings, unconstrained demand, real-time inventory or experimentally observed price elasticity.

So at this point my current view is:

pricing is clearly a relevant business concern, but the available dataset does not provide a strong supervised-learning target for genuine price optimisation;
reservation fall-through has a clearly observed outcome, affects a substantial share of reservations, persists across the observed period, and shows meaningful relationships with pre-outcome booking characteristics;
the original “last-minute recovery” framing should still be softened because the earlier timing analysis showed that most cancellations occur well before arrival.

I think we are now close to selecting the ML problem. Can you help me evaluate this evidence and formulate a concise final problem statement and target definition for Section 5 before we start the ML pipeline? Please also challenge the fall-through choice if you think the evidence still supports a better alternative.

[AI] Yes. Based on the evidence you now have, I think reservation fall-through prediction is the strongest and most defensible ML problem in this dataset.

I would not switch to pricing. The business concern is real, but the data does not contain a credible supervised target for optimal price. Historical ADR is an observed decision, not an observed optimum. The assessment asks you to refine the vague business request into a well-defined problem and then build an ML pipeline that addresses it, so choosing the problem that the data can actually support is exactly the point.

The one alternative I would seriously consider is cancellation-only prediction rather than combined fall-through. But I still prefer the combined target, with one caveat.

My assessment of the target choice

A combined fall_through_flag is defensible because cancellation and no-show share the same operational consequence you care about:

a reservation expected to occupy inventory does not become a completed stay.

No-shows are also only 2.74% of fall-through cases, so creating a separate no-show modelling task would add complexity while being supported by only 1,179 examples. And your EDA shows their hotel distribution is broadly similar even though some channel differences exist.

The caveat is that the resulting model will fundamentally be a cancellation-dominated model. You should acknowledge that rather than implying it models both outcomes equally well.

So later, in model evaluation, I would add one small diagnostic:

performance on cancellations;
performance on no-shows separately.

That will tell you whether the combined model is completely failing on the minority subtype.

Section 5 — Problem Selection

I would make Section 5 fairly short. You now have enough evidence; don't bury the decision beneath more EDA.

Suggested markdown
## 5. Problem Selection

The business raised two main opportunities for machine learning: reducing the impact of reservation fall-through and improving room pricing.

The EDA indicates that reservation fall-through is the stronger problem for the available dataset.

After excluding known exact duplicate source records, 36.40% of reservations did not result in a completed stay. The issue is present across both properties and throughout the observed period, although the City Hotel has a higher fall-through rate than the Airport Hotel.

The cancellation-timing analysis only partially supports the stakeholder's concern that cancellations are predominantly last-minute. The median cancellation was recorded 56 days before arrival and only 12.04% occurred within seven days. Therefore, the opportunity is better framed as providing earlier visibility of future reservation risk rather than primarily supporting last-minute room recovery.

Importantly, several characteristics available before the final reservation outcome show substantial differences in fall-through rate. These include lead time, deposit type, market segment, distribution channel and customer type. This provides evidence that the available booking information may contain useful predictive signal, although actual predictive performance must be established through model evaluation.

Pricing remains an important business concern. Historical ADR varies substantially across hotels and time periods, but the available dataset does not contain an observed optimal price or sufficient information to estimate a reliable pricing response function. In particular, competitor prices, rejected demand, real-time inventory, unconstrained demand and experimentally observed price elasticity are unavailable. Predicting historical ADR would therefore risk reproducing past pricing decisions rather than identifying better prices.

Based on these findings, reservation fall-through prediction is selected as the machine learning problem for the assessment.

That gives a clean chain:

business problem → EDA evidence → alternative considered → why rejected → selected ML problem.

That coherence will later help the README, because the assessment explicitly expects pipeline choices to link back to EDA findings.

5.1 Final problem statement

I recommend something like this:

Develop a supervised classification model that estimates, once a reservation is confirmed and before its final outcome is known, the probability that the reservation will fall through rather than result in a completed stay. The predicted risk can provide Travelers' Inn's Revenue & Reservations team with earlier visibility of future inventory and revenue exposure, allowing high-risk reservations to be identified for proactive operational planning.

I like this formulation because it avoids overclaiming.

It does not say:

the model will prevent cancellations;
the model will automatically overbook rooms;
the model will recover every cancelled room;
the model will optimise room prices.

It says the model provides risk visibility, which is exactly what the data can support.

One wording change I strongly recommend

Use:

“earlier visibility of future inventory and revenue exposure”

rather than:

“predict lost revenue.”

You do not know whether cancelled inventory was eventually resold, and you don't know the financial treatment of deposits or cancellation charges.

So "exposure" is safer and more accurate than "loss".

5.2 Target definition

I would put this explicitly in the notebook.

### Target definition

The modelling target is a binary `fall_through_flag` defined from the final reservation outcome:

- `0` — `Check-Out`: the reservation resulted in a completed stay.
- `1` — `Canceled` or `No-Show`: the reservation did not result in a completed stay.

Cancellations account for 97.26% of the positive class and no-shows account for 2.74%. Although the two outcomes are not assumed to be behaviourally identical, they are combined because they represent the same high-level operational outcome — reserved inventory not becoming a completed stay — and the number of no-shows is relatively small for a standalone modelling task.

Model performance on cancellations and no-shows should nevertheless be reviewed separately to determine whether aggregate fall-through performance masks poor performance on the smaller no-show subgroup.

That is much stronger than simply saying:

target = is_canceled

because you explain the business meaning and acknowledge the composition of the positive class.

5.3 Prediction point

This deserves its own short subsection because it controls leakage.

I suggest:

### Prediction point

The intended prediction point is when a reservation has been confirmed, before its eventual cancellation, no-show or completed stay is known.

Only information that would reasonably be available by this point should be eligible as predictive features. Variables that describe events occurring after this point must be excluded even if they are strongly associated with the target.

Why confirmation rather than simply "at booking"?

Because it gives you a clean operational moment and potentially makes days_in_waiting_list logically available if you decide to use it.

But be strict: a variable being present in the booking table does not automatically mean it existed at the prediction point.

5.4 Leakage exclusions

You already identified several. I would document them now so the pipeline doesn't drift away from your EDA reasoning.

Field	Decision	Reason
reservation_status	Exclude	Directly defines eventual outcome
reservation_status_date	Exclude	Recorded as part of eventual outcome
assigned_room_type	Exclude	Actual room assigned at check-in; unavailable pre-arrival
booking_changes	Exclude from confirmation-time model	Final count includes amendments between creation and check-in/cancellation
review rating	Exclude	Post-stay information
review comments	Exclude	Post-stay information
review existence	Exclude	Review availability itself depends on reaching/posting after the stay
booking_id	Exclude as predictor	Identifier rather than generalisable business signal
client_email	Exclude as raw predictor	Customer identifier/high-cardinality personally identifying field rather than a suitable direct feature

The source specifically states that assigned_room_type is what was actually assigned at check-in, while booking_changes covers amendments through check-in/cancellation. Reviews are explicitly post-stay information.

That gives you a very defensible leakage boundary.

5.5 Features that appear potentially usable

Don't call these "selected features" yet.

Call them candidate features because modelling will determine whether they actually help.

Your EDA has already produced particularly strong evidence around:

lead_time
deposit_type
market_segment
distribution_channel
customer_type

And other plausible pre-outcome fields include:

hotel;
arrival timing;
stay duration;
party composition;
reserved room type;
repeated-guest flag;
previous cancellations;
previous non-cancelled bookings;
agent/company presence;
special requests;
car parking requests;
promo usage;
ADR.

The interesting thing about your EDA is that you've already established that this isn't merely a target with a high prevalence. There appears to be heterogeneity associated with information available before the outcome.

For example:

No Deposit: 27.71%
Non Refund: 99.35%
Direct channel: 17.26%
TA/TO: 40.33%
0–7 day lead time: 9.53%

365 day lead time: 66.87%

Those are large separations.

As you correctly said, they do not prove good model performance. But they do establish enough signal to justify proceeding to modelling.

One result I would treat very carefully: Non Refund = 99.35%

Don't interpret that yet as:

Non-refundable deposits cause cancellation.

That would be a major leap.

There could be:

segment confounding;
historical policy effects;
interaction with long lead times;
channel-specific practices;
small or unusual subgroup composition.

For ML it may be highly predictive. For causal business recommendations it tells us almost nothing by itself.

You can phrase it as:

“Deposit type exhibits a particularly strong association with historical fall-through.”

That's enough.

One more important modelling consequence from your EDA

The temporal results mean I would now strongly favour a time-based validation design rather than only a random train/test split.

You have roughly:

Aug 2023 → Aug 2025

and you've already observed variation over time.

The real deployment question is:

Can a model trained on historical reservations predict future reservations?

A temporal holdout simulates that much better than randomly scattering reservations from every month across train and test sets.

We don't need to design the split in detail yet, but this is precisely the type of pipeline decision that should flow from Section 4 into the modelling phase.

Is there a better ML problem hidden in this dataset?

From what you've shown, I don't see one that is more defensible.

Pricing optimisation

High business value, weak target/data support.

Predict ADR

Technically easy, but weak business validity because you'd be learning the hotel's historical pricing decisions.

Review sentiment / rating prediction

Possible, but only ~17.5k reviewed completed stays and much less directly connected to the stated profitability problem. It would also ignore most of the booking dataset.

No-show prediction

Relevant, but only 1,179 positive records and only 1% of reservations.

Cancellation-only prediction

Perfectly defensible and arguably slightly cleaner statistically, but it discards a genuine business failure state that management explicitly mentioned. Given how small no-show is, combining it into fall-through adds relatively little heterogeneity while preserving the full operational definition.

Fall-through prediction

Has:

a clear label;
substantial prevalence;
business relevance;
persistence across hotels/time;
pre-outcome signal;
an obvious user of the prediction;
an actionable prediction point;
manageable class balance;
a defensible path to evaluation.

So this is the choice I would make.

The one-sentence version

If you want a crisp sentence to anchor Section 5, README, Decision Log reasoning, and later pipeline documentation, I would use:

The selected machine-learning problem is to predict the probability that a confirmed reservation will fall through through cancellation or no-show, using only information available before the outcome, so that Travelers' Inn can identify future inventory and revenue exposure earlier and support proactive reservation planning.

That's coherent with the EDA without pretending the original "last-minute recovery" hypothesis survived unchanged.

And that evolution in the problem framing is actually a strength: you started with the stakeholder's claim, tested it, found that the timing evidence only partially supported it, and changed the business justification based on the data rather than forcing the data to fit the original idea. That is exactly the reasoning trail your Decision Log and AI history should show.

[User] ’ve finished the EDA and implemented src/data.py and src/features.py. The pipeline now reproduces the EDA counts exactly: 118,549 raw rows, 353 exact duplicates removed, 118,196 modelling rows, with 36.40% fall-through.

I’m thinking of using a chronological split: Aug 2023–Dec 2024 train, Jan–Apr 2025 validation, May–Aug 2025 test. Does this make sense for the deployment scenario, and what should I be careful about before implementing it?

[AI] Yes — Aug 2023–Dec 2024 train / Jan–Apr 2025 validation / May–Aug 2025 test is a sensible primary split for your deployment scenario, and I prefer it to a random split.

It tests the question you actually care about:

Can a model learned from earlier reservations generalise to reservations arriving in a later period?

Your proposed split also gives you a decent training window and two untouched future blocks for model selection and final evaluation.

There are a few things I would check before coding it.

1. Split on arrival_date, but state the limitation

For this dataset, I would use arrival date as the temporal split key.

Conceptually, the model is scored when a reservation is confirmed, so splitting by booking/confirmation date might sound even closer to deployment. Since:

$$ booking\_date = arrival\_date - lead\_time $$

you could theoretically derive it.

I would not make derived booking date your primary split, though. The dataset is bounded by arrival dates through 31 Aug 2025. Near the end of the dataset, bookings created in 2025 with long lead times and arrivals after Aug 2025 are necessarily absent. Splitting by derived booking date could therefore make the latest period systematically biased toward short-lead bookings.

Arrival-date splitting avoids that particular end-of-window truncation problem and is straightforward to defend.

You can say:

“The temporal holdout is defined using scheduled arrival date because the source dataset is observed over an arrival-date window. This provides a clean future-period evaluation while avoiding additional truncation effects from deriving booking dates near the end of the dataset.”

2. Check class prevalence in each split before modelling

Run something like:

split_summary = (
    df.groupby("split")
      .agg(
          rows=("fall_through_flag", "size"),
          fall_throughs=("fall_through_flag", "sum"),
          fall_through_rate=("fall_through_flag", "mean"),
      )
)

split_summary["fall_through_rate"] *= 100
split_summary

You don't need identical rates.

In fact, some movement is useful because that is realistic temporal drift.

But you want to know if you suddenly get something extreme like:

train 34%
validation 52%
test 21%

If that happens, investigate before attributing model performance purely to the algorithm.

Also break it out by hotel once:

pd.crosstab(
    [df["split"], df["hotel"]],
    df["fall_through_flag"],
    normalize="index"
) * 100

Since City and Airport already have quite different base rates, a shift in hotel mix could move your overall metric.

3. Keep the test period completely untouched

This is the big one.

Use:

Train

fit preprocessing;
fit models.

Validation

compare models;
tune hyperparameters;
choose classification threshold;
possibly choose feature variants.

Test

evaluate the single final selected approach once.

Do not keep checking May–Aug 2025 after every modelling decision. If you do, it quietly becomes another validation set.

4. Any learned preprocessing must be fitted on train only

Your deterministic cleaning can happen before the split:

exact duplicate removal;
category spelling/case normalization;
parsing dates;
repairing known numeric formats;
creating total nights;
deriving month, etc.

Those rules don't learn anything from future rows.

But things that learn from the distribution must be trained only using the training set:

median imputation;
scaling;
one-hot category vocabulary if relevant;
target encoding;
frequency encoding;
feature selection based on target association;
resampling;
class weights based on observed counts, if you explicitly calculate them.

Ideally this is handled inside a scikit-learn Pipeline / ColumnTransformer.

For one-hot encoding, make sure unseen future categories don't crash the pipeline:

OneHotEncoder(handle_unknown="ignore")

That matters in a chronological evaluation because new agents, promo codes, countries, etc. may appear later.

5. Be especially careful about engineered historical features

This is where temporal leakage often sneaks in.

Suppose later you create something like:

historical cancellation rate by agent
historical fall-through rate by country
mean ADR by segment

If those values are calculated once using all 118,196 rows, future target information leaks backward.

Such features must be derived only from information available prior to each observation—or, much more simply for this assessment, don't build target-based historical aggregates unless you genuinely need them.

You already have plenty of useful source features.

6. Preserve your prediction-point leakage rules

Your temporal split does not fix feature leakage.

I would still exclude the fields we identified as unavailable at confirmation time, particularly:

reservation_status
reservation_status_date
assigned_room_type
final booking_changes
review data
identifiers such as booking_id and raw client_email

A model can have a perfect chronological split and still be invalid if its features tell it the future.

7. Look for category drift across the three periods

Before fitting models, a compact diagnostic is useful:

categorical_cols = [
    "hotel",
    "market_segment",
    "distribution_channel",
    "deposit_type",
    "customer_type",
]

for col in categorical_cols:
    train_values = set(train[col].dropna())
    val_values = set(val[col].dropna())
    test_values = set(test[col].dropna())

    print(f"\n{col}")
    print("Validation unseen:", val_values - train_values)
    print("Test unseen:", test_values - train_values)

You don't need to eliminate unseen categories. Seeing them is actually realistic.

You just need your preprocessing to handle them.

8. Your four-month validation and test windows are reasonable, with one caveat

Your periods are:

Split	Period	Approx. duration
Train	Aug 2023–Dec 2024	17 months
Validation	Jan–Apr 2025	4 months
Test	May–Aug 2025	4 months

I like this.

The caveat is that validation and test represent different parts of the year. So performance differences may partly reflect seasonality rather than model instability.

That's not a flaw—it is actually realistic—but acknowledge it when interpreting results.

For example, if validation ROC-AUC is 0.86 and test is 0.81, don't immediately conclude something went wrong. Check whether:

class rate changed;
hotel mix changed;
market/channel composition changed;
ADR/lead-time distributions changed.
9. You could add rolling validation later, but don't make the pipeline unnecessarily complicated

If you had unlimited time, a stronger development scheme would be rolling temporal validation within the training period.

For example:

Train → Aug 2023–Jun 2024
Validate → Jul–Sep 2024

Train → Aug 2023–Sep 2024
Validate → Oct–Dec 2024

Then retain Jan–Apr 2025 for final development validation and May–Aug for test.

But given your deadline, I would not start with this.

Your fixed chronological split is already much better aligned with deployment than a standard random 80/20 split. Get the end-to-end pipeline working cleanly first.

One thing I'd decide before implementing models

Because your positive class is 36.4%, this isn't an extreme imbalance problem.

So don't reflexively use SMOTE or aggressive resampling.

Start with the natural distribution.

The business question is probability/risk estimation, so preserving realistic prevalence is useful, especially if you eventually want predicted probabilities to mean something operationally.

We can consider class weighting later if the chosen metric and error trade-off justify it.

I would implement your proposed split

Something along these lines is clean:

train_mask = (
    (df["arrival_date"] >= "2023-08-01")
    & (df["arrival_date"] <= "2024-12-31")
)

val_mask = (
    (df["arrival_date"] >= "2025-01-01")
    & (df["arrival_date"] <= "2025-04-30")
)

test_mask = (
    (df["arrival_date"] >= "2025-05-01")
    & (df["arrival_date"] <= "2025-08-31")
)

train_df = df.loc[train_mask].copy()
val_df = df.loc[val_mask].copy()
test_df = df.loc[test_mask].copy()

Then assert that you didn't accidentally lose or overlap anything:

assert len(train_df) + len(val_df) + len(test_df) == len(df)

assert train_df["arrival_date"].max() < val_df["arrival_date"].min()
assert val_df["arrival_date"].max() < test_df["arrival_date"].min()

assert set(train_df.index).isdisjoint(val_df.index)
assert set(train_df.index).isdisjoint(test_df.index)
assert set(val_df.index).isdisjoint(test_df.index)

And print a compact split summary every pipeline run.

The reasoning I'd eventually put in the README

A chronological train/validation/test split was used instead of a random split to better approximate deployment, where the model is trained on historical reservations and applied to future reservation periods. Reservations arriving from Aug 2023–Dec 2024 are used for training, Jan–Apr 2025 for model selection and threshold tuning, and May–Aug 2025 is retained as an untouched final test set.

That is a very defensible design.

The next decision I'd make is evaluation metrics before model choice. For this problem, accuracy alone would be a poor primary metric; we should decide what false positives versus false negatives mean operationally and then choose ROC-AUC / PR-AUC / recall / precision and thresholding accordingly before you start comparing algorithms.

[User] I implemented the chronological split successfully. The results are:

Train: 77,577 rows, Aug 2023–Dec 2024, 35.18% fall-through
Validation: 18,442 rows, Jan–Apr 2025, 36.53%
Test: 22,177 rows, May–Aug 2025, 40.57%

The test period has a somewhat higher base fall-through rate, so there appears to be some temporal shift.

Before I train the Dummy, Logistic Regression and Random Forest models, what evaluation metrics would you choose for model selection and why? I want the eventual metric choice to make business sense rather than defaulting to accuracy.

[AI] Yes. Given your business framing, I would not use accuracy as the primary metric.

Your model is meant to rank confirmed reservations by the probability of fall-through so the hotel gets earlier visibility of inventory/revenue exposure. That makes positive-class detection and probability ranking more important than simply maximizing the percentage of correct labels.

Recommended metric hierarchy
Role	Metric	Why
Primary model-selection metric	PR-AUC / Average Precision	Directly evaluates how well the model identifies fall-through reservations while controlling false alarms
Secondary discrimination metric	ROC-AUC	Measures overall ranking ability across thresholds; useful for comparison but less focused on the positive class
Threshold evaluation	Precision + Recall	Shows the actual operational trade-off once you decide which bookings to flag
Summary threshold metric	F1 or preferably F2 if missed fall-throughs are considered more costly	Useful only after you have an operating threshold
Probability quality	Brier score / calibration	Important because your proposed output is a risk probability, not just 0/1
Business-facing diagnostic	Recall among top-risk X% / Lift	Answers “if staff focus on the highest-risk bookings, how many future fall-throughs do we capture?”
1. Make PR-AUC / Average Precision your primary validation metric

I would use average_precision_score in scikit-learn.

Why?

Your positive class is:

fall_through_flag = 1

and that's exactly the outcome management is trying to identify early.

Precision asks:

Of the reservations we flag as risky, how many actually fall through?

Recall asks:

Of all reservations that eventually fall through, how many did we identify?

PR-AUC evaluates that trade-off across thresholds.

Your class imbalance isn't extreme at ~36%, but it is enough that PR-AUC remains more directly aligned with the problem than accuracy.

There is also a useful baseline:

A non-informative model's Average Precision is approximately the positive-class prevalence.

So on your validation set, the rough baseline is 36.53%.

If you get:

Dummy       AP ≈ 0.365
Logistic    AP = 0.70
RF          AP = 0.78

that is intuitively meaningful: both trained models rank fall-through bookings far better than simply reflecting prevalence.

2. Keep ROC-AUC as an important secondary metric

I would still report ROC-AUC.

It answers:

How often does the model assign a higher risk score to a randomly selected fall-through reservation than to a randomly selected completed stay?

That is useful because your intended application is fundamentally a risk-ranking problem.

But I wouldn't select the winner purely on ROC-AUC.

A model can achieve a respectable ROC-AUC while still producing a precision/recall trade-off that isn't particularly useful for the bookings you actually want to flag.

So:

Primary: PR-AUC
Secondary: ROC-AUC

is a defensible combination.

3. Don't select the classification threshold using 0.5 automatically

This is arguably more important than whether you choose F1 versus F2.

A predicted probability of 0.5 is not inherently the correct business cutoff.

Suppose:

Threshold	Precision	Recall
0.30	55%	88%
0.45	67%	74%
0.60	80%	49%

Which is best?

There is no mathematical answer without knowing what management does with a flagged reservation.

A false negative means:

A reservation eventually falls through, but the model didn't identify it as high risk.

A false positive means:

The model flags a reservation as risky, but the guest ultimately completes the stay.

Those have different operational consequences.

Threshold 0.50
Predicted negative
Predicted positive
Actual Positive
Actual Negative
0
Model score
1
TPTrue positive	3
FPFalse positive	3
TNTrue negative	2
FNFalse negative	2
At threshold 0.50:
Precision=
TP+FP
TP
	​

=
3+3
3
	​

=50%
Recall=
TP+FN
TP
	​

=
3+2
3
	​

=60%
Threshold
Threshold
Give feedback

The threshold moves you along that precision–recall trade-off; it should therefore be chosen using validation data, not test data.

4. I would lean toward recall, but not blindly maximize it

For your business case, missing a genuine fall-through probably matters more than flagging some reservations that ultimately stay — provided the response to the prediction is low-risk.

For example, if a high-risk prediction merely triggers:

closer inventory monitoring;
forecasting adjustments;
prioritisation for reservation review;

then false positives aren't terribly damaging.

That makes recall valuable.

But if the operational action were something aggressive like:

immediately resell or overbook a room because the model thinks this guest will cancel,

false positives become much more costly.

Your current problem statement wisely promises decision support / earlier visibility, not automatic overbooking. So I'd lean moderately toward recall.

If you need one summary metric at the chosen threshold, F2 is reasonable because it weights recall more than precision:

from sklearn.metrics import fbeta_score

fbeta_score(y_val, y_pred, beta=2)

But I would not make F2 the primary model-selection metric.

Why?

Because F2 depends on one arbitrary threshold.

PR-AUC lets you compare the underlying models before choosing an operating point.

5. Calibration actually matters for your problem

This is something I'd include because it elevates the pipeline beyond a generic classifier.

You're framing the output as:

probability that a reservation will fall through.

Then:

0.82 risk

should ideally mean something reasonably close to an 82% empirical fall-through frequency among similar predictions.

A Random Forest can rank cases well but have worse-calibrated probabilities than Logistic Regression.

So report a Brier score:

from sklearn.metrics import brier_score_loss

brier_score_loss(y_val, y_val_proba)

Lower is better.

You can later also make a calibration curve if useful, but don't over-expand this yet.

This creates an interesting possibility:

Random Forest may win on discrimination, while Logistic Regression may produce better-calibrated probabilities.

That is a meaningful model-selection discussion rather than just "RF accuracy is higher."

6. Add one business-facing metric: lift / top-risk capture

I think this could be particularly strong for your assessment.

Imagine Revenue & Reservations can realistically focus attention on only the highest-risk 20% of upcoming bookings.

Then ask:

What proportion of all eventual fall-throughs are contained within that highest-risk 20%?

For example:

Top 20% highest-risk bookings contain 43% of future fall-throughs.

That is far more understandable to a stakeholder than:

PR-AUC = 0.74.

You can calculate it later like this:

val_results = pd.DataFrame({
    "actual": y_val.to_numpy(),
    "risk_score": y_val_proba
})

val_results = val_results.sort_values(
    "risk_score",
    ascending=False
)

top_fraction = 0.20
top_n = int(len(val_results) * top_fraction)

top_risk = val_results.head(top_n)

recall_at_top_20 = (
    top_risk["actual"].sum()
    / val_results["actual"].sum()
)

precision_at_top_20 = top_risk["actual"].mean()

print(f"Recall in top 20%: {recall_at_top_20:.2%}")
print(f"Fall-through rate in top 20%: {precision_at_top_20:.2%}")

Then compute lift:

base_rate = val_results["actual"].mean()

lift_at_top_20 = (
    precision_at_top_20 / base_rate
)

print(f"Lift in top 20%: {lift_at_top_20:.2f}x")

If validation prevalence is 36.53% and the top 20% has a 70% fall-through rate:

$$ \text{Lift} \approx 70 / 36.53 = 1.92\times $$

That's a very intuitive result.

7. Your temporal shift makes one detail especially important

You have:

Train: 35.18%
Validation: 36.53%
Test: 40.57%

So the baseline probability is shifting upward.

That matters for two reasons.

First, accuracy becomes even less attractive, because its interpretation changes as class prevalence changes.

Second, raw PR-AUC also has a prevalence-dependent baseline.

For your final report, I'd therefore report something like:

Validation prevalence: 36.53%
Validation Average Precision: 0.xx

Test prevalence: 40.57%
Test Average Precision: 0.xx

You can optionally express AP relative to baseline:

ap_lift = average_precision / y_true.mean()

Don't compare validation and test AP blindly without mentioning that the test period itself contains a larger proportion of fall-through reservations.

ROC-AUC is less directly affected by class prevalence, so having both ROC-AUC and PR-AUC is useful here.

8. Dummy model: make it a meaningful baseline

For classification metrics, I'd use something like:

DummyClassifier(strategy="prior")

This predicts the training class prior as probability.

That's better for your probability-based comparison than only using:

strategy="most_frequent"

because you'll be evaluating PR-AUC, ROC-AUC and probability quality.

Expect:

ROC-AUC ≈ 0.50
AP approximately the validation prevalence
poor ranking/lift

That gives Logistic Regression and Random Forest something meaningful to beat.

9. Concrete model-selection rule I would use

Before training, I would write down the rule so you don't subconsciously choose metrics after seeing which model wins.

Something like:

Models will primarily be compared using validation Average Precision (PR-AUC), because the objective is to identify future reservation fall-throughs while accounting for false-positive alerts. ROC-AUC will be reported as a secondary measure of overall discrimination. Precision and recall will be examined when selecting an operating threshold, with greater emphasis on recall because the proposed use case is risk visibility rather than automated cancellation action. Probability calibration will also be assessed because model outputs are intended to represent fall-through risk.

That's a strong methodology statement.

Then your model table might eventually look like:

Model	PR-AUC ↑	ROC-AUC ↑	Brier ↓
Dummy	...	...	...
Logistic Regression	...	...	...
Random Forest	...	...	...

Select model architecture primarily on validation PR-AUC, with ROC-AUC and calibration as supporting evidence.

Then choose its threshold separately and report:

precision;
recall;
F1/F2;
confusion matrix;
optionally top-20% recall/lift.

Finally, freeze everything and evaluate once on May–Aug 2025.

That clean separation — model discrimination first, operating threshold second, untouched future test last — will make your pipeline reasoning much stronger than optimizing accuracy at 0.5.

[User] I ran the first validation comparison. Results are:

Dummy: ROC-AUC 0.5000, Average Precision 0.3653
Logistic Regression: ROC-AUC 0.8565, Average Precision 0.8044, precision 0.7054, recall 0.7001, F1 0.7027
Random Forest: ROC-AUC 0.8868, Average Precision 0.8413, precision 0.8314, recall 0.5710, F1 0.6770

Random Forest has the strongest threshold-independent ranking metrics, while Logistic Regression currently has better recall/F1 at the default 0.5 threshold.

My interpretation is that I shouldn't choose Logistic just because of the 0.5-threshold F1. I'm thinking of using Average Precision as the primary model-selection metric, doing only light Random Forest tuning on validation, then selecting the classification threshold on validation before touching the test set. Does that reasoning make sense, and would you use a different primary metric or threshold-selection rule?

[AI] Your reasoning makes sense, and I would not choose Logistic Regression just because its F1 is better at the arbitrary 0.5 threshold.

The validation results actually tell a fairly clean story:

Model	ROC-AUC	Average Precision	Precision @ 0.5	Recall @ 0.5	F1 @ 0.5
Dummy	0.5000	0.3653	—	—	—
Logistic Regression	0.8565	0.8044	0.7054	0.7001	0.7027
Random Forest	0.8868	0.8413	0.8314	0.5710	0.6770

Random Forest is doing a better job ranking risky reservations above safer reservations. Its lower recall at 0.5 mainly tells you that 0.5 is currently a conservative operating threshold for that model.

I would keep Average Precision as the primary selection metric

For your problem, I think that remains the best choice.

Your target is the positive class — reservations that fall through — and the model is meant to identify/rank those bookings early. Average Precision directly rewards useful precision–recall performance across thresholds.

The improvement is also substantial relative to baseline:

Dummy AP: 0.3653
Logistic AP: 0.8044
RF AP: 0.8413

So Random Forest isn't winning because of some tiny metric fluctuation. It improves AP over Logistic by about 0.037 absolute, while also improving ROC-AUC by about 0.030.

I would therefore currently consider RF the leading model.

I would keep ROC-AUC as a secondary confirmation rather than replacing AP with it.

I would slightly change your tuning plan

Your proposal is:

light RF tuning on validation → choose threshold on validation → test once.

That's acceptable, especially under your deadline.

But avoid repeatedly trying dozens of RF configurations against the same validation set. Eventually you start overfitting your decisions to that four-month period even though you aren't directly fitting model coefficients on it.

I'd define a small tuning space in advance.

For example, only investigate a few parameters that meaningfully control RF complexity:

n_estimators
max_depth
min_samples_leaf
max_features

Something modest like:

{
    "n_estimators": [300, 500],
    "max_depth": [None, 10, 20],
    "min_samples_leaf": [1, 5, 10],
    "max_features": ["sqrt", 0.5]
}

Even that is 36 combinations, which may already be more than you need.

Given your strong untuned result, I'd probably make it smaller.

The objective isn't to squeeze AP from 0.8413 to 0.8421; it's to show sensible optimisation without turning this assessment into exhaustive search.

Threshold selection: don't maximize F1 automatically

This is the one place I'd change the methodology.

F1 implicitly treats precision and recall as equally important.

But your business framing doesn't necessarily do that.

For Travelers' Inn:

False negative

A reservation falls through but wasn't flagged.

False positive

A reservation was flagged as risky but eventually completed its stay.

Because you're proposing risk visibility and proactive planning, rather than automatically cancelling/reselling rooms, false positives should usually be less damaging than missed fall-throughs.

So some preference for recall makes sense.

But you still shouldn't maximize recall blindly — labeling every reservation "high risk" gives 100% recall and is useless.

Threshold 0.50
Predicted negative
Predicted positive
Actual Positive
Actual Negative
0
Model score
1
TP
True positive
	3

FP
False positive
	3

TN
True negative
	2

FN
False negative
	2
At threshold 0.50:
Precision=
TP+FP
TP
	​

=
3+3
3
	​

=50%
Recall=
TP+FN
TP
	​

=
3+2
3
	​

=60%
Threshold
Threshold
Give feedback
Best business-style rule: recall subject to a minimum precision

If you can justify an acceptable precision level, this is the threshold rule I like most:

Choose the validation threshold that maximizes recall while maintaining precision of at least X%.

For example:

maximize recall subject to precision ≥ 70%.

That directly translates to:

Find as many future fall-throughs as possible while ensuring that at least 7 in 10 flagged reservations historically actually fell through.

That's easier to explain to a stakeholder than:

“We optimized F1.”

Use the precision-recall curve:

from sklearn.metrics import precision_recall_curve

precision, recall, thresholds = precision_recall_curve(
    y_val,
    rf_val_proba
)

threshold_results = pd.DataFrame({
    "threshold": thresholds,
    "precision": precision[:-1],
    "recall": recall[:-1]
})

eligible = threshold_results[
    threshold_results["precision"] >= 0.70
]

selected = eligible.loc[
    eligible["recall"].idxmax()
]

selected

The 0.70 is only an example. Don't pretend it came from management if they never supplied such a requirement.

If you don't have a defensible minimum precision, use F2 as a transparent proxy

You currently don't have real business costs like:

cost of reviewing a flagged booking;
expected recovered revenue;
cost of over-reserving;
cost of missing a cancellation.

So there may be no defensible way to claim "70% precision is the business requirement."

In that situation, I would use:

Maximum validation F2

rather than F1.

F2 weights recall more heavily than precision, which matches your low-consequence risk-alert use case.

You could say:

In the absence of quantified business costs, F2 was used as a practical threshold-selection criterion because the intended use is early risk identification, where missing a genuine fall-through is considered more undesirable than flagging some reservations that ultimately complete their stay.

That's honest about the assumption.

Do not imply F2 is objectively economically optimal.

There's actually an even more business-natural alternative: capacity-based ranking

Since your model is fundamentally a risk-ranking system, you might not need a hard probability threshold operationally.

Suppose Revenue & Reservations can review only 20% of upcoming reservations.

Then the real rule becomes:

Review the highest-risk 20%.

You could report:

Precision@20%
Recall@20%
Lift@20%

That is highly intuitive.

For example:

“By focusing on the 20% of reservations with the highest predicted risk, the model identifies X% of eventual fall-throughs, with a fall-through rate Y times the overall baseline.”

I'd definitely calculate this as a business diagnostic.

But unless you have a real capacity assumption from the stakeholder, I wouldn't use an arbitrary top-20% rule as your official threshold-selection criterion.

One thing to check before final RF selection: probability calibration

There's an important distinction:

Your results currently show that RF has better discrimination.

They don't yet show that:

predicted probability = 0.80

really means approximately 80% fall-through probability.

Since your stated solution produces reservation risk probabilities, check calibration before calling those numbers literal probabilities.

At minimum compare Brier score:

from sklearn.metrics import brier_score_loss

print(
    "Logistic Brier:",
    brier_score_loss(y_val, logistic_val_proba)
)

print(
    "RF Brier:",
    brier_score_loss(y_val, rf_val_proba)
)

And perhaps one calibration curve if needed.

It's entirely possible to find:

RF has better AP/ROC-AUC;
Logistic has better calibration.

That would not automatically make Logistic the better model.

You could still select RF for ranking and later calibrate its probabilities if warranted.

Given the assessment deadline, I wouldn't overcomplicate this unless RF calibration is obviously poor.

Also don't be surprised if the final test precision changes

Your validation prevalence is 36.53%, while test prevalence is 40.57%.

Once you've selected an RF configuration and threshold using validation:

freeze them.

Then apply exactly the same model and threshold to May–Aug 2025.

Do not retune because test precision/recall changes.

With a higher positive base rate, the operating characteristics may shift. That's part of what your temporal test is designed to reveal.

That gives you a useful deployment discussion:

The later test period had a higher underlying fall-through rate than training/validation, providing a more challenging assessment of temporal generalisation.

The methodology I would use from here

I would lock this down before seeing more results:

Primary model metric: validation Average Precision.
Secondary: ROC-AUC.
Supporting: Brier/calibration because you're outputting risk scores.
Do a small, predefined RF hyperparameter search using validation AP.
Choose the final RF configuration.
Select its threshold separately, preferably:
recall subject to a justified precision floor, or
validation F2 if no business precision constraint exists.
Also report precision/recall/lift among a top-risk fraction as a stakeholder-facing diagnostic.
Freeze model + preprocessing + threshold.
Evaluate once on the test set using AP, ROC-AUC, precision, recall, F1/F2, confusion matrix and calibration.

Your interpretation right now is therefore correct:

Random Forest currently appears superior at separating high- and low-risk reservations; Logistic Regression's higher recall and F1 at 0.5 are threshold-specific and are not sufficient reasons to select it over RF.

That is the reasoning I'd carry forward.

[User] I’ve now completed the development-stage decisions using validation data only.

I kept the Random Forest tuning deliberately small:

RF base: Average Precision 0.8413, ROC-AUC 0.8868
RF max_depth=20: Average Precision 0.8434, ROC-AUC 0.8892
RF min_samples_leaf=5: Average Precision 0.8430, ROC-AUC 0.8883

I selected the depth-20 model because it had the highest validation Average Precision. The improvement over the base model is small, so I don’t plan to keep tuning further.

Because we don’t have an actual business precision requirement or cost matrix, I used maximum validation F2 for threshold selection. This gave a threshold of 0.13, with:

precision 52.70%
recall 96.30%
F1 0.6812
F2 0.8263

I also checked the ranking performance. The highest-risk 20% of validation reservations contains 48.56% of all fall-throughs, with an 88.69% fall-through rate and 2.43x lift over baseline.

My interpretation is that 0.13 should be treated as a recall-oriented screening threshold for risk visibility, not as a trigger for automatic action.

At this point I’m planning to freeze:

Random Forest
300 trees
max_depth=20
min_samples_leaf=2
threshold=0.13

and evaluate it once on the untouched May–Aug 2025 test period.

Before I do that, do you see any reason to change the model-selection or threshold logic, or is this now ready for final test evaluation?

[AI]Your development logic is coherent, and I would freeze the model now rather than continue tuning. The small gain from the depth-20 forest is enough to justify the choice, but not enough to justify chasing more hyperparameters.

The threshold logic is also defensible. Maximising validation F2 is a transparent way to encode your stated preference for catching fall-throughs when you lack an actual cost matrix or stakeholder precision constraint. At 0.13, the model is clearly operating as a high-recall screening system:

recall 96.30%
precision 52.70%
F2 0.8263

That is appropriate only because your proposed action is risk visibility / prioritisation, not automatic overbooking or cancellation action. I would state that explicitly in the README.

There is just one check I would do before opening the test set.

Check probability calibration on validation

You have been describing the output as a probability of fall-through. Random Forest scores can rank extremely well without being well calibrated. A threshold of 0.13 also does not necessarily mean “13% actual risk.”

At minimum, calculate Brier score for Logistic Regression and your final RF:

from sklearn.metrics import brier_score_loss

print(
    "Logistic Brier:",
    brier_score_loss(y_val, logistic_val_proba)
)

print(
    "Final RF Brier:",
    brier_score_loss(y_val, rf_val_proba)
)

If RF calibration is reasonably sensible, proceed.

If RF discrimination is excellent but calibration is noticeably poor, I would not reopen model selection automatically. The simplest defensible approach for this assessment may be to describe its output as a fall-through risk score rather than claiming the raw RF value is a calibrated probability.

I would only add probability calibration now if the validation evidence shows a genuine problem. Otherwise it risks unnecessary scope expansion.

One methodological limitation to acknowledge

You used the same Jan–Apr validation block to:

choose RF over Logistic;
choose the RF hyperparameters;
choose the 0.13 threshold.

That means the validation results are somewhat optimistically tailored to that period.

This isn't fatal. You deliberately kept the search small, and the untouched May–Aug test set is exactly what protects you from this.

I would not create another split now. Just acknowledge that validation was used for development decisions and treat the test as genuinely final.

Your top-20% result is particularly strong

I would definitely keep this in the eventual README:

The highest-risk 20% of validation reservations contained 48.56% of all fall-throughs and had an 88.69% fall-through rate, representing 2.43× lift over the validation baseline.

That translates the model into an operationally understandable statement.

It also reinforces why Average Precision was a good selection metric: the system's real value is its ability to concentrate future fall-throughs toward the top of the ranking, not merely generate correct 0/1 classifications at an arbitrary cutoff.

Now freeze everything

I would lock exactly what you listed:

Model              Random Forest
n_estimators        300
max_depth           20
min_samples_leaf    2
threshold           0.13

Also freeze:

preprocessing;
feature list;
category normalisation;
imputation rules;
encoding;
random seed;
prediction-point leakage exclusions.

Do not modify any of these based on test results.

Then evaluate once on May–Aug 2025.

For the final test, I would report:

Evaluation	Why
Average Precision	Primary discrimination metric
ROC-AUC	Secondary ranking metric
Precision @ 0.13	Cost/quality of alerts
Recall @ 0.13	Coverage of actual fall-throughs
F1 and F2 @ 0.13	Summary threshold metrics
Confusion matrix	Concrete FP/FN consequences
Top-20% precision/recall/lift	Business-facing ranking performance
Brier score	Risk-score/probability quality
Fall-through prevalence	Context for AP and lift

And because your combined target is 97.26% cancellations and only 2.74% no-shows, add one very small final diagnostic:

Of test cancellations, what percentage were identified at threshold 0.13? Of test no-shows, what percentage were identified?

You don't need separate models. This simply ensures that aggregate recall isn't hiding total failure on the small no-show subgroup.

One last thing: expect the test metrics to differ. Test prevalence is 40.57%, versus validation's 36.53%. The period is genuinely later and appears to have shifted. If AP, precision, recall, or calibration move, that's useful deployment evidence—not a reason to change the frozen model.

So my recommendation is: do the validation calibration sanity check, then open the test set once. Your model-selection and threshold methodology are already strong enough to defend.

[User] I’ve now completed the final untouched test evaluation and the end-to-end pipeline is reproducible through run.sh and GitHub Actions.

Final May–Aug 2025 test results:

Average Precision: 0.8051
ROC-AUC: 0.8510
Brier score: 0.1600
Precision @ 0.13: 52.71%
Recall @ 0.13: 97.87%
F1: 0.6852
F2: 0.8355

Confusion matrix:

TP 8,806
FN 192
FP 7,901
TN 5,278

The top-risk 20% of reservations captured 41.13% of all fall-throughs, had an 83.45% fall-through rate, and 2.06x lift over the test baseline.

Subtype recall was 97.97% for cancellations and 92.12% for no-shows.

Performance dropped somewhat from validation on AP/ROC-AUC and Brier, but the recall-oriented screening behaviour remained stable. I’m treating that as realistic temporal generalisation rather than reopening tuning.

I also packaged the pipeline with src/main.py, requirements.txt and run.sh, and the GitHub Actions workflow passed successfully on a fresh runner.

Before I write the README, is there anything important in how I’m interpreting the final test results or limitations that I should correct?

[AI] Your interpretation is mostly right. I would not reopen tuning. The test did what an untouched temporal test is supposed to do: performance weakened somewhat on a later period, but the model still generalized meaningfully.

There are, however, a few limitations I would make explicit in the README—especially one important operational point around the 0.13 threshold.

1. The temporal drop is real, not just noise to explain away

Validation → test:

AP: 0.8434 → 0.8051
ROC-AUC: 0.8892 → 0.8510

That is roughly a 0.038 drop in both discrimination metrics.

Since ROC-AUC is not driven by the higher test prevalence in the same way AP is, the fact that both metrics fall supports your interpretation that there is some genuine temporal shift/generalization degradation.

So I would phrase it as:

Performance declined moderately on the later test period, indicating some temporal drift, but discrimination remained strong and the predefined recall-oriented operating behavior generalized well.

I would avoid wording like “the model is stable” without qualification. Better:

The screening behavior remained relatively stable despite reduced ranking performance.

That is exactly what your numbers show.

2. The biggest practical limitation: your 0.13 threshold flags about 75% of bookings

From the confusion matrix:

predicted positive = TP + FP
8,806 + 7,901 = 16,707

Out of 22,177 test reservations, that means roughly 75% are flagged high-risk.

That is important.

Your threshold achieves exceptional recall:

97.87%

but it does so by screening a very large proportion of reservations, with precision of only:

52.71%

So roughly 47% of the flagged reservations ultimately complete their stay.

That doesn't invalidate the threshold because you selected it explicitly for recall-oriented risk visibility. But it means the README should not imply that 0.13 creates a small, targeted operational watchlist.

I would say:

The selected threshold is deliberately recall-oriented and identifies nearly all fall-throughs, but at the cost of flagging a large proportion of reservations and generating substantial false positives. It is therefore suitable as a screening threshold rather than an automatic intervention rule.

This is probably your most important deployment limitation.

3. Your top-20% ranking result may actually be more operationally compelling than the 0.13 threshold

This result is excellent:

Highest-risk 20% → 41.13% of all fall-throughs captured

with:

83.45% fall-through rate

and:

2.06× lift

That's a very strong stakeholder-facing result.

It means if operational capacity is limited, the hotel could prioritize the highest-risk fraction rather than act on every reservation above 0.13.

So I would present two possible uses, without pretending the business supplied either rule:

Recall-oriented screening

threshold 0.13
catches 97.87% of fall-throughs
but generates a large review population.

Capacity-constrained prioritization

focus on top-risk reservations;
top 20% contains 41.13% of eventual fall-throughs;
those bookings fall through at more than twice the overall rate.

That makes the model look more useful and also more honestly describes the trade-off.

4. Don't call 0.13 a “13% cancellation probability”

This is important.

Unless you've demonstrated strong calibration, the RF output should be described as a:

fall-through risk score

rather than a literal probability.

Your Brier score of 0.1600 is useful evidence that the scores contain meaningful probabilistic information, but Brier score alone does not prove perfect calibration because it reflects both calibration and discrimination.

So:

“Reservations with predicted probability above 13% are high risk”

is a little too strong.

Prefer:

“A validation-selected risk-score threshold of 0.13 was used.”

If you did produce a calibration curve and it looks good, you can be more confident with probability language. Otherwise “risk score” is safer.

5. Put the Brier score in context

A Brier score by itself is hard for a reader to interpret.

The test prevalence is 40.57%. A naive constant model predicting approximately that prevalence for everybody would have a Brier score around 0.24.

Your RF obtains:

0.1600

So it provides substantially more informative probability estimates than simply assigning everyone the population average risk.

I wouldn't over-focus on that calculation in the README, but it gives you a better explanation than:

“Brier = 0.16, lower is good.”

6. Your subtype result supports the combined target, with a caveat

These are reassuring:

cancellation recall: 97.97%
no-show recall: 92.12%

That means the combined model isn't achieving high recall solely by catching cancellations while missing almost every no-show.

That's useful evidence supporting your earlier target decision.

But still state that:

Cancellations dominate the positive class, so the model is primarily trained on cancellation patterns and conclusions about no-shows are less statistically robust.

If possible, show the number of no-show observations in the test set alongside that 92.12%. A percentage over a small subgroup can look more precise than it really is.

You don't need confidence intervals unless you want them.

7. Don't interpret the model as causal

Your EDA found huge associations such as:

Non Refund deposit → very high fall-through;
long lead time → higher fall-through;
TA/TO → higher fall-through.

The model can exploit those patterns.

But the README should not turn feature importance into recommendations such as:

“Non-refundable deposits increase cancellations, therefore change deposit policy.”

The model is predictive, not causal.

Better:

Certain reservation characteristics are predictive of historical fall-through and help the model rank future booking risk.

8. The model does not prove recovered revenue

Keep the distinction you established during EDA.

The model predicts:

whether a reservation will fail to become a completed stay.

It does not measure:

whether the room would actually remain empty;
whether it would later be resold;
cancellation fees retained;
incremental revenue recovered by intervention;
cost of acting on false positives.

Therefore the appropriate benefit is:

earlier visibility of inventory and revenue exposure

rather than:

guaranteed lost revenue prevention.

9. Your test only establishes one form of temporal generalization

You now have strong evidence that:

a model trained through Dec 2024 retains meaningful performance on May–Aug 2025.

But you haven't demonstrated that performance will remain unchanged:

next year;
after pricing/policy changes;
after channel-mix changes;
during major events;
if customer behavior changes.

So deployment considerations should mention:

periodic monitoring of class prevalence, feature distributions, ranking metrics, and calibration, followed by retraining when performance materially deteriorates.

That's a good “next steps/deployment” point without requiring you to build monitoring now.

How I would summarize the final result

Something close to this would be accurate:

The final Random Forest retained good discrimination on the untouched May–Aug 2025 temporal test set (Average Precision 0.8051; ROC-AUC 0.8510), despite lower performance than validation and a higher test-period fall-through rate. At the validation-selected recall-oriented threshold of 0.13, the model identified 97.87% of fall-throughs, although the resulting precision of 52.71% and high proportion of flagged reservations make this more appropriate for screening than automatic operational action.

For capacity-constrained prioritization, the ranking itself is operationally useful: the highest-risk 20% of reservations contained 41.13% of all fall-throughs, had an 83.45% fall-through rate and achieved 2.06× lift over the test baseline.

That is strong without overselling it.

And yes: do not reopen tuning now. Doing so after seeing the test set would undermine one of the strongest methodological choices you've made. The test result is now evidence about the frozen system, not feedback for another development cycle.

[User] Before I finalise the submission, can you check whether my eda, pipeline choices, final metrics and deployment limitations are internally consistent? Please flag contradictions only and do not rewrite my decision log

[AI] Based on the final results and decisions you've reported in this conversation, the overall story is internally consistent. I see four items worth checking for contradiction before submission. I’m not rewriting the Decision Log.

One limitation on this review: the eda.ipynb currently attached here is the earlier version from before the later business EDA/model results, so I can verify the reasoning trail you've reported, but I cannot line-by-line verify your latest notebook or src/ code unless you upload the final versions. The earlier notebook does establish the intended EDA-first problem selection and leakage-aware framing.

Do not retain “last-minute room recovery” as the main problem justification. Your later EDA contradicts that framing: median cancellation notice was 56 days, only 12.04% occurred within 7 days, and nearly half occurred 61+ days ahead. So anywhere the final EDA/README says the model primarily solves last-minute cancellations or last-minute room recovery should be changed. The consistent framing is earlier visibility of future inventory/revenue exposure and proactive planning.
Check whether the final test model was refitted on train + validation. This is the biggest methodological item to verify. Your threshold 0.13 was selected using validation predictions from a particular fitted RF. If you then retrained a new RF on train + validation before testing but carried over 0.13 unchanged, the threshold was technically optimized for a different fitted model and score distribution. If instead the final test used the exact frozen model fitted on Aug 2023–Dec 2024, with validation used only for selection/tuning/thresholding, then everything is consistent. I would not change anything now if that is what you did.
Be consistent about “probability” versus “risk score.” Your selected ML problem was originally phrased as estimating the probability of fall-through. That is fine conceptually, but Brier 0.1600 alone does not establish that RF outputs are perfectly calibrated probabilities. If your deployment limitations acknowledge calibration uncertainty, don't elsewhere describe 0.13 as meaning “13% chance of cancellation.” Call it a validation-selected risk-score threshold of 0.13, unless you have separately demonstrated calibration.
Do not describe threshold 0.13 as producing a small targeted high-risk list. Your confusion matrix implies 16,707 / 22,177 ≈ 75.3% of test reservations were flagged. That is completely consistent with your recall-oriented F2 strategy, but it would contradict wording such as “the model flags only the highest-risk reservations.” Your two operational interpretations should remain distinct:
0.13 = broad screening threshold, 97.87% recall but many false positives.
top 20% ranking = prioritisation use case, capturing 41.13% of fall-throughs at 83.45% precision / 2.06× lift.

Everything else you reported lines up:

118,549 − 353 = 118,196 modelling reservations.
Overall fall-through = 36.40%.
Chronological split totals exactly 77,577 + 18,442 + 22,177 = 118,196.
Test confusion matrix totals exactly 22,177 and reproduces the stated 40.57% prevalence, 52.71% precision and 97.87% recall.
AP as the primary model-selection metric is consistent with the earlier methodology.
RF depth 20 was selected on validation AP before touching test.
F2 threshold selection is consistent with the recall-oriented, low-consequence screening use case.
The test decline in AP/ROC-AUC is consistent with your claim of temporal degradation rather than a reason to retune.
97.97% cancellation recall and 92.12% no-show recall support—not prove—the practical decision to combine them while acknowledging that cancellations dominate the target.
Rejecting pricing optimisation as the final supervised problem is consistent with the EDA finding that historical ADR exists but an observed optimal price/price-response target does not.
Your pipeline reproducing the raw-to-modelling counts and running successfully via run.sh/GitHub Actions is aligned with the assessment requirement that preprocessing and modelling be implemented in Python scripts and executable end-to-end.

So the only item I would actively investigate before submission is #2: confirm exactly what data the fitted model used when you produced the final test predictions. The other three are mainly wording/interpretation consistency checks.

[User] eda(20260830-071551).ipynb
File

[AI] I checked the newly uploaded final EDA against the pipeline/model decisions and final metrics you've described. The core story is consistent. I found two actual wording contradictions and one model-configuration point that you should verify before submission:

“Three years of booking records” vs actual observed coverage. Your opening says the notebook explores “three years of booking records,” but Section 4 establishes arrival coverage of 1 Aug 2023 to 31 Aug 2025, which is about 25 months rather than three full years. Since the assessment itself describes the source as three years, the safest notebook wording is something like “booking records spanning 2023–2025” rather than asserting three complete years.
“Key drivers of revenue loss” is stronger than what the EDA establishes. Your introduction says the EDA aims to identify “key drivers of revenue loss,” while your later reasoning correctly becomes much more careful: you identify associations with fall-through and talk about inventory/revenue exposure, not proven causal drivers or observed revenue loss. You do not know whether cancelled rooms were resold, what cancellation fees were retained, or whether any feature causally drives the outcome. So that phrase conflicts with the more defensible interpretation later in the notebook.
Check the exact winning RF configuration. Your reported tuning sequence was base RF → max_depth=20 → min_samples_leaf=5, and you selected the depth-20 model because AP was 0.8434. Your frozen configuration is 300 trees, max_depth=20, min_samples_leaf=2. That is internally consistent only if min_samples_leaf=2 was already part of the base/depth-20 configuration. If the depth-20 experiment actually used another leaf setting (e.g. sklearn default 1), then the model tested as the validation winner is not exactly the model you froze for final evaluation.

There is also one terminology point that is only a contradiction if your README/deployment section uses different wording: Section 5.2 currently says the model estimates the “probability” of fall-through. Your final RF has a Brier score, but unless you separately demonstrated adequate calibration, I would avoid elsewhere saying that 0.13 literally means a 13% probability. Calling the RF output a risk score or estimated fall-through probability/risk score keeps the deployment interpretation aligned.

Apart from those points, I did not find contradictions in the important EDA chain: 118,549 → 353 duplicates removed → 118,196; 36.40% fall-through; the weakened “last-minute” hypothesis; combined cancellation/no-show target; leakage exclusions; rejection of pricing optimisation as the final supervised problem; and the move toward chronological model validation all line up with the modelling decisions you've described. That coherence matters because the README is specifically expected to summarize the EDA findings and explain pipeline choices that follow from them.

One non-logic submission check: the uploaded copy is named eda(20260830-071551).ipynb; make sure the repository version is actually named eda.ipynb, as required.

---
