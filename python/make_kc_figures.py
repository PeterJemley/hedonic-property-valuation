"""
make_kc_figures.py
=================

Regenerates the King County figures (11, 12, 13). Runs the full 10-fold model
comparison on 21,613 sales once, so allow a few minutes:

    python python/make_kc_figures.py
"""

import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

warnings.filterwarnings("ignore", category=RuntimeWarning)

from kingcounty_valuation import KC_CONFIG, load_kc
from uffi_pipeline import compare_models, fit_interpretable, coefficient_effects

FIG = Path(__file__).resolve().parents[1] / "figures"
DATA = Path(__file__).resolve().parents[1] / "data" / "kc_house_data.csv"
cfg = KC_CONFIG
df = load_kc(DATA)
plt.rcParams.update({"figure.dpi": 120, "font.size": 10, "axes.grid": True,
                     "grid.alpha": 0.3})
NAVY, RUST = "#1f3a5f", "#c1440e"


def save(fig, name):
    fig.tight_layout(); fig.savefig(FIG / name, bbox_inches="tight"); plt.close(fig)
    print("wrote", name)


# 11 -- Leaderboard: with 21k sales the ranking flips vs. the 99-home study.
print("running 10-fold model comparison on 21,613 sales (a few minutes)...")
board = compare_models(df, cfg)
fig, ax = plt.subplots(figsize=(6.8, 3.8))
colors = [RUST if m == board.iloc[0].model else NAVY for m in board.model]
ax.barh(board.model, board.cv_rmse, color=colors); ax.invert_yaxis()
for y, v in enumerate(board.cv_rmse):
    ax.text(v, y, f" ${v/1000:,.0f}k", va="center", fontsize=9)
ax.set(xlabel="10-fold CV RMSE ($) — lower is better",
       title="King County (n=21,613): with enough data, tree ensembles win\n"
             "(the reverse of the 99-home result — that is bias–variance)")
save(fig, "11_kc_leaderboard.png")

# 12 -- Strongest drivers per SD: location (lat) leads.
fit = fit_interpretable(df, cfg)
eff = coefficient_effects(fit, cfg).query("term != 'const'").copy()
eff["sd"] = [df[t].std() for t in eff.term]
eff["pct_per_sd"] = (np.exp(eff.coef * eff.sd) - 1) * 100
eff = eff.set_index("term")
spatial = {"lat", "long"}
order = eff.pct_per_sd.abs().sort_values().index
colors = [RUST if t in spatial else NAVY for t in order]
fig, ax = plt.subplots(figsize=(6.8, 4.6))
ax.barh(order, eff.loc[order, "pct_per_sd"], color=colors)
ax.axvline(0, color="black", lw=0.8)
ax.set(xlabel="Approx. % effect on price per +1 SD",
       title="What drives King County prices (rust = location)\n"
             "latitude is the single strongest driver")
save(fig, "12_kc_drivers.png")

# 13 -- The map: plotting each sale at its lat/long, colored by price, draws
# King County and shows price is overwhelmingly a function of WHERE.
fig, ax = plt.subplots(figsize=(6.2, 6.0))
sc = ax.scatter(df.long, df.lat, c=np.log(df.price), cmap="viridis",
                s=4, alpha=0.5)
cb = fig.colorbar(sc, fraction=0.046, pad=0.04); cb.set_label("log(price)")
ax.set(xlabel="Longitude", ylabel="Latitude",
       title="Price is a map: King County sales by location\n"
             "(Seattle / Bellevue / waterfront command the premium)")
ax.set_aspect("equal", adjustable="datalim")
save(fig, "13_kc_price_map.png")

print("\nKing County figures regenerated.")
