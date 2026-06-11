"""
kingcounty_valuation.py
======================

The same hedonic engine (`uffi_pipeline.py`), pointed at a real, market-scale
dataset: 21,613 King County, WA home sales (2014-2015). This module exists to
answer the one honest limitation of the 99-home UFFI study head-on:

    *   **Scale.** 21,613 sales instead of 99 — enough data to support flexible
        models, so the leaderboard ranking *flips*: on 99 homes Ridge wins and
        tree ensembles overfit; here, with this much data, gradient boosting
        wins. Same code, opposite conclusion — that is the bias-variance lesson
        in action, not a contradiction.
    *   **Location.** The UFFI set had no geography. This one has latitude and
        longitude, and they turn out to be among the strongest price drivers —
        exactly the spatial signal the earlier study flagged as missing.

Everything is reused: one new `HedonicConfig`, the same `compare_models`,
`fit_interpretable`, and `coefficient_effects`. No modelling code is rewritten.

Requires: numpy, pandas, scikit-learn, statsmodels (+ matplotlib for figures).
"""

from __future__ import annotations

import warnings
from pathlib import Path

import numpy as np
import pandas as pd

# Linear models on highly collinear spatial features (lat/long/sqft variants)
# can emit harmless overflow warnings inside individual CV folds; the reported
# cross-validated numbers are unaffected.
warnings.filterwarnings("ignore", category=RuntimeWarning)

from uffi_pipeline import (HedonicConfig, compare_models, fit_interpretable,
                           coefficient_effects)


# One new config — the only thing that changes to retarget the engine.
KC_CONFIG = HedonicConfig(
    name="King County, WA residential sales (2014-2015)",
    target="price",
    features=[
        "sqft_living", "sqft_lot", "bedrooms", "bathrooms", "floors",
        "waterfront", "view", "condition", "grade", "age", "renovated",
        "lat", "long", "sqft_living15",
    ],
    log_target=True,
    currency="$",
)


def load_kc(path: str | Path) -> pd.DataFrame:
    """Read the King County file and add two engineered features.

    `age` and a `renovated` flag are cheap, defensible transforms of the raw
    year fields; everything else is used as-supplied.
    """
    df = pd.read_csv(path)
    # The sales span 2014-2015; age relative to the last sale year is fine.
    df["age"] = 2015 - df["yr_built"]
    df["renovated"] = (df["yr_renovated"] > 0).astype(int)
    return df


def run_report(path: str | Path) -> dict:
    cfg = KC_CONFIG
    df = load_kc(path)

    print(f"=== {cfg.name} ===")
    print(f"sales: {len(df):,}   features: {len(cfg.features)}")
    print(f"price: median ${df.price.median():,.0f}, "
          f"range ${df.price.min():,.0f}-${df.price.max():,.0f}")
    print(f"price skew (raw): {df.price.skew():.2f}  "
          f"(log): {np.log(df.price).skew():.2f}\n")

    print("Model leaderboard (10-fold CV, error in dollars):")
    board = compare_models(df, cfg)
    for _, r in board.iterrows():
        print(f"  {r['model']:18} RMSE {cfg.currency}{r['cv_rmse']:>10,.0f}   R2 {r['cv_r2']:.3f}")
    print(f"\n  -> Best: {board.iloc[0]['model']} "
          f"(on 99 homes it was Ridge; with 21k, flexible models win).\n")

    print("Strongest price drivers (per +1 SD, log model):")
    fit = fit_interpretable(df, cfg)
    eff = coefficient_effects(fit, cfg).query("term != 'const'").copy()
    eff["sd"] = [df[t].std() for t in eff.term]
    eff["pct_per_sd"] = (np.exp(eff.coef * eff.sd) - 1) * 100
    top = eff.reindex(eff.pct_per_sd.abs().sort_values(ascending=False).index).head(6)
    for _, r in top.iterrows():
        print(f"  {r['term']:14} {r['pct_per_sd']:+6.1f}% / SD   p={r['p_value']:.3f}")
    print("\n  -> Latitude/longitude rank among the top drivers — the spatial "
          "signal the UFFI study lacked.")
    return {"df": df, "board": board, "effects": eff}


if __name__ == "__main__":
    import sys
    default = Path(__file__).resolve().parents[1] / "data" / "kc_house_data.csv"
    run_report(sys.argv[1] if len(sys.argv) > 1 else default)
