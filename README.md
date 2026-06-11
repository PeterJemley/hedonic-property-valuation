# Hedonic Pricing — what a property characteristic is worth

A compact, reproducible study that estimates how much a single building
characteristic — the presence of **urea-formaldehyde foam insulation (UFFI)** —
changes a home's sale price, after controlling for everything else about the
property. The same machinery, a **hedonic regression**, is the analytical
backbone of how acquisitions teams underwrite an asset's value from its
attributes.

The project is implemented **twice, side by side** — once in **R** and once in
**Python** — so the modelling choices are language-independent and easy to
audit. Every headline number below was produced by the code in this repo.

---

## Headline results

| Question | Answer | Where |
|---|---|---|
| What does UFFI do to value? | **−6% of price** (log model, p ≈ 0.08); **−$14,700** in a simpler dollar model (p ≈ 0.02) | [`06_characteristic_effects.png`](figures/06_characteristic_effects.png) |
| Best out-of-sample model (n = 99) | **Ridge regression on log price**, 10-fold CV RMSE **$24,862**, R² **0.62** | [`04_model_leaderboard.png`](figures/04_model_leaderboard.png) |
| Value of an example home | **$160,900**, 95% prediction interval **$117,600 – $204,200** | [`07_prediction_interval.png`](figures/07_prediction_interval.png) |
| Biggest price drivers | Living area (+13% / SD) and sale year, i.e. the market cycle (+9% / SD) | [`06_characteristic_effects.png`](figures/06_characteristic_effects.png) |

![Model leaderboard](figures/04_model_leaderboard.png)

---

## What this gets right

Originated as graduate coursework (Northeastern, *DA5030 Machine Learning*, 2019)
and rebuilt and extended to a professional standard. The emphasis is on the four
disciplines that separate a hedonic model you can underwrite against from one
that merely *looks* accurate — each a common pitfall in practice:

1. **Don't delete the expensive assets.** Trimming the response variable to
   remove "outliers" is the most common way to fake a good error number. On this
   data, dropping every sale more than 1.5 SD from the mean discards **26% of the
   homes and every sale above $179k** (the true maximum is $347k), pulling the
   reported error from a realistic **$24,317** down to an artificial **$16,720**.
   This pipeline keeps every observation and instead *flags* influence with
   Cook's distance.
2. **Measure error out-of-sample.** In-sample residuals flatter a model. Every
   headline number here is **10-fold cross-validated** and reported in dollars.
3. **Quote a correct prediction interval.** The `point ± 1.96 × residual_SE`
   shortcut understates uncertainty; this uses a proper prediction interval that
   also accounts for the uncertainty in the fitted coefficients.
4. **Model the skew, keep the signal.** Price is right-skewed, so the target is
   modelled on the **log scale**, and the `year_sold` market-cycle variable is
   retained as a price driver.

The reasoning behind each, with verified numbers: [`docs/methodology.md`](docs/methodology.md).

---

## Commercial extension — pricing a systematic mispricing

The same engine, pointed at commercial real estate, demonstrates a concrete
underwriting edge: **measuring an attribute the market fails to price.**

In a transparently simulated book of net-leased industrial/office assets, a
hedonic model fit on transaction prices shows the market pays for the
credit-tenancy attributes (tenant credit, lease term, submarket) but assigns a
*mission-critical defense lease* an effect of **−0.4%, statistically
indistinguishable from zero** — i.e. it is priced as generic credit tenancy.
Underwriting that attribute as defense infrastructure (a sensitivity-tested
cap-rate compression) converts it into a capturable spread: at a 75 bps base
case, **~10.7% of value (~$10.8M per 1.0M SF)**.

![CRE market pricing](figures/08_cre_market_pricing.png)

This is the same statistics as the housing study with the sign flipped — there,
an attribute the market *discounts*; here, one it *ignores*. Full walkthrough,
sensitivity table, and scope/disclaimers: [`docs/cre_defense_platform.md`](docs/cre_defense_platform.md).

---

## What's in here

```
hedonic-property-valuation/
├── data/        uffidata.xlsx + a full data dictionary
├── python/      reusable pipeline + housing notebook + the CRE extension
├── R/           the same housing analysis as a commented R Markdown report
├── figures/     ten committed visualizations (regenerated from data)
└── docs/        methodology, applications, and the CRE / acquisitions write-ups
```

- **`python/uffi_pipeline.py`** — a small, **dataset-agnostic** hedonic engine.
  Point it at a different priced-asset dataset by writing one `HedonicConfig`
  and changing nothing else.
- **`python/cre_defense_lease.py`** — the engine applied to commercial real
  estate: detecting and pricing an attribute the market ignores.
- **`R/uffi_hedonic_model.Rmd`** — the housing workflow as a knit-ready R report.
- **`docs/cre_defense_platform.md`** — the defense-leased mispricing demonstration.
- **`docs/cre_acquisitions.md`** — how the toolkit maps to acquisitions work.
- **`docs/applications.md`** — how it transfers to other commerce areas.

---

## Run it

**Python**
```bash
pip install -r requirements.txt
python python/uffi_pipeline.py        # housing: prints the full report
python python/make_figures.py         # housing: regenerates figures 01–07
python python/cre_defense_lease.py    # commercial: the defense-lease demo
python python/make_cre_figures.py     # commercial: regenerates figures 08–10
jupyter notebook python/uffi_hedonic_model.ipynb
```

**R**
```r
install.packages(c("tidyverse","readxl","janitor","caret","glmnet",
                   "ranger","car","broom","e1071"))
# open R/uffi_hedonic_model.Rmd in RStudio and Knit
```

Both languages read the same `data/uffidata.xlsx` and reproduce the same
conclusions.

---

## A note on scope

The dataset is small (n = 99) and local. The **method** generalizes; the
**specific coefficients do not** — they illustrate technique, not a transferable
appraisal. See [`docs/applications.md`](docs/applications.md) for where the
approach extends and where it doesn't.
