# Explainer — what a price is, and how to read what the market knows

This document explains why the methods here work when they work, why they fail
when they fail, and what in the world they are claims about. The wager, following
Popper and Deutsch, is that a method is only as good as the explanation behind
it: improve the explanation, or find where it conflicts with the phenomena, and
the method improves with it. A recipe you cannot explain is a recipe you cannot
correct.

---

## 1. The phenomenon: a price is a trace of distributed knowledge

Start with the thing itself. A house sells for $450,000. Where did that number
come from? Not from any single mind. It is the visible residue of a great many
dispersed judgments — a buyer's sense of the neighborhood, a seller's reserve, a
lender's appraisal, the going rate two doors down — colliding in a transaction.
The price is what those judgments *agreed on* for one moment.

So a market is, among other things, an **inference engine**. It takes knowledge
that no one possesses in full — how much a finished basement is worth here, this
year, to people like these — and compresses it into a single number. The deep
claim of this project is that the compression is partly *recoverable*: if prices
encode what attributes are worth, then with enough transactions we can run the
inference backwards and read off the market's implicit valuation of each
attribute. That backwards inference is what a **hedonic model** is.

This already tells us what could go wrong. We are reconstructing an aggregate of
human judgment that is itself fallible, local, and time-bound, and any number we
recover inherits those limitations. Keeping that in view is what stops us from
mistaking a fitted coefficient for a law of nature.

---

## 2. The conjecture: price decomposes into the worth of its parts

The hedonic move is a conjecture about the world: that the price of a complex,
heterogeneous good can be written, to a useful approximation, as the **sum of
what the market pays for each of its measurable attributes**. Living area,
location, age, condition — each contributes; the price is their accumulation.

This is a substantive claim, and it can fail. An attribute is only valuable when
the market pays for it, not when the spreadsheet labels it an amenity: a
six-figure kitchen renovation routinely returns a fraction of its cost, and
leased rooftop solar can lower a sale price as easily as lift it. What an
attribute is worth is an empirical fact the market settles, and the market can
contradict the listing — paying nothing for a prized feature, or paying most of a
home's premium for something no spreadsheet records, like the afternoon light or
the character of the neighbors. The conjecture earns its keep only to the degree
that, tested, it predicts prices it has not seen. When it does, we have learned
something real about how this market values things; when it fails, the failure
points at what we missed.

Notice the shape of the reasoning. We do not "let the data speak." Data never
speak; they answer questions, and the questions come from conjectures. The
hedonic decomposition is the conjecture. Everything downstream is an attempt to
expose it to refutation.

---

## 3. Why model the logarithm of price — the claim inside the transform

Prices in this data are right-skewed: most homes cluster low, a few run very
high. The standard response — model `log(price)` instead of `price` — is usually
presented as a statistical fix for skew. That undersells it. The log transform is
a **claim about the generating process**: that attributes act on price
*multiplicatively*. An extra hundred square feet is worth proportionally more on
an expensive home than on a cheap one, because value scales.

Read this way, the skew is the signature of a multiplicative process. Logging is
the hypothesis that recovers additivity by working in the right coordinates, and
the hypothesis is testable: if effects really were additive in dollars, the log
model would fit worse and its residuals would betray it. They don't — a small
corroboration that the multiplicative account is the better explanation. The
transform is hard-to-vary in the good sense: what we believe about how value
composes forces it.

---

## 4. The most instructive error: deleting the expensive houses

The original 2019 version of this analysis "cleaned" the data by removing any
sale more than 1.5 standard deviations from the mean. The reported error fell
from a realistic **$24,317** to an impressive-looking **$16,720**. The impressive
number was an artifact: the deletion had thrown out 26% of the homes, including
*every* sale above $179,000 (the true maximum is $347,000).

This deserves to be dwelt on, because it is a perfect specimen of how a method
lies when its explanation goes unexamined. The procedure "remove outliers"
*sounds* like cleaning. But an outlier in the **response variable** is the hard
case the model exists to handle. Deleting it does not clean the phenomenon; it
*quietly replaces the phenomenon* with an easier one (cheap homes only) and then
reports success on the substitute. The mistake lives in the concept of "outlier"
— a wrong account of the word, never checked against what the model is *for*.

The repair is to keep every observation and flag the influential points (Cook's
distance) for inspection. The general lesson is Popperian to its core: a method
that makes your error go away should be the first thing you distrust, because the
easiest way to be right is to stop testing.

---

## 5. Out-of-sample testing is conjecture and refutation, mechanized

In-sample error — how well a model fits the data it was trained on — is almost
worthless, and for a principled reason: a flexible enough model can fit *any*
training set perfectly, including its noise. A claim that cannot fail is not a
claim. Fitting your own data and admiring the fit is the statistical form of
confirmation bias.

Cross-validation is the corrective, and it is exactly Popper's method in
operational dress. Hide some of the data. Build the explanation on the rest. Then
make a **risky prediction** about the part it never saw, and check. A model that
has merely memorized is exposed here; a model that has captured something real
about how attributes drive price survives. Every headline error number in this
repository is out-of-sample for this reason. Prediction of the unseen is the
decisive empirical test of an explanation that has survived criticism, and a
method that refuses the test forfeits its claim to know anything. (It is not the
only test — most bad explanations are killed by criticism before any data arrive,
as Section 6 will show — but among explanations still standing, it is the one the
world administers.)

---

## 6. What is hard to vary, and why that is the measure of the model

Deutsch's criterion for a good explanation is that it is **hard to vary** while
still accounting for what it explains: its parts are pinned down by the problem,
so you cannot tweak them freely without breaking the fit to reality. It is worth
asking where this model is hard to vary and where it is loose, because that is
where its real content lives.

- The coefficient on living area is pinned. Change it appreciably and you
  contradict thousands of transactions at once. That rigidity is the model
  earning its claim.
- The choice to model log-price is hard to vary, as argued above — forced by the
  multiplicative structure.
- The *list of features* is comparatively loose: we could include others, and on
  the small UFFI set we had no location at all. Flagging that looseness is honest,
  because it marks where the explanation is least constrained and most fallible.

A model is strong exactly where reality has left it no room to wiggle. Reporting
which parts those are — and which parts remain free — is more useful than any
single accuracy figure, because it tells you where the explanation can still be
wrong.

---

## 7. The mispricing thesis is an omitted-variable claim — and the ~0 is a test

Now the part that matters for commercial real estate, and the cleanest piece of
Popper in the whole project. The thesis behind a defense-leased platform is that
the broad market prices a mission-critical, prime-defense-leased asset as
*generic credit tenancy* — that the market's own hedonic explanation of price
**omits a variable**: the durability of procurement-backed cash flows.

It is a falsifiable hypothesis, and the model tests it directly. Fit the hedonic
model on transaction prices, include the defense-lease attribute, and look at its
coefficient:

- If the market *were* paying for that attribute, the coefficient would be large
  and statistically distinguishable from zero. The "market ignores it" thesis
  would be **refuted**.
- In the (simulated) demonstration here, the coefficient lands at **−0.4%, not
  significant (p ≈ 0.34)** — indistinguishable from zero. The thesis is
  **corroborated**: on this evidence, the market is not pricing the attribute.

The entire epistemic value of the result lies in the fact that *it could have come
out the other way*. A test the thesis cannot fail is no test. Here it could fail —
a significant coefficient would sink it — and it didn't, which is what makes the
~0 informative. (In the simulation the result is true by construction, which is
the point: it shows the estimator correctly *finds* the omission when the omission
is real. On a true comparable set the same test runs for real, and could genuinely
refute the thesis.)

The capturable spread then follows from a *separate* conjecture — that the omitted
attribute is worth a cap-rate compression of some size — which we refuse to assert
as a single number because it is the weakest link. We expose it instead as a
sensitivity across 25–125 bps. Stating an assumption and showing how the
conclusion moves with it is error-correction made visible: it hands the reader the
lever to disagree, which is exactly what a good argument should do.

---

## 8. Why the "best model" changed when the data grew — complexity is earned

On 99 UFFI homes, regularized linear regression (Ridge) wins and tree ensembles
overfit. On 21,613 real King County sales, the ranking *reverses*: Random Forest
wins decisively (R² 0.88) and the linear models trail. The same code, the
opposite conclusion. This reversal is one of the most important things the
project has to teach.

A flexible model can represent a richer explanation — curves, interactions,
location effects that bend and cross. Richness is only warranted to the extent
that reality *constrains* it. With 99 data points, a flexible model has enough
freedom to fit the noise: it invents structure that isn't there, an explanation
easy to vary and therefore worthless. With 21,000 points, the data pin that
richer structure down, and the flexible model's extra expressiveness now tracks
real patterns — above all, that price is largely a function of *where*.

The right complexity of an explanation is whatever the world's constraints will
support. Cross-validation lets the world decide. Choosing the simpler model on
small data and the richer one on large data obeys that principle.

A caution is owed here, because the winning forest sits uncomfortably close to the
explanationless oracle this whole document argues against: predictively superior,
explanatorily opaque. You cannot read a hard-to-vary claim about how value
composes out of five hundred trees. Two observations keep the result from
collapsing into instrumentalism.

First, the forest's victory is itself a *phenomenon demanding explanation*. What
it revealed is that the hedonic conjecture, as specified, omits spatial structure
— price is largely a function of *where*, and a model free to bend around latitude
and longitude exploits what the linear specification cannot express. The forest is
the instrument that exposed the omission; the work now is to repair the conjecture
— the spatially explicit model Section 9 names as the open problem.

Second, for the commercial thesis of Section 7, the linear hedonic model is doing
the epistemic work regardless. The omitted-variable test is a claim about a
coefficient — about explanatory structure — and a Random Forest could not even
have expressed it. The "best model by RMSE" and the "model that carries the
explanation" are legitimately different objects, and confusing them is the
instrumentalist mistake: taking predictive accuracy for the content of the
knowledge.

---

## 9. Where the explanation is weak — the frontier, stated as problems

In this view the limitations are the most interesting part: each marks a place the
explanation could be improved.

- **The UFFI set is small (n=99) and had no geography.** The King County module
  exists *because* of this gap, and shows location to be the dominant driver.
  The open problem it leaves: a properly spatial model (coordinates, or submarket
  structure) would almost certainly improve on a model that treats latitude as
  just another column.
- **Coefficients are local and dated.** They do not transfer between markets or
  years. The method transfers; the numbers are an instance, not a law.
- **The commercial book is simulated.** It demonstrates the mechanism and lets us
  check the estimator against a known truth; it is not evidence about any real
  market. The next step is the same test on real comparable sales — where it
  could, and should be allowed to, fail.
- **The cap-rate overlay is an assumption, not a measurement.** Its size is the
  weakest link, and the sensitivity analysis admits it.

Each of these is a conjecture-shaped hole: a place where a better explanation, or
better data, would let the method find an error it currently cannot.

---

## 10. Reach — why the same explanation travels

A mark of a good explanation, Deutsch argues, is **reach**: it explains more than
it was built for. The hedonic account has reach. It was built on houses, but it
does not know or care that the asset is a house. Anywhere value is set as a bundle
of measurable attributes priced by a market — used vehicles, equipment, insured
property, commercial rents, land — the same decomposition applies, the same
multiplicative structure tends to hold, and the same omitted-variable test can ask
whether the market is pricing some attribute it shouldn't be ignoring.

That reach is evidence that the explanation has hold of something general about
how markets price heterogeneous things — the surest sign it is worth improving.

---

*Companion explainers: [credit-risk-underwriting](https://github.com/PeterJemley/credit-risk-underwriting)
(why default is predictable and why accuracy is the wrong goal) and
[geospatial-market-analytics](https://github.com/PeterJemley/geospatial-market-analytics)
(why activity concentrates in space and time). The methodology, with the numbers,
is in [`methodology.md`](methodology.md).*
