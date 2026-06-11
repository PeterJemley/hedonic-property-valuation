# Data dictionary — `uffidata.xlsx`

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
