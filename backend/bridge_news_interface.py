from mentor_ia import MarketGuard
import os
from datetime import datetime, timedelta

class BridgeNewsInterface:
    def __init__(self):
        # On passe la clé NewsAPI aussi si nécessaire
        self.guard = MarketGuard(os.getenv("POLYGON_API_KEY"))

    def get_live_alerts(self, actif, mode):
        # 1. Macro (avec cache interne de MarketGuard)
        macro_events = self.guard.get_forex_factory_news(actif)
        high_impact = [e for e in macro_events if "High" in e]
        
        # 2. Géopolitique (on utilise LA méthode corrigée du MarketGuard)
        # Elle gère déjà le tri et le filtre de date.
        geo_news = self.guard.get_geopolitical_news(actif, mode=mode)
        
        if not high_impact and not geo_news:
            return None
            
        alert_msg = "⚠️ [ALERTE FLASH]"
        if high_impact:
            alert_msg += f"\n📊 MACRO: {', '.join(high_impact[:2])}"
        if geo_news:
            # On prend la première (la plus récente)
            alert_msg += f"\n🌍 GÉOPOLITIQUE: {geo_news[0]}"
            
        return alert_msg