"""
make_figures.py
===============

Regenerates every PNG in ../figures from the data. Run after any change to the
data or pipeline so the committed visualizations always match the numbers:

    python python/make_figures.py
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # headless: write files, never open a window
import matplotlib.pyplot as plt
import numpy as np
import statsmodels.api as sm

from uffi_pipeline import (UFFI_CONFIG, load_data, flag_influence,
                           compare_models, fit_interpretable)

FIG = Path(__file__).resolve().parents[1] / "figures"
FIG.mkdir(exist_ok=True)
DATA = Path(__file__).resolve().parents[1] / "data" / "uffidata.xlsx"
cfg = UFFI_CONFIG
df = load_data(DATA, cfg)
plt.rcParams.update({"figure.dpi": 120, "font.size": 10, "axes.grid": True,
                     "grid.alpha": 0.3})
NAVY, RUST = "#1f3a5f", "#c1440e"


def save(fig, name):
    fig.tight_layout()
    fig.savefig(FIG / name, bbox_inches="tight")
    plt.close(fig)
    print("wrote", name)


# 1 -- Why a log target: raw price is right-skewed, log price is near-symmetric.
fig, ax = plt.subplots(1, 2, figsize=(9, 3.6))
ax[0].hist(df.sale_price, bins=20, color=NAVY, alpha=0.85)
ax[0].set(title=f"Sale price (skew {df.sale_price.skew():.2f})", xlabel="$")
ax[1].hist(np.log(df.sale_price), bins=20, color=RUST, alpha=0.85)
ax[1].set(title=f"log(Sale price) (skew {np.log(df.sale_price).skew():.2f})",
          xlabel="log $")
fig.suptitle("Modelling log(price) stabilises the skew", fontweight="bold")
save(fig, "01_target_distribution.png")

# 2 -- The single strongest driver: living area vs price, UFFI homes marked.
fig, ax = plt.subplots(figsize=(6.2, 4.4))
for flag, color, lab in [(0, NAVY, "No UFFI"), (1, RUST, "UFFI present")]:
    s = df[df.uffi_in == flag]
    ax.scatter(s.living_area, s.sale_price, c=color, label=lab, alpha=0.8,
               edgecolor="white", s=42)
ax.set(xlabel="Living area (sq ft)", ylabel="Sale price ($)",
       title="Living area is the dominant price driver")
ax.legend()
save(fig, "02_living_area_vs_price.png")

# 3 -- Correlation heatmap of every numeric characteristic.
corr = df[[cfg.target] + cfg.features].corr()
fig, ax = plt.subplots(figsize=(6.8, 5.6))
im = ax.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1)
ax.set_xticks(range(len(corr))); ax.set_xticklabels(corr.columns, rotation=90)
ax.set_yticks(range(len(corr))); ax.set_yticklabels(corr.columns)
for i in range(len(corr)):
    for j in range(len(corr)):
        ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center",
                color="white" if abs(corr.iloc[i, j]) > 0.5 else "black", fontsize=7)
fig.colorbar(im, fraction=0.046, pad=0.04)
ax.set_title("Correlation matrix", fontweight="bold")
save(fig, "03_correlation_matrix.png")

# 4 -- Honest out-of-sample model leaderboard.
board = compare_models(df, cfg)
fig, ax = plt.subplots(figsize=(6.6, 3.8))
colors = [RUST if m == board.iloc[0].model else NAVY for m in board.model]
ax.barh(board.model, board.cv_rmse, color=colors)
ax.invert_yaxis()
for y, v in enumerate(board.cv_rmse):
    ax.text(v, y, f" ${v:,.0f}", va="center", fontsize=9)
ax.set(xlabel="10-fold CV RMSE ($)  -- lower is better",
       title="Out-of-sample error: regularised linear wins on n=99")
save(fig, "04_model_leaderboard.png")

# 5 -- Residual diagnostics for the interpretable model.
fit = fit_interpretable(df, cfg)
fitted, resid = fit.fittedvalues, fit.resid
fig, ax = plt.subplots(1, 2, figsize=(9, 3.6))
ax[0].scatter(fitted, resid, color=NAVY, alpha=0.7, edgecolor="white")
ax[0].axhline(0, color=RUST, lw=1)
ax[0].set(xlabel="Fitted (log $)", ylabel="Residual", title="Residuals vs fitted")
sm.qqplot(resid, line="s", ax=ax[1], markerfacecolor=NAVY, markeredgecolor=NAVY,
          alpha=0.7)
ax[1].set_title("Normal Q-Q")
fig.suptitle("Log model residuals are well-behaved", fontweight="bold")
save(fig, "05_residual_diagnostics.png")

# 6 -- Characteristic value as a % price effect of a ONE-STANDARD-DEVIATION
#       increase. Per-SD (not per-unit) puts a $/sq-ft variable and a 0/1 flag
#       on comparable footing, so living area reads as the driver it is rather
#       than looking near-zero just because one square foot is a tiny step.
eff = fit.params.drop("const")
pvals = fit.pvalues.drop("const")
sds = df[cfg.features].std()
pct = (np.exp(eff * sds) - 1) * 100          # % price change per +1 SD of x
order = pct.abs().sort_values().index
fig, ax = plt.subplots(figsize=(6.6, 4.4))
colors = [RUST if pvals[i] < 0.05 else "#9aa7b4" for i in order]
ax.barh(order, pct[order], color=colors)
ax.axvline(0, color="black", lw=0.8)
for y, k in enumerate(order):
    ax.text(pct[k], y, f" {pct[k]:+.0f}%", va="center",
            ha="left" if pct[k] >= 0 else "right", fontsize=8)
ax.set(xlabel="Approx. % effect on price per +1 standard deviation",
       title="What the market pays for each characteristic\n"
             "(per-SD increase; rust = significant at p<0.05)")
save(fig, "06_characteristic_effects.png")

# 7 -- Point estimate and correct prediction interval for the scenario home.
from uffi_pipeline import predict_with_interval
scenario = dict(uffi_in=1, brick_ext=0, age_45plus=1, basement_sf=0,
                lot_area=7800, park_spaces=1, living_area=1720,
                central_air=0, pool=0)
pi = predict_with_interval(df, cfg, scenario)
fig, ax = plt.subplots(figsize=(6.6, 2.4))
ax.errorbar(pi["point"], 0, xerr=[[pi["point"] - pi["lower"]],
            [pi["upper"] - pi["point"]]], fmt="o", color=RUST, capsize=6,
            markersize=10, lw=2)
ax.set_yticks([])
ax.set(xlabel="Predicted sale price ($)",
       title=f"Scenario home: ${pi['point']:,.0f}  "
             f"(95% PI ${pi['lower']:,.0f} - ${pi['upper']:,.0f})")
ax.annotate("point estimate", (pi["point"], 0), xytext=(pi["point"], 0.4),
            ha="center", fontsize=9)
save(fig, "07_prediction_interval.png")

print("\nAll figures regenerated.")
