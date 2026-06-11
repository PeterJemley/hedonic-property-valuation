# Applications — using this "off the shelf" beyond one housing dataset

The code in this repository is deliberately built around a generic
`HedonicConfig`, not around houses. The modelling body never names a specific
column; it reads the target, the features, and a few options from the config.
To run the entire pipeline on a different priced asset, you write **one config
object** and change nothing else:

```python
USED_TRUCK_CONFIG = HedonicConfig(
    name="Used medium-duty trucks",
    target="sale_price",
    features=["odometer", "model_year", "engine_hours", "has_liftgate",
              "region_index", "auction_vs_retail"],
    log_target=True,
)
```

That portability is the point of this section: the same four disciplines —
**model the skew, keep every observation, grade out-of-sample, quote a real
interval** — apply anywhere a heterogeneous asset is priced from its attributes.

---

## Where the same method transfers

| Commerce area | "Price" (target) | Example characteristics (features) | What the model buys you |
|---|---|---|---|
| **Residential & commercial real estate** | Sale price or rent/SF | Size, age, condition, location index, amenities, lease terms | Attribute-level valuation, defensible price ranges, what a feature is worth |
| **Used vehicles & equipment** | Resale / auction price | Mileage/hours, year, options, condition grade, channel | Reconditioning ROI, fleet residual-value forecasting |
| **Insurance & risk** | Claim severity or premium | Property/asset attributes, exposure, prior history | Rating factors, reserve estimates, fairness checks |
| **Retail & consumer goods** | Realized price / markdown | Brand, specs, seasonality, channel, condition | Dynamic pricing, trade-in valuation, markdown timing |
| **Commercial leasing** | Effective rent | SF, floor, term, TI/concessions, building class, submarket | Rent benchmarking, concession trade-offs, mark-to-market |
| **Land & development** | Price per buildable unit | Zoning, entitlements, frontage, utilities, location | Site comparison, residual land value |

In every row, the asset is **heterogeneous** (no two units are identical) and
priced as a **bundle of measurable attributes** — exactly the setting a hedonic
model is built for.

---

## What carries over, and what you must re-do per domain

**Carries over unchanged**
- The pipeline structure (load → flag influence → cross-validate a model slate →
  interpret coefficients → predict with an interval).
- The four disciplines that keep the answer honest.
- The reusable code: a new `HedonicConfig` is usually the only edit.

**Must be re-done for each dataset**
- **The features.** Real estate needs *location*; vehicles need *mileage*; rent
  needs *lease terms*. Domain knowledge chooses the columns.
- **The coefficients.** They are estimated fresh from each dataset and never
  transfer between markets, asset types, or time periods.
- **The transform.** Log fits most price targets, but verify the skew first.
- **Validation scheme.** Time-ordered data (most markets) should be validated
  forward in time, not with random folds, to avoid leaking the future.

---

## When *not* to reach for this

- **Thin or non-comparable inventory.** Hedonic models need enough comparable
  transactions to learn from. A handful of trophy assets won't support one.
- **Price set by a few mega-attributes you can't measure.** If value is driven by
  an unrecorded factor (a specific tenant's credit, an off-market relationship),
  the model will be confidently wrong about the part it can't see.
- **Strong spatial or network effects with no location data.** Add the geography
  first; a non-spatial model will mis-price.

---

## The one-paragraph pitch

> Give me a table of comparable transactions with a price column and a handful of
> attribute columns, and this repository will tell you — honestly, with
> out-of-sample error and a real confidence range — what each attribute is worth
> and what any new unit should sell for. It was built on housing, but it doesn't
> know or care that the asset is a house.

See [`cre_acquisitions.md`](cre_acquisitions.md) for how this maps specifically
to commercial-real-estate acquisitions and diligence work.
