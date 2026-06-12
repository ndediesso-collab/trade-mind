from mentor_ia import MarketGuard
import os
from datetime import datetime

class BridgeNewsInterface:
    def __init__(self):
        self.guard = MarketGuard()

    def get_live_alerts(self, actif, mode="SCALP"):
        """
        Récupère et agrège les données CNN, Macro et Géo.
        Version sécurisée contre les erreurs de type NoneType et erreurs 429.
        """
        # 1. Récupération sécurisée du sentiment (CNN)
        sentiment_data = self.guard.fetch_cnn_index()
        # Assurer un format dict par défaut
        sentiment = sentiment_data if isinstance(sentiment_data, dict) else {"score": 50, "label": "NEUTRAL"}
        
        # 2. Récupération des news (Macro et Géo)
        macro_events = self.guard.get_forex_factory_news(actif)
        geo_news = self.guard.get_geopolitical_news(actif, mode=mode)
        
        # 3. Construction de la réponse agrégée
        alert_msg = "⚠️ [FLASH INFO MARCHÉ - EXHAUSTIF]"
        
        # Ajout du score CNN
        alert_msg += f"\n\n🎭 INDICE FEAR & GREED (CNN): {sentiment_data.get('score', 'N/A')}/100"
        
        # Bloc Macro
        if isinstance(macro_events, list) and len(macro_events) > 0:
            alert_msg += "\n\n📊 MACRO (Calendrier complet):"
            for event in macro_events:
                # Gestion sécurisée du titre
                titre = event.get('title', str(event)) if isinstance(event, dict) else str(event)
                alert_msg += f"\n• {titre}"
        else:
            alert_msg += "\n\n📊 MACRO: Aucune donnée disponible. Veuillez vérifier directement sur le site officielle de forex factory."
            
        # Bloc Géo
        if isinstance(geo_news, list) and len(geo_news) > 0:
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