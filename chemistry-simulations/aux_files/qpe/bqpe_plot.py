"""
BQPE plotting utilities with NVIDIA color scheme.

Plot posterior distributions from one or two BQPE experiments with mean, SD,
and exact FCI reference. Designed for import into the QPE notebook.
"""

from typing import List, Optional, Tuple
import numpy as np
import matplotlib.pyplot as plt

# NVIDIA color scheme (dark theme)
NV_GREEN = "#76b900"
NV_GREEN_DARK = "#5e9400"
NV_DARK = "#1A1A1A"
NV_MID = "#2A2A2A"
NV_ACCENT = "#444444"
NV_LIGHT = "#E0E0E0"
NV_GRAY = "#AAAAAA"


def plot_bqpe_comparison(
    posteriors_list: List[List[np.ndarray]],
    mu_list: List[List[float]],
    sigma_list: List[List[float]],
    labels: List[str],
    fci_energy: float,
    delta_t: float = 0.1,
    identity_coeff: float = 0.0,
    x_range: Optional[Tuple[float, float]] = None,
    n_grid: int = 2**14,
    figsize: Tuple[float, float] = (10, 6),
) -> plt.Figure:
    """
    Plot posteriors from two (or more) BQPE experiments with mean, SD, and FCI.

    For each experiment group, plot:
    - Mean (vertical line)
    - ±1 SD (shaded band)
    - Posterior curve(s) in experiment color

    Uses phase grid phi in [-1, 1) (half-turns);
    energy E = π φ / delta_t + identity_coeff (hartree), matching BQPE notebook.

    Args:
        posteriors_list: List of experiment groups. Each group is a list of
            posterior arrays (e.g. [post1, post2] for two runs of experiment A).
        mu_list: List of lists of energy means (hartree) per experiment group.
        sigma_list: List of lists of energy sigma (hartree) per experiment group.
        labels: One label per experiment group (e.g. ["50 samples", "200 samples"]).
        fci_energy: Exact FCI energy (hartree) to draw as reference line.
        delta_t: Time step for phase-to-energy conversion (default 0.1).
        identity_coeff: Constant energy offset (identity term of Hamiltonian).
        x_range: (x_min, x_max) for energy axis; default auto from data.
        n_grid: Number of grid points for phi (must match posterior length).
        figsize: Figure size (width, height).

    Returns:
        matplotlib Figure (NVIDIA-styled).
    """
    phi = np.linspace(-1, 1, n_grid + 1)[:-1]
    x_energy = np.pi * phi / delta_t + identity_coeff

    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(NV_DARK)
    ax.set_facecolor(NV_MID)
    ax.tick_params(colors=NV_LIGHT)
    ax.xaxis.label.set_color(NV_LIGHT)
    ax.yaxis.label.set_color(NV_LIGHT)
    ax.spines["bottom"].set_color(NV_ACCENT)
    ax.spines["top"].set_color(NV_ACCENT)
    ax.spines["left"].set_color(NV_ACCENT)
    ax.spines["right"].set_color(NV_ACCENT)

    colors = [NV_GREEN, "#87CEEB"]  # NVIDIA green + secondary (sky blue for contrast)
    if len(labels) > 2:
        colors = [NV_GREEN, "#87CEEB", NV_GREEN_DARK, NV_GRAY][: len(labels)]

    global_ymax = 0.0
    for group_idx, (posteriors, mus, sigmas, label) in enumerate(
        zip(posteriors_list, mu_list, sigma_list, labels)
    ):
        color = colors[group_idx % len(colors)]
        # Mean and SD across runs (if multiple posteriors per group)
        mus_arr = np.array(mus)
        sigmas_arr = np.array(sigmas)
        mean_mu = np.mean(mus_arr)
        mean_sigma = np.mean(sigmas_arr)
        std_mu = np.std(mus_arr) if len(mus_arr) > 1 else 0.0
        std_sigma = np.std(sigmas_arr) if len(sigmas_arr) > 1 else 0.0

        # Plot each posterior curve (P(φ) vs E(φ)) so the full distribution is visible
        n_curves = len(posteriors)
        alpha_curve = 1.0 if n_curves == 1 else 0.5 + 0.5 / max(n_curves, 2)
        for ii, p in enumerate(posteriors):
            if p is not None and len(p) == len(x_energy):
                lab = "posterior" if (group_idx == 0 and ii == 0) else None  # legend entry once
                ax.plot(x_energy, p, color=color, alpha=alpha_curve, linewidth=2, label=lab)
            global_ymax = max(global_ymax, np.max(p) if p is not None and len(p) else 0)

        # Mean line
        ax.axvline(
            mean_mu,
            color=color,
            linestyle="--",
            linewidth=2,
            alpha=0.9,
            label=f"{label}: μ = {mean_mu:.5f} Ha",
        )
        # ±1 SD band
        ax.axvspan(
            mean_mu - mean_sigma,
            mean_mu + mean_sigma,
            color=color,
            alpha=0.15,
        )
        # Optional: show SD in legend if we have multiple runs
        if len(mus) > 1:
            ax.plot(
                [],
                [],
                " ",
                label=f"  σ_μ={std_mu:.5f}, σ_σ={std_sigma:.5f} (run std)",
            )

    # FCI reference
    ax.axvline(
        fci_energy,
        color=NV_LIGHT,
        linestyle=":",
        linewidth=2.5,
        label=f"FCI = {fci_energy:.5f} Ha",
    )
    ax.legend(loc="best", facecolor=NV_MID, edgecolor=NV_ACCENT, labelcolor=NV_LIGHT)
    ax.set_xlabel(r"Energy $E$ / hartree", fontsize=12)
    ax.set_ylabel(r"Posterior $P(E)$", fontsize=12)
    if x_range is not None:
        ax.set_xlim(x_range)
    else:
        ax.set_xlim([-1.35, -0.95])
    ax.set_ylim(0, global_ymax * 1.15)
    ax.grid(True, alpha=0.2, color=NV_ACCENT)
    plt.tight_layout()
    return fig
