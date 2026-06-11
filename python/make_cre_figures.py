"""
make_cre_figures.py
==================

Regenerates the commercial / defense-lease figures (08, 09, 10) from the
simulated CRE book. Run after any change to `cre_defense_lease.py`:

    python python/make_cre_figures.py
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from cre_defense_lease import (simulate_market, market_prices_defense,
                               underwrite_overlay, sensitivity)

FIG = Path(__file__).resolve().parents[1] / "figures"
plt.rcParams.update({"figure.dpi": 120, "font.size": 10, "axes.grid": True,
                     "grid.alpha": 0.3})
NAVY, RUST, GREY = "#1f3a5f", "#c1440e", "#9aa7b4"

df = simulate_market()


def save(fig, name):
    fig.tight_layout(); fig.savefig(FIG / name, bbox_inches="tight"); plt.close(fig)
    print("wrote", name)


# 08 -- What the market pays for: the defense attribute reads ~0 and
# insignificant, while the credit-tenancy attributes are paid for. This is the
# empirical statement of "the market prices these as generic credit tenancy."
eff = market_prices_defense(df).set_index("term")
order = eff.pct_per_sd.abs().sort_values().index
fig, ax = plt.subplots(figsize=(7, 4.4))
colors = [RUST if t == "mission_critical_defense"
          else (NAVY if eff.loc[t, "p_value"] < 0.05 else GREY) for t in order]
ax.barh(order, eff.loc[order, "pct_per_sd"], color=colors)
ax.axvline(0, color="black", lw=0.8)
d = eff.loc["mission_critical_defense"]
ax.annotate(f"defense attribute:\n{d.pct_per_sd:+.1f}% / SD, p={d.p_value:.2f}\n(market does not price it)",
            xy=(d.pct_per_sd, list(order).index("mission_critical_defense")),
            xytext=(0.30, 0.45), textcoords="axes fraction", color=RUST, fontsize=9,
            arrowprops=dict(arrowstyle="->", color=RUST))
ax.set(xlabel="Approx. % effect on price per +1 SD",
       title="What the market pays for in net-leased CRE\n"
             "(navy = significant credit-tenancy driver; rust = defense attribute)")
save(fig, "08_cre_market_pricing.png")

# 09 -- Sensitivity: captured value uplift on defense assets vs the assumed
# cap-rate compression. Direct support for "run sensitivity analyses."
s = sensitivity(df)
fig, ax = plt.subplots(figsize=(6.6, 4.0))
ax.plot(s.compression_bps, s.avg_captured_pct, "o-", color=RUST, lw=2, markersize=7)
for x, y in zip(s.compression_bps, s.avg_captured_pct):
    ax.annotate(f"{y:.1f}%", (x, y), textcoords="offset points", xytext=(0, 8),
                ha="center", fontsize=9)
ax.set(xlabel="Defense-infrastructure cap-rate compression (bps)",
       ylabel="Captured value uplift on defense assets (%)",
       title="Sensitivity of capturable mispricing to the underwriting overlay")
save(fig, "09_cre_sensitivity.png")

# 10 -- Where the spread lives: at a base 75 bps overlay, the captured spread is
# concentrated entirely in the mission-critical defense subset; generic assets
# sit at ~0 (priced correctly by the market).
u = underwrite_overlay(df, 75)
fig, ax = plt.subplots(figsize=(6.6, 4.0))
ax.hist(u.loc[u.mission_critical_defense == 0, "captured_pct"], bins=25,
        color=GREY, alpha=0.85, label="Generic credit tenancy")
ax.hist(u.loc[u.mission_critical_defense == 1, "captured_pct"], bins=25,
        color=RUST, alpha=0.85, label="Mission-critical defense")
ax.axvline(0, color="black", lw=0.8)
ax.set(xlabel="Captured spread vs price paid (%)", ylabel="Assets",
       title="Capturable spread concentrates in the defense subset (75 bps overlay)")
ax.legend()
save(fig, "10_cre_spread_distribution.png")

print("\nCRE figures regenerated.")
