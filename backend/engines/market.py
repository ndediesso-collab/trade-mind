import pytz
from datetime import datetime
from typing import Dict, Any
from mentor_ia import MarketGuard
class MarketEngine:
    """
    Moteur d'analyse temporelle et environnementale du marché.
    [Rigueur maintenue : Synchronisation UTC stricte pour le Mind Engine, avec export Local]
    """
    def __init__(self):
        self.timezone = pytz.utc
        self.local_timezone = pytz.timezone("Africa/Libreville") # Fuseau horaire Gabon (UTC+1)

        self.guard = MarketGuard()

    def analyze_regime(self) -> Dict[str, Any]:
        """
        Détecte les sessions, les chevauchements (overlap) et définit l'environnement de trading.
        Heures UTC de référence :
        - Londres : 08:00 - 16:00 UTC (09:00 - 17:00 au Gabon)
        - New York : 13:00 - 21:00 UTC (14:00 - 22:00 au Gabon)
        """
        now = datetime.now(self.timezone)
        now_local = now.astimezone(self.local_timezone)
        
        h = now.hour
        m = now.minute
        
        # Heure flottante pour une précision à la minute près (ex: 13.5 = 13:30)
        time_float = h + (m / 60)
        
        # 1. Détection des statuts de sessions
        ny_status = "OPEN" if 13 <= h < 21 else "CLOSED"
        lon_status = "OPEN" if 8 <= h < 16 else "CLOSED"
        
        # 2. Détection du chevauchement critique (Overlap Londres/NY)
        # C'est la période la plus liquide et la plus "toxique" (haute volatilité)
        is_overlap = 13 <= time_float < 16
        
        # 3. Détermination de la toxicité (Régime de marché)
        if ny_status == "CLOSED" and lon_status == "CLOSED":
            environment = "LOW_VOLUME"
        elif is_overlap:
            environment = "HIGH_VOLATILITY_OVERLAP"
        else:
            environment = "STABLE"
            
        # 4. Détection du Pre-Market (30 min avant ouverture NY)
        is_pre_market_ny = 12.5 <= time_float < 13
        sentiment = self.guard.fetch_cnn_index()
        
        return {
            "NY": ny_status,
            "LON": lon_status,
            "is_overlap": is_overlap,
            "is_pre_market_ny": is_pre_market_ny,
            "time_utc": now.strftime("%H:%M"),
            "time_local": now_local.strftime("%H:%M"), # Injection pour ton interface Next.js
            "environment": environment,
            "timestamp": now.timestamp()
        }

    def check_analysis_freshness(self, last_audit_timestamp: float) -> Dict[str, Any]:
        """
        Calcule la validité temporelle de l'analyse (Time Decay).
        Si > 48h, l'analyse est considérée comme périmée pour le mode Swing.
        """
        now = datetime.now(self.timezone).timestamp()
        diff_hours = (now - last_audit_timestamp) / 3600
        
        return {
            "needs_refresh": diff_hours >= 48,
            "hours_since_audit": round(diff_hours, 4),
            "status": "STALE" if diff_hours >= 48 else "FRESH"
        }

    def get_market_sentiment_bias(self, session_type: str) -> str:
        """
        Permet au Mind Engine d'adapter ses attentes selon le régime détecté.
        """
        regime = self.analyze_regime()
        
        if regime["environment"] == "HIGH_VOLATILITY_OVERLAP":
            return "CAUTION_HIGH_SLIPPAGE"
        elif regime["environment"] == "LOW_VOLUME":
            return "WAIT_FOR_LIQUIDITY"
        
        return "STANDARD_EXECUTION"