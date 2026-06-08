import logging
import database as db
from Logic import collecter_metriques_completes

# Configuration du logging pour le monitoring
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DashboardManager:
    """
    Cette classe agit comme la passerelle finale entre le Mind Engine 
    et l'API FastAPI pour le Frontend Next.js.
    """
    def __init__(self):
        self.logger = logging.getLogger("DashboardManager")
        
    def get_full_metrics(self):
        """
        Récupère et agrège l'intégralité des données traitées par l'orchestrateur Logic.py
        et synchronise avec les données brutes de Supabase.
        """
        try:
            # 1. On récupère les données traitées par l'intelligence (Logic.py)
            engine_data = collecter_metriques_completes()

            if "error" in engine_data and engine_data.get("status") == "LOCKDOWN":
                self.logger.warning("🚨 Mind Engine en mode LOCKDOWN détecté")

            # 2. Injection forcée des données brutes unifiées pour le Dashboard
            # Cela garantit que Swing, Daily, Scalp et Investor apparaissent toujours
            trades_bruts = db.recuperer_tout_historique()
            engine_data["trades"] = trades_bruts
            
            # 3. Agrégation dynamique par TYPE (pour tes graphiques dans Next.js)
            # Sécurisation Supabase : Prise en compte du format Dictionnaire (Supabase Client) ou Tuple (psycopg2)
            distribution = {"SWING": 0, "DAILY": 0, "SCALP": 0, "INVESTOR": 0}
            
            for t in trades_bruts:
                # Détection dynamique du format renvoyé par ton module database
                if isinstance(t, dict):
                    # Format Supabase JSON standard
                    t_type = str(t.get("type", "")).upper()
                else:
                    # Format Tuple SQL brut (Fallback de sécurité si index 9)
                    t_type = str(t[9] if len(t) > 9 else "").upper()
                
                # Aiguillage et incrémentation selon la nomenclature stricte du Hub Next.js
                if t_type in ["SWING"]:
                    distribution["SWING"] += 1
                elif t_type in ["INTRADAY", "DAILY"]:
                    distribution["DAILY"] += 1
                elif t_type in ["SCALPING", "SCALP"]:
                    distribution["SCALP"] += 1
                elif t_type in ["INVESTOR", "LONG_TERM"]:
                    distribution["INVESTOR"] += 1

            engine_data["distribution_par_type"] = distribution

            # 4. Recalcul du capital global basé sur la table capital_flux
            engine_data["capital_total"] = db.calculer_capital_total()

            return engine_data

        except Exception as e:
            self.logger.error(f"❌ ERREUR CRITIQUE DashboardManager : {e}")
            return {
                "health": {"global": 0, "discipline": 0, "risk": 0, "exec": 0},
                "psychology": {"state": "EMERGENCY", "confidence": 0, "patterns": []},
                "capital_total": 0,
                "winrate": 0,
                "distribution_par_type": {"SWING": 0, "DAILY": 0, "SCALP": 0, "INVESTOR": 0},
                "recent_flux": [],
                "equity": [0]
            }

    def update_base_capital(self, nouveau_montant):
        """Met à jour le capital de départ via l'API."""
        try:
            montant_float = float(nouveau_montant)
            if db.update_capital_initial(montant_float):
                return {
                    "success": True, 
                    "new_cap": db.calculer_capital_total(),
                    "message": "Capital initial synchronisé"
                }
            return {"success": False, "error": "Échec de la mise à jour SQL"}
        except ValueError:
            return {"success": False, "error": "Format numérique invalide"}

# Instance unique pour l'import dans api.py
dashboard_engine = DashboardManager()

def collecter_metriques_completes_api():
    """Fonction helper pour api.py qui appelle le manager"""
    return dashboard_engine.get_full_metrics()