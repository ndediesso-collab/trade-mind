import sys
import os
import requests
from mentor_ia import MarketGuard

# Ajustement du path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_tous_les_services(actif):
    print(f"\n--- LANCEMENT DES TESTS POUR : {actif} ---")
    guard = MarketGuard()
    
    # 1. TEST CALENDRIER (SÉCURISÉ)
    print("\n⏳ Test Calendrier...")
    try:
        # Appel correct sur l'instance guard
        resultats = guard.get_forex_factory_news(actif)
        if resultats:
            print(f"✅ Succès ! {len(resultats)} événements trouvés.")
        else:
            print("⚠️ Aucune donnée (Source peut-être bloquée/vide).")
    except Exception as e:
        print(f"❌ Erreur calendrier : {e}")

    # 2. TEST SENTIMENT CNN (PÉPITE)
    print("\n⏳ Test Sentiment CNN...")
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json().get('fear_and_greed', {})
            score = data.get('score')
            if score is not None:
                print(f"✅ Succès CNN ! Score arrondi : {int(round(float(score)))}")
            else:
                print("⚠️ Format JSON inattendu.")
        else:
            print(f"⚠️ Erreur CNN : {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur connexion CNN : {e}")

if __name__ == "__main__":
    test_tous_les_services()