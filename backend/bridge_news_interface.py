from mentor_ia import MarketGuard
import os
from datetime import datetime

class BridgeNewsInterface:
    def __init__(self):
        # Initialisation propre du moteur de données
        self.guard = MarketGuard()

    def get_live_alerts(self, actif, mode):
        # Si on veut TOUT le marché, on ne filtre pas par actif
        # On définit une constante ou un mot-clé spécial pour le GLOBAL
        cible = None if actif in ["GLOBAL", "ALL", "MARKET"] else actif
        
        # 1. Récupération (On passe 'cible' qui peut être None)
        macro_events = self.guard.get_forex_factory_news(cible)
        geo_news = self.guard.get_geopolitical_news(cible, mode=mode)
        
        # 3. Vérification s'il y a quelque chose à afficher
        if not macro_events and not geo_news:
            return None
            
        # 4. Formatage exhaustif (Affichage de TOUTES les news)
        alert_msg = "⚠️ [FLASH INFO MARCHÉ]"
        
        # Bloc Macro
        if macro_events:
            alert_msg += "\n\n📊 MACRO (Calendrier):"
            for event in macro_events:
                # Nettoyage rapide pour ne pas saturer l'affichage
                alert_msg += f"\n• {event[:60]}..." if len(event) > 60 else f"\n• {event}"
        
        # Bloc Géopolitique
        if geo_news:
            alert_msg += "\n\n🌍 GÉOPOLITIQUE:"
            for news in geo_news:
                alert_msg += f"\n• {news}"
            
        return alert_msg

    def get_market_context(self, actif):
        """
        Méthode utilitaire pour envoyer tout le contexte à ton IA principale
        lors de la prise de décision.
        """
        return self.guard.preparer_contexte_marche(actif)