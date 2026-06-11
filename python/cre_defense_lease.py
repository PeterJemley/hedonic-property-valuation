"""
cre_defense_lease.py
====================

A commercial-real-estate extension of the hedonic engine in `uffi_pipeline.py`,
built to demonstrate one specific underwriting thesis:

    The broad market prices a net-leased asset on *generic credit tenancy* —
    building quality, location, lease term, and tenant credit. When the tenant
    is a prime defense contractor in a *mission-critical* facility, that asset
    carries durability the generic frame misses (procurement-backed cash flows,
    high relocation cost, sticky renewals). If the market does not price that
    attribute, the asset is systematically mispriced, and the gap is capturable
    at acquisition.

This is the **same problem** as the UFFI study, with the sign flipped: there, a
binary attribute the market *discounts*; here, a binary attribute the market
*ignores*. The same hedonic estimator measures both.

------------------------------------------------------------------------------
IMPORTANT — this module uses a TRANSPARENT SIMULATION, not real transactions.
A seeded generator produces a synthetic book of net-leased CRE deals whose
prices reflect generic credit-tenancy pricing (the defense attribute is
deliberately NOT priced into them). We then show two things:

    1.  A hedonic model fit on those prices recovers a defense coefficient of
        ~0 and statistically insignificant — i.e. it *detects* that the market
        priced these as generic credit tenancy. (With real comparable sales you
        would run exactly this test; a ~0 coefficient is what validates the
        thesis.)
    2.  An underwriting overlay (a cap-rate compression justified by defense
        infrastructure characteristics) translates that omitted attribute into a
        per-SF value uplift, with a sensitivity analysis over the assumption.

Because the effect is injected by construction, this also serves as a recovery
check: the estimator returns ~0 on prices that contain no defense premium, and
the overlay quantifies the spread the thesis claims. Real diligence (FAR/DFARS,
contract-vehicle exposure, option-year structure) would set the overlay; here it
is an explicit, sensitivity-tested parameter.
------------------------------------------------------------------------------
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from uffi_pipeline import HedonicConfig, fit_interpretable, coefficient_effects


# The same HedonicConfig abstraction the housing model uses — one new config,
# same engine. Target is price per square foot; the defense flag is included so
# we can test whether the market paid for it.
CRE_CONFIG = HedonicConfig(
    name="Net-leased CRE (industrial / office)",
    target="price_psf",
    features=[
        "building_sf", "age_years", "submarket_index", "walt_years",
        "tenant_credit", "industrial", "mission_critical_defense",
    ],
    log_target=True,
    currency="$",
)


def simulate_market(n: int = 400, seed: int = 7) -> pd.DataFrame:
    """Generate a synthetic book of net-leased CRE transactions.

    Prices are built from generic credit-tenancy economics (NOI capitalised at a
    market cap rate that responds to tenant credit, lease term, age, and
    submarket). The ``mission_critical_defense`` flag is intentionally absent
    from the price mechanism, so any coefficient a model later assigns it should
    be ~0 — that is the whole point of the demonstration.
    """
    rng = np.random.default_rng(seed)

    industrial = rng.binomial(1, 0.6, n)                  # 1 = industrial, 0 = office
    building_sf = rng.uniform(20_000, 500_000, n)
    age_years = rng.uniform(0, 50, n)
    submarket_index = rng.uniform(0.85, 1.25, n)          # location desirability
    walt_years = rng.uniform(1, 15, n)                    # weighted avg lease term remaining
    tenant_credit = rng.integers(1, 6, n)                 # 1 = weak ... 5 = investment grade
    mission_critical_defense = rng.binomial(1, 0.25, n)   # prime-defense, mission-critical

    # Rent psf: industrial lower base than office; better submarket and newer
    # buildings rent higher.
    base_rent = np.where(industrial == 1, 8.0, 28.0)
    rent_psf = base_rent * submarket_index * (1 - 0.004 * age_years) \
        * rng.normal(1.0, 0.05, n)
    noi_psf = rent_psf * rng.uniform(0.60, 0.70, n)       # NOI margin

    # Generic-market cap rate: compresses for stronger credit, longer WALT, and
    # better submarket; widens with age. NOTE: no defense term here.
    market_cap = (0.075
                  - 0.0030 * (tenant_credit - 3)
                  - 0.0010 * (walt_years - 7)
                  - 0.0200 * (submarket_index - 1.0)
                  + 0.0005 * age_years)
    market_cap = np.clip(market_cap, 0.045, 0.10)

    market_value_psf = noi_psf / market_cap
    price_psf = market_value_psf * rng.normal(1.0, 0.06, n)   # transaction noise

    return pd.DataFrame(dict(
        building_sf=building_sf, age_years=age_years,
        submarket_index=submarket_index, walt_years=walt_years,
        tenant_credit=tenant_credit, industrial=industrial,
        mission_critical_defense=mission_critical_defense,
        noi_psf=noi_psf, market_cap=market_cap, price_psf=price_psf,
    ))


def market_prices_defense(df: pd.DataFrame) -> pd.DataFrame:
    """Fit the hedonic model on transaction prices and report what the market
    paid for each attribute — in particular, whether it paid for the defense
    flag at all.
    """
    fit = fit_interpretable(df, CRE_CONFIG)
    eff = coefficient_effects(fit, CRE_CONFIG).query("term != 'const'").copy()
    eff["sd"] = [df[t].std() for t in eff.term]
    eff["pct_per_sd"] = (np.exp(eff.coef * eff.sd) - 1) * 100
    return eff[["term", "coef", "p_value", "pct_per_sd"]].reset_index(drop=True)


def underwrite_overlay(df: pd.DataFrame, compression_bps: float = 75.0) -> pd.DataFrame:
    """Apply Seastone's defense-infrastructure overlay to mission-critical assets.

    The overlay compresses the cap rate by ``compression_bps`` basis points for
    mission-critical defense facilities — the analyst's underwriting judgment,
    grounded in procurement-backed cash-flow durability and relocation cost. The
    captured spread is the underwritten value minus the price actually paid.
    """
    comp = compression_bps / 10_000.0
    is_def = df.mission_critical_defense == 1
    underwrite_cap = df.market_cap - np.where(is_def, comp, 0.0)
    underwrite_value_psf = df.noi_psf / underwrite_cap
    captured_psf = underwrite_value_psf - df.price_psf
    out = df.copy()
    out["underwrite_value_psf"] = underwrite_value_psf
    out["captured_psf"] = captured_psf
    out["captured_pct"] = captured_psf / df.price_psf * 100
    return out


def sensitivity(df: pd.DataFrame, grid=(25, 50, 75, 100, 125)) -> pd.DataFrame:
    """Capturable spread on the defense subset across overlay assumptions."""
    rows = []
    deff = df[df.mission_critical_defense == 1]
    for bps in grid:
        u = underwrite_overlay(df, bps)
        ud = u[u.mission_critical_defense == 1]
        rows.append({
            "compression_bps": bps,
            "avg_captured_pct": ud.captured_pct.mean(),
            "avg_captured_psf": ud.captured_psf.mean(),
            # Portfolio illustration: 1.0M SF acquired across the defense subset.
            "capture_on_1M_sf": ud.captured_psf.mean() * 1_000_000,
        })
    return pd.DataFrame(rows)


def run_report(n: int = 400, seed: int = 7) -> dict:
    df = simulate_market(n, seed)
    n_def = int(df.mission_critical_defense.sum())
    print(f"=== {CRE_CONFIG.name} (SIMULATED, n={len(df)}) ===")
    print(f"mission-critical defense assets: {n_def}\n")

    print("What the market paid for (hedonic on transaction prices):")
    eff = market_prices_defense(df)
    for _, r in eff.iterrows():
        sig = "significant" if r.p_value < 0.05 else "NOT significant"
        print(f"  {r.term:26} {r.pct_per_sd:+6.1f}% / SD   p={r.p_value:.3f}  ({sig})")
    def_row = eff.loc[eff.term == "mission_critical_defense"].iloc[0]
    print(f"\n  -> Market pays {def_row.pct_per_sd:+.1f}% for the defense attribute "
          f"(p={def_row.p_value:.2f}): priced as generic credit tenancy.\n")

    print("Captured spread under the defense-infrastructure overlay:")
    s = sensitivity(df)
    for _, r in s.iterrows():
        print(f"  {int(r.compression_bps):3d} bps compression -> "
              f"{r.avg_captured_pct:5.1f}% uplift  "
              f"(${r.avg_captured_psf:6.2f}/SF, "
              f"${r.capture_on_1M_sf/1e6:5.2f}M per 1.0M SF)")
    return {"df": df, "effects": eff, "sensitivity": s}


if __name__ == "__main__":
    run_report()
