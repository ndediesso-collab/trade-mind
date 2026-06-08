import logging
from database import (
    recuperer_stats_mind_engine, calculer_capital_total,
    calculer_winrate, get_recent_flux, get_last_active_trade, get_equity_curve
)
from engines.risk import RiskEngine
from engines.market import MarketEngine

# Configuration du logging pour le monitoring
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Instances des moteurs
risk_tool = RiskEngine()
market_tool = MarketEngine()

def psychology_audit(health_score, safety_status, patterns):
    """
    Analyse la cohérence psychologique plafonnée par le risque.
    """
    confidence = health_score
    if safety_status == "CRITICAL": confidence = min(confidence, 30)
    elif safety_status == "LOCKDOWN": confidence = 0
    elif safety_status == "ELEVATED": confidence = min(confidence, 50)

    state = "OPTIMAL"
    if "REVENGE_TRADING" in patterns: state = "TILT_DANGER"
    elif "DISCIPLINE_FRIABLE" in patterns: state = "COGNITIVE_OVERLOAD"
    
    return {
        "state": state,
        "confidence": int(confidence),
        "safety_cap_active": confidence < health_score,
        "patterns": patterns
    }

def get_behavioral_memory(stats, winrate):
    """Analyse des tendances long terme."""
    return {
        "avg_rr_trend": "STABLE" if float(stats.get("rr", 0)) > 1.5 else "DEGRADING",
        "tilt_frequency": "LOW" if int(stats.get("alerts", 0)) < 2 else "HIGH",
        "consistency_score": int(winrate)
    }

def calculer_modulaire_global(stats, winrate, dd_percent, mode):
    """
    Système de scoring adaptatif pondéré.
    """
    s_disc = max(0, 100 - (int(stats.get("alerts", 0)) * 15))
    s_risk = max(0, 100 - (dd_percent * 6))
    
    rr = float(stats.get("rr", 0))
    s_exec = 100 if rr >= 2 else 60

    # Unification des poids incluant le mode INVESTOR
    WEIGHTS = {
        "SCALP": {"disc": 0.3, "risk": 0.2, "exec": 0.5},
        "SCALPING": {"disc": 0.3, "risk": 0.2, "exec": 0.5}, # Alignement format BDD
        "DAILY": {"disc": 0.4, "risk": 0.3, "exec": 0.3},
        "INTRADAY": {"disc": 0.4, "risk": 0.3, "exec": 0.3}, # Alignement format BDD
        "SWING": {"disc": 0.3, "risk": 0.5, "exec": 0.2},
        "INVESTOR": {"disc": 0.2, "risk": 0.7, "exec": 0.1}
    }
    w = WEIGHTS.get(mode.upper(), WEIGHTS["DAILY"])
    
    score_brut = (s_disc * w["disc"]) + (s_risk * w["risk"]) + (s_exec * w["exec"])
    return risk_tool.apply_penalty(score_brut, dd_percent)

def collecter_metriques_completes():
    """
    Point d'entrée principal : Neural Assembly.
    [Ajusté pour supporter l'unification des types Supabase]
    """
    try:
        raw_last_trade = get_last_active_trade()
        
        # Sécurisation Supabase : gestion du retour sous forme de liste ou d'objet direct
        last_trade = None
        if raw_last_trade:
            if isinstance(raw_last_trade, list) and len(raw_last_trade) > 0:
                last_trade = raw_last_trade[0]
            elif isinstance(raw_last_trade, dict):
                last_trade = raw_last_trade

        # On extrait le mode de manière robuste
        mode = last_trade.get("mode", "DAILY") if last_trade else "DAILY"
        
        equity_data = get_equity_curve()
        winrate = float(calculer_winrate() or 0)
        stats_db = recuperer_stats_mind_engine() or {}
        
        stats = {
            "score": round(float(stats_db.get("score", 0)), 1),
            "rr": round(float(stats_db.get("rr", 0)), 2),
            "total": int(stats_db.get("total", 0)),
            "alerts": int(stats_db.get("alerts", 0))
        }

        # 1. Calcul Risque (via RiskEngine)
        max_dd = risk_tool.calculate_true_max_drawdown(equity_data)
        safety = risk_tool.get_safety_status(max_dd, stats)

        # 2. Analyse Marché (via MarketEngine)
        market = market_tool.analyze_regime()

        # 3. Scoring adaptatif
        health_val = calculer_modulaire_global(stats, winrate, max_dd, mode)

        # 4. Psychologie & Patterns
        patterns = []
        if winrate < 35: patterns.append("PERFORMANCE_DIP")
        if stats["alerts"] > 2: patterns.append("DISCIPLINE_FRIABLE")
        if winrate < 30 and stats["total"] > 4: patterns.append("REVENGE_TRADING")

        psy = psychology_audit(health_val, safety, patterns)
        memory = get_behavioral_memory(stats, winrate)

        return {
            "health": {"global": health_val},
            "psychology": psy,
            "behavioral_memory": memory,
            "risk_engine": {
                "status": safety,
                "environment": market.get("environment", "STABLE"),
                "max_drawdown_historical": max_dd
            },
            "capital_total": round(float(calculer_capital_total() or 0), 2),
            "winrate": round(winrate, 1),
            "equity": equity_data,
            "recent_flux": get_recent_flux(limit=10),
            "sessions": market,
            "focus": {
                "actif": last_trade.get("actif", "N/A") if last_trade else "N/A",
                "mode": mode,
                "type": last_trade.get("type", "INTRADAY") if last_trade else "INTRADAY",
                "conviction": last_trade.get("conviction", 0) if last_trade else 0
            } if last_trade else None
        }
    except Exception as e:
        logging.error(f"❌ Erreur critique Mind Engine : {e}")
        return {"status": "LOCKDOWN", "error": str(e)}

def collecter_metriques_completes_api():
    """Fonction helper pour api.py qui appelle le manager"""
    return collecter_metriques_completes()