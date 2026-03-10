import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.stats import norm
import warnings



def run():
    warnings.filterwarnings("ignore")
    st.set_page_config(
        page_title="Options Strategy Lab",
        page_icon="◈",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    st.markdown("""
    <style>
    [data-testid="stSidebar"]        { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    .block-container { padding-top: 2rem; max-width: 1400px; }
    .section-title {
        font-size: 0.72rem; font-weight: 700; text-transform: uppercase;
        letter-spacing: 0.1em; opacity: 0.55; margin-bottom: 4px; margin-top: 4px;
    }
    .be-row  { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 8px; }
    .be-chip {
        background: rgba(22,163,74,0.12); border: 1px solid rgba(22,163,74,0.4);
        color: #16a34a; border-radius: 4px; padding: 3px 12px;
        font-size: 0.78rem; font-weight: 600;
    }
    .leg-header {
        font-size: 0.72rem; font-weight: 700; text-transform: uppercase;
        letter-spacing: 0.08em; opacity: 0.5; margin-bottom: 6px;
    }
    </style>
    """, unsafe_allow_html=True)


    # ══════════════════════════════════════════════
    #  BLACK-SCHOLES CORE
    # ══════════════════════════════════════════════
    def bs_d1_d2(S, K, T, r, sigma, q=0.0):
        """Retourne (d1, d2) ou (nan, nan) si les inputs sont invalides."""
        if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
            return np.nan, np.nan
        d1 = (np.log(S / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        return d1, d1 - sigma * np.sqrt(T)


    def bs_price(S, K, T, r, sigma, option_type="call", q=0.0):
        """Prix Black-Scholes avec dividendes continus q."""
        if T <= 0:
            return max(S - K, 0.0) if option_type == "call" else max(K - S, 0.0)
        d1, d2 = bs_d1_d2(S, K, T, r, sigma, q)
        if np.isnan(d1):
            return 0.0
        disc_S = S * np.exp(-q * T)
        disc_K = K * np.exp(-r * T)
        if option_type == "call":
            return disc_S * norm.cdf(d1) - disc_K * norm.cdf(d2)
        return disc_K * norm.cdf(-d2) - disc_S * norm.cdf(-d1)


    def bs_greeks(S, K, T, r, sigma, option_type="call", q=0.0):
        """
        Greeks complets :
        delta, gamma, vega (/1% σ), theta (/jour), rho (/1% r),
        vanna, charm (/jour), volga.
        Retourne des zéros si T ou sigma sont quasi-nuls.
        """
        zero = dict(delta=0.0, gamma=0.0, vega=0.0, theta=0.0,
                    rho=0.0, vanna=0.0, charm=0.0, volga=0.0)
        if T <= 1e-6 or sigma <= 1e-6:
            return zero

        d1, d2 = bs_d1_d2(S, K, T, r, sigma, q)
        if np.isnan(d1):
            return zero

        n_d1   = norm.pdf(d1)
        sqT    = np.sqrt(T)
        disc_S = np.exp(-q * T)
        disc_K = np.exp(-r * T)

        # ── Delta ──
        delta = disc_S * norm.cdf(d1) if option_type == "call" else -disc_S * norm.cdf(-d1)

        # ── Gamma (identique call / put) ──
        gamma = disc_S * n_d1 / (S * sigma * sqT)

        # ── Vega par 1 % de vol ──
        vega = S * disc_S * n_d1 * sqT / 100.0

        # ── Theta par jour calendaire ──
        base_theta = -(S * disc_S * n_d1 * sigma) / (2.0 * sqT)
        if option_type == "call":
            theta = (base_theta
                    - r * K * disc_K * norm.cdf(d2)
                    + q * S * disc_S * norm.cdf(d1)) / 365.0
            rho   =  K * T * disc_K * norm.cdf(d2)  / 100.0
            charm = -disc_S * (n_d1 * ((r - q) / (sigma * sqT) - d2 / (2.0 * T))
                            + q * norm.cdf(d1))
        else:
            theta = (base_theta
                    + r * K * disc_K * norm.cdf(-d2)
                    - q * S * disc_S * norm.cdf(-d1)) / 365.0
            rho   = -K * T * disc_K * norm.cdf(-d2) / 100.0
            charm = -disc_S * (n_d1 * ((r - q) / (sigma * sqT) - d2 / (2.0 * T))
                            - q * norm.cdf(-d1))

        # ── Vanna = d(Delta)/d(sigma) ──
        vanna = -disc_S * n_d1 * d2 / sigma

        # ── Charm par jour = d(Delta)/d(t) ──
        charm = charm / 365.0

        # ── Volga = d(Vega)/d(sigma) par 1 % ──
        volga = vega * 100.0 * d1 * d2 / sigma

        return dict(delta=delta, gamma=gamma, vega=vega, theta=theta,
                    rho=rho, vanna=vanna, charm=charm, volga=volga)


    def moneyness_label(S, K):
        ratio = S / K
        if   ratio > 1.03: return "ITM Call / OTM Put"
        elif ratio < 0.97: return "OTM Call / ITM Put"
        return "ATM"


    def strategy_payoff(legs, S_range, r=0.0, q=0.0):
        """Payoff à expiry + valeur BS + Greeks agrégés sur toute la plage de spots."""
        n = len(S_range)
        payoffs = np.zeros(n); values = np.zeros(n)
        deltas  = np.zeros(n); gammas = np.zeros(n)
        vegas   = np.zeros(n); thetas = np.zeros(n); rhos = np.zeros(n)
        for leg in legs:
            K, T, sigma  = leg["strike"], leg["maturity"], leg["vol"]
            otype        = leg["type"]
            pos, qty, prem = leg["position"], leg["quantity"], leg["premium"]
            for i, S in enumerate(S_range):
                intrinsic   = max(S - K, 0.0) if otype == "call" else max(K - S, 0.0)
                payoffs[i] += pos * qty * (intrinsic - prem)
                values[i]  += pos * qty * (bs_price(S, K, T, r, sigma, otype, q) - prem)
                g           = bs_greeks(S, K, T, r, sigma, otype, q)
                deltas[i]  += pos * qty * g["delta"]
                gammas[i]  += pos * qty * g["gamma"]
                vegas[i]   += pos * qty * g["vega"]
                thetas[i]  += pos * qty * g["theta"]
                rhos[i]    += pos * qty * g["rho"]
        return payoffs, values, deltas, gammas, vegas, thetas, rhos


    def leg_time_remaining(T_rem, leg_maturity, max_T):
        """
        Temps restant RÉEL pour une jambe individuelle.
        Indispensable pour les calendar spreads : la jambe courte peut
        avoir expiré avant que la jambe longue arrive à maturité.

        T_rem      : temps restant par rapport à la jambe la plus longue (max_T)
        leg_maturity : maturité initiale de cette jambe
        max_T      : maturité de la jambe la plus longue de la stratégie
        """
        return max(0.0, leg_maturity - (max_T - T_rem))


    # ══════════════════════════════════════════════
    #  SESSION STATE
    # ══════════════════════════════════════════════
    T_DEF = 30 / 365

    def default_leg(spot, vol_decimal):
        return {"type": "call", "position": "Long", "strike": float(spot),
                "maturity": T_DEF, "vol": float(vol_decimal),
                "quantity": 1, "premium": 0.0}

    if "legs"          not in st.session_state:
        st.session_state.legs = [default_leg(100.0, 0.20)]
    if "preset_loaded" not in st.session_state:
        st.session_state.preset_loaded = "— Custom —"
    if "custom_n_legs" not in st.session_state:
        st.session_state.custom_n_legs = 1
    if "legs_version"  not in st.session_state:
        st.session_state.legs_version = 0


    # ══════════════════════════════════════════════
    #  HEADER
    # ══════════════════════════════════════════════
    st.title("◈ Options Strategy Lab")
    st.caption("Black-Scholes · Greeks · Payoff Diagrams · Scenario Analysis")
    st.divider()


    # ══════════════════════════════════════════════
    #  SECTION 1 — MARKET PARAMS
    # ══════════════════════════════════════════════
    st.markdown('<p class="section-title">Paramètres du marché</p>', unsafe_allow_html=True)
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1: spot        = st.number_input("Spot (S)",             value=100.0, min_value=0.01, step=0.5,  format="%.2f")
    with c2: r_rate      = st.number_input("Taux sans risque (%)", value=5.0,   min_value=0.0,  max_value=30.0,  step=0.1, format="%.2f") / 100
    with c3: q           = st.number_input("Div. Yield q (%)",     value=0.0,   min_value=0.0,  max_value=20.0,  step=0.1, format="%.2f") / 100
    with c4: default_vol = st.number_input("Vol. défaut σ (%)",    value=20.0,  min_value=0.1,  max_value=200.0, step=0.5, format="%.2f")
    with c5:
        spot_range_pct = st.slider("Plage graphiques ± (%)", min_value=5, max_value=60, value=30, step=5,
                                    help="Étendue de l'axe X. Ex : ±30 % avec Spot=100 → axe 70–130.")
    with c6:
        show_current = st.checkbox("Afficher valeur T>0", value=True,
                                    help="Trace la valeur BS actuelle (avant expiry) en pointillés.")
    st.divider()


    # ══════════════════════════════════════════════
    #  SECTION 2 — STRATEGY BUILDER
    # ══════════════════════════════════════════════
    st.markdown('<p class="section-title">Construction de la stratégie</p>', unsafe_allow_html=True)

    dv  = default_vol / 100.0
    K_p = spot

    PRESETS = {
        "Long Call":          [{"type":"call","position":"Long", "strike":K_p,       "maturity":T_DEF,  "vol":dv,"quantity":1,"premium":0.0}],
        "Long Put":           [{"type":"put", "position":"Long", "strike":K_p,       "maturity":T_DEF,  "vol":dv,"quantity":1,"premium":0.0}],
        "Short Call (naked)": [{"type":"call","position":"Short","strike":K_p,       "maturity":T_DEF,  "vol":dv,"quantity":1,"premium":0.0}],
        "Short Put (naked)":  [{"type":"put", "position":"Short","strike":K_p,       "maturity":T_DEF,  "vol":dv,"quantity":1,"premium":0.0}],
        "Bull Call Spread":   [{"type":"call","position":"Long", "strike":K_p*0.97,  "maturity":T_DEF,  "vol":dv,"quantity":1,"premium":0.0},
                            {"type":"call","position":"Short","strike":K_p*1.03,  "maturity":T_DEF,  "vol":dv,"quantity":1,"premium":0.0}],
        "Bear Put Spread":    [{"type":"put", "position":"Long", "strike":K_p*1.03,  "maturity":T_DEF,  "vol":dv,"quantity":1,"premium":0.0},
                            {"type":"put", "position":"Short","strike":K_p*0.97,  "maturity":T_DEF,  "vol":dv,"quantity":1,"premium":0.0}],
        "Long Straddle":      [{"type":"call","position":"Long", "strike":K_p,       "maturity":T_DEF,  "vol":dv,"quantity":1,"premium":0.0},
                            {"type":"put", "position":"Long", "strike":K_p,       "maturity":T_DEF,  "vol":dv,"quantity":1,"premium":0.0}],
        "Short Straddle":     [{"type":"call","position":"Short","strike":K_p,       "maturity":T_DEF,  "vol":dv,"quantity":1,"premium":0.0},
                            {"type":"put", "position":"Short","strike":K_p,       "maturity":T_DEF,  "vol":dv,"quantity":1,"premium":0.0}],
        "Long Strangle":      [{"type":"call","position":"Long", "strike":K_p*1.05,  "maturity":T_DEF,  "vol":dv,"quantity":1,"premium":0.0},
                            {"type":"put", "position":"Long", "strike":K_p*0.95,  "maturity":T_DEF,  "vol":dv,"quantity":1,"premium":0.0}],
        "Iron Condor":        [{"type":"put", "position":"Long", "strike":K_p*0.90,  "maturity":T_DEF,  "vol":dv,"quantity":1,"premium":0.0},
                            {"type":"put", "position":"Short","strike":K_p*0.95,  "maturity":T_DEF,  "vol":dv,"quantity":1,"premium":0.0},
                            {"type":"call","position":"Short","strike":K_p*1.05,  "maturity":T_DEF,  "vol":dv,"quantity":1,"premium":0.0},
                            {"type":"call","position":"Long", "strike":K_p*1.10,  "maturity":T_DEF,  "vol":dv,"quantity":1,"premium":0.0}],
        "Butterfly (Call)":   [{"type":"call","position":"Long", "strike":K_p*0.95,  "maturity":T_DEF,  "vol":dv,"quantity":1,"premium":0.0},
                            {"type":"call","position":"Short","strike":K_p,       "maturity":T_DEF,  "vol":dv,"quantity":2,"premium":0.0},
                            {"type":"call","position":"Long", "strike":K_p*1.05,  "maturity":T_DEF,  "vol":dv,"quantity":1,"premium":0.0}],
        "Covered Call":       [{"type":"call","position":"Short","strike":K_p*1.05,  "maturity":T_DEF,  "vol":dv,"quantity":1,"premium":0.0}],
        "Protective Put":     [{"type":"put", "position":"Long", "strike":K_p*0.95,  "maturity":T_DEF,  "vol":dv,"quantity":1,"premium":0.0}],
        "Risk Reversal":      [{"type":"call","position":"Long", "strike":K_p*1.05,  "maturity":T_DEF,  "vol":dv,"quantity":1,"premium":0.0},
                            {"type":"put", "position":"Short","strike":K_p*0.95,  "maturity":T_DEF,  "vol":dv,"quantity":1,"premium":0.0}],
        "Calendar Spread":    [{"type":"call","position":"Long", "strike":K_p,       "maturity":60/365, "vol":dv,"quantity":1,"premium":0.0},
                            {"type":"call","position":"Short","strike":K_p,       "maturity":T_DEF,  "vol":dv,"quantity":1,"premium":0.0}],
        "Ratio Back Spread":  [{"type":"call","position":"Short","strike":K_p*0.97,  "maturity":T_DEF,  "vol":dv,"quantity":1,"premium":0.0},
                            {"type":"call","position":"Long", "strike":K_p*1.03,  "maturity":T_DEF,  "vol":dv,"quantity":2,"premium":0.0}],
    }

    # ── Ligne : sélecteur preset  +  (si Custom) nombre de jambes ───────────────
    # IMPORTANT : on gère les changements d'état AVANT de rendre les widgets
    # des jambes, afin que les clés incluent legs_version et forcent Streamlit
    # à recréer les widgets avec les nouvelles valeurs (pas les anciennes).

    col_pre, col_n, col_pad = st.columns([3, 2, 3])

    with col_pre:
        preset = st.selectbox(
            "Stratégie",
            ["— Custom —"] + list(PRESETS.keys()),
            key="preset_select",
            label_visibility="collapsed",
        )

    is_custom = (preset == "— Custom —")

    # ── Chargement d'un preset ───────────────────────────────────────────────────
    # On met à jour session_state ICI (avant le rendu des jambes) et on incrémente
    # legs_version pour invalider les anciens widgets Streamlit.
    if not is_custom and preset != st.session_state.preset_loaded:
        st.session_state.legs          = [leg.copy() for leg in PRESETS[preset]]
        st.session_state.custom_n_legs = len(st.session_state.legs)
        st.session_state.preset_loaded = preset
        st.session_state.legs_version += 1   # invalide les anciens widgets

    # ── Gestion du nombre de jambes en mode Custom ───────────────────────────────
    with col_n:
        if is_custom:
            new_n = st.number_input(
                "Nombre de jambes",
                min_value=1, max_value=10,
                value=st.session_state.custom_n_legs,
                step=1,
                key="custom_n_input",
                help="Modifie instantanément le nombre de jambes.",
            )
            current = st.session_state.legs
            if new_n != len(current):
                if new_n > len(current):
                    for _ in range(new_n - len(current)):
                        current.append(default_leg(spot, dv))
                else:
                    del current[new_n:]
                st.session_state.legs          = current
                st.session_state.custom_n_legs = new_n
                st.session_state.legs_version += 1   # invalide les anciens widgets
            if st.session_state.preset_loaded != "— Custom —":
                st.session_state.preset_loaded  = "— Custom —"

    # Version courante — intégrée dans toutes les clés de widgets des jambes
    _v   = st.session_state.legs_version
    legs = st.session_state.legs

    st.markdown("---")

    # ── Affichage des jambes en colonnes (max MAX_COLS par ligne) ────────────────
    MAX_COLS = 5

    for row_start in range(0, len(legs), MAX_COLS):
        row_legs = legs[row_start : row_start + MAX_COLS]
        cols     = st.columns(len(row_legs))

        for col_idx, (col, leg) in enumerate(zip(cols, row_legs)):
            i        = row_start + col_idx
            pos_icon = "🟢" if leg["position"] == "Long" else "🔴"

            with col:
                st.markdown(
                    f'<div class="leg-header">{pos_icon} Jambe {i+1} · '
                    f'{leg["position"].upper()} {leg["type"].upper()}</div>',
                    unsafe_allow_html=True,
                )
                # Clés préfixées par _v : recréées à chaque changement de preset/nb jambes
                leg["type"] = st.selectbox(
                    "Type", ["call", "put"],
                    index=0 if leg["type"] == "call" else 1,
                    key=f"type_{_v}_{i}",
                )
                leg["position"] = st.selectbox(
                    "Position", ["Long", "Short"],
                    index=0 if leg["position"] == "Long" else 1,
                    key=f"pos_{_v}_{i}",
                )
                leg["quantity"] = st.number_input(
                    "Quantité", value=int(leg["quantity"]),
                    min_value=1, max_value=1000, step=1,
                    key=f"qty_{_v}_{i}",
                )
                leg["strike"] = st.number_input(
                    "Strike (K)", value=float(leg["strike"]),
                    min_value=0.01, step=0.5, format="%.2f",
                    key=f"K_{_v}_{i}",
                )
                leg["maturity"] = st.number_input(
                    "Maturité (jours)", value=int(round(leg["maturity"] * 365)),
                    min_value=1, max_value=730, step=1,
                    key=f"T_{_v}_{i}",
                ) / 365.0
                leg["vol"] = st.number_input(
                    "Vol σ (%)", value=float(leg["vol"] * 100),
                    min_value=0.1, max_value=300.0, step=0.5, format="%.1f",
                    key=f"vol_{_v}_{i}",
                ) / 100.0
                leg["premium"] = st.number_input(
                    "Prime (0 = auto BS)", value=float(leg["premium"]),
                    min_value=0.0, step=0.01, format="%.4f",
                    key=f"prem_{_v}_{i}",
                    help="Laisser à 0 pour calculer automatiquement le prix Black-Scholes.",
                )

        if row_start + MAX_COLS < len(legs):
            st.markdown("---")

    st.divider()


    # ══════════════════════════════════════════════
    #  CALCULS PRINCIPAUX
    # ══════════════════════════════════════════════
    if not st.session_state.legs:
        st.warning("Configurez au moins une jambe pour analyser la stratégie.")
        st.stop()

    # Résoudre les primes auto-BS et ajouter position_sign
    legs_processed = []
    for leg in st.session_state.legs:
        lp = leg.copy()
        lp["position_sign"] = 1 if lp["position"] == "Long" else -1
        if lp["premium"] == 0.0:
            lp["premium"] = bs_price(spot, lp["strike"], lp["maturity"],
                                    r_rate, lp["vol"], lp["type"], q)
        legs_processed.append(lp)

    # Plage de spots
    S_min   = spot * (1.0 - spot_range_pct / 100.0)
    S_max   = spot * (1.0 + spot_range_pct / 100.0)
    S_range = np.linspace(S_min, S_max, 500)

    legs_for_payoff = [
        {"type": l["type"], "position": l["position_sign"], "strike": l["strike"],
        "maturity": l["maturity"], "vol": l["vol"],
        "quantity": l["quantity"], "premium": l["premium"]}
        for l in legs_processed
    ]
    payoffs, values, deltas, gammas, vegas, thetas, rhos = strategy_payoff(
        legs_for_payoff, S_range, r_rate, q
    )

    def agg(key):
        return sum(
            l["position_sign"] * l["quantity"] *
            bs_greeks(spot, l["strike"], l["maturity"], r_rate, l["vol"], l["type"], q)[key]
            for l in legs_processed
        )

    total_cost = sum(l["position_sign"] * l["quantity"] * l["premium"] for l in legs_processed)
    max_profit = float(np.max(payoffs))
    max_loss   = float(np.min(payoffs))

    breakevens = []
    for i in range(len(payoffs) - 1):
        if payoffs[i] * payoffs[i + 1] < 0:
            be = S_range[i] - payoffs[i] * (S_range[i+1] - S_range[i]) / (payoffs[i+1] - payoffs[i])
            breakevens.append(round(float(be), 2))


    # ══════════════════════════════════════════════
    #  RÉSUMÉ MÉTRIQUES
    # ══════════════════════════════════════════════
    st.markdown('<p class="section-title">Résumé au spot</p>', unsafe_allow_html=True)
    m1, m2, m3, m4, m5, m6, m7, m8 = st.columns(8)
    m1.metric("Prime Nette",   f"{total_cost:+.3f}",
            delta="débit" if total_cost < 0 else "crédit",
            delta_color="inverse" if total_cost < 0 else "normal")
    m2.metric("Δ Delta",       f"{agg('delta'):+.4f}", help="Sensibilité au prix spot")
    m3.metric("Γ Gamma",       f"{agg('gamma'):+.4f}", help="Variation du delta par unité de spot")
    m4.metric("ν Vega /1%σ",   f"{agg('vega'):+.4f}",  help="Gain/perte pour +1 % de vol implicite")
    m5.metric("Θ Theta /jour", f"{agg('theta'):+.4f}", help="Gain/perte par jour écoulé")
    m6.metric("ρ Rho /1%r",    f"{agg('rho'):+.4f}",   help="Gain/perte pour +1 % du taux sans risque")
    m7.metric("Profit Max",    f"{max_profit:.2f}" if max_profit < 1e8 else "∞")
    m8.metric("Perte Max",     f"{max_loss:.2f}"   if max_loss  > -1e8 else "-∞")

    if breakevens:
        chips = "".join(f'<span class="be-chip">⚡ BE {be}</span>' for be in breakevens)
        st.markdown(f'<div class="be-row">{chips}</div>', unsafe_allow_html=True)
        st.write("")
    st.divider()


    # ══════════════════════════════════════════════
    #  ONGLETS
    # ══════════════════════════════════════════════
    tab1, tab2, tab3, tab4, tab6 = st.tabs([
        "📈 Payoff", "🧮 Greeks", "🌊 Greeks vs Vol",
        "⏳ Time Decay", "📋 Détail Jambes"
    ])

    # ── TAB 1 — PAYOFF ──────────────────────────────────────────────────────────
    with tab1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=S_range, y=np.where(payoffs >= 0, payoffs, 0),
            fill="tozeroy", fillcolor="rgba(22,163,74,0.08)",
            line=dict(width=0), showlegend=False, hoverinfo="skip"))
        fig.add_trace(go.Scatter(
            x=S_range, y=np.where(payoffs <= 0, payoffs, 0),
            fill="tozeroy", fillcolor="rgba(220,38,38,0.08)",
            line=dict(width=0), showlegend=False, hoverinfo="skip"))
        if show_current:
            fig.add_trace(go.Scatter(
                x=S_range, y=values, name="Valeur actuelle (T>0)",
                line=dict(width=2, dash="dot"),
                hovertemplate="S=%{x:.2f}<br>P&L=%{y:.4f}<extra></extra>"))
        fig.add_trace(go.Scatter(
            x=S_range, y=payoffs, name="Payoff à expiry",
            line=dict(width=2.5),
            hovertemplate="S=%{x:.2f}<br>Payoff=%{y:.4f}<extra></extra>"))
        fig.add_hline(y=0, line=dict(width=1, dash="dot", color="gray"))
        fig.add_vline(x=float(spot), line=dict(width=1.5, dash="dash"),
                    annotation_text=f"Spot {spot:.2f}", annotation_position="top right")
        for l in legs_processed:
            fig.add_vline(x=float(l["strike"]), line=dict(width=1, dash="dot"),
                        annotation_text=f"K={l['strike']:.0f}{'C' if l['type']=='call' else 'P'}",
                        annotation_position="top", annotation_font_size=10)
        for be in breakevens:
            fig.add_vline(x=float(be), line=dict(width=1.5, dash="dashdot", color="green"),
                        annotation_text=f"BE {be}", annotation_position="bottom right",
                        annotation_font=dict(color="green", size=10))
        fig.update_layout(
            title="Diagramme de Payoff — stratégie complète",
            xaxis_title="Prix sous-jacent (S)", yaxis_title="P&L",
            height=500, margin=dict(l=50, r=20, t=45, b=45),
            legend=dict(orientation="h", y=1.02),
            xaxis=dict(range=[S_min, S_max]))
        st.plotly_chart(fig, use_container_width=True)

    # ── TAB 2 — GREEKS vs SPOT ──────────────────────────────────────────────────
    with tab2:
        fig2 = make_subplots(rows=2, cols=3,
            subplot_titles=["Δ Delta","Γ Gamma","ν Vega","Θ Theta /jour","ρ Rho","P&L à expiry"],
            vertical_spacing=0.16, horizontal_spacing=0.09)
        for data, name, row, col in [
            (deltas,"Delta",1,1),(gammas,"Gamma",1,2),(vegas,"Vega",1,3),
            (thetas,"Theta",2,1),(rhos,"Rho",2,2),(payoffs,"Payoff",2,3),
        ]:
            fig2.add_trace(go.Scatter(
                x=S_range, y=data, name=name, line=dict(width=2),
                hovertemplate=f"S=%{{x:.2f}}<br>{name}=%{{y:.4f}}<extra></extra>"),
                row=row, col=col)
            fig2.add_hline(y=0, line=dict(width=1, dash="dot", color="gray"), row=row, col=col)
            fig2.add_vline(x=float(spot), line=dict(width=1, dash="dash"), row=row, col=col)
        fig2.update_layout(height=600, showlegend=False,
                        title="Profil des Greeks en fonction du prix sous-jacent",
                        margin=dict(l=50, r=20, t=55, b=45))
        st.plotly_chart(fig2, use_container_width=True)

    # ── TAB 3 — GREEKS vs VOL ───────────────────────────────────────────────────
    with tab3:
        vol_range = np.linspace(0.01, 1.5, 200)
        vd, vg, vv, vt = [], [], [], []
        for vol in vol_range:
            d = g = v = t = 0.0
            for l in legs_processed:
                gr = bs_greeks(spot, l["strike"], l["maturity"], r_rate, vol, l["type"], q)
                d += l["position_sign"] * l["quantity"] * gr["delta"]
                g += l["position_sign"] * l["quantity"] * gr["gamma"]
                v += l["position_sign"] * l["quantity"] * gr["vega"]
                t += l["position_sign"] * l["quantity"] * gr["theta"]
            vd.append(d); vg.append(g); vv.append(v); vt.append(t)

        # Vol de référence = moyenne des vols des jambes (évite crash si une seule jambe)
        ref_vol = float(np.mean([l["vol"] for l in legs_processed])) * 100.0

        fig3 = make_subplots(rows=2, cols=2,
            subplot_titles=["Δ Delta vs Vol","Γ Gamma vs Vol","ν Vega vs Vol","Θ Theta vs Vol"],
            vertical_spacing=0.16, horizontal_spacing=0.1)
        for data, name, row, col in [
            (vd,"Delta",1,1),(vg,"Gamma",1,2),(vv,"Vega",2,1),(vt,"Theta",2,2)
        ]:
            fig3.add_trace(go.Scatter(
                x=vol_range * 100, y=data, name=name, line=dict(width=2),
                hovertemplate=f"σ=%{{x:.1f}}%<br>{name}=%{{y:.4f}}<extra></extra>"),
                row=row, col=col)
            fig3.add_hline(y=0, line=dict(width=1, dash="dot", color="gray"), row=row, col=col)
            fig3.add_vline(x=ref_vol, line=dict(width=1, dash="dash"), row=row, col=col)
        fig3.update_xaxes(title_text="Vol implicite (%)")
        fig3.update_layout(height=530, showlegend=False,
                        title="Sensibilité des Greeks à la Volatilité Implicite",
                        margin=dict(l=50, r=20, t=55, b=45))
        st.plotly_chart(fig3, use_container_width=True)

    # ── TAB 4 — TIME DECAY ──────────────────────────────────────────────────────
    with tab4:
        max_T   = max(l["maturity"] for l in legs_processed)
        t_steps = np.linspace(max_T, 1.0 / 365, 100)

        smults  = {0.90: [], 0.95: [], 1.00: [], 1.05: [], 1.10: []}
        th_time = []

        for T_rem in t_steps:
            for mult in smults:
                S_t = spot * mult
                smults[mult].append(sum(
                    l["position_sign"] * l["quantity"] * (
                        bs_price(S_t, l["strike"],
                                leg_time_remaining(T_rem, l["maturity"], max_T),
                                r_rate, l["vol"], l["type"], q)
                        - l["premium"]
                    ) for l in legs_processed
                ))
            th_time.append(sum(
                l["position_sign"] * l["quantity"] *
                bs_greeks(spot, l["strike"],
                        leg_time_remaining(T_rem, l["maturity"], max_T),
                        r_rate, l["vol"], l["type"], q)["theta"]
                for l in legs_processed
            ))

        days   = [t * 365 for t in t_steps]
        labels = {0.90:"S×0.90", 0.95:"S×0.95", 1.00:"Au Spot", 1.05:"S×1.05", 1.10:"S×1.10"}

        fig4 = make_subplots(rows=1, cols=2,
            subplot_titles=["P&L selon le temps restant","Theta en fonction du temps"],
            horizontal_spacing=0.1)
        for mult in [0.90, 0.95, 1.00, 1.05, 1.10]:
            fig4.add_trace(go.Scatter(
                x=days, y=smults[mult], name=labels[mult], line=dict(width=2),
                hovertemplate="Jours=%{x:.0f}<br>P&L=%{y:.4f}<extra></extra>"),
                row=1, col=1)
        fig4.add_trace(go.Scatter(
            x=days, y=th_time, name="Theta", line=dict(width=2, color="orange"),
            hovertemplate="Jours=%{x:.0f}<br>Θ=%{y:.5f}<extra></extra>"),
            row=1, col=2)
        fig4.add_hline(y=0, line=dict(width=1, dash="dot", color="gray"), row=1, col=1)
        fig4.add_hline(y=0, line=dict(width=1, dash="dot", color="gray"), row=1, col=2)
        fig4.update_xaxes(title_text="Jours restants", autorange="reversed")
        fig4.update_layout(height=430, title="Analyse de la Décroissance Temporelle",
                        margin=dict(l=50, r=20, t=55, b=45))
        st.plotly_chart(fig4, use_container_width=True)

   
    with tab6:
        rows = []
        for i, l in enumerate(legs_processed):
            gr   = bs_greeks(spot, l["strike"], l["maturity"], r_rate, l["vol"], l["type"], q)
            theo = bs_price(spot, l["strike"], l["maturity"], r_rate, l["vol"], l["type"], q)
            ps   = l["position_sign"]
            rows.append({
                "Leg":       i + 1,
                "Type":      l["type"].upper(),
                "Pos.":      l["position"],
                "Qté":       l["quantity"],
                "Strike":    f"{l['strike']:.2f}",
                "Moneyness": moneyness_label(spot, l["strike"]),
                "Mat.(j)":   f"{l['maturity']*365:.0f}",
                "σ (%)":     f"{l['vol']*100:.1f}",
                "Prix BS":   f"{theo:.4f}",
                "Prime":     f"{l['premium']:.4f}",
                "Δ":         f"{ps*l['quantity']*gr['delta']:+.4f}",
                "Γ":         f"{ps*l['quantity']*gr['gamma']:+.4f}",
                "ν":         f"{ps*l['quantity']*gr['vega']:+.4f}",
                "Θ":         f"{ps*l['quantity']*gr['theta']:+.4f}",
                "ρ":         f"{ps*l['quantity']*gr['rho']:+.4f}",
                "Vanna":     f"{ps*l['quantity']*gr['vanna']:+.4f}",
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        st.divider()
        st.markdown('<p class="section-title">Grille de Scénarios P&L</p>', unsafe_allow_html=True)
        st.caption("Lignes = choc de vol multiplié à chaque jambe · Colonnes = prix sous-jacent")

        spot_sc   = [spot * m for m in [0.85, 0.90, 0.95, 0.97, 1.00, 1.03, 1.05, 1.10, 1.15]]
        vol_mults = [0.70, 0.85, 1.00, 1.15, 1.30]
        grid = []
        for vm in vol_mults:
            row_data = {"Choc Vol": f"×{vm:.2f}"}
            for S_sc in spot_sc:
                val = sum(
                    l["position_sign"] * l["quantity"] * (
                        bs_price(S_sc, l["strike"], l["maturity"], r_rate,
                                l["vol"] * vm, l["type"], q)
                        - l["premium"]
                    ) for l in legs_processed
                )
                row_data[f"S={S_sc:.0f}"] = f"{val:+.2f}"
            grid.append(row_data)

        df_grid  = pd.DataFrame(grid)
        pnl_cols = [c for c in df_grid.columns if c != "Choc Vol"]

        def color_pnl(val):
            try:
                v = float(val)
                if   v > 0: return "color:#16a34a; font-weight:600"
                elif v < 0: return "color:#dc2626; font-weight:600"
            except Exception:
                pass
            return ""

        try:
            styled = df_grid.style.map(color_pnl, subset=pnl_cols)
        except AttributeError:
            styled = df_grid.style.applymap(color_pnl, subset=pnl_cols)

        st.dataframe(styled, use_container_width=True, hide_index=True)

    st.divider()
    st.caption("Options Strategy Lab · Modèle Black-Scholes · Usage éducatif uniquement · Pas de conseil financier")