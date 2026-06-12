from mentor_ia import MarketGuard
import os
from datetime import datetime

class BridgeNewsInterface:
    def __init__(self):
        self.guard = MarketGuard()

    def get_live_alerts(self, actif, mode="SCALP"):
        """
        Récupère et agrège les données CNN, Macro et Géo.
        Force l'utilisation du cache via MarketGuard.
        """
        # 1. Récupération sécurisée du sentiment (CNN)
        sentiment_data = self.guard.fetch_cnn_index()
        sentiment = sentiment_data if isinstance(sentiment_data, dict) else {"score": "N/A", "label": "NEUTRAL"}
        
        # 2. Récupération des news
        # On appelle la fonction du guard qui GÈRE DÉJÀ LE CACHE en interne
        macro_events = self.guard.get_forex_factory_news(actif)
        geo_news = self.guard.get_geopolitical_news(actif, mode=mode)
        
        # 3. Construction de la réponse agrégée
        alert_msg = "⚠️ [FLASH INFO MARCHÉ - EXHAUSTIF]"
        alert_msg += f"\n\n🎭 INDICE FEAR & GREED (CNN): {sentiment.get('score', 'N/A')}/100"
        
        # Bloc Macro : Utilisation du cache via get_forex_factory_news
        # Liste des jours pour le formatage
        jours = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
        
        if isinstance(macro_events, list):
            if len(macro_events) > 0:
                alert_msg += "\n\n📊 MACRO (Calendrier complet):"
                for event in macro_events[:5]: # Limité à 5 pour la clarté
                    titre = event.get('title', str(event)) if isinstance(event, dict) else str(event)
                    
                    # Extraction et formatage du jour
                    date_str = event.get('date', '') if isinstance(event, dict) else ''
                    prefixe_jour = ""
                    if date_str:
                        try:
                            # Extraction YYYY-MM-DD
                            dt = datetime.strptime(date_str.split('T')[0], '%Y-%m-%d')
                            prefixe_jour = f"[{jours[dt.weekday()]}] "
                        except:
                            prefixe_jour = ""
                            
                    alert_msg += f"\n• {prefixe_jour}{titre}"
            else:
                alert_msg += "\n\n📊 MACRO: Aucune actualité majeure cette semaine."
        else:
            alert_msg += "\n\n📊 MACRO: Flux en attente de synchronisation..."
            
             
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