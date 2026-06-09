from mentor_ia import MarketGuard
import os
from datetime import datetime, timedelta

class BridgeNewsInterface:
    def __init__(self):
        # CORRECTION : On initialise MarketGuard sans aucun argument
        self.guard = MarketGuard()

    def get_live_alerts(self, actif, mode):
        # 1. Macro (avec cache interne de MarketGuard)
        macro_events = self.guard.get_forex_factory_news(actif)
        # Gestion propre au cas où macro_events serait None
        if macro_events is None:
            macro_events = []
            
        high_impact = [e for e in macro_events if "High" in e]
        
        # 2. Géopolitique (via LA méthode corrigée du MarketGuard)
        geo_news = self.guard.get_geopolitical_news(actif, mode=mode)
        
        if not high_impact and not geo_news:
            return None
            
        alert_msg = "⚠️ [ALERTE FLASH]"
        if high_impact:
            alert_msg += f"\n📊 MACRO: {', '.join(high_impact[:2])}"
        if geo_news and isinstance(geo_news, list) and len(geo_news) > 0:
            # On prend la première (la plus récente)
            alert_msg += f"\n🌍 GÉOPOLITIQUE: {geo_news[0]}"
            
        return alert_msg