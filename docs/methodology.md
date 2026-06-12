# Methodology — in plain language

This note explains, without assuming a statistics background, **what the model
does and why each modelling choice makes the result trustworthy** — including
the common pitfalls the pipeline is built to avoid. Every number is reproduced
by the code in this repository.

---

## 1. The question

We have 99 home sales. Each home is described by ten characteristics — living
area, lot size, age, parking, whether it has a pool, the year it sold, and so
on — plus one we particularly care about: whether the home contains
**urea-formaldehyde foam insulation (UFFI)**, a material buyers may discount.

We want to answer three things:

1. **How much does each characteristic add to or subtract from price?**
2. **How accurately can we predict a home's price from its characteristics?**
3. **For a specific home, what's our best price estimate, and how sure are we?**

This is a **hedonic model**: the price of a complex thing is explained as the
sum of what the market pays for each of its measurable parts.

---

## 2. How the model works, in one paragraph

We fit a regression: a formula that multiplies each characteristic by a learned
weight and adds the results to predict price. The weights are chosen to make the
predictions as close as possible to the actual sale prices. Once fitted, each
weight tells us the marginal value of that characteristic, and the formula can
price a home we've never seen.

---

## 3. Four choices that make the answer trustworthy

Each addresses a common pitfall in applied price modelling. The pitfalls share a
theme: they make a model *look* better than it is.

### 3.1 Keep the expensive homes (flag, don't delete)

A tempting "cleanup" step is to remove any sale more than 1.5 standard deviations
from the average on price, basement, lot, or living area. It sounds like tidy
"outlier removal," but on this data it deletes **26 of 99 homes (26%) —
including every sale above $179,000**, when the true range goes to $347,000.

Deleting the expensive homes mechanically shrinks the error, because the hardest
homes to price are simply gone:

| Approach | Homes kept | Highest price kept | Model error (RMSE) |
|---|---|---|---|
| Trim outliers (the pitfall) | 73 | $179,000 | **$16,720** |
| Keep all data (this pipeline) | 99 | $347,000 | **$24,317** |

That "impressive" $16,720 is an artifact of the deletion — the same model on the
full data has a realistic error of $24,317. This pipeline instead **keeps every
home** and uses **Cook's distance** to *flag* the handful (5 homes) with
outsized influence, so they can be reviewed rather than silently dropped.

### 3.2 Grade the model on homes it didn't see

A model graded on the same homes it trained on is flattered — it can memorise
its training data. This pipeline uses **10-fold
cross-validation**: split the data into ten parts, train on nine, predict the
tenth, rotate, and repeat. Every home is priced by a model that never saw it.
That out-of-sample error is the honest number.

| Model (10-fold CV, error in dollars) | RMSE | R² |
|---|---|---|
| **Ridge regression (log price)** ← best | **$24,862** | **0.62** |
| Elastic Net | $25,798 | 0.59 |
| Lasso | $25,801 | 0.59 |
| Ordinary least squares | $25,805 | 0.59 |
| Gradient boosting | $27,137 | 0.54 |
| Random forest | $28,224 | 0.51 |

On a dataset this small, **regularised linear regression wins** and the fancier
tree ensembles overfit. Reporting that honestly is the point — out-of-sample
error is the test a model must pass before its numbers mean anything. (It is the
decisive *empirical* check, not the whole story: a model can also be a poor
*explanation* even when it predicts well — see [`../EXPLAINER.md`](../EXPLAINER.md) §8.)

### 3.3 State uncertainty correctly

A common shortcut produces a prediction interval as `point ± 1.96 × residual_SE`.
That formula ignores the fact that the model's own weights are estimated with
error, so it reports an interval that is too narrow. A proper **prediction
interval** combines the spread of individual homes around the line *and* the
uncertainty in the line itself.

For the example home (older, no finished basement, 7,800 sq ft lot, wood
exterior, one parking space, 1,720 sq ft living area, UFFI, no central air, no
pool) — both intervals computed on the **same** full-data model, so the only
thing that differs is the method:

| Method (same model, point estimate $160,913) | 95% interval | Width |
|---|---|---|
| Naive shortcut: `point ± 1.96 × SE` | $121,222 – $200,603 | $79,381 |
| Proper prediction interval | **$117,626 – $204,200** | **$86,574** |

The proper interval is wider because it carries the coefficient uncertainty the
shortcut drops — the responsible answer when you have only 99 data points.

### 3.4 Model the skew; keep the market signal

House prices are **right-skewed** — a few homes cost far more than the typical
one (skew ≈ 2.55). Fitting a straight line to skewed dollars lets those few
homes dominate. Taking the **logarithm** of price makes the distribution nearly
symmetric (skew ≈ 1.12) and turns each weight into an approximate **percentage**
effect, which is how value differences are naturally expressed ("a pool adds ~5%"
rather than "a pool adds $X").

It would be easy to discard `year_sold` as a mere timestamp. But the sales span
**2009–2016**, a period of real price movement, so the year is a useful proxy
for the market cycle. The pipeline keeps it — and it turns out to be the
second-strongest driver.

---

## 4. What the model says

- **Living area** is the dominant driver (+13% of price per one-standard-deviation
  increase), followed by the **sale year / market cycle** (+9%).
- **UFFI lowers value**: about **−6%** in the log model (p ≈ 0.08, borderline) or
  about **−$14,700** in a simpler dollar model (p ≈ 0.02, significant). Either
  way the sign and rough magnitude are stable: UFFI is a modest but real
  discount.
- The model explains roughly **60%** of price variation out-of-sample — decent
  for 99 homes and ten plain physical attributes, and honest about the rest.

---

## 5. Honest limitations

- **n = 99.** Small. Coefficients have real uncertainty; treat them as
  directional.
- **Local, dated sample.** The specific numbers don't transfer to other markets
  or years. The *method* does.
- **No location features.** With latitude/longitude or neighborhood, a spatial
  model would almost certainly beat this one. That's a natural next step, not a
  flaw in the approach.
