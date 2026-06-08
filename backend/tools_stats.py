import sqlite3
import json
import logging
from database import DB_PATH  # Import direct sans 'backend.'

# Configuration du log pour capturer les erreurs de calcul
logging.basicConfig(level=logging.INFO)

# ========================================================
# FONCTION 1 : STATISTIQUES (GRAPHIQUE)
# ========================================================

def calculer_statistiques_reelles():
    """
    Calcule le Winrate et les stats de performance en ignorant 
    les Brouillons et les trades En Attente.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # 1. RÉCUPÉRATION DES COMPTES PAR STATUT
        cursor.execute("SELECT statut, COUNT(*) FROM journal_final GROUP BY statut")
        stats = dict(cursor.fetchall()) # Exemple : {'Win': 10, 'Loss': 5, 'En attente': 3}

        wins = stats.get('Win', 0)
        losses = stats.get('Loss', 0)
        en_attente = stats.get('En attente', 0)
        brouillons = stats.get('Brouillon', 0)

        # 2. CALCUL DU WINRATE (Uniquement sur les trades terminés)
        total_termines = wins + losses
        winrate = (wins / total_termines * 100) if total_termines > 0 else 0

        # 3. ANALYSE DE LA PERFECTION (Optionnel mais puissant)
        # Score moyen de l'IA sur les trades gagnants vs perdants
        cursor.execute("SELECT AVG(score_ia) FROM journal_final WHERE statut = 'Win'")
        avg_score_win = cursor.fetchone()[0] or 0

        conn.close()

        return {
            "winrate": round(winrate, 2),
            "total_trades": total_termines,
            "en_cours": en_attente,
            "brouillons": brouillons,
            "score_moyen_ia_win": round(avg_score_win, 1)
        }

    except Exception as e:
        print(f"❌ Erreur tools_stats : {e}")
        return {"winrate": 0, "total_trades": 0, "en_cours": 0, "brouillons": 0}
    
# ========================================================
# FONCTION 2 : CALCULATEUR DE RISQUE
# ========================================================

def calculer(capital, risque_pourcent, sl_pips):
    """
    Calcule la taille de lot sans UI.
    Formule : (Capital * %Risque) / (SL * Valeur du Pip)
    """
    try:
        c = float(capital)
        r = float(risque_pourcent) / 100
        s = float(sl_pips)
        
        if s <= 0: return 0.0
        
        # Formule standard (0.1 lot = 1$ par pip sur bcp de paires)
        lot_size = (c * r) / (s * 10) 
        return round(lot_size, 2)
    except:
        return 0.0

# ========================================================
# FONCTION 3 : EXPORT  PROFESSIONNEL
# ========================================================
def preparer_donnees_export():
    """Renvoie les données pour que le navigateur puisse générer un CSV/PDF"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM journal_final ORDER BY date DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        return {"error": str(e)}