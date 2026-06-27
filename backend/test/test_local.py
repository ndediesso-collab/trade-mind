import sys
import os
import requests
import feedparser  # <-- Import manquant ajouté
from datetime import datetime
from datetime import datetime, timezone
import time # Si tu l'utilises pour ton timestamp

# Configuration du chemin pour trouver mentor_ia
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(backend_path)

# Maintenant il devrait trouver mentor_ia
from mentor_ia import MarketGuard

import os
import mentor_ia
from mentor_ia import MarketGuard

 1. Analyse de test (Ton plan)
analyse_complete = """
. Analyse Daily : GBPUSD
Contexte Macro & Setup Technique

1. Contexte du Marché

Tendance dominante : Baisse (Structure HTF marquée par des sommets descendants).

Dynamique actuelle : Impulsive (Accélération suite à la cassure du support majeur).

News & Fondamentaux : Aucune news majeure ce dimanche. En toile de fond : les attentes divergentes entre la BoE (Bank of England) qui lutte contre une inflation persistante et la Fed (USA) qui temporise. Les données sur l'emploi US de vendredi dernier pèsent encore, renforçant le dollar.

2. Setup Technique & Timing

Setup : Pullback sur ancien support devenu résistance.

Confirmation : Rejet en zone 1.2700 (ancien support) validé par une divergence RSI sur H4 et une bougie d'épuisement en daily.

Invalidation : 30 pips au-dessus de la mèche de rejet.

Session ciblée : Londres (08h00 - 10h00) pour exploiter la reprise du flux institutionnel européen face au dollar.
"""

# 2. Paramètres de test : ON FORCE LE MODE "DAILY" ICI
conviction = 75
actif = "USDJPY"
# C'est ici que tu injectes le mode pour que mentor_ia puisse router vers le bon prompt
settings = {
    "ia_severite": "Neutre",
    "mode": "DAILY"  
}

print("--- DÉBUT DU TEST UNITAIRE : MODE DAILY ---")

try:
    guard = MarketGuard()
    print(f"Test MarketGuard pour {actif}...")
    context = guard.preparer_contexte_marche(actif)
    print("MarketGuard OK.")

    print("\nLancement de l'analyse par le Mentor (Mode DAILY)...")
    
    # Appel ajusté : on passe le mode dans les settings ou en argument direct
    # selon la signature de ta fonction lancer_analyse dans mentor_ia.py
    resultat = mentor_ia.lancer_analyse(
        analyse_complete, 
        conviction, 
        actif, 
        settings  # Le mentor va lire settings['mode']
    )
    
    print("\n--- RÉSULTAT REÇU ---")
    print(resultat)

except Exception as e:
    print(f"\n❌ ERREUR LORS DU TEST : {str(e)}")

print("\n--- FIN DU TEST ---")