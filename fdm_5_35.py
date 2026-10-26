#!/usr/bin/env python3
"""
fdm_5_35.py  -  Numerical Methods in Heat Transfer
Textbook Problem 5-35 (original) and a forced-air-cooled adaptation.

WALL (x measured from the heated bottom face, upward):
    layer 1  ASME SB-96 Cu-Si plate (UNS C65500)  k1 = 36 W/m.K, L1 = 30 mm
    layer 2  stainless steel plate (904L-type)    k2 = 13 W/m.K, L2 = 10 mm
    x = 0     (surface 1): uniform heat flux q0 = 750 W/m^2 into the wall
    x = 40 mm (surface 2): convection + radiation, h_comb, T_inf = T_surr = 20 C
    dx = 5 mm  ->  nodes 0..8 (node 6 = interface)

DESIGNS
    original : h_comb = 7.76 W/m^2.K  (natural convection + radiation, textbook)
    adapted  : h_comb = 40   W/m^2.K  (fan-forced air + high-emissivity coating)

WHAT THE SCRIPT DOES
    1. Steady FD solution for both designs, solved two independent ways
       (numpy on the energy-balance equations, Thomas algorithm on the
       hand-written equations) and compared with the exact resistance network.
    2. Residuals, interface flux continuity and the overall energy balance.
    3. ASME check (93 C), highest allowable heat flux, minimum h for compliance.
    4. ADDED transient analysis (not part of the textbook problem): the heat flux
       is switched off with the wall at a uniform 93 C and the bottom becomes
       adiabatic. Explicit FD gives the time for the hottest point (node 0) to
       reach 40 C. Cross-checks: Crank-Nicolson, a finer grid, lumped capacitance,
       and the one-term series solution. Transient energy balance is also checked.
    5. Sensitivity study, design sweep over h_comb, CSV tables and figures.

RUN:    python fdm_5_35.py          (requires numpy and matplotlib)
OUTPUT: results/*.csv, results/run_log.txt, figures/*.png

Property sources (density, specific heat): C65500 - Wieland Diversified data
sheet (8530 kg/m^3, 377 J/kg.K); 904L - Atlas Steels grade data sheet
(8000 kg/m^3, 500 J/kg.K). Both sheets list the same k as the textbook.
"""

import csv
import math
import os
import sys

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results")
FIG = os.path.join(HERE, "figures")
os.makedirs(RES, exist_ok=True)
os.makedirs(FIG, exist_ok=True)

# ---------------------------------------------------------------- input data
K1, L1 = 36.0, 0.030            # SB-96 Cu-Si plate            [W/m.K], [m]
K2, L2 = 13.0, 0.010            # stainless steel plate        [W/m.K], [m]
RHO1, CP1 = 8530.0, 377.0       # C65500 (transient only)      [kg/m^3], [J/kg.K]
RHO2, CP2 = 8000.0, 500.0       # 904L   (transient only)      [kg/m^3], [J/kg.K]
DX = 0.005                      # nodal spacing                [m]
Q0 = 750.0                      # heat flux into surface 1     [W/m^2]
T_INF = 20.0                    # air and surroundings         [C]
T_ALLOW = 93.0                  # ASME BPVC.IV-2015 HF-300     [C]
H_ORIG = 7.76                   # original combined coeff.     [W/m^2.K]
H_ADAPT = 40.0                  # adapted combined coeff.      [W/m^2.K]
T_START, T_TARGET = 93.0, 40.0  # cooldown test                [C]
DT = 1.0                        # explicit time step           [s]
SIGMA = 5.670e-8                # Stefan-Boltzmann constant    [W/m^2.K^4]

DESIGNS = [("Original", H_ORIG), ("Adapted", H_ADAPT)]

# chart styling (one colour per design, used in every figure)
COL = {"Original": "#898781", "Adapted": "#2a78d6"}
INK, INK2, GRID, AXIS = "#0b0b0b", "#52514e", "#e1e0d9", "#c3c2b7"
LIMIT = "#d03b3b"

LOG_LINES = []


def log(*parts):
    """Print to the screen and keep a copy for results/run_log.txt."""
    line = " ".join(str(p) for p in parts)
    print(line)
    LOG_LINES.append(line)


# ============================================================ wall geometry
class Wall:
    """Two-layer plane wall discretised with uniform spacing dx.

    G[m] : conductance of the interval between node m and m+1 = k/dx [W/m^2.K]
    C[m] : heat capacity of node m's control volume per unit area [J/m^2.K]
           (half-volumes at the two surfaces, two half-volumes at the interface)
    """

    def __init__(self, k1=K1, l1=L1, k2=K2, l2=L2, rho1=RHO1, cp1=CP1,
                 rho2=RHO2, cp2=CP2, dx=DX):
        self.k1, self.l1, self.k2, self.l2, self.dx = k1, l1, k2, l2, dx
        self.rc1, self.rc2 = rho1 * cp1, rho2 * cp2
        self.n1 = int(round(l1 / dx))          # intervals in layer 1
        self.n2 = int(round(l2 / dx))          # intervals in layer 2
        if abs(self.n1 * dx - l1) > 1e-12 or abs(self.n2 * dx - l2) > 1e-12:
            raise ValueError("dx must divide both layer thicknesses")
        self.M = self.n1 + self.n2             # index of the last node
        self.x = np.arange(self.M + 1) * dx
        self.G = np.array([(k1 if m < self.n1 else k2) / dx for m in range(self.M)])
        self.C = np.zeros(self.M + 1)
        for m in range(self.M):
            rc = self.rc1 if m < self.n1 else self.rc2
            self.C[m] += rc * dx / 2.0
            self.C[m + 1] += rc * dx / 2.0

    @property
    def r_cond(self):
        """Conduction resistance of both plates [m^2.K/W]."""
        return self.l1 / self.k1 + self.l2 / self.k2

    @property
    def c_total(self):
        """Heat capacity of the wall per unit area [J/m^2.K]."""
        return self.rc1 * self.l1 + self.rc2 * self.l2

    def material(self, m):
        if m < self.n1:
            return "Cu-Si (SB-96)"
        if m == self.n1:
            return "interface"
        return "stainless steel"


# ============================================================ steady state
def steady_energy_system(w, h, q0=Q0, t_inf=T_INF):
    """Energy balance on each node's control volume (W/m^2):
    heat conducted in from both neighbours + boundary heat in = 0."""
    n = w.M + 1
    a = np.zeros((n, n))
    b = np.zeros(n)
    for m in range(n):
        if m > 0:                      # conduction from node m-1
            a[m, m - 1] += w.G[m - 1]
            a[m, m] -= w.G[m - 1]
        if m < w.M:                    # conduction from node m+1
            a[m, m + 1] += w.G[m]
            a[m, m] -= w.G[m]
    b[0] -= q0                         # + q0 into node 0, moved to the RHS
    a[w.M, w.M] -= h                   # + h (T_inf - T_M) into node M
    b[w.M] -= h * t_inf
    return a, b


def hand_form(w, h, q0=Q0, t_inf=T_INF):
    """The same equations written exactly as in the report (divided through).
    Returns tridiagonal coefficients: a (left), bd (centre), c (right), d (RHS)."""
    n = w.M + 1
    a, bd, c, d = (np.zeros(n) for _ in range(4))
    for m in range(n):
        if m == 0:                                   # heat-flux node
            bd[m], c[m], d[m] = -1.0, 1.0, -q0 * w.dx / w.k1
        elif m == w.M:                               # convection node
            bi = h * w.dx / w.k2
            a[m], bd[m], d[m] = 1.0, -(1.0 + bi), -bi * t_inf
        elif m == w.n1:                              # interface node
            a[m], bd[m], c[m] = w.k1, -(w.k1 + w.k2), w.k2
        else:                                        # interior node
            a[m], bd[m], c[m] = 1.0, -2.0, 1.0
    return a, bd, c, d


def thomas(a, bd, c, d):
    """Thomas algorithm (tridiagonal Gaussian elimination).
    Returns the solution and the forward-sweep coefficients c' and d'."""
    n = len(d)
    cp, dp = np.zeros(n), np.zeros(n)
    cp[0] = c[0] / bd[0]
    dp[0] = d[0] / bd[0]
    for i in range(1, n):
        den = bd[i] - a[i] * cp[i - 1]
        cp[i] = c[i] / den if i < n - 1 else 0.0
        dp[i] = (d[i] - a[i] * dp[i - 1]) / den
    x = np.zeros(n)
    x[-1] = dp[-1]
    for i in range(n - 2, -1, -1):
        x[i] = dp[i] - cp[i] * x[i + 1]
    return x, cp, dp


def exact_profile(w, h, x, q0=Q0, t_inf=T_INF):
    """Exact steady solution from the thermal resistance network."""
    t_top = t_inf + q0 / h
    t_if = t_top + q0 * w.l2 / w.k2
    return np.where(x >= w.l1 - 1e-15,
                    t_top + q0 * (w.l1 + w.l2 - x) / w.k2,
                    t_if + q0 * (w.l1 - x) / w.k1)


def solve_steady(w, h, q0=Q0, t_inf=T_INF):
    a_mat, b_vec = steady_energy_system(w, h, q0, t_inf)
    t_np = np.linalg.solve(a_mat, b_vec)
    a, bd, c, d = hand_form(w, h, q0, t_inf)
    t_th, cp, dp = thomas(a, bd, c, d)
    t_ex = exact_profile(w, h, w.x, q0, t_inf)
    resid = a_mat @ t_np - b_vec                      # W/m^2 per node
    q_int = w.G * (t_np[:-1] - t_np[1:])               # flux between nodes
    q_out = h * (t_np[-1] - t_inf)
    return dict(T=t_np, T_thomas=t_th, T_exact=t_ex, resid=resid, q_int=q_int,
                q_out=q_out, coeffs=(a, bd, c, d, cp, dp))


# ============================================================ transient
def explicit_coefficients(w, h, dt=DT):
    """Mesh Fourier numbers and node coefficients of the explicit scheme."""
    tau1 = w.k1 / w.rc1 * dt / w.dx ** 2
    tau2 = w.k2 / w.rc2 * dt / w.dx ** 2
    beta = 2.0 * dt / ((w.rc1 + w.rc2) * w.dx ** 2)
    bi_dx = h * w.dx / w.k2
    k_diag = np.zeros(w.M + 1)
    k_diag[:-1] += w.G
    k_diag[1:] += w.G
    k_diag[w.M] += h
    dt_crit = float(np.min(w.C / k_diag))   # every "self" coefficient >= 0
    return dict(tau1=tau1, tau2=tau2, beta=beta, bi_dx=bi_dx, dt_crit=dt_crit,
                self_coef=1.0 - dt * k_diag / w.C)


def cooldown_explicit(w, h, dt=DT, t_i=T_START, t_target=T_TARGET,
                      t_inf=T_INF, t_end=None, store_every=60):
    """Explicit FD cooldown. Bottom adiabatic (heat flux off), top convection.
    Integrates until node 0 reaches t_target (and until t_end if given)."""
    co = explicit_coefficients(w, h, dt)
    if dt > co["dt_crit"] + 1e-12:
        raise ValueError(f"dt = {dt} s exceeds the stability limit {co['dt_crit']:.4f} s")
    g, cap, m_last = w.G, w.C, w.M
    t_nodes = np.full(m_last + 1, float(t_i))
    u0 = cap @ t_nodes
    t, step, e_conv = 0.0, 0, 0.0
    t_cross = t_cross_mean = None
    hist = [(0.0, *t_nodes, cap @ t_nodes / cap.sum())]
    first_steps = [t_nodes.copy()]
    while True:
        q_in = np.zeros(m_last + 1)
        q_in[:-1] += g * (t_nodes[1:] - t_nodes[:-1])    # from the right neighbour
        q_in[1:] += g * (t_nodes[:-1] - t_nodes[1:])     # from the left neighbour
        q_in[m_last] += h * (t_inf - t_nodes[m_last])    # convection at node M
        e_conv += h * (t_nodes[m_last] - t_inf) * dt
        t_new = t_nodes + dt * q_in / cap
        if t_cross is None and t_new[0] <= t_target:
            t_cross = t + dt * (t_nodes[0] - t_target) / (t_nodes[0] - t_new[0])
        mean_old = cap @ t_nodes / cap.sum()
        mean_new = cap @ t_new / cap.sum()
        if t_cross_mean is None and mean_new <= t_target:
            t_cross_mean = t + dt * (mean_old - t_target) / (mean_old - mean_new)
        t_nodes, t, step = t_new, t + dt, step + 1
        if step <= 2:
            first_steps.append(t_nodes.copy())
        if step % store_every == 0:
            hist.append((t, *t_nodes, mean_new))
        done = t_cross is not None and (t_end is None or t >= t_end)
        if done or t > 1e6:
            break
    du = u0 - cap @ t_nodes
    return dict(t_cross=t_cross, t_cross_mean=t_cross_mean, hist=np.array(hist),
                energy_error=(e_conv - du) / du, coeffs=co, first_steps=first_steps)


def cooldown_crank_nicolson(w, h, dt=10.0, t_i=T_START, t_target=T_TARGET, t_inf=T_INF):
    """Independent check: Crank-Nicolson on the matrix form C dT/dt = -K T + f."""
    n = w.M + 1
    k = np.zeros((n, n))
    for m in range(w.M):
        k[m, m] += w.G[m]
        k[m + 1, m + 1] += w.G[m]
        k[m, m + 1] -= w.G[m]
        k[m + 1, m] -= w.G[m]
    k[w.M, w.M] += h
    f = np.zeros(n)
    f[w.M] = h * t_inf
    cmat = np.diag(w.C) / dt
    lhs_inv = np.linalg.inv(cmat + k / 2.0)
    rhs = cmat - k / 2.0
    t_nodes = np.full(n, float(t_i))
    t = 0.0
    while True:
        t_new = lhs_inv @ (rhs @ t_nodes + f)
        if t_new[0] <= t_target:
            return t + dt * (t_nodes[0] - t_target) / (t_nodes[0] - t_new[0])
        t_nodes, t = t_new, t + dt


def lumped(w, h, t_i=T_START, t_target=T_TARGET, t_inf=T_INF):
    tau = w.c_total / h
    return tau * math.log((t_i - t_inf) / (t_target - t_inf)), tau


def one_term(w, h, t_i=T_START, t_target=T_TARGET, t_inf=T_INF):
    """One-term series (the basis of the Heisler chart) for an equivalent
    homogeneous wall, insulated at x = 0 and cooled at x = L. Approximate for a
    composite wall; used only as a cross-check."""
    bi = h * w.r_cond
    lo, hi = 1e-12, math.pi / 2 - 1e-12
    for _ in range(200):                      # bisection on lambda*tan(lambda) = Bi
        mid = 0.5 * (lo + hi)
        if mid * math.tan(mid) > bi:
            hi = mid
        else:
            lo = mid
    lam = 0.5 * (lo + hi)
    a1 = 4.0 * math.sin(lam) / (2.0 * lam + math.sin(2.0 * lam))
    theta = (t_target - t_inf) / (t_i - t_inf)
    fo = math.log(a1 / theta) / lam ** 2
    return dict(Bi=bi, lam=lam, A1=a1, Fo=fo, t=fo * w.r_cond * w.c_total)


# ============================================================ helpers
def write_csv(name, header, rows):
    with open(os.path.join(RES, name), "w", newline="") as fh:
        wr = csv.writer(fh)
        wr.writerow(header)
        wr.writerows(rows)


def pct_lower_is_better(orig, adapt):
    return (orig - adapt) / orig * 100.0


def pct_higher_is_better(orig, adapt):
    return (adapt - orig) / orig * 100.0


def style_axes(ax):
    ax.set_facecolor("white")
    ax.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(AXIS)
    ax.tick_params(colors=INK2, labelsize=9)
    ax.xaxis.label.set_color(INK2)
    ax.yaxis.label.set_color(INK2)


# ============================================================ main
def main():
    w = Wall()
    log("=" * 74)
    log("PROBLEM 5-35  -  steady finite difference solution and adaptation")
    log("=" * 74)
    log(f"Nodes 0..{w.M}, interface node {w.n1}, dx = {w.dx*1000:.1f} mm")
    log(f"q0*dx/k1 = {Q0*DX/K1:.7f} C   q0*dx/k2 = {Q0*DX/K2:.7f} C")
    log(f"R_cond = L1/k1 + L2/k2 = {L1/K1:.7f} + {L2/K2:.7f} = {w.r_cond:.7f} m2.K/W")

    steady = {}
    for name, h in DESIGNS:
        s = solve_steady(w, h)
        steady[name] = s
        a, bd, c, d, cp, dp = s["coeffs"]
        r_tot = 1.0 / h + w.r_cond
        log("")
        log(f"--- {name} design: h_comb = {h} W/m2.K ---")
        log(f"h*dx/k2 = {h*DX/K2:.7f}   R_conv = 1/h = {1/h:.7f}   R_total = {r_tot:.7f} m2.K/W")
        log("Hand-form equations  a*T(m-1) + b*T(m) + c*T(m+1) = d   and Thomas sweep")
        log(f"{'m':>2} {'a':>8} {'b':>12} {'c':>8} {'d':>12} {'c_prime':>10} {'d_prime':>12}")
        for i in range(w.M + 1):
            log(f"{i:>2} {a[i]:8.3f} {bd[i]:12.7f} {c[i]:8.3f} {d[i]:12.7f} {cp[i]:10.5f} {dp[i]:12.7f}")
        log(f"{'m':>2} {'x[mm]':>6} {'material':>16} {'T_FD[C]':>11} {'T_Thomas':>11} {'T_exact':>11} {'resid[W/m2]':>12}")
        for i in range(w.M + 1):
            log(f"{i:>2} {w.x[i]*1000:6.1f} {w.material(i):>16} {s['T'][i]:11.5f} "
                f"{s['T_thomas'][i]:11.5f} {s['T_exact'][i]:11.5f} {s['resid'][i]:12.2e}")
        log(f"max |FD - exact| = {np.max(np.abs(s['T'] - s['T_exact'])):.2e} C ; "
            f"max |numpy - Thomas| = {np.max(np.abs(s['T'] - s['T_thomas'])):.2e} C")
        log("Flux between nodes [W/m2]: " + ", ".join(f"{q:.4f}" for q in s["q_int"]))
        q_left = s["q_int"][w.n1 - 1]
        q_right = s["q_int"][w.n1]
        log(f"Interface continuity: k1(T5-T6)/dx = {q_left:.6f}, k2(T6-T7)/dx = {q_right:.6f} W/m2")
        log(f"Energy balance: q_in = {Q0:.6f}, q_out = h(T8-Tinf) = {s['q_out']:.6f} W/m2, "
            f"error = {(s['q_out']-Q0)/Q0*100:.2e} %")
        t_max = s["T"][: w.n1 + 1].max()
        verdict = "COMPLIES" if t_max <= T_ALLOW else "DOES NOT COMPLY"
        log(f"Hottest SB-96 temperature = T0 = {t_max:.4f} C vs 93 C -> {verdict}")
        # highest allowable heat flux (T is linear in q0)
        r_fd = (s["T"][0] - T_INF) / Q0
        q_max = (T_ALLOW - T_INF) / r_fd
        chk = solve_steady(w, h, q0=q_max)["T"][0]
        log(f"q0_max = (93-20)/R = {T_ALLOW-T_INF:.0f}/{r_fd:.7f} = {q_max:.3f} W/m2 "
            f"(FD check: T0 = {chk:.6f} C)")
        s.update(t_max=t_max, q_max=q_max, r_tot=r_tot)

    # minimum h for compliance at the original heat flux
    h_min = 1.0 / ((T_ALLOW - T_INF) / Q0 - w.r_cond)
    t0_hmin = solve_steady(w, h_min)["T"][0]
    log("")
    log(f"Minimum h_comb for compliance at 750 W/m2: {h_min:.4f} W/m2.K "
        f"(FD check: T0 = {t0_hmin:.6f} C)")
    log(f"Bi = 0.1 is reached at h = 0.1/R_cond = {0.1/w.r_cond:.3f} W/m2.K")

    # radiation estimate for a high-emissivity coating (eps = 0.9)
    log("")
    for ts in (40.0, 93.0):
        tsk, tsu = ts + 273.15, T_INF + 273.15
        hr = 0.9 * SIGMA * (tsk + tsu) * (tsk ** 2 + tsu ** 2)
        log(f"h_rad (eps = 0.9) at Ts = {ts:.0f} C: {hr:.3f} W/m2.K")

    # ------------------------------------------------------------ transient
    log("")
    log("=" * 74)
    log("ADDED TRANSIENT ANALYSIS: cooldown 93 C -> 40 C, heat flux off, bottom adiabatic")
    log("=" * 74)
    log(f"rho1*c1 = {w.rc1:.0f} J/m3.K, rho2*c2 = {w.rc2:.0f} J/m3.K, "
        f"alpha1 = {K1/w.rc1:.5e}, alpha2 = {K2/w.rc2:.5e} m2/s")
    log(f"C'' = rho1 c1 L1 + rho2 c2 L2 = {w.rc1*L1:.1f} + {w.rc2*L2:.1f} = {w.c_total:.1f} J/m2.K")
    log("Node capacities C_m [J/m2.K]: " + ", ".join(f"{cc:.1f}" for cc in w.C))
    trans = {}
    t_plot_end = None
    for name, h in DESIGNS:
        co = explicit_coefficients(w, h)
        log("")
        log(f"--- {name}: h = {h} ---")
        log(f"tau1 = {co['tau1']:.6f}, tau2 = {co['tau2']:.6f}, beta = {co['beta']:.7f}, "
            f"h*dx/k2 = {co['bi_dx']:.7f}")
        log(f"Stability limit dt_crit = {co['dt_crit']:.4f} s (dt used = {DT} s)")
        log("Self-coefficients (1 - dt*K_mm/C_m): " + ", ".join(f"{v:.6f}" for v in co["self_coef"]))
        trans[name] = cooldown_explicit(w, h)
        r = trans[name]
        log("First steps (all nodes):")
        for k_step, tn in enumerate(r["first_steps"]):
            log(f"  t = {k_step:.0f} s: " + ", ".join(f"{v:.6f}" for v in tn))
        t_l, tau = lumped(w, h)
        ot = one_term(w, h)
        t_cn = cooldown_crank_nicolson(w, h)
        w_fine = Wall(dx=0.0025)
        dt_fine = 0.25
        t_fine = cooldown_explicit(w_fine, h, dt=dt_fine)["t_cross"]
        r.update(t_lumped=t_l, tau=tau, one=ot, t_cn=t_cn, t_fine=t_fine)
        log(f"Biot number Bi = h*R_cond = {ot['Bi']:.5f}  (lumped valid if < 0.1)")
        log(f"Explicit FD  : node 0 reaches 40 C at {r['t_cross']:.1f} s = {r['t_cross']/3600:.4f} h")
        log(f"               mass-weighted mean reaches 40 C at {r['t_cross_mean']:.1f} s")
        log(f"Crank-Nicolson (dt = 10 s): {t_cn:.1f} s")
        log(f"Explicit, dx = 2.5 mm, dt = 0.25 s: {t_fine:.1f} s")
        log(f"Lumped: tau = C''/h = {tau:.1f} s, t = tau*ln(73/20) = {t_l:.1f} s")
        log(f"One-term: lambda1 = {ot['lam']:.6f}, A1 = {ot['A1']:.6f}, Fo = {ot['Fo']:.3f}, t = {ot['t']:.1f} s")
        log(f"Transient energy balance error = {r['energy_error']:.2e}")
        if t_plot_end is None or r["t_cross"] > t_plot_end:
            t_plot_end = r["t_cross"]

    # long runs for the plot (same time window for both designs)
    t_window = math.ceil(t_plot_end / 1800.0) * 1800.0 + 1800.0
    for name, h in DESIGNS:
        trans[name]["hist_plot"] = cooldown_explicit(w, h, t_end=t_window)["hist"]

    # ------------------------------------------------------------ summary
    so, sa = steady["Original"], steady["Adapted"]
    to, ta = trans["Original"], trans["Adapted"]
    log("")
    log("=" * 74)
    log("SUMMARY")
    log("=" * 74)
    rows = [
        ("h_comb [W/m2.K]", H_ORIG, H_ADAPT, "", "input"),
        ("Hottest SB-96 temperature T0 [C]", so["t_max"], sa["t_max"], "", "lower is better"),
        ("Rise above ambient T0 - Tinf [C]", so["t_max"] - T_INF, sa["t_max"] - T_INF,
         pct_lower_is_better(so["t_max"] - T_INF, sa["t_max"] - T_INF), "lower is better"),
        ("Total thermal resistance [m2.K/W]", so["r_tot"], sa["r_tot"],
         pct_lower_is_better(so["r_tot"], sa["r_tot"]), "lower is better"),
        ("Heat flux through wall [W/m2]", so["q_out"], sa["q_out"], 0.0, "fixed by the boundary condition"),
        ("Highest allowable heat flux [W/m2]", so["q_max"], sa["q_max"],
         pct_higher_is_better(so["q_max"], sa["q_max"]), "higher is better"),
        ("Biot number h*R_cond [-]", to["one"]["Bi"], ta["one"]["Bi"], "", "< 0.1 means lumped valid"),
        ("Time constant C''/h [s]", to["tau"], ta["tau"],
         pct_lower_is_better(to["tau"], ta["tau"]), "lower is better"),
        ("Cooldown 93->40 C, node 0, explicit FD [s]", to["t_cross"], ta["t_cross"],
         pct_lower_is_better(to["t_cross"], ta["t_cross"]), "lower is better"),
        ("Cooldown, lumped capacitance [s]", to["t_lumped"], ta["t_lumped"],
         pct_lower_is_better(to["t_lumped"], ta["t_lumped"]), "lower is better"),
        ("Cooldown, one-term series [s]", to["one"]["t"], ta["one"]["t"],
         pct_lower_is_better(to["one"]["t"], ta["one"]["t"]), "lower is better"),
        ("Cooldown, Crank-Nicolson [s]", to["t_cn"], ta["t_cn"],
         pct_lower_is_better(to["t_cn"], ta["t_cn"]), "lower is better"),
        ("Cooldown, fine grid [s]", to["t_fine"], ta["t_fine"],
         pct_lower_is_better(to["t_fine"], ta["t_fine"]), "lower is better"),
    ]
    for r_ in rows:
        imp = f"{r_[3]:.2f} %" if r_[3] != "" else ""
        log(f"{r_[0]:<44} {r_[1]:>12.4f} {r_[2]:>12.4f} {imp:>10}  {r_[4]}")
    log(f"Speed-up factor (FD) = {to['t_cross']/ta['t_cross']:.3f}x")
    write_csv("summary.csv", ["metric", "original", "adapted", "improvement_percent", "note"], rows)

    write_csv("steady_nodes.csv",
              ["node", "x_mm", "material", "T_original_FD_C", "T_original_exact_C",
               "T_adapted_FD_C", "T_adapted_exact_C"],
              [(i, round(w.x[i] * 1000, 1), w.material(i), so["T"][i], so["T_exact"][i],
                sa["T"][i], sa["T_exact"][i]) for i in range(w.M + 1)])
    for name in ("Original", "Adapted"):
        a, bd, c, d, cp, dp = steady[name]["coeffs"]
        write_csv(f"thomas_{name.lower()}.csv",
                  ["node", "a", "b", "c", "d", "c_prime", "d_prime", "T_C", "residual_W_m2"],
                  [(i, a[i], bd[i], c[i], d[i], cp[i], dp[i], steady[name]["T"][i],
                    steady[name]["resid"][i]) for i in range(w.M + 1)])
        hist = trans[name]["hist_plot"]
        write_csv(f"transient_{name.lower()}.csv",
                  ["t_s"] + [f"T{i}_C" for i in range(w.M + 1)] + ["T_mean_C"],
                  hist.tolist())

    # ------------------------------------------------------------ sensitivity
    log("")
    log("SENSITIVITY (one change at a time, original design as reference)")
    cases = [
        ("Original design", dict(), H_ORIG, T_INF),
        ("k1 doubled (36 -> 72)", dict(k1=72.0), H_ORIG, T_INF),
        ("k2 doubled (13 -> 26)", dict(k2=26.0), H_ORIG, T_INF),
        ("L1 halved (30 -> 15 mm)", dict(l1=0.015), H_ORIG, T_INF),
        ("L2 halved (10 -> 5 mm)", dict(l2=0.005), H_ORIG, T_INF),
        ("h_comb doubled (7.76 -> 15.52)", dict(), 2 * H_ORIG, T_INF),
        ("Air 10 C cooler (20 -> 10 C)", dict(), H_ORIG, 10.0),
        ("Adapted design (h_comb = 40)", dict(), H_ADAPT, T_INF),
    ]
    sens_rows = []
    base_t = base_cool = None
    for label, kw, h, tinf in cases:
        ww = Wall(**kw)
        tmax = solve_steady(ww, h, t_inf=tinf)["T"][0]
        # a higher k raises the diffusivity, so the stable time step shrinks
        dt_case = min(DT, 0.9 * explicit_coefficients(ww, h)["dt_crit"])
        tc = cooldown_explicit(ww, h, dt=dt_case, t_inf=tinf)["t_cross"]
        if base_t is None:
            base_t, base_cool = tmax, tc
        sens_rows.append((label, tmax, tmax - base_t, tc / 3600.0,
                          pct_lower_is_better(base_cool, tc)))
        log(f"{label:<34} T0 = {tmax:8.3f} C ({tmax-base_t:+8.3f})   "
            f"cooldown = {tc/3600:6.3f} h ({pct_lower_is_better(base_cool, tc):6.1f} % faster)")
    write_csv("sensitivity.csv", ["case", "T0_steady_C", "change_C", "cooldown_h",
                                  "cooldown_reduction_percent"], sens_rows)

    # ------------------------------------------------------------ design sweep
    h_values = sorted(set(np.round(np.geomspace(5, 200, 41), 3).tolist()
                          + [H_ORIG, round(h_min, 3), H_ADAPT]))
    sweep = []
    for h in h_values:
        tmax = solve_steady(w, h)["T"][0]
        tc = cooldown_explicit(w, h)["t_cross"]
        tl, _ = lumped(w, h)
        sweep.append((h, h * w.r_cond, tmax, tc / 3600.0, tl / 3600.0,
                      (T_ALLOW - T_INF) / (1.0 / h + w.r_cond)))
    write_csv("design_sweep.csv", ["h_W_m2K", "Bi", "T0_steady_C", "cooldown_FD_h",
                                   "cooldown_lumped_h", "q_max_W_m2"], sweep)
    sweep = np.array(sweep)

    # ------------------------------------------------------------ figures
    plt.rcParams.update({"font.size": 10, "font.family": "DejaVu Sans"})
    xmm = w.x * 1000

    # Figure 1: physical model and nodal grid
    fig, ax = plt.subplots(figsize=(7.6, 3.4), dpi=200)
    ax.set_xlim(-14, 56)
    ax.set_ylim(-3.2, 13)
    ax.axis("off")
    ax.add_patch(plt.Rectangle((0, 0), 30, 9, facecolor="#f3e3d3", edgecolor=AXIS, linewidth=1))
    ax.add_patch(plt.Rectangle((30, 0), 10, 9, facecolor="#e3e8ee", edgecolor=AXIS, linewidth=1))
    ax.text(15, 7.6, "ASME SB-96 Cu-Si plate", ha="center", fontsize=9.5, color=INK, weight="bold")
    ax.text(15, 6.5, "k1 = 36 W/m·K, L1 = 30 mm", ha="center", fontsize=8.5, color=INK2)
    ax.text(35, 7.6, "Steel", ha="center", fontsize=9.5, color=INK, weight="bold")
    ax.text(35, 6.5, "k2 = 13", ha="center", fontsize=8, color=INK2)
    ax.text(35, 5.6, "L2 = 10 mm", ha="center", fontsize=8, color=INK2)
    for i, xv in enumerate(xmm):
        ax.plot(xv, 4.0, "o", ms=6.5, color=COL["Adapted"] if i == w.n1 else INK2, zorder=3)
        ax.text(xv, 2.6, str(i), ha="center", fontsize=9, color=INK)
    ax.plot([0, 40], [4.0, 4.0], color=AXIS, linewidth=1, zorder=1)
    ax.text(30, 1.4, "interface", ha="center", fontsize=8, color=COL["Adapted"])
    for yv in (1.5, 4.5, 7.5):
        ax.annotate("", xy=(-0.6, yv), xytext=(-9, yv),
                    arrowprops=dict(arrowstyle="-|>", color=LIMIT, lw=1.4))
    ax.text(-7, 10.0, "Surface 1\nq̇₀ = 750 W/m²", ha="center", fontsize=8.5, color=INK)
    for yv in (1.5, 4.5, 7.5):
        ax.annotate("", xy=(49, yv), xytext=(40.6, yv),
                    arrowprops=dict(arrowstyle="-|>", color=COL["Adapted"], lw=1.4))
    ax.text(47.5, 10.0, "Surface 2\nh_comb, T∞ = T_surr = 20 °C", ha="center", fontsize=8.5, color=INK)
    ax.annotate("", xy=(44, -2.2), xytext=(0, -2.2),
                arrowprops=dict(arrowstyle="-|>", color=INK2, lw=1))
    ax.text(45, -2.6, "x", fontsize=10, color=INK2)
    ax.text(0, -1.6, "x = 0", ha="center", fontsize=8, color=INK2)
    ax.text(40, -1.6, "40 mm", ha="center", fontsize=8, color=INK2)
    ax.text(-14, 12.4, "Nine nodes at 5-mm spacing; node 6 sits on the Cu-Si / steel interface",
            fontsize=10.5, color=INK, weight="bold")
    fig.savefig(os.path.join(FIG, "fig1_model.png"), bbox_inches="tight", facecolor="white")
    plt.close(fig)

    # Figure 2: steady temperature distribution, both designs
    fig, ax = plt.subplots(figsize=(7.6, 4.3), dpi=200)
    style_axes(ax)
    ax.axvspan(0, 30, color="#f3e3d3", alpha=0.45, lw=0)
    ax.axvspan(30, 40, color="#e3e8ee", alpha=0.7, lw=0)
    ax.axhline(T_ALLOW, color=LIMIT, lw=1.2, ls="--")
    ax.text(0.6, T_ALLOW + 2.0, "ASME HF-300 limit for SB-96: 93 °C", color=LIMIT, fontsize=8.5)
    for name, h in DESIGNS:
        s = steady[name]
        ax.plot(xmm, s["T"], "-o", color=COL[name], lw=2, ms=4.5, label=f"{name}, h_comb = {h:g} W/m²·K")
        ax.text(40.7, s["T"][-1], f"{name}\nT₈ = {s['T'][-1]:.1f} °C", va="center",
                fontsize=8.5, color=INK)
        ax.annotate(f"T₀ = {s['t_max']:.1f} °C", (0, s["T"][0]), xytext=(6, 7),
                    textcoords="offset points", fontsize=8.5, color=INK)
    ax.text(15, 8, "Cu-Si (SB-96)", ha="center", fontsize=8.5, color=INK2)
    ax.text(35, 8, "Steel", ha="center", fontsize=8.5, color=INK2)
    ax.set_xlim(0, 40)
    ax.set_ylim(0, 130)
    ax.set_xlabel("Position from heated surface, x (mm)")
    ax.set_ylabel("Temperature (°C)")
    ax.legend(loc="center left", fontsize=8.5, frameon=False)
    ax.set_title("Forced-air cooling drops the hottest SB-96 temperature from "
                 f"{so['t_max']:.1f} °C to {sa['t_max']:.1f} °C", fontsize=10.5, color=INK,
                 loc="left", weight="bold")
    fig.savefig(os.path.join(FIG, "fig2_steady_profiles.png"), bbox_inches="tight", facecolor="white")
    plt.close(fig)

    # Figure 3: internal profile T(x) - T(L), identical for both designs
    fig, ax = plt.subplots(figsize=(7.6, 3.6), dpi=200)
    style_axes(ax)
    ax.axvspan(0, 30, color="#f3e3d3", alpha=0.45, lw=0)
    ax.axvspan(30, 40, color="#e3e8ee", alpha=0.7, lw=0)
    rel = so["T"] - so["T"][-1]
    ax.plot(xmm, rel, "-o", color=COL["Adapted"], lw=2, ms=4.5)
    xf = np.linspace(0, 40, 401)
    ax.plot(xf, exact_profile(w, H_ORIG, xf / 1000) - so["T"][-1], color=INK2, lw=0.8)
    ax.text(13, 0.68, f"Cu-Si: slope = q̇₀/k₁ = {Q0/K1:.1f} °C/m", ha="center", fontsize=8.5, color=INK)
    ax.text(35.4, 0.62, f"Steel: slope\n= q̇₀/k₂ = {Q0/K2:.1f} °C/m", ha="center", fontsize=8.5, color=INK)
    ax.set_xlim(0, 40)
    ax.set_ylim(0, 1.35)
    ax.set_xlabel("Position from heated surface, x (mm)")
    ax.set_ylabel("T(x) − T at surface 2 (°C)")
    ax.set_title(f"Inside the wall both designs drop the same {rel[0]:.3f} °C; "
                 "only the surface level moves", fontsize=10.5, color=INK, loc="left", weight="bold")
    fig.savefig(os.path.join(FIG, "fig3_internal_profile.png"), bbox_inches="tight", facecolor="white")
    plt.close(fig)

    # Figure 4: cooldown curves
    fig, ax = plt.subplots(figsize=(7.6, 4.3), dpi=200)
    style_axes(ax)
    ax.axhline(T_TARGET, color=INK2, lw=1, ls="--")
    ax.text(3.6, T_TARGET + 1.5, "target 40 °C", ha="center", fontsize=8.5, color=INK2)
    for name, h in DESIGNS:
        hist = trans[name]["hist_plot"]
        ax.plot(hist[:, 0] / 3600, hist[:, 1], color=COL[name], lw=2,
                label=f"{name}, h_comb = {h:g} W/m²·K (explicit FD, node 0)")
        tl = np.linspace(0, hist[-1, 0], 300)
        ax.plot(tl / 3600, T_INF + (T_START - T_INF) * np.exp(-h * tl / w.c_total),
                color=COL[name], lw=1, ls=":")
        tc = trans[name]["t_cross"] / 3600
        ax.plot(tc, T_TARGET, "o", ms=7, color=COL[name], mec="white", mew=1.5, zorder=4)
        ax.annotate(f"{tc:.2f} h", (tc, T_TARGET), xytext=(10, -18), textcoords="offset points",
                    fontsize=9, color=INK)
    ax.plot([], [], color=INK2, lw=1, ls=":", label="lumped-capacitance check")
    ax.set_xlim(0, trans["Original"]["hist_plot"][-1, 0] / 3600)
    ax.set_ylim(15, 100)
    ax.set_xlabel("Time after the heat flux is switched off (h)")
    ax.set_ylabel("Hottest SB-96 temperature, T₀ (°C)")
    ax.legend(loc="upper right", fontsize=8.5, frameon=False)
    ax.set_title(f"Cooling from 93 °C to 40 °C takes {to['t_cross']/3600:.2f} h originally "
                 f"and {ta['t_cross']/3600:.2f} h with forced air", fontsize=10.5, color=INK,
                 loc="left", weight="bold")
    fig.savefig(os.path.join(FIG, "fig4_cooldown.png"), bbox_inches="tight", facecolor="white")
    plt.close(fig)

    # Figure 5: design chart (two panels, one measure each)
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.6, 6.2), dpi=200, sharex=True)
    for axx in (a1, a2):
        style_axes(axx)
        axx.set_xscale("log")
        axx.axvline(0.1 / w.r_cond, color=AXIS, lw=1)
    a1.plot(sweep[:, 0], sweep[:, 2], color=INK2, lw=2)
    a1.axhline(T_ALLOW, color=LIMIT, lw=1.2, ls="--")
    a1.text(150, T_ALLOW + 3, "93 °C limit", color=LIMIT, fontsize=8.5, ha="center")
    a2.plot(sweep[:, 0], sweep[:, 3], color=INK2, lw=2)
    marks = [("Original", H_ORIG, COL["Original"]), ("Minimum for code", h_min, INK),
             ("Adapted", H_ADAPT, COL["Adapted"])]
    for lab, hv, colr in marks:
        tm = solve_steady(w, hv)["T"][0]
        tcv = cooldown_explicit(w, hv)["t_cross"] / 3600
        a1.plot(hv, tm, "o", ms=8, color=colr, mec="white", mew=1.5, zorder=4)
        a2.plot(hv, tcv, "o", ms=8, color=colr, mec="white", mew=1.5, zorder=4)
        off = (10, 16) if lab == "Adapted" else (10, 0)
        a1.annotate(f"{lab} (h = {hv:.2f})\nT₀ = {tm:.1f} °C", (hv, tm), xytext=off,
                    textcoords="offset points", fontsize=8.5, color=INK, va="center")
        a2.annotate(f"{lab} (h = {hv:.2f})\n{tcv:.2f} h", (hv, tcv), xytext=off,
                    textcoords="offset points", fontsize=8.5, color=INK, va="center")
    a1.text(0.1 / w.r_cond * 1.05, 112, "Bi = 0.1\n(lumped limit)", fontsize=8.5, color=INK2)
    ticks = [5, 10, 20, 50, 100, 200]
    a2.set_xticks(ticks)
    a2.set_xticklabels([str(t) for t in ticks])
    a2.minorticks_off()
    a1.minorticks_off()
    a1.set_ylabel("Hottest SB-96 temp., steady (°C)")
    a2.set_ylabel("Cooldown 93 → 40 °C (h)")
    a2.set_xlabel("Combined heat transfer coefficient, h_comb (W/m²·K, log scale)")
    a1.set_ylim(20, 130)
    a2.set_ylim(0, 9.5)
    a1.set_title("Raising h_comb is the lever: one change fixes compliance and cooling time",
                 fontsize=10.5, color=INK, loc="left", weight="bold")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "fig5_design_chart.png"), bbox_inches="tight", facecolor="white")
    plt.close(fig)

    with open(os.path.join(RES, "run_log.txt"), "w") as fh:
        fh.write("\n".join(LOG_LINES) + "\n")
    log("")
    log(f"Wrote CSV files to {RES} and figures to {FIG}")


if __name__ == "__main__":
    sys.exit(main())
