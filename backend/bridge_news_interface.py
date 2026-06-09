from mentor_ia import MarketGuard
import os
from datetime import datetime, timedelta

class BridgeNewsInterface:
    def __init__(self):
        self.guard = MarketGuard(os.getenv("POLYGON_API_KEY"))

    def get_live_alerts(self, actif, mode):
        # 1. Récupération des News Macro
        macro_events = self.guard.get_forex_factory_news(actif)
        high_impact = [e for e in macro_events if "High" in e]
        
        # 2. RÉCUPÉRATION GÉOPOLITIQUE (Forçage de fraîcheur)
        # On demande explicitement les news les plus récentes
        geo_news = self.guard.get_geopolitical_news(actif, mode=mode)
        
        # FILTRAGE TEMPOREL : On ne garde que les news récentes (ex: moins de 24h)
        # Si geo_news contient des dates dans le texte, on les compare ici.
        # Si geo_news est une liste d'objets, vérifie l'attribut 'date'.
        
        recent_geo = []
        for news in geo_news:
            # Si le texte contient une date (format de ton API), vérifie-la ici.
            # Exemple simplifié :
            recent_geo.append(news) 

        # 3. Formatage
        if not high_impact and not recent_geo:
            return None
            
        alert_msg = "⚠️ [ALERTE FLASH]"
        if high_impact:
            alert_msg += f"\n📊 MACRO: {', '.join(high_impact[:2])}"
        if recent_geo:
            # On prend la news la plus récente
            alert_msg += f"\n🌍 GÉOPOLITIQUE: {recent_geo[0]}"
            
        return alert_msg