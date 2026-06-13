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

# 1. Ton analyse injectée
analyse_complete = """
Analyse soumise au Mentor (Copie ce bloc)
A - IDENTITÉ & CONVICTION

Actif : USDJPY

Biais : Long (Achat). Score de conviction : 90%.
Justification : Le prix est au-dessus de ma moyenne mobile 20 et j'ai une intuition forte qu'il va monter.

B - ANALYSE MACRO & CONTEXTE GLOBALE

Sentiment : Risk-off (peur) mais j'achète USD car c'est une valeur refuge.

Rendements : US02Y en baisse, mais je pense que le dollar va monter quand même.

Différentiel : Le Japon a des taux bas, les US ont des taux hauts, donc c'est logique.

Inflation : Les USA ont une inflation élevée, donc le dollar doit monter.

Géopolitique : Pas vraiment regardé, mais ça n'impacte pas le forex.

Corrélations : L'or baisse, donc l'USDJPY doit monter.

Événement à venir : Non, je ne regarde pas le calendrier.
🔎 Conclusion : Le dollar est dominant car c'est la monnaie mondiale. Dites-moi si je dois acheter maintenant pour profiter de la hausse.

D - ANALYSE TECHNIQUE

Structure : Tendance haussière partout.

Momentum : Bougies vertes fortes.

Zones : Je suis en plein milieu de nulle part, mais ça a l'air de vouloir monter.

Liquidité : Pas regardé si les sommets ont été nettoyés.

E - GESTION DU RISQUE

Pourquoi maintenant : Parce que je veux faire du profit avant ce soir.

Stop Loss : 145.00 (valeur arbitraire).

RR : 1:1.5.

Confirmation : Non, mais je sens que ça va passer.
"""

# 2. Paramètres de test
conviction = 75
actif = "AUDNZD"
settings = {"ia_severite": "Neutre"}

print("--- DÉBUT DU TEST UNITAIRE IA ---")

try:
    # Test de récupération MarketGuard (Juste pour vérifier que l'API n'est pas bloquée)
    guard = MarketGuard()
    print(f"Test MarketGuard pour {actif}...")
    context = guard.preparer_contexte_marche(actif)
    print("MarketGuard OK.")

    # Test IA Mentor
    print("\nLancement de l'analyse par le Mentor...")
    resultat = mentor_ia.lancer_analyse(
        analyse_complete, 
        conviction, 
        actif, 
        settings
    )
    
    print("\n--- RÉSULTAT REÇU ---")
    print(resultat)

except Exception as e:
    print(f"\n❌ ERREUR LORS DU TEST : {str(e)}")

print("\n--- FIN DU TEST ---")
