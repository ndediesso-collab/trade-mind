import sys
import os
import requests
import feedparser  # <-- Import manquant ajouté
from datetime import datetime

# Configuration du chemin pour trouver mentor_ia
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(backend_path)

# Maintenant il devrait trouver mentor_ia
from mentor_ia import MarketGuard

def get_geopolitical_news(actif, mode="SCALP"):
    """
    Récupère 10 news récentes. Si un mot-clé est détecté, la news est taguée en ALERTE.
    """
    KEYWORDS = [
        'War', 'Geopolitical', 'Sanctions', 'Tension', 'Conflict', 'Middle East', 'Ukraine', 'Trade War', 'Crisis', 'Embargo',
        'Russia', 'China', 'Taiwan', 'Israel', 'Iran', 'Gaza', 'Terrorism', 'Border', 'Defense', 'NATO', 'Diplomacy',
        'Military', 'Attack', 'Invasion', 'Treaty', 'Bilateral', 'Geopolitical Risk', 'Nuclear',
        'FED', 'ECB', 'BOC', 'BOJ', 'Rate', 'Interest Rate', 'Inflation', 'CPI', 'PPI', 'Jobs', 'Payroll', 'Unemployment',
        'Recession', 'Slowdown', 'GDP', 'Growth', 'Yield', 'Treasury', 'Bond', 'Monetary Policy', 'Tightening', 'Easing',
        'Hike', 'Cut', 'Hawkish', 'Dovish', 'Liquidity', 'Default', 'Debt', 'Fiscal', 'Stimulus', 'Deficit',
        'Oil', 'Gold', 'Energy', 'Gas', 'Commodity', 'Supply Chain', 'Shortage', 'Blackout', 'Volatility', 'Crash',
        'S&P', 'Dow Jones', 'Nasdaq', 'Nvidia', 'Tech', 'Stock', 'Share', 'Bankruptcy', 'Earnings', 'Outlook', 'Guidance',
        'Corporate', 'Merger', 'Acquisition', 'Profit', 'Revenue', 'Margin', 'Downgrade', 'Upgrade', 'Liquidation',
        'Cyberattack', 'Data Breach', 'Leak', 'Investigation', 'Probe', 'Scandal', 'Fraud', 'SEC', 'Regulation', 
        'Compliance', 'Lawsuit', 'Strike', 'Union', 'Labor', 'Protest', 'Unrest', 'Election', 'Policy', 'Executive', 
        'Central Bank', 'Currency', 'Devaluation', 'Peg', 'Intervention', 'Volatility Spike', 'Panic', 'Selloff'
    ]

    try:
        url = "https://fr.investing.com/rss/news_285.rss"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        
        feed = feedparser.parse(response.content)
        news_list = []
        
        for entry in feed.entries:
            title = entry.title.replace('"', "'")
            
            # Vérification si le titre contient un mot-clé
            is_alert = any(k.lower() in title.lower() for k in KEYWORDS)
            
            # Taggage automatique : [ALERTE] ou [INFO]
            prefixe = "⚠️ [ALERTE]" if is_alert else "🌍 [INFO]"
            news_list.append(f"{prefixe}[{mode}] {title}")
            
            if len(news_list) >= 10:
                break
        
        return news_list

    except Exception as e:
        return [f"❌ Erreur flux RSS: {e}"]

# --- TEST D'EXÉCUTION ---
if __name__ == "__main__":
    print("--- TEST FONCTION GÉOPOLITIQUE ---")
    results = get_geopolitical_news("EURUSD")
    for news in results:
        print(news)