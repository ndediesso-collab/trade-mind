from mentor_ia import MarketGuard
import os
from datetime import datetime

class BridgeNewsInterface:
    def __init__(self):
        self.guard = MarketGuard()

    def get_live_alerts(self, actif, mode="SCALP"):
        """
        Récupère et affiche ABSOLUMENT TOUT : CNN, Macro, et Géopolitique.
        Sans aucun filtrage ni restriction.
        """
        cible = None if actif in ["GLOBAL", "ALL", "MARKET"] else actif
        
        # 1. Récupération exhaustive
        # CNN (Fear & Greed)
        sentiment_data = self.guard.get_sentiment_data()
        # Macro (Forex Factory)
        macro_events = self.guard.get_forex_factory_news(cible)
        # Géo (Flux RSS 10 news)
        geo_news = self.guard.get_geopolitical_news(cible, mode=mode)
        
        alert_msg = "⚠️ [FLASH INFO MARCHÉ - EXHAUSTIF]"
        
        # 2. Ajout du score CNN (Obligatoire)
        alert_msg += f"\n\n🎭 INDICE FEAR & GREED (CNN): {sentiment_data.get('score', 'N/A')}/100"
        
        # 3. Bloc Macro (Tout le calendrier)
        if macro_events:
            alert_msg += "\n\n📊 MACRO (Calendrier complet):"
            for event in macro_events:
                titre = event.get('title', str(event))
                alert_msg += f"\n• {titre}"
        else:
            alert_msg += "\n\n📊 MACRO: Aucun événement trouvé."
        
        # 4. Bloc Géo (Toutes les news, même les [INFO] neutres)
        if geo_news:
            alert_msg += "\n\n🌍 GÉOPOLITIQUE & MARCHÉ (Liste complète):"
            for news in geo_news:
                alert_msg += f"\n• {news}"
        else:
            alert_msg += "\n\n🌍 GÉOPOLITIQUE: Aucune news trouvée."
            
        return alert_msg

    def get_market_context(self, actif):
        """
        Envoie TOUT le contexte brut à l'IA pour analyse.
        """
        # Utilise l'orchestrateur qui centralise tout
        return self.guard.preparer_contexte_marche(actif)