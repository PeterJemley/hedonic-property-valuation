# Data dictionaries

This folder holds two real datasets. `uffidata.xlsx` (below) is the core 99-home
study; `kc_house_data.csv` is the 21,613-sale King County set used to show the
method at scale (see [`../docs/kingcounty_valuation.md`](../docs/kingcounty_valuation.md)).
The simulated commercial book is generated in code, not stored here.

---

## `uffidata.xlsx`

99 arm's-length residential sales used to study how the presence of
**urea-formaldehyde foam insulation (UFFI)** affects sale price, controlling for
the other physical characteristics of each home. One row per sale.

| Column (raw)     | Clean name    | Type        | Description |
|------------------|---------------|-------------|-------------|
| `Observation`    | `observation` | id          | Row identifier (dropped before modelling — carries no price signal). |
| `Year Sold`      | `year_sold`   | int 2009–16 | Calendar year of sale. Proxy for the market cycle / appreciation. |
| `Sale Price`     | `sale_price`  | $ (target)  | Transaction price. Range $76,900–$347,000; right-skewed (skew ≈ 2.55). |
| `UFFI IN`        | `uffi_in`     | 0/1         | 1 if the home contains UFFI. **The variable of interest.** |
| `Brick Ext`      | `brick_ext`   | 0/1         | 1 if brick exterior (vs wood). |
| `45 Yrs+`        | `age_45plus`  | 0/1         | 1 if the home is older than 45 years. |
| `Bsmnt Fin_SF`   | `basement_sf` | sq ft       | Finished basement area. |
| `Lot Area`       | `lot_area`    | sq ft       | Lot size. |
| `Enc Pk Spaces`  | `park_spaces` | count 0–2   | Enclosed (garage) parking spaces. |
| `Living Area_SF` | `living_area` | sq ft       | Above-grade living area. The dominant price driver. |
| `Central Air`    | `central_air` | 0/1         | 1 if central air conditioning. |
| `Pool`           | `pool`        | 0/1         | 1 if the property has a pool (rare in this sample). |

## Provenance & scope

The dataset is a teaching dataset distributed with a graduate machine-learning
course and is included here unchanged for reproducibility. It is small (n = 99)
and local, so the **method** generalizes (see [`../docs/applications.md`](../docs/applications.md))
but the **specific coefficients do not** transfer to other markets. Treat the
numbers as an illustration of technique, not a market appraisal.

## Notes for modelling

- The trailing all-blank spreadsheet row is dropped on load.
- No missing values remain after that drop.
- `sale_price` is modelled on the **log scale** (skew ≈ 2.55 → 1.12 after log).
- Outliers are **flagged** by Cook's distance, not deleted (see methodology).

---

## `kc_house_data.csv`

21,613 home sales in King County, WA (May 2014 – May 2015) — a well-known public
dataset. One row per sale. Target is `price`. The model uses the columns below
plus two engineered features (`age = 2015 − yr_built`, `renovated = yr_renovated > 0`).

| Column | Type | Description |
|--------|------|-------------|
| `price` | $ (target) | Sale price. Median $450,000; range $75k–$7.7M; skew ≈ 4.02 (→ 0.43 logged). |
| `sqft_living` | sq ft | Above-grade living area. |
| `sqft_lot` | sq ft | Lot size. |
| `bedrooms` / `bathrooms` | count | Room counts. |
| `floors` | count | Number of floors. |
| `waterfront` | 0/1 | Waterfront property. |
| `view` | 0–4 | Quality-of-view rating. |
| `condition` | 1–5 | Overall condition. |
| `grade` | 1–13 | King County construction-quality grade. |
| `yr_built` / `yr_renovated` | year | Used to derive `age` and `renovated`. |
| `lat` / `long` | degrees | Location — among the strongest price drivers. |
| `sqft_living15` | sq ft | Avg living area of the 15 nearest homes (neighborhood proxy). |
| `zipcode`, `id`, `date`, `sqft_above`, `sqft_basement`, `sqft_lot15` | — | Present in the file; not used by the base model. |

Local and dated: the coefficients are specific to this market and period. The
**method** transfers; the numbers do not.
