# From hedonic pricing to real-estate acquisitions

A hedonic regression and an acquisitions underwriting model are the same idea
wearing different clothes: both **decompose the value of an asset into the
contributions of its measurable attributes**, then use that to price the next
deal and stress-test the assumptions. This note maps the techniques in this
repository to the day-to-day work of an acquisitions analyst.

---

## Mapping the toolkit to the work

### Build financial models and run sensitivity analyses

The model here already *is* a small valuation engine with uncertainty attached.
Two pieces translate directly:

- **Point value + prediction interval.** `predict_with_interval()` returns not
  just an estimate but a defensible range (e.g. $160,900 with a 95% band of
  $117,600 – $204,200). In underwriting terms, that band is a data-driven
  downside/upside case rather than a guessed +/- on a single number.
- **Attribute sensitivities.** The per-characteristic effects (e.g. living area
  ≈ +13% per standard deviation, UFFI ≈ −6%) are exactly the levers a
  sensitivity table flexes. The same code that estimates "what UFFI costs"
  estimates "what 5,000 SF or one floor of better quality is worth," and feeds
  the high/base/low rows of a model.

The discipline of **honest, out-of-sample error** is the habit that matters most
in an IC setting: it forces a model to state how wrong it can be before anyone
commits capital.

### Conduct market research on demographics and supply/demand

Hedonic models are the standard tool for **rent and price benchmarking** across a
competitive set. Given a table of comparable assets and their attributes
(submarket, vintage, class, amenities, lease terms), the same pipeline answers:

- What is the market paying per unit of each attribute *right now*?
- Is a target asset priced above or below what its characteristics justify?
- How much of a rent gap is explained by fundamentals vs. mispricing?

Add demographic or supply/demand indices (population growth, absorption,
pipeline) as additional features and they become measurable price drivers — the
`year_sold` market-cycle variable in this project is a miniature version of
exactly that.

### Support tenant and credit diligence

The classification side of the same coursework (not shown in this repo, but in
the same skill set) covers **credit and default modelling** — predicting a
binary outcome (default / no default, renew / vacate) from borrower or tenant
attributes. For diligence that means:

- Scoring **tenant credit and rollover risk** from financials and lease data.
- Flagging **concentration risk**, including exposure to a single counterparty or
  to **government-contract-dependent tenants** whose cash flows track
  appropriations rather than the market.
- Quantifying how much a credit assumption moves the valuation band above.

### Manage data rooms, diligence timelines, and documentation

This repository is itself a worked example of **reproducible, auditable
analysis**: versioned code, a data dictionary, regenerable figures, and a
written methodology that a third party can check line by line. The same habits —
single source of truth, documented assumptions, nothing computed by hand that
can't be reproduced — are what keep a data room clean and a diligence timeline
defensible.

### Contribute to investment memoranda and IC materials

The `docs/` and `figures/` here are structured the way memo exhibits are: a
plain-language thesis, a small number of clear charts, a defensible valuation
range, and an explicit list of risks and limitations. The
[`methodology.md`](methodology.md) note is written for a non-technical reader on
purpose — the same register an IC memo demands.

---

## Honest scope

This is a **technique demonstration on a small, dated housing sample**, not a
live underwriting model. Its value to an acquisitions desk is the *transferable
method and the analytical discipline* — attribute-level valuation, sensitivity
analysis, out-of-sample validation, and clear documentation — not the specific
coefficients. Pointed at a real comparable set, the same pipeline produces the
benchmarking and valuation ranges those workflows depend on.
