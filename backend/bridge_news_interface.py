# bridge_news_interface.py
from mentor_ia import MarketGuard
import os

class BridgeNewsInterface:
    def __init__(self):
        self.guard = MarketGuard(os.getenv("POLYGON_API_KEY"))

    def get_live_alerts(self, actif, mode):
        """
        Cette fonction est appelée par ton frontend pour mettre à jour la console IA.
        """
        # 1. Récupération des News Macro (ForexFactory)
        macro_events = self.guard.get_forex_factory_news(actif)
        # On ne garde que le "High Impact" pour le mode Scalp
        high_impact = [e for e in macro_events if "High" in e]
        
        # 2. Récupération Géopolitique
        geo_news = self.guard.get_geopolitical_news(actif, mode=mode)
        
        # 3. Formatage pour affichage direct dans la console IA
        if not high_impact and not geo_news:
            return None # Pas d'alerte, on ne sature pas la console
            
        alert_msg = "⚠️ [ALERTE FLASH]"
        if high_impact:
            alert_msg += f"\n📊 MACRO: {', '.join(high_impact[:2])}"
        if geo_news:
            alert_msg += f"\n🌍 GÉOPOLITIQUE: {geo_news[0]}"
            
        return alert_msg