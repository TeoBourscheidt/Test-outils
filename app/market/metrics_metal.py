
def metric_speculative_net_pos(long, short, open_interest):
    """
    CME: M_Money_Long, M_Money_Short | LME: Funds_Long, Funds_Short
    Interprétation : > 0 Bullish, < 0 Bearish.
    """
    if open_interest == 0 or open_interest is None: return 0
    return ((long - short) / open_interest) * 100

def metric_hedging_pressure(comm_long, comm_short):
    """
    CME: Prod_Merc_Long/Short | LME: Commercial_Long/Short
    Interprétation : > 1 les usines achètent (peur de la hausse). 
    < 1 les miniers vendent (couverture de production).
    """
    if comm_short == 0 or comm_short is None: return 0
    return comm_long / comm_short
def metric_crowding_score_improved(net_position, total_traders, top_traders_count=4):
    """
    Calcule le ratio : Position moyenne par trader / Position totale
    Plus le score est élevé, plus les positions sont concentrées
    """
    if total_traders == 0 or net_position == 0:
        return 0
    
    avg_per_trader = net_position / total_traders
    # Si quelques traders dominent, le ratio sera élevé
    return (avg_per_trader * top_traders_count) / net_position * 100

def metric_spreading_intensity(spreading_pos, open_interest):
    """
    CME: M_Money_Positions_Spread_All
    Interprétation : Si le ratio monte, le marché perd sa directionnelle. 
    Phase de transition ou d'attente.
    """
    if open_interest == 0 or open_interest is None: return 0
    return (spreading_pos / open_interest) * 100

def metric_market_conviction(current_oi, previous_oi):
    """
    Interprétation : 
    Prix Hausse + OI Hausse = Conviction forte (Achat).
    Prix Hausse + OI Baisse = Short Squeeze (Fausse hausse).
    """
    if previous_oi == 0 or previous_oi is None: return 0
    return ((current_oi - previous_oi) / previous_oi) * 100

def metric_commercial_spec_divergence(comm_net_pos, spec_net_pos):
    """
    Mesure la divergence entre industriels et spéculateurs.

    Si les deux sont du même côté : Consensus fort → retourne 0.
    Si opposés : Bataille → retourne l'écart absolu (plus c'est élevé, plus c'est significatif).
    Les commerciaux ont généralement raison à long terme.
    """
    if (comm_net_pos > 0 and spec_net_pos > 0) or (comm_net_pos < 0 and spec_net_pos < 0):
        return 0  # Alignés
    else:
        # Divergence : plus l'écart est grand, plus c'est significatif
        return abs(comm_net_pos - spec_net_pos)
