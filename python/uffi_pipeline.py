"""
hedonic_pipeline.py
===================

A small, dataset-agnostic **hedonic pricing** pipeline.

A hedonic model explains the price of a heterogeneous asset as the sum of the
values the market places on each of its measurable characteristics. For a
house: location, living area, lot size, age, condition, and (here) the presence
of urea-formaldehyde foam insulation (UFFI). The same idea underpins valuation
in many commerce areas -- used vehicles, used equipment, insured property,
and the rent/price of a commercial building -- so the code below is written
around a generic ``HedonicConfig`` rather than anything UFFI-specific.

The pipeline does four things, in order:

    1.  Load and clean a tabular dataset.
    2.  Fit and HONESTLY evaluate several candidate models (k-fold
        cross-validation -- never in-sample residuals).
    3.  Report the marginal value of each characteristic with a defensible
        statistical interval.
    4.  Produce a point estimate AND a correct prediction interval for a new,
        unseen asset.

Design choices worth calling out (each avoids a common pitfall in applied price
modelling; see ../docs/methodology.md):

    *   The skewed price target is modelled on the LOG scale, so coefficients
        read as approximate percentage effects and the error variance is stable.
    *   Influential rows are FLAGGED (Cook's distance), never deleted. Deleting
        extreme prices is the single most common way to fake a good RMSE.
    *   Every headline error number is OUT-OF-SAMPLE (10-fold CV).
    *   Prediction intervals come from ``statsmodels.get_prediction`` so they
        propagate both residual noise and coefficient-estimation uncertainty.

Requires: numpy, pandas, scikit-learn, statsmodels, matplotlib, openpyxl.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression, RidgeCV, LassoCV, ElasticNetCV
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import KFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


# ---------------------------------------------------------------------------
# Configuration: everything that changes between datasets lives here, so the
# pipeline body never has to be edited to point it at a new commerce domain.
# ---------------------------------------------------------------------------
@dataclass
class HedonicConfig:
    """Describes one dataset to the pipeline.

    Attributes
    ----------
    name:        Human label used in printouts and figure titles.
    target:      Column holding the price/value to be explained.
    features:    Predictor columns the model is allowed to use.
    log_target:  Model log(price) instead of price. Strongly recommended when
                 the target is right-skewed (skew > ~1), which prices usually
                 are.
    rename:      Optional {raw_column: clean_name} map applied right after load.
    drop:        Columns to discard before modelling (IDs, leakage, etc.).
    currency:    Symbol used only for pretty-printing.
    """

    name: str
    target: str
    features: list[str]
    log_target: bool = True
    rename: dict[str, str] = field(default_factory=dict)
    drop: list[str] = field(default_factory=list)
    currency: str = "$"


# The concrete configuration for the UFFI housing dataset. To reuse the pipeline
# on, say, a used-vehicle price file, you would write a second HedonicConfig and
# change nothing else.
UFFI_CONFIG = HedonicConfig(
    name="UFFI residential sales",
    target="sale_price",
    features=[
        "uffi_in", "brick_ext", "age_45plus", "basement_sf", "lot_area",
        "park_spaces", "living_area", "central_air", "pool", "year_sold",
    ],
    log_target=True,
    rename={
        "Observation": "observation", "Year Sold": "year_sold",
        "Sale Price": "sale_price", "UFFI IN": "uffi_in",
        "Brick Ext": "brick_ext", "45 Yrs+": "age_45plus",
        "Bsmnt Fin_SF": "basement_sf", "Lot Area": "lot_area",
        "Enc Pk Spaces": "park_spaces", "Living Area_SF": "living_area",
        "Central Air": "central_air", "Pool": "pool",
    },
    drop=["observation"],
)


# ---------------------------------------------------------------------------
# 1. Load & clean
# ---------------------------------------------------------------------------
def load_data(path: str | Path, cfg: HedonicConfig) -> pd.DataFrame:
    """Read an .xlsx/.csv file, apply the config's renames, and drop blank rows.

    We deliberately do NOT remove outliers here -- see ``flag_influence``.
    """
    path = Path(path)
    raw = pd.read_excel(path) if path.suffix in {".xlsx", ".xls"} else pd.read_csv(path)
    df = raw.rename(columns=cfg.rename)
    # Drop fully-blank trailing rows that spreadsheets often carry.
    df = df.dropna(how="all").dropna(subset=[cfg.target]).reset_index(drop=True)
    return df.drop(columns=[c for c in cfg.drop if c in df.columns])


# ---------------------------------------------------------------------------
# 2. Influence diagnostics -- flag, never amputate
# ---------------------------------------------------------------------------
def flag_influence(df: pd.DataFrame, cfg: HedonicConfig) -> np.ndarray:
    """Return a boolean mask of high-influence rows via Cook's distance.

    The classic 4/n threshold is used. These rows are reported to the analyst
    but kept in the model -- an unusually expensive asset is signal, not noise.
    """
    y = np.log(df[cfg.target]) if cfg.log_target else df[cfg.target]
    X = sm.add_constant(df[cfg.features])
    fit = sm.OLS(y, X).fit()
    cooks = fit.get_influence().cooks_distance[0]
    return cooks > (4 / len(df))


# ---------------------------------------------------------------------------
# 3. Honest evaluation -- 10-fold CV, error reported in original price units
# ---------------------------------------------------------------------------
def _cv_rmse(model, X: np.ndarray, y: np.ndarray, log: bool, seed: int = 42):
    """Out-of-sample RMSE and R^2 via 10-fold CV, always back on price units."""
    kf = KFold(n_splits=10, shuffle=True, random_state=seed)
    pred = np.zeros(len(y))
    for tr, te in kf.split(X):
        if log:
            model.fit(X[tr], np.log(y[tr]))
            pred[te] = np.exp(model.predict(X[te]))
        else:
            model.fit(X[tr], y[tr])
            pred[te] = model.predict(X[te])
    return np.sqrt(mean_squared_error(y, pred)), r2_score(y, pred)


def compare_models(df: pd.DataFrame, cfg: HedonicConfig) -> pd.DataFrame:
    """Cross-validate a slate of models and return a tidy leaderboard.

    On a small dataset (n~100) regularised linear models typically beat tree
    ensembles; we include both so the comparison is honest rather than assumed.
    """
    X = df[cfg.features].to_numpy(dtype=float)
    y = df[cfg.target].to_numpy(dtype=float)
    log = cfg.log_target

    candidates = {
        "OLS": make_pipeline(StandardScaler(), LinearRegression()),
        "Ridge": make_pipeline(StandardScaler(), RidgeCV(alphas=np.logspace(-3, 3, 50))),
        "Lasso": make_pipeline(StandardScaler(), LassoCV(cv=5, max_iter=50_000)),
        "ElasticNet": make_pipeline(StandardScaler(), ElasticNetCV(cv=5, max_iter=50_000)),
        "RandomForest": RandomForestRegressor(n_estimators=400, random_state=0),
        "GradientBoosting": GradientBoostingRegressor(
            n_estimators=300, max_depth=2, learning_rate=0.05, random_state=0),
    }
    rows = []
    for label, model in candidates.items():
        rmse, r2 = _cv_rmse(model, X, y, log)
        rows.append({"model": label, "cv_rmse": rmse, "cv_r2": r2})
    return pd.DataFrame(rows).sort_values("cv_rmse").reset_index(drop=True)


# ---------------------------------------------------------------------------
# 4. Interpretable fit + correct prediction interval
# ---------------------------------------------------------------------------
def fit_interpretable(df: pd.DataFrame, cfg: HedonicConfig):
    """Fit an OLS model we can read coefficients off of (statsmodels).

    Returns the fitted results object. Use ``.summary()`` for the full table or
    ``coefficient_effects`` below for a tidy view.
    """
    y = np.log(df[cfg.target]) if cfg.log_target else df[cfg.target]
    X = sm.add_constant(df[cfg.features])
    return sm.OLS(y, X).fit()


def coefficient_effects(fit, cfg: HedonicConfig) -> pd.DataFrame:
    """Tidy table of each characteristic's marginal effect.

    For a log target, ``pct_effect`` is the approximate % change in price for a
    one-unit increase in the characteristic (exp(beta) - 1).
    """
    out = pd.DataFrame({
        "term": fit.params.index,
        "coef": fit.params.values,
        "p_value": fit.pvalues.values,
    })
    if cfg.log_target:
        out["pct_effect"] = (np.exp(out["coef"]) - 1) * 100
    return out


def predict_with_interval(df: pd.DataFrame, cfg: HedonicConfig,
                          scenario: dict, alpha: float = 0.05) -> dict:
    """Point estimate and a CORRECT prediction interval for one new asset.

    We fit on the RAW price scale here so the returned interval is already in
    dollars and needs no back-transform bias correction. ``get_prediction``
    propagates residual variance and coefficient uncertainty -- unlike the
    ``point +/- 1.96 * residual_SE`` shortcut, which understates the spread.
    """
    fit = sm.OLS(df[cfg.target], sm.add_constant(df[cfg.features])).fit()
    row = {"const": 1.0, **{f: scenario.get(f, df[f].median()) for f in cfg.features}}
    Xnew = pd.DataFrame([row])[["const"] + cfg.features]
    pr = fit.get_prediction(Xnew).summary_frame(alpha=alpha)
    return {
        "point": float(pr["mean"].iloc[0]),
        "lower": float(pr["obs_ci_lower"].iloc[0]),
        "upper": float(pr["obs_ci_upper"].iloc[0]),
        "level": 1 - alpha,
    }


# ---------------------------------------------------------------------------
# Convenience: run the whole UFFI analysis and print a report.
# ---------------------------------------------------------------------------
def run_uffi_report(data_path: str | Path) -> dict:
    cfg = UFFI_CONFIG
    df = load_data(data_path, cfg)
    infl = flag_influence(df, cfg)

    print(f"=== {cfg.name} ===")
    print(f"rows: {len(df)}   features: {len(cfg.features)}")
    print(f"target skew (raw): {df[cfg.target].skew():.2f}  "
          f"(log): {np.log(df[cfg.target]).skew():.2f}")
    print(f"influential rows flagged (kept): {int(infl.sum())}\n")

    board = compare_models(df, cfg)
    print("Model leaderboard (10-fold CV, error in dollars):")
    for _, r in board.iterrows():
        print(f"  {r['model']:18} RMSE {cfg.currency}{r['cv_rmse']:>9,.0f}   R2 {r['cv_r2']:.3f}")

    fit = fit_interpretable(df, cfg)
    eff = coefficient_effects(fit, cfg)
    uffi = eff.loc[eff.term == "uffi_in"].iloc[0]
    print(f"\nUFFI marginal effect: {uffi['pct_effect']:+.1f}% of value "
          f"(p = {uffi['p_value']:.3f})")

    # Practicum scenario: older home, no finished basement, wood exterior, UFFI.
    scenario = dict(uffi_in=1, brick_ext=0, age_45plus=1, basement_sf=0,
                    lot_area=7800, park_spaces=1, living_area=1720,
                    central_air=0, pool=0)
    pi = predict_with_interval(df, cfg, scenario)
    print(f"\nScenario prediction: {cfg.currency}{pi['point']:,.0f}  "
          f"({int(pi['level']*100)}% PI {cfg.currency}{pi['lower']:,.0f}"
          f" - {cfg.currency}{pi['upper']:,.0f})")
    return {"df": df, "board": board, "fit": fit, "effects": eff, "scenario_pi": pi}


if __name__ == "__main__":
    import sys
    default = Path(__file__).resolve().parents[1] / "data" / "uffidata.xlsx"
    run_uffi_report(sys.argv[1] if len(sys.argv) > 1 else default)
