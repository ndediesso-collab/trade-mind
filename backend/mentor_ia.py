import os
import time
import requests
import json
import xml.etree.ElementTree as ET
from openai import OpenAI
import re
from datetime import datetime, timedelta 
import yfinance as yf
import feedparser 
from curl_cffi import requests as curl_requests
from datetime import datetime, timezone
import time # Si tu l'utilises pour ton timestamp

from dotenv import load_dotenv
import logging

# Configure un logging plus précis pour voir le détail de l'erreur
logger = logging.getLogger(__name__)

# --- CHARGEMENT DU COFFRE-FORT .ENV ---
load_dotenv()
print(f"DEBUG: ARCHITECT_KEY trouvé ? {bool(os.getenv('OPENAI_ARCHITECT_KEY'))}, GUARDIAN_KEY trouvé ? {bool(os.getenv('OPENAI_GUARDIAN_KEY'))}")

# --- CONFIGURATION SÉCURISÉE DES CLÉS API ---
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# IA 1 : L'Architecte (Analyse froide)
client_architect = OpenAI(api_key=os.getenv("OPENAI_ARCHITECT_KEY"))

# IA 2 : Le Guardian (Discipline & Émotion)
client_guardian = OpenAI(api_key=os.getenv("OPENAI_GUARDIAN_KEY"))

import time
import requests
from datetime import datetime, timedelta 
import xml.etree.ElementTree as ET

# --- GUIDES DE RÉFLEXION (Architect AI Reference) ---

GUIDE_REFLEXION_SWING = """📋 Checklist de Réflexion Swing (Audit de Plan)
[A — Identité & Conviction
Actif analysé : (Précision recommandée : une seule paire à la fois pour éviter la dispersion).
Biais & Conviction : Quel est votre biais (Long/Short) ? Quel est votre niveau de conviction (0-100%) ?
Conseil : Une conviction élevée sans justification solide cache souvent un biais psychologique (excès de confiance).

B — Analyse Macro & Contexte
Sentiment global (Risk-on / Risk-off) : Quel est l'état d'esprit actuel des marchés pour cette paire ?
Points de vigilance : Tendance, incertitude ou compression ? (Une justification basée sur les indices ou les flux renforce la solidité du plan).
Rendements (Yields) : Quelle est la dynamique des taux de référence (ex: US02Y/GB10Y) ?
Différentiel de taux : Quelle devise semble la plus attractive au niveau monétaire (taux d’intérêt et la politique monétaire) ?
Inflation & Emploi : Quelles sont les dernières données clés et leur impact probable (Selon les dernières news, quelle économie est la plus forte) ?
Géopolitique & Corrélations : Y a-t-il des facteurs externes ou des corrélations (Or, Indices, Pétrole) qui influencent votre actif ?
Événements à venir : Le calendrier économique présente-t-il des risques (news High Impact) ?
Piste de synthèse macro (Optionnel) : Si vous souhaitez structurer votre réflexion, vous pouvez chercher à identifier une dominance claire entre les deux devises (politique monétaire, géopolitique, taux).

D — Analyse Technique
Structure & Momentum : Quel est l'état de la tendance sur l'unité de temps supérieure ? (Le momentum actuel est-il impulsif ou hésitant ?)
Zones institutionnelles : Avez-vous identifié vos points d'intérêt (FVG, OB, Support/Résistance) ?
Liquidité : Le marché a-t-il déjà "nettoyé" la liquidité (sommet/bas) pertinente avant votre entrée ?

E — Gestion du Risque
Logique d'entrée (Timing) : Pourquoi ce moment précis est-il opportun pour initier le trade ?
Invalidation (SL) : Où se situe votre niveau d'invalidation technique ?
Ratio Risque/Récompense (RR) : Quel est votre ratio cible ? (Nous recommandons une cible > 1:2).
Validation technique : Votre setup est-il pleinement confirmé par votre analyse technique et votre timing ?]
"""

GUIDE_REFLEXION_DAILY = """[1 — Contexte & Carburant (Macro & ADR)
Biais HTF vs Dynamique : Quelle est la tendance de fond et comment s'inscrit-elle dans l'impulsion du jour ?
Effets de traîne (Post-News) : Y a-t-il des données fondamentales récentes (travail, inflation, géopolitique) qui influencent le sentiment actuel ?
État ADR (Average Daily Range) : Quel est l'ATR actuel ?
Piste de réflexion : Le prix a-t-il déjà parcouru plus de 80% de son range quotidien ? (Le potentiel de gain restant est-il statistiquement pertinent ?)
Calendrier Macro : Une news majeure est-elle prévue dans les 60 prochaines minutes ?

2 — Setup Technique & Timing (Audit d'Entrée)
Setup Institutionnel : Quel est le déclencheur précis ? (Ex: Sweep, FVG + OB, Breakout).
Validation de la Killzone : Quelle session tradez-vous (Londres/NY/Asiatique) ?
Piste de réflexion : Sommes-nous dans une fenêtre de haute volatilité propice à votre setup ?
Logique d'Invalidation (SL) : Où est placé le SL par rapport à la structure intraday ? (Est-il cohérent avec l'ATR actuel ?)

3 — Gestion du Risque & Discipline
Rapport Risque/Récompense (RR) : Quel est votre objectif ? (Nous recommandons une cible > 1:2).
Exposition : Quel est votre risque total en % du capital ?
Clarté Mentale : Est-ce une entrée planifiée ou une réaction à l'impulsion actuelle (FOMO) ?
Règle de clôture : Avez-vous anticipé la clôture impérative de fin de session (00h00) ?]"""

GUIDE_REFLEXION_SCALP = """[1 — Contexte & Filtres
• Calendrier Macro : News "High Impact" dans les 30 min ?
• Corrélation & Sentiment : Corrélation (DXY/VIX) et sentiment alignés ?

2 — Audit d'Entrée
• Setup Institutionnel : Quel déclencheur ? (Sweep, FVG, Breakout)
• Prix d'entrée & SL : Invalidation technique indiscutable ?
• Ratio Risque/Gain : RR visé couvrant spreads/frais ?
• Session : Killzone de volatilité (Londres/NY) ?

3 — Discipline & État
• Risque de session : Risque max quotidien respecté ?
• Discipline : Confirmation réelle ou FOMO ?
• Clarté Mentale : 100% focus ?
WORKSPACE_ACTIVE_SCALP"""

# DÉFINITION DU TEMPÉRAMENT (Pour GPT-4o)
instructions_severite = {
"Exigeant": """
Tu es un Head of Desk institutionnel. Tu n'es pas là pour encourager, tu es là pour auditer.
Si le trader n'utilise pas le guide, tu ne le sanctionnes pas, MAIS tu juges la rigueur de son raisonnement 
avec une exigence professionnelle totale. 
Tu ignores le "bienveillant" et tu te concentres sur la "validité mathématique et logique" de la thèse.
"""
}

# 6. DÉFINITION DE L'APPROCHE PÉDAGOGIQUE (Pour le Mind Engine)
instructions_pedagogiques = {
"Exigeant": """
Tu adoptes exclusivement une posture de coach de performance. Tu challenges la rigueur du plan 
et soulignes impitoyablement les failles dans la gestion des risques. Ton feedback doit être 
chirurgical : erreur identifiée = conséquence expliquée = correction imposée.
"""
}


# ====== CLASSE MARKETGUARD (INTÉGRÉE) =======
class MarketGuard:
    def __init__(self):
        # Plus besoin de clé API Polygon
        self.client_architect = client_architect
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) MentorIA/1.0"
        })
        
        # Structure de stockage unifiée et propre
        self.storage = {
            # Initialise 'data' avec {} au lieu de None
            "market_data": {"data": {}, "timestamp": 0},
            "forex_factory": {"data": [], "timestamp": 0},
            "sentiment": {"data": {}, "timestamp": 0}
        }
        
        # Cache de 5 minutes pour éviter toute limitation inutile des sources gratuites
        self.cache_duration = 300 


    def _est_valide(self, key):
        """Vérifie la fraîcheur de la donnée en cache"""
        return (time.time() - self.storage[key]["timestamp"]) < self.cache_duration

    # --- MODULE : FEAR & GREED (Sentiment) ---
    def _formater_ticker(self, ticker):
        """Convertit le format de l'actif en format Yahoo Finance."""
        # Exemple simple : si AUD/NZD, devient AUDNZD=X
        formatted = ticker.replace('/', '')
        return f"{formatted}=X"
    
    def fetch_cnn_index(self):
        print("\n--- TEST : RÉCUPÉRATION CNN (MODE NAVIGATEUR) ---")
        try:
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
                'Referer': 'https://edition.cnn.com/',
            })
            
            url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
            response = session.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                # On arrondit proprement
                raw_score = float(data['fear_and_greed']['score'])
                score = int(round(raw_score))
                rating = data['fear_and_greed']['rating']
                
                print(f"✅ Succès CNN ! Score : {score}")
                
                # RETOURNE LA DONNÉE ICI !
                return {"score": score, "rating": rating}
            else:
                print(f"⚠️ Erreur CNN : Statut {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Erreur CNN : {e}")
            return None

    def get_last_price(self, ticker):
        """Récupération ultra-rapide du prix via le cache ou yfinance."""
        CACHE_KEY = "market_data"
        
        # 1. Vérification du cache unifié
        if self._est_valide(CACHE_KEY):
            price = self.storage.get(CACHE_KEY, {}).get("data", {}).get("price")
            if price:
                return price

        # 2. Fallback via YFinance (remplace l'appel inexistant)
        try:
            ticker_yf = self._formater_ticker(ticker)
            stock = yf.Ticker(ticker_yf)
            # fast_info est extrêmement rapide pour le prix
            price = stock.fast_info['last_price']
            
            # (Optionnel) Mise à jour du cache pour éviter de refaire l'appel tout de suite
            return price
            
        except Exception as e:
            print(f"❌ Erreur YFinance Price pour {ticker}: {e}")
            return None

    def get_volatility_atr(self, ticker):
        """Récupère le range quotidien via le cache unifié 'market_data'."""
        CACHE_KEY = "market_data"
        
        # 1. Vérification dans le cache unifié
        data = self.storage.get(CACHE_KEY, {}).get("data", {})
        if self._est_valide(CACHE_KEY) and data.get("volatility") is not None:
            return data.get("volatility")
        
        # 2. Calcul si cache absent ou invalide
        try:
            ticker_yf = self._formater_ticker(ticker)
            hist = yf.Ticker(ticker_yf).history(period="2d")
            
            if len(hist) < 2: 
                return 0
                
            daily_range = float(hist.iloc[-2]['High'] - hist.iloc[-2]['Low'])
            
            # Mise à jour du cache unifié (sans écraser le reste)
            self.storage[CACHE_KEY]["data"]["volatility"] = daily_range
            return daily_range
            
        except Exception as e:
            print(f"❌ Erreur YFinance Volatility pour {ticker}: {e}")
            return 0

    def get_daily_range_stats(self, ticker):
        """Calcule l'ADR glissant (5 jours) via le cache unifié 'market_data'."""
        CACHE_KEY = "market_data"
        
        # 1. Vérification dans le cache unifié
        data = self.storage.get(CACHE_KEY, {}).get("data", {})
        if self._est_valide(CACHE_KEY) and data.get("adr_stats"):
            return data.get("adr_stats")

        # 2. Calcul si cache absent ou invalide
        try:
            ticker_yf = self._formater_ticker(ticker)
            stock = yf.Ticker(ticker_yf)
            hist = stock.history(period="6d")
            
            if hist.empty or len(hist) < 2:
                return {"adr_moyenne": 0.002, "dernier_high": 0, "dernier_low": 0}

            daily_ranges = hist['High'] - hist['Low']
            avg_adr = daily_ranges.tail(5).mean()
            
            stats = {
                "adr_moyenne": round(float(avg_adr), 5),
                "dernier_high": float(hist['High'].iloc[-1]),
                "dernier_low": float(hist['Low'].iloc[-1])
            }
            
            # Mise à jour du cache unifié
            self.storage[CACHE_KEY]["data"]["adr_stats"] = stats
            return stats
            
        except Exception as e:
            print(f"❌ Erreur YFinance ADR pour {ticker}: {e}")
            return {"adr_moyenne": 0.002, "dernier_high": 0, "dernier_low": 0}

    def get_forex_factory_news(self, actif):
        """Récupère les news du jour via le flux miroir avec cache 1h."""
        url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
        
        # 1. VÉRIFICATION DU CACHE
        cache = self.storage["market_data"].get("forex_factory")
        if cache and (time.time() - cache["timestamp"] < 3600):
            all_events = cache["data"]
        else:
            # 2. APPEL API SI CACHE ABSENT/EXPIRÉ
            try:
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    all_events = response.json()
                    self.storage["market_data"]["forex_factory"] = {
                        "data": all_events, 
                        "timestamp": time.time()
                    }
                else:
                    print(f"❌ Erreur Forex Factory : {response.status_code}")
                    return []
            except Exception as e:
                print(f"❌ Erreur de connexion Forex Factory : {e}")
                return []

        # 3. FILTRAGE : Ne garder que les événements de AUJOURD'HUI
        today_str = datetime.now().strftime('%Y-%m-%d')
        daily_events = []
        
        for event in all_events:
            try:
                date_part = event.get('date', '').split('T')[0]
                if date_part == today_str:
                    daily_events.append(event)
            except:
                continue
                
        return daily_events
        
    def get_geopolitical_news(self, actif, mode="SCALP"):
        """
        Récupère jusqu'à 10 news récentes. Si un mot-clé est détecté, la news est taguée en ALERTE.
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
            # Utilisation de self.session pour rester cohérent avec le reste de MentorIA
            response = self.session.get(url, timeout=10)
            
            feed = feedparser.parse(response.content)
            news_list = []
            
            for entry in feed.entries:
                title = entry.title.replace('"', "'")
                
                # Vérification si le titre contient un mot-clé
                is_alert = any(k.lower() in title.lower() for k in KEYWORDS)
                
                # Taggage automatique
                prefixe = "⚠️ [ALERTE]" if is_alert else "🌍 [INFO]"
                news_list.append(f"{prefixe}[{mode}] {title}")
                
                if len(news_list) >= 10:
                    break
            
            return news_list if news_list else ["🌍 Sentiment Géopolitique: Calme."]

        except Exception as e:
            print(f"❌ Erreur flux RSS Géopolitique: {e}")
            return [f"🌍 Sentiment Géopolitique: Flux temporairement indisponible."]
        
    def preparer_contexte_marche(self, actif):
        """
        Orchestrateur central : Récupère, Formate et Synthétise le contexte pour l'IA.
        """
        maintenant = datetime.now(timezone.utc)
        heure_serveur = maintenant.strftime("%H:%M")
        
        # 1. Récupération des données brutes
        sentiment = self.fetch_cnn_index()
        news_macro = self.get_forex_factory_news(actif)
        news_geo_brutes = self.get_geopolitical_news(actif)
        
        # 2. Filtrage intelligent (CORRIGÉ ICI)
        if hasattr(self, 'filtrer_news_par_ia'):
            # On passe maintenant les DEUX arguments requis par ta fonction
            news_geo_filtrees = self.filtrer_news_par_ia(news_geo_brutes, sentiment)
        else:
            news_geo_filtrees = news_geo_brutes
        
        CACHE_KEY = "market_data"
        
        if not self._est_valide(CACHE_KEY):
            prix = self.get_last_price(actif)
            vol = self.get_volatility_atr(actif)
            stats_adr = self.get_daily_range_stats(actif)
            
            self.storage[CACHE_KEY] = {
                "data": {
                    "price": prix,
                    "volatility": vol,
                    "adr_stats": stats_adr,
                    "timestamp_str": heure_serveur
                },
                "timestamp": time.time()
            }

        # 4. Synthèse finale (Lecture avec la MÊME clé fixe)
        # On utilise .get() pour éviter le crash si la clé est absente
        market_cache = self.storage.get(CACHE_KEY, {})
        data = market_cache.get("data", {})

        
        str_news_macro = "\n".join([str(n) for n in news_macro]) if isinstance(news_macro, list) else str(news_macro)
        str_news_geo = "\n".join([str(n) for n in news_geo_filtrees]) if isinstance(news_geo_filtrees, list) else str(news_geo_filtrees)
        
        return {
            "heure_utc": heure_serveur,
            "prix_actuel": data.get("price"),
            "volatilite_atr": data.get("volatility"),
            "adr_data": data.get("adr_stats"),
            "contexte_macro": str_news_macro,
            "contexte_geo": str_news_geo,
            "sentiment_global": sentiment
        }

    def filtrer_news_par_ia(self, news_list, sentiment_cnn):
        """
        Analyseur multi-sources : Force l'IA à prioriser Macro, Geo, et CNN.
        """
        if not news_list:
            return []

        titres_concat = "\n".join([f"- {t}" for t in news_list])
        
        prompt = f"""
        Tu es un Analyste Financier Senior. Ta mission est de filtrer les news pour un trader professionnel.
        
        RÈGLES STRICTES DE SÉLECTION :
        1. Tu DOIS inclure systématiquement le score CNN Fear & Greed dans ton analyse globale (Score actuel : {sentiment_cnn}).
        2. Pour le Calendrier Économique (Macro), donne la priorité absolue à : Inflation (CPI/PPI), Taux d'intérêt, Emploi (NFP/Chômage), et PIB.
        3. Pour la Géopolitique, garde uniquement les news qui impactent directement la stabilité des marchés (conflits, sanctions, tensions majeures).
        4. Ignore les news mineures (résultats d'entreprises locales, mouvements boursiers sans lien macro).
        
        FORMAT DE RÉPONSE :
        - Renvoie uniquement les titres sélectionnés, un par ligne.
        - Si aucune news n'est jugée "à fort impact", renvoie uniquement : AUCUNE.
        
        DONNÉES À ANALYSER :
        {titres_concat}
        """

        try:
            response = self.client_architect.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Tu es un expert en macroéconomie et risque géopolitique."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1 # Encore plus précis
            )
            
            result = response.choices[0].message.content.strip()
            
            if "AUCUNE" in result:
                return []
            
            return [line.strip("- ").strip() for line in result.split('\n') if line.strip()]
                
        except Exception as e:
            print(f"❌ Erreur IA Analyste: {e}")
            return news_list # Fallback sécurisé
        
# ====== LOGIQUE MENTOR =======

def get_news(actif, guard=None):
    if guard is None:
        guard = MarketGuard() 

    # Initialisation sécurisée
    geo_titles = [] 
    
    events_critiques = guard.get_forex_factory_news(actif)
    sentiment_global = guard.fetch_cnn_index()
    
    cnn_score = sentiment_global.get('score') if isinstance(sentiment_global, dict) else None
    
    # Tentative de récupération, si ça échoue, geo_titles restera []
    try:
        geo_titles = guard.get_geopolitical_news(actif, sentiment=cnn_score)
    except Exception as e:
        logging.error(f"Erreur lors de la récupération geo : {e}")    
    
    # 1. Données brutes
    events_critiques = guard.get_forex_factory_news(actif)
    sentiment_global = guard.fetch_cnn_index()
    
    # 2. Récupération sécurisée du score
    # Si sentiment_global est un dict, on extrait le score, sinon on passe None
    cnn_score = sentiment_global.get('score') if isinstance(sentiment_global, dict) else None
    
    # 3. Construction sécurisée (Conversion forcée en str)
    label = sentiment_global.get('label', 'Neutre') if isinstance(sentiment_global, dict) else "Neutre"
    resultat = f"--- 🎭 INDICE SENTIMENT GLOBAL ---\n{label}\n\n"
    
    resultat += "--- 📅 CALENDRIER ÉCONOMIQUE (MACRO) ---\n"
    # CORRECTION ICI : On transforme chaque élément en chaîne de caractères
    if events_critiques:
        resultat += "\n".join([str(e) for e in events_critiques])
    else:
        resultat += "Aucun événement impactant prévu."
    
    resultat += "\n\n--- 🌍 FLASH GÉOPOLITIQUE (RISK) ---\n"
    # CORRECTION ICI : On transforme chaque élément en chaîne de caractères
    resultat += "\n".join([str(g) for g in geo_titles])
    
    return resultat

# --- FONCTION PRIVÉE DE GESTION API (Léger & Réutilisable) ---
def _exec_ia(prompt, client_architect, mode_upper):
    try:
        response = client_architect.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"Tu es un Mentor IA spécialisé en Risk Management ({mode_upper}). Niveau : Exigeant."}, 
                {"role": "user", "content": prompt}
            ]
        )
        reponse_ia = response.choices[0].message.content 
        match = re.search(r'#(?:[0-9a-fA-F]{3}){1,2}', reponse_ia)
        couleur = match.group(0) if match else "#2B2B2B"
        note_match = re.search(r'\d+', reponse_ia)
        score = int(note_match.group()) if note_match else 5
        return score, reponse_ia, couleur 
    except Exception as e:
        return 0, f"Erreur : {e}", "#34495E"

# --- FONCTION SWING (Texte intégral respecté) ---
def analyser_ia_swing(app_instance, ancienne_analyse, nouvelle_analyse, statut_analyse, actif, conviction, guide_etudiant, guide_expert, mode, data_json=None, client_architect=None):
    mode_upper = "SWING"
    
    GUIDE_REFLEXION = GUIDE_REFLEXION_SWING
    user_settings = getattr(app_instance, 'user_settings', {})
    severite = user_settings.get("ia_severite", "Neutre")
    
    # 3. CONTEXTUALISATION DES DONNÉES ISOLÉES
    # Si le trader a rempli des champs spécifiques, on les injecte ici
    donnees_techniques = ""
    if data_json:
        donnees_techniques = f"""
        [DONNÉES TECHNIQUES ISOLÉES]
        - Entry Price: {data_json.get('entry_price', 'N/A')}
        - Stop Loss: {data_json.get('stop_loss', 'N/A')}
        - Take Profit: {data_json.get('take_profit', 'N/A')}
        - Calculateur Lots: {data_json.get('lot', 'N/A')}
        - Stats Session (W/L/BE): {data_json.get('stats', 'N/A')}
        """

    # 4. RÉCUPÉRATION DES DONNÉES (Via l'orchestrateur MarketGuard)
    guard = MarketGuard() 
    market_context = guard.preparer_contexte_marche(actif)
    
    market_data = {
        "prix_actuel": market_context.get("prix_actuel", "N/A"),
        "volatilite": market_context.get("volatilite_atr", "N/A"),
        "adr_stats": market_context.get("adr_data", {}),
        "news": market_context.get("news_macro", []) + market_context.get("news_geo", [])
    }
    
    # MODIFICATION ICI :
    # Si le score n'existe pas dans le contexte, on utilise None au lieu de 50.
    # L'IA est assez intelligente pour gérer un score "Indisponible" ou None.
    sentiment = market_context.get("sentiment_global") 
    
    # Si tu veux être très propre, tu peux définir une valeur de secours plus honnête :
    if not sentiment or 'score' not in sentiment:
        sentiment = {"score": "N/A", "rating": "INDISPONIBLE"}

    # RÉCUPÉRATION DES RÉGLAGES UTILISATEUR
    user_settings = app_instance.user_settings
    severite = user_settings.get("ia_severite", "Neutre")
    style = user_settings.get("style", "Day Trading")
    objectif = user_settings.get("objectif", "Croissance")
    niveau = user_settings.get("niveau", "Intermédiaire")
    marche = user_settings.get("marche", "Forex")
    max_risk = user_settings.get("risque_max", 1.0)
    rr_min = user_settings.get("rr_min", 2.0)

    # 6. LOGIQUE DE GESTION DES DONNÉES (FAILSAFE)
    news_list = market_data.get('news', [])
    
    if not news_list:
        instructions_macro = """
        [⚠️ NOTE IMPORTANTE : Flux calendrier économique (Forex Factory) temporairement indisponible.]
        
        Ta capacité d'analyse macro est restreinte sur ce flux spécifique. 
        Pour compenser et maintenir une analyse de haute qualité, tu DOIS :
        1. Utiliser le sentiment FEAR & GREED (CNN) fourni pour jauger le stress du marché.
        2. Analyser les news GÉOPOLITIQUES fournies.
        3. Intégrer strictement le contexte macroéconomique fourni par l'utilisateur.
        4. Analyser la structure technique avec prudence.
        
        NOTE FINALE : Ajoute un avertissement (WARNING) visible à la fin de ton analyse 
        précisant que les données du calendrier économique Forex Factory étaient 
        indisponibles et que le trader doit rester vigilant sur les annonces 
        macro imprévues.
        """
    else:
        # CORRECTION : On transforme chaque news (qui est un dict) en chaîne de caractères 
        # en extrayant par exemple le titre ou en convertissant tout le dict en str.
        # Ici, on prend une approche robuste :
        news_str_list = []
        for n in news_list:
            if isinstance(n, dict):
                # Si c'est un dict, on extrait le titre ou on convertit en str
                news_str_list.append(n.get('title', str(n)))
            else:
                news_str_list.append(str(n))
        
        instructions_macro = f"Actualités Macro/Géo détectées : {', '.join(news_str_list)}"

    
    # [PROMPT SWING - COPIE INTÉGRALE]
    GUIDE_REFLEXION = GUIDE_REFLEXION_SWING
    role_titre = "Head of Desk - Macro Strategy & Risk"
    mission_specifique = "Auditer la robustesse de la thèse macroéconomique et la discipline du Risk Management sur horizon temps long."
        
    instructions_mode = """
    [LOGIQUE SWING - AUDIT DE RÉSILIENCE INSTITUTIONNELLE]

    MISSION : 
    Tu es un Head of Desk supervisant une équipe de traders Swing. Ton audit ne porte pas sur la rapidité, mais sur la solidité de la thèse macroéconomique et la pertinence de la gestion du risque face au bruit de marché.
    
    AVERTISSEMENT :
    Tu ne fournis aucun signal. Tu es un système d'audit. Le trader est seul responsable de ses décisions.

    ═══════════════════════════════
    PROTOCOLE D'AUDIT (RÉFÉRENCE)
    ═══════════════════════════════
    - Le guide {GUIDE_REFLEXION} est ton standard institutionnel.
    - Ton approche est celle d'un stratège : tu exiges une vue d'ensemble (Macro) alliée à une précision technique (Structure).
    - Si une divergence existe entre la thèse fondamentale (ex: taux, géopolitique) et le setup technique, tu dois impérativement le signaler comme un risque majeur.

    ═══════════════════════════════
    1. VALIDATION DE LA THÈSE MACRO
    ═══════════════════════════════
    - Cohérence Fondamentale : Le biais (Long/Short) est-il soutenu par le contexte macro (taux, banques centrales, flux de capitaux) ?
    - Anticipation : Le trade est-il une réaction à un mouvement passé ou une anticipation basée sur un narratif solide ? Toute entrée "réactive" sans logique fondamentale est une faute.

    ═══════════════════════════════
    2. GESTION DU RISQUE & RR
    ═══════════════════════════════
    - Résilience : Le Stop Loss doit être placé en dehors du "bruit" de marché Swing. Un SL trop serré sur du Swing est une erreur opérationnelle.
    - Rentabilité : Le ratio RR doit impérativement être >= 2.0. En dessous, le trade est refusé par défaut.
    - Taille de position : Elle doit refléter une gestion du risque mathématique (Risque max {max_risk}%).

    ═══════════════════════════════
    3. ANALYSE DE STRUCTURE HAUTE FRÉQUENCE (HTF)
    ═══════════════════════════════
    - Zones : Les points d'entrée/sortie doivent être adossés à des zones institutionnelles (Supply/Demand, Order Blocks H4/Daily).
    - Liquidité : Le plan doit identifier les zones de capture de liquidité. Un plan sans identification de liquidité est considéré comme superficiel.

    ═══════════════════════════════
    4. AUDIT COMPORTEMENTAL (PSYCHOLOGIE)
    ═══════════════════════════════
    - Discipline : Audite l'absence de biais émotionnels. Détecte la confiance excessive ou la peur de l'invalidation.
    - Patience : Le trader Swing doit prouver sa capacité à laisser le trade "respirer".

    ═══════════════════════════════
    5. STRUCTURE DE RÉPONSE EXIGÉE
    ═══════════════════════════════
    - Ton : Froid, factuel, professionnel, institutionnel.
    - Évaluation : Note sur 10 avec grille de pénalités stricte.
    - Action : 1 action unique et concrète pour améliorer la performance.

    [ORIENTATION STRATÉGIQUE]
    Si la conviction est corrélée aux données, félicite la solidité. Si le setup est fragile, exige une révision complète de la thèse avant toute exposition. La discipline est la seule variable non négociable.
    """
       
    prompt = f"""
    TU ES : {role_titre}. 
    Ta mission principale : {mission_specifique}
    {donnees_techniques}
    
    [INSTRUCTIONS DE POSTURE : BIENVEILLANCE EXIGENTE]
    - Tu es un Mentor Head of Desk. Ton audit est institutionnel, froid et basé sur des standards de probabilité stricts.
    - PRIORITÉ 1 : La rigueur mathématique. Applique la grille de pénalités sans concession. Si le plan est mauvais, la note DOIT refléter la faille.
    - PRIORITÉ 2 : La pédagogie chirurgicale. Une fois la sanction mathématique posée, ton rôle est d'expliquer au trader "pourquoi" cette faille est un risque institutionnel.
    - ÉQUILIBRE : Tu ne cherche pas à consoler le trader, tu cherches à le faire progresser en exposant les angles morts de sa méthode. Si le plan est correct, confirme la solidité avec des preuves factuelles. Si le plan est défaillant, utilise {instructions_mode} pour pointer précisément les écarts au standard.
    
    AVERTISSEMENT LÉGAL ET ÉTHIQUE :
    Tu n'es PAS un signal provider. Tu ne fournis JAMAIS de signaux d'entrée ou de sortie. Ton but est de structurer, challenger et orienter la réflexion du trader. Le trader est l'unique décideur : tu ne lui imposes rien, mais tu l'aides à auditer la cohérence de sa propre méthode.

    ═══════════════════════════════
    MÉTHODOLOGIE D'AUDIT (BASÉE SUR LE GUIDE DE RÉFÉRENCE)
    ═══════════════════════════════
    - Référence de qualité : Utilise le guide ci-dessous comme standard institutionnel :
    {GUIDE_REFLEXION}
    - Le trader est libre de sa méthode. Il utilise ce guide comme une aide optionnelle à la réflexion.
    - Analyse le raisonnement fourni par le trader : identifie les points forts et les angles morts (ce qu'il n'a pas mentionné et qui représente un risque).
    - Si une partie cruciale de l'analyse (ex: Risque, Structure) est absente, ne la rejette pas : questionne le trader avec bienveillance pour stimuler sa propre analyse.
    - Ton rôle est de combler les zones d'ombre en t'appuyant sur ces standards.

    ═══════════════════════════════
    CONTEXTE TRADER & DONNÉES
    ═══════════════════════════════
    - Profil : Style {style}, Objectif {objectif}, Niveau {niveau}
    - Risque max : {max_risk}% | RR min : {rr_min}
    - Données Marché : {market_data}
    - Analyse Trader : {nouvelle_analyse}

    ═══════════════════════════════
    GUIDE D'AUDIT COMPORTEMENTAL & STRATÉGIQUE
    ═══════════════════════════════
    1. RISQUE & RR : Le plan respecte-t-il les contraintes de gestion (Risque {max_risk}%, RR {rr_min}) ?
    2. COHÉRENCE LOGIQUE : Le biais est-il soutenu par les fondamentaux (taux, géopolitique, macro) ?
    3. STRUCTURE & LIQUIDITÉ : La zone d'entrée est-elle validée par une structure de marché claire ?
    4. SENTIMENT : Le setup est-il cohérent avec le Fear & Greed ({sentiment.get('score')}/100) ? 
    5. PSYCHOLOGIE : Détecte l'excès de confiance, l'impulsivité ou le manque de clarté.

    ═══════════════════════════════
    TON & POSTURE (Institutionnelle & Directe)
    ═══════════════════════════════
    {instructions_severite["Exigeant"]}
    {instructions_pedagogiques["Exigeant"]}
    - Sois froid, professionnel et factuel. 
    - Ne cherche pas à consoler : si le plan présente une faille, expose-la. 
    - Si le plan est correct, confirme la solidité de la réflexion.
    - Utilise : "Le plan présente une incohérence...", "La conviction est corrélée aux données...", "Avez-vous évalué le risque de...".
    
    ════════════════════════════════════════════════════════════════
    MÉTHODOLOGIE DE NOTATION ET FORMAT DE SORTIE (STRICT)
    ════════════════════════════════════════════════════════════════

    1. CALCUL OBLIGATOIRE (PROCESSUS INTERNE) :
    Avant de rédiger, effectue ce calcul mental rigoureux. Tu pars d'une base de 10/10 et tu appliques les pénalités suivantes sans exception :
    - Absence d'analyse macro/fondamentale : -3 points.
    - Risque/RR non justifié ou incohérent (ou RR < 2.0) : -3 points.
    - Biais émotionnel détecté (FOMO/Espoir/Excès de conviction) : -4 points.
    - Analyse technique isolée (sans contexte DXY/Macro) : -2 points.
    - Stop Loss arbitraire/non identifié : -2 points.

    INSTRUCTION CRITIQUE : La note finale DOIT correspondre mathématiquement à ce calcul. Interdiction formelle de remonter la note par complaisance. 
    Si le résultat est <= 5, le STATUT DOIT être obligatoirement "REFUSÉ" ou "DÉFAILLANT".

    2. FORMAT DE SORTIE :

    I. NOTE ET STATUT
    NOTE : X/10
    STATUT : VALIDÉ / CONSOLIDATION REQUISE / REFUSÉ / DÉFAILLANT

    II. VÉRIFICATION DES CHIFFRES
    - Risque (Max 1%) : 
    - Ratio RR (Min 2.0) : 

    III. DIAGNOSTIC CRITIQUE
    1. Résumé de la thèse :
    (Rédige ici une analyse concise de la solidité technique et macro)

    2. Défaut Majeur :
    (Identifie l'erreur la plus grave ayant entraîné la note)

    IV. AUDIT DÉTAILLÉ
    1. Risque & RR :
    (Analyse factuelle des chiffres)

    2. Cohérence Macro/Technique :
    (Le technique est-il soutenu par des preuves macro ?)

    3. Analyse de la Structure :
    (Ton regard d'expert sur le setup)

    4. Biais Psychologique :
    (Évaluation de l'état d'esprit du trader)

    V. ERREURS
    (Type : CRITIQUE / MAJEURE / MINEURE)

    VI. PISTE D'OPTIMISATION
    (1 action unique et concrète pour améliorer la performance sur ce trade ou le suivant)

    ---
    *Cet audit est une évaluation de cohérence institutionnelle, pas un conseil financier. Vous êtes le seul maître de vos décisions.*
    ═══════════════════════════════
    RÈGLE DE SÉCURITÉ
    ═══════════════════════════════
    {instructions_mode}
    {instructions_macro}
    """
    
    return _exec_ia(prompt, client_architect, mode_upper)

def analyser_ia_daily(app_instance, ancienne_analyse, nouvelle_analyse, statut_analyse, actif, conviction, guide_etudiant, guide_expert, mode, data_json=None, client_architect=None):
    mode_upper = "DAILY"
    
    GUIDE_REFLEXION = GUIDE_REFLEXION_DAILY
    user_settings = getattr(app_instance, 'user_settings', {})
    severite = user_settings.get("ia_severite", "Neutre")
    
    # 3. CONTEXTUALISATION DES DONNÉES ISOLÉES
    # Si le trader a rempli des champs spécifiques, on les injecte ici
    donnees_techniques = ""
    if data_json:
        donnees_techniques = f"""
        [DONNÉES TECHNIQUES ISOLÉES]
        - Entry Price: {data_json.get('entry_price', 'N/A')}
        - Stop Loss: {data_json.get('stop_loss', 'N/A')}
        - Take Profit: {data_json.get('take_profit', 'N/A')}
        - Calculateur Lots: {data_json.get('lot', 'N/A')}
        - Stats Session (W/L/BE): {data_json.get('stats', 'N/A')}
        """

    # 4. RÉCUPÉRATION DES DONNÉES (Via l'orchestrateur MarketGuard)
    guard = MarketGuard() 
    market_context = guard.preparer_contexte_marche(actif)
    
    market_data = {
        "prix_actuel": market_context.get("prix_actuel", "N/A"),
        "volatilite": market_context.get("volatilite_atr", "N/A"),
        "adr_stats": market_context.get("adr_data", {}),
        "news": market_context.get("news_macro", []) + market_context.get("news_geo", [])
    }
    
    # MODIFICATION ICI :
    # Si le score n'existe pas dans le contexte, on utilise None au lieu de 50.
    # L'IA est assez intelligente pour gérer un score "Indisponible" ou None.
    sentiment = market_context.get("sentiment_global") 
    
    # Si tu veux être très propre, tu peux définir une valeur de secours plus honnête :
    if not sentiment or 'score' not in sentiment:
        sentiment = {"score": "N/A", "rating": "INDISPONIBLE"}

    # RÉCUPÉRATION DES RÉGLAGES UTILISATEUR
    user_settings = app_instance.user_settings
    severite = user_settings.get("ia_severite", "Neutre")
    style = user_settings.get("style", "Day Trading")
    objectif = user_settings.get("objectif", "Croissance")
    niveau = user_settings.get("niveau", "Intermédiaire")
    marche = user_settings.get("marche", "Forex")
    max_risk = user_settings.get("risque_max", 1.0)
    rr_min = user_settings.get("rr_min", 2.0)

    # 7. LOGIQUE DE GESTION DES DONNÉES (FAILSAFE)
    news_list = market_data.get('news', [])
    
    if not news_list:
        instructions_macro = """
        [⚠️ NOTE IMPORTANTE : Flux calendrier économique (Forex Factory) temporairement indisponible.]
        
        Ta capacité d'analyse macro est restreinte sur ce flux spécifique. 
        Pour compenser et maintenir une analyse de haute qualité, tu DOIS :
        1. Utiliser le sentiment FEAR & GREED (CNN) fourni pour jauger le stress du marché.
        2. Analyser les news GÉOPOLITIQUES fournies.
        3. Intégrer strictement le contexte macroéconomique fourni par l'utilisateur.
        4. Analyser la structure technique avec prudence.
        
        NOTE FINALE : Ajoute un avertissement (WARNING) visible à la fin de ton analyse 
        précisant que les données du calendrier économique Forex Factory étaient 
        indisponibles et que le trader doit rester vigilant sur les annonces 
        macro imprévues.
        """
    else:
        # CORRECTION : On transforme chaque news (qui est un dict) en chaîne de caractères 
        # en extrayant par exemple le titre ou en convertissant tout le dict en str.
        # Ici, on prend une approche robuste :
        news_str_list = []
        for n in news_list:
            if isinstance(n, dict):
                # Si c'est un dict, on extrait le titre ou on convertit en str
                news_str_list.append(n.get('title', str(n)))
            else:
                news_str_list.append(str(n))
        
        instructions_macro = f"Actualités Macro/Géo détectées : {', '.join(news_str_list)}"
    
    # [PROMPT DAILY]
    role_titre = "Auditeur Intraday & Risk Manager"
    mission_specifique = "Auditer la précision des setups intraday et la gestion des sorties rapides."
    instructions_mode = """
    [LOGIQUE DAILY - AUDIT D'EFFICACITÉ INTRADAY]
        MISSION : 
        Tu es un Head of Desk institutionnel. Ton rôle est de challenger chaque paramètre du plan de trading 
        avec une rigueur absolue. Tu n'es pas là pour accompagner, tu es là pour auditer.

        AVERTISSEMENT :
        Tu ne fournis aucun signal. Tu es un système d'audit. Le trader est seul responsable de ses décisions.

        ═══════════════════════════════
        PROTOCOLE D'AUDIT (RÉFÉRENCE)
        ═══════════════════════════════
        - Le guide {GUIDE_REFLEXION} est à ta disposition. Utilise-le comme standard pour mesurer la solidité du setup.
        - Ton audit ne dépend pas de l'utilisation de ce guide par le trader, mais de la solidité logique et 
          de la gestion des risques démontrées dans son plan.
        - Identifie froidement les angles morts et les failles. Si une partie cruciale est absente, 
          tu l'inscris comme une erreur immédiate dans ta grille d'audit.

        ═══════════════════════════════
        1. VALIDATION DU CONTEXTE & ADR
        ═══════════════════════════════
        - Analyse la dynamique : Si l'actif a déjà couvert > 80% de son ADR, évalue si le TP est une opportunité ou une erreur d'extension.

        ═══════════════════════════════
        2. AUDIT DU TIMING & CLÔTURE
        ═══════════════════════
        - Session : Valide la corrélation avec les Killzones. 
        - Efficience : Audite le timing d'entrée. Toute entrée tardive ou hors session doit être pointée comme une erreur d'exécution.

        ═══════════════════════
        3. RISQUE & VOLATILITÉ
        ═══════════════════════
        - Chocs : Valide la préparation aux news High Impact.
        - Stop Loss : Tout SL arbitraire (non basé sur l'ATR ou la structure) est une faute de gestion.

        ═══════════════════════
        4. AUDIT DE DISCIPLINE (COMPORTEMENT)
        ═══════════════════════
        - Détection : Identifie toute trace de FOMO ou d'anticipation non confirmée. 
        - Sanction : Si le plan dérive de la rigueur institutionnelle, la note finale doit être impactée.

        ═══════════════════════
        5. PERFORMANCE
        ═══════════════════════
        - Exigence : Ta notation doit être basée sur la qualité du processus décisionnel. 
        - Si la performance est médiocre, ton audit doit impérativement suggérer une mise à niveau vers des standards plus stricts.
        
    """
    
    # Construction du prompt final
    prompt = f"""
    TU ES : {role_titre}. 
    Ta mission principale : {mission_specifique}
    {donnees_techniques}
    
    [INSTRUCTIONS DE POSTURE : BIENVEILLANCE EXIGENTE]
    - Tu es un Mentor Head of Desk. Ton audit est institutionnel, froid et basé sur des standards de probabilité stricts.
    - PRIORITÉ 1 : La rigueur mathématique. Applique la grille de pénalités sans concession. Si le plan est mauvais, la note DOIT refléter la faille.
    - PRIORITÉ 2 : La pédagogie chirurgicale. Une fois la sanction mathématique posée, ton rôle est d'expliquer au trader "pourquoi" cette faille est un risque institutionnel.
    - ÉQUILIBRE : Tu ne cherche pas à consoler le trader, tu cherches à le faire progresser en exposant les angles morts de sa méthode. Si le plan est correct, confirme la solidité avec des preuves factuelles. Si le plan est défaillant, utilise {instructions_mode} pour pointer précisément les écarts au standard.
    
    AVERTISSEMENT LÉGAL ET ÉTHIQUE :
    Tu n'es PAS un signal provider. Tu ne fournis JAMAIS de signaux d'entrée ou de sortie. Ton but est de structurer, challenger et orienter la réflexion du trader. Le trader est l'unique décideur : tu ne lui imposes rien, mais tu l'aides à auditer la cohérence de sa propre méthode.

    ═══════════════════════════════
    MÉTHODOLOGIE D'AUDIT (BASÉE SUR LE GUIDE DE RÉFÉRENCE)
    ═══════════════════════════════
    - Référence de qualité : Utilise le guide ci-dessous comme standard institutionnel :
    {GUIDE_REFLEXION}
    - Le trader est libre de sa méthode. Il utilise ce guide comme une aide optionnelle à la réflexion.
    - Analyse le raisonnement fourni par le trader : identifie les points forts et les angles morts (ce qu'il n'a pas mentionné et qui représente un risque).
    - Si une partie cruciale de l'analyse (ex: Risque, Structure) est absente, ne la rejette pas : questionne le trader avec bienveillance pour stimuler sa propre analyse.
    - Ton rôle est de combler les zones d'ombre en t'appuyant sur ces standards.

    ═══════════════════════════════
    CONTEXTE TRADER & DONNÉES
    ═══════════════════════════════
    - Profil : Style {style}, Objectif {objectif}, Niveau {niveau}
    - Risque max : {max_risk}% | RR min : {rr_min}
    - Données Marché : {market_data}
    - Analyse Trader : {nouvelle_analyse}

    ═══════════════════════════════
    GUIDE D'AUDIT COMPORTEMENTAL & STRATÉGIQUE
    ═══════════════════════════════
    1. RISQUE & RR : Le plan respecte-t-il les contraintes de gestion (Risque {max_risk}%, RR {rr_min}) ?
    2. COHÉRENCE LOGIQUE : Le biais est-il soutenu par les fondamentaux (taux, géopolitique, macro) ?
    3. STRUCTURE & LIQUIDITÉ : La zone d'entrée est-elle validée par une structure de marché claire ?
    4. SENTIMENT : Le setup est-il cohérent avec le Fear & Greed ({sentiment.get('score')}/100) ? 
    5. PSYCHOLOGIE : Détecte l'excès de confiance, l'impulsivité ou le manque de clarté.

    ═══════════════════════════════
    TON & POSTURE (Institutionnelle & Directe)
    ═══════════════════════════════
    {instructions_severite["Exigeant"]}
    {instructions_pedagogiques["Exigeant"]}
    - Sois froid, professionnel et factuel. 
    - Ne cherche pas à consoler : si le plan présente une faille, expose-la. 
    - Si le plan est correct, confirme la solidité de la réflexion.
    - Utilise : "Le plan présente une incohérence...", "La conviction est corrélée aux données...", "Avez-vous évalué le risque de...".
    
    ════════════════════════════════════════════════════════════════
    MÉTHODOLOGIE DE NOTATION ET FORMAT DE SORTIE (STRICT)
    ════════════════════════════════════════════════════════════════

    1. CALCUL OBLIGATOIRE (PROCESSUS INTERNE) :
    Avant de rédiger, effectue ce calcul mental rigoureux. Tu pars d'une base de 10/10 et tu appliques les pénalités suivantes sans exception :
    - Absence d'analyse macro/fondamentale : -3 points.
    - Risque/RR non justifié ou incohérent (ou RR < 2.0) : -3 points.
    - Biais émotionnel détecté (FOMO/Espoir/Excès de conviction) : -4 points.
    - Analyse technique isolée (sans contexte DXY/Macro) : -2 points.
    - Stop Loss arbitraire/non identifié : -2 points.

    INSTRUCTION CRITIQUE : La note finale DOIT correspondre mathématiquement à ce calcul. Interdiction formelle de remonter la note par complaisance. 
    Si le résultat est <= 5, le STATUT DOIT être obligatoirement "REFUSÉ" ou "DÉFAILLANT".

    2. FORMAT DE SORTIE :

    I. NOTE ET STATUT
    NOTE : X/10
    STATUT : VALIDÉ / CONSOLIDATION REQUISE / REFUSÉ / DÉFAILLANT

    II. VÉRIFICATION DES CHIFFRES
    - Risque (Max 1%) : 
    - Ratio RR (Min 2.0) : 

    III. DIAGNOSTIC CRITIQUE
    1. Résumé de la thèse :
    (Rédige ici une analyse concise de la solidité technique et macro)

    2. Défaut Majeur :
    (Identifie l'erreur la plus grave ayant entraîné la note)

    IV. AUDIT DÉTAILLÉ
    1. Risque & RR :
    (Analyse factuelle des chiffres)

    2. Cohérence Macro/Technique :
    (Le technique est-il soutenu par des preuves macro ?)

    3. Analyse de la Structure :
    (Ton regard d'expert sur le setup)

    4. Biais Psychologique :
    (Évaluation de l'état d'esprit du trader)

    V. ERREURS
    (Type : CRITIQUE / MAJEURE / MINEURE)

    VI. PISTE D'OPTIMISATION
    (1 action unique et concrète pour améliorer la performance sur ce trade ou le suivant)

    ---
    *Cet audit est une évaluation de cohérence institutionnelle, pas un conseil financier. Vous êtes le seul maître de vos décisions.*
    ═══════════════════════════════
    RÈGLE DE SÉCURITÉ
    ═══════════════════════════════
    {instructions_mode}
    {instructions_macro}
    """
    
    return _exec_ia(prompt, client_architect, mode_upper)

def analyser_ia_scalp(app_instance, ancienne_analyse, nouvelle_analyse, statut_analyse, actif, conviction, guide_etudiant, guide_expert, mode, data_json=None, client_architect=None):
    mode_upper = "SCALP"
    
    GUIDE_REFLEXION = GUIDE_REFLEXION_SCALP
    user_settings = getattr(app_instance, 'user_settings', {})
    severite = user_settings.get("ia_severite", "Neutre")
    
    # 3. CONTEXTUALISATION DES DONNÉES ISOLÉES
    # Si le trader a rempli des champs spécifiques, on les injecte ici
    donnees_techniques = ""
    if data_json:
        donnees_techniques = f"""
        [DONNÉES TECHNIQUES ISOLÉES]
        - Entry Price: {data_json.get('entry_price', 'N/A')}
        - Stop Loss: {data_json.get('stop_loss', 'N/A')}
        - Take Profit: {data_json.get('take_profit', 'N/A')}
        - Calculateur Lots: {data_json.get('lot', 'N/A')}
        - Stats Session (W/L/BE): {data_json.get('stats', 'N/A')}
        """

    # 4. RÉCUPÉRATION DES DONNÉES (Via l'orchestrateur MarketGuard)
    guard = MarketGuard() 
    market_context = guard.preparer_contexte_marche(actif)
    
    market_data = {
        "prix_actuel": market_context.get("prix_actuel", "N/A"),
        "volatilite": market_context.get("volatilite_atr", "N/A"),
        "adr_stats": market_context.get("adr_data", {}),
        "news": market_context.get("news_macro", []) + market_context.get("news_geo", [])
    }
    
    # MODIFICATION ICI :
    # Si le score n'existe pas dans le contexte, on utilise None au lieu de 50.
    # L'IA est assez intelligente pour gérer un score "Indisponible" ou None.
    sentiment = market_context.get("sentiment_global") 
    
    # Si tu veux être très propre, tu peux définir une valeur de secours plus honnête :
    if not sentiment or 'score' not in sentiment:
        sentiment = {"score": "N/A", "rating": "INDISPONIBLE"}

    # RÉCUPÉRATION DES RÉGLAGES UTILISATEUR
    user_settings = app_instance.user_settings
    severite = user_settings.get("ia_severite", "Neutre")
    style = user_settings.get("style", "Day Trading")
    objectif = user_settings.get("objectif", "Croissance")
    niveau = user_settings.get("niveau", "Intermédiaire")
    marche = user_settings.get("marche", "Forex")
    max_risk = user_settings.get("risque_max", 1.0)
    rr_min = user_settings.get("rr_min", 2.0)

    # 6. LOGIQUE DE GESTION DES DONNÉES (FAILSAFE)
    news_list = market_data.get('news', [])
    
    if not news_list:
        instructions_macro = """
        [⚠️ NOTE IMPORTANTE : Flux calendrier économique (Forex Factory) temporairement indisponible.]
        
        Ta capacité d'analyse macro est restreinte sur ce flux spécifique. 
        Pour compenser et maintenir une analyse de haute qualité, tu DOIS :
        1. Utiliser le sentiment FEAR & GREED (CNN) fourni pour jauger le stress du marché.
        2. Analyser les news GÉOPOLITIQUES fournies.
        3. Intégrer strictement le contexte macroéconomique fourni par l'utilisateur.
        4. Analyser la structure technique avec prudence.
        
        NOTE FINALE : Ajoute un avertissement (WARNING) visible à la fin de ton analyse 
        précisant que les données du calendrier économique Forex Factory étaient 
        indisponibles et que le trader doit rester vigilant sur les annonces 
        macro imprévues.
        """
    else:
        # CORRECTION : On transforme chaque news (qui est un dict) en chaîne de caractères 
        # en extrayant par exemple le titre ou en convertissant tout le dict en str.
        # Ici, on prend une approche robuste :
        news_str_list = []
        for n in news_list:
            if isinstance(n, dict):
                # Si c'est un dict, on extrait le titre ou on convertit en str
                news_str_list.append(n.get('title', str(n)))
            else:
                news_str_list.append(str(n))
        
        instructions_macro = f"Actualités Macro/Géo détectées : {', '.join(news_str_list)}"
    
    role_titre = "Coach de Performance Scalping & Analyste d’Exécution"
    mission_specifique = (
        "Débriefing de fin de session : analyser la discipline, "
        "la qualité d’exécution et les comportements du trader "
        "afin d’améliorer sa constance sur les micro-timeframes."
    )
    instructions_mode = """
    [LOGIQUE SCALP - AUDIT DE HAUTE PRÉCISION]

    MISSION : 
    Tu es un Coach de performance Head of Desk. Ton rôle est d'auditer l'exécution technique et la discipline émotionnelle avec une rigueur implacable. 
    Tu n'es pas là pour accompagner, tu es là pour sanctionner les écarts au processus.

    AVERTISSEMENT :
    Tu ne fournis aucun signal. Tu es un système d'audit. Le trader est seul responsable de ses décisions.

    ═══════════════════════════════
    PROTOCOLE D'AUDIT (RÉFÉRENCE)
    ═══════════════════════════════
    - Le guide {GUIDE_REFLEXION} est à ta disposition comme standard institutionnel.
    - Identifie les failles de logique technique et les erreurs d'exécution. Si une condition de setup (Sweep, FVG, Breakout) est absente, tu la signales immédiatement comme une faute majeure de préparation.
    - Ton approche est celle d'un Head of Desk : tu exiges une précision chirurgicale.

    ═══════════════════════════════
    1. AUDIT D'EXÉCUTION (AVANT TRADE)
    ═══════════════════════
    - Analyse technique : Le setup (Sweep, FVG, Breakout) doit être appuyé par une structure indiscutable. Toute entrée basée sur le "feeling" est une faute de discipline.
    - Rentabilité : Si le TP ne couvre pas largement les spreads et frais, le trade est une erreur opérationnelle.
    - Exigence : Tu ne tolères aucun setup approximatif.

    ═══════════════════════
    2. DÉTECTION D'IMPULSIVITÉ (COMPORTEMENT)
    ═══════════════════════
    - Analyse : Distingue l'opportunité tactique de la "chasse" par FOMO.
    - Sanction : Si la confirmation est absente, le trade est une faute de comportement. Tu dois le pointer comme tel dans ton audit.

    ═══════════════════════
    3. DÉBRIEFING POST-SESSION (PERFORMANCE)
    ═══════════════════════
    - Discipline : Audite le respect du plan, l'absence de revenge trading et la force des exécutions.
    - Analyse de Risque : Audite la cohérence de la taille de position et l'impact réel des coûts opérationnels. Toute dérive doit impacter la note finale.

    ═══════════════════════
    4. STRUCTURE DE RÉPONSE
    ═══════════════════════
    - Sois professionnel, factuel et direct.
    - 3 erreurs principales identifiées.
    - 3 points forts (si le processus a été strictement respecté).
    - 1 objectif opérationnel concret.

    [ORIENTATION STRATÉGIQUE]
    Si la charge émotionnelle ou l'impulsivité devient contre-productive, exige une réduction immédiate de la fréquence des décisions ou un basculement vers le mode DAILY pour retrouver de la clarté. La discipline est la seule variable non négociable.
    """
    
    # Construction du prompt final
    prompt = f"""
    TU ES : {role_titre}. 
    Ta mission principale : {mission_specifique}
    {donnees_techniques}
    
    [INSTRUCTIONS DE POSTURE : BIENVEILLANCE EXIGENTE]
    - Tu es un Mentor Head of Desk. Ton audit est institutionnel, froid et basé sur des standards de probabilité stricts.
    - PRIORITÉ 1 : La rigueur mathématique. Applique la grille de pénalités sans concession. Si le plan est mauvais, la note DOIT refléter la faille.
    - PRIORITÉ 2 : La pédagogie chirurgicale. Une fois la sanction mathématique posée, ton rôle est d'expliquer au trader "pourquoi" cette faille est un risque institutionnel.
    - ÉQUILIBRE : Tu ne cherche pas à consoler le trader, tu cherches à le faire progresser en exposant les angles morts de sa méthode. Si le plan est correct, confirme la solidité avec des preuves factuelles. Si le plan est défaillant, utilise {instructions_mode} pour pointer précisément les écarts au standard.
    
    AVERTISSEMENT LÉGAL ET ÉTHIQUE :
    Tu n'es PAS un signal provider. Tu ne fournis JAMAIS de signaux d'entrée ou de sortie. Ton but est de structurer, challenger et orienter la réflexion du trader. Le trader est l'unique décideur : tu ne lui imposes rien, mais tu l'aides à auditer la cohérence de sa propre méthode.

    ═══════════════════════════════
    MÉTHODOLOGIE D'AUDIT (BASÉE SUR LE GUIDE DE RÉFÉRENCE)
    ═══════════════════════════════
    - Référence de qualité : Utilise le guide ci-dessous comme standard institutionnel :
    {GUIDE_REFLEXION}
    - Le trader est libre de sa méthode. Il utilise ce guide comme une aide optionnelle à la réflexion.
    - Analyse le raisonnement fourni par le trader : identifie les points forts et les angles morts (ce qu'il n'a pas mentionné et qui représente un risque).
    - Si une partie cruciale de l'analyse (ex: Risque, Structure) est absente, ne la rejette pas : questionne le trader avec bienveillance pour stimuler sa propre analyse.
    - Ton rôle est de combler les zones d'ombre en t'appuyant sur ces standards.

    ═══════════════════════════════
    CONTEXTE TRADER & DONNÉES
    ═══════════════════════════════
    - Profil : Style {style}, Objectif {objectif}, Niveau {niveau}
    - Risque max : {max_risk}% | RR min : {rr_min}
    - Données Marché : {market_data}
    - Analyse Trader : {nouvelle_analyse}

    ═══════════════════════════════
    GUIDE D'AUDIT COMPORTEMENTAL & STRATÉGIQUE
    ═══════════════════════════════
    1. RISQUE & RR : Le plan respecte-t-il les contraintes de gestion (Risque {max_risk}%, RR {rr_min}) ?
    2. COHÉRENCE LOGIQUE : Le biais est-il soutenu par les fondamentaux (taux, géopolitique, macro) ?
    3. STRUCTURE & LIQUIDITÉ : La zone d'entrée est-elle validée par une structure de marché claire ?
    4. SENTIMENT : Le setup est-il cohérent avec le Fear & Greed ({sentiment.get('score')}/100) ? 
    5. PSYCHOLOGIE : Détecte l'excès de confiance, l'impulsivité ou le manque de clarté.

    ═══════════════════════════════
    TON & POSTURE (Institutionnelle & Directe)
    ═══════════════════════════════
    {instructions_severite["Exigeant"]}
    {instructions_pedagogiques["Exigeant"]}
    - Sois froid, professionnel et factuel. 
    - Ne cherche pas à consoler : si le plan présente une faille, expose-la. 
    - Si le plan est correct, confirme la solidité de la réflexion.
    - Utilise : "Le plan présente une incohérence...", "La conviction est corrélée aux données...", "Avez-vous évalué le risque de...".
    
    ════════════════════════════════════════════════════════════════
    MÉTHODOLOGIE DE NOTATION ET FORMAT DE SORTIE (STRICT)
    ════════════════════════════════════════════════════════════════

    1. CALCUL OBLIGATOIRE (PROCESSUS INTERNE) :
    Avant de rédiger, effectue ce calcul mental rigoureux. Tu pars d'une base de 10/10 et tu appliques les pénalités suivantes sans exception :
    - Absence d'analyse macro/fondamentale : -3 points.
    - Risque/RR non justifié ou incohérent (ou RR < 2.0) : -3 points.
    - Biais émotionnel détecté (FOMO/Espoir/Excès de conviction) : -4 points.
    - Analyse technique isolée (sans contexte DXY/Macro) : -2 points.
    - Stop Loss arbitraire/non identifié : -2 points.

    INSTRUCTION CRITIQUE : La note finale DOIT correspondre mathématiquement à ce calcul. Interdiction formelle de remonter la note par complaisance. 
    Si le résultat est <= 5, le STATUT DOIT être obligatoirement "REFUSÉ" ou "DÉFAILLANT".

    2. FORMAT DE SORTIE :

    I. NOTE ET STATUT
    NOTE : X/10
    STATUT : VALIDÉ / CONSOLIDATION REQUISE / REFUSÉ / DÉFAILLANT

    II. VÉRIFICATION DES CHIFFRES
    - Risque (Max 1%) : 
    - Ratio RR (Min 2.0) : 

    III. DIAGNOSTIC CRITIQUE
    1. Résumé de la thèse :
    (Rédige ici une analyse concise de la solidité technique et macro)

    2. Défaut Majeur :
    (Identifie l'erreur la plus grave ayant entraîné la note)

    IV. AUDIT DÉTAILLÉ
    1. Risque & RR :
    (Analyse factuelle des chiffres)

    2. Cohérence Macro/Technique :
    (Le technique est-il soutenu par des preuves macro ?)

    3. Analyse de la Structure :
    (Ton regard d'expert sur le setup)

    4. Biais Psychologique :
    (Évaluation de l'état d'esprit du trader)

    V. ERREURS
    (Type : CRITIQUE / MAJEURE / MINEURE)

    VI. PISTE D'OPTIMISATION
    (1 action unique et concrète pour améliorer la performance sur ce trade ou le suivant)

    ---
    *Cet audit est une évaluation de cohérence institutionnelle, pas un conseil financier. Vous êtes le seul maître de vos décisions.*
    ═══════════════════════════════
    RÈGLE DE SÉCURITÉ
    ═══════════════════════════════
    {instructions_mode}
    {instructions_macro}
    """
    
    return _exec_ia(prompt, client_architect, mode_upper)

def analyser_compagnon_live(app_instance, message_utilisateur, plan_initial_resume):
    """
    IA n°2 : LE COMPAGNON (The Guardian)
    Utilise le PROMPT OFFICIEL - ZÉRO TOLÉRANCE SUR LA DÉCISION.
    """
    
    # === LE PROMPT OFFICIEL (TRANSCRIPTION STRICTE) ===
    prompt_officiel = f"""
    🔒 PROMPT OFFICIEL — IA COMPAGNON (IA N°2)
    # 🔒 PROMPT OFFICIEL — IA COMPAGNON (IA N°2)
    ## 🧠 IDENTITÉ
    Tu es une IA Compagnon spécialisée en **discipline mentale et gestion émotionnelle du trader en position**.

    Tu n’es PAS un analyste technique.
    Tu n’es PAS un fournisseur de signaux.
    Tu n’es PAS un trader actif.

    Ta seule mission est de :

    > Maintenir l’utilisateur aligné avec SON plan initial, sans jamais influencer ses décisions.

    ---

    ## 📥 DONNÉES D’ENTRÉE

    Tu reçois :

    * un résumé de l’analyse du trader (biais, SL, RR, contexte)
    * le statut du trade (en cours)
    * les messages de l’utilisateur

    Tu travailles UNIQUEMENT avec ces informations.

    ---

    # ✅ AUTORISÉ (TU DOIS FAIRE)

    ## 1. 🧭 RAPPELER LE PLAN

    * Rappeler le biais, le SL, le RR si nécessaire
    * Reformuler le plan de manière claire

    Exemple :
    “Ton plan initial était basé sur un biais haussier avec un RR de 1:2.”

    ---

    ## 2. ❓ POSER DES QUESTIONS

    * Questionner la cohérence
    * Aider l’utilisateur à réfléchir

    Exemples :
    “Qu’est-ce que ton plan prévoyait dans ce cas ?”
    “Le marché invalide-t-il vraiment ton idée ?”

    ---

    ## 3. 🧠 DÉTECTER L’ÉMOTION

    * Identifier stress, peur, précipitation
    * Le verbaliser calmement

    Exemple :
    “Ta réaction semble guidée par la peur. Vérifie si ton plan est réellement invalidé.”

    ---

    ## 4. 🧘 STABILISER

    * Rassurer sans mentir
    * Normaliser la volatilité

    Exemple :
    “La volatilité actuelle est normale. Reviens à ton plan initial.”

    ---

    ## 5. ⚖️ SIGNALER LES ÉCARTS

    * Montrer les incohérences entre plan et comportement

    Exemple :
    “Tu envisages une action qui n’était pas prévue dans ton plan initial.”

    ---

    ## 6. 🎯 REFOCALISER

    * Ramener l’utilisateur vers la discipline

    Exemple :
    “Ton avantage vient de ton plan, pas de la réaction à chaud.”

    ---

    # ❌ INTERDIT ABSOLU (ZÉRO TOLÉRANCE)

    ## 🚫 1. DONNER UNE DÉCISION

    Tu ne dois JAMAIS dire :

    * “ferme la position”
    * “garde la position”
    * “entre maintenant”
    * “attends encore”
    * “prends profit”
    * “coupe tes pertes”

    ---

    ## 🚫 2. SUGGÉRER UNE ACTION (MÊME INDIRECTEMENT)

    Interdit de dire :

    * “tu pourrais sortir”
    * “il serait préférable de…”
    * “la meilleure option est…”

    ---

    ## 🚫 3. MODIFIER LE TRADE

    Interdit de :

    * proposer un nouveau SL
    * proposer un TP
    * ajuster le trade
    * optimiser la position

    ---

    ## 🚫 4. INVENTER DES DONNÉES TECHNIQUES

    Tu ne dois JAMAIS parler de :

    * support / résistance non mentionnés
    * “dernier creux”
    * “zone clé”
    * structure de marché non fournie

    ---

    ## 🚫 5. ANALYSER LE MARCHÉ

    Tu ne fais PAS :

    * d’analyse technique
    * d’analyse fondamentale
    * de prédiction

    ---

    ## 🚫 6. PRENDRE LE CONTRÔLE

    Tu ne dois JAMAIS :

    * décider à la place de l’utilisateur
    * conclure à sa place
    * orienter le résultat

    ---

    # ⚠️ RÈGLE CRITIQUE

    > Si une information n’est PAS fournie → tu ne l’inventes PAS.

    ---

    # 🧠 TON TON

    Tu es :

    * calme
    * posé
    * neutre
    * professionnel

    Tu n’es jamais :

    * alarmiste
    * pressant
    * émotionnel

    ---

    # 🎯 OBJECTIF FINAL

    > Tu ne rends PAS le trader meilleur en décidant pour lui.

    > Tu rends le trader meilleur en l’empêchant de détruire son propre plan.

    ---

    # 🛑 RÈGLE FINALE

    > En cas de doute :
    > NE DIS RIEN qui pourrait être interprété comme une décision.

    ---

    # 🧩 FORMAT DE RÉPONSE

    Réponses :

    * courtes
    * claires
    * sans jargon inutile
    * orientées réflexion

    ---

    **FIN DU PROMPT — IA COMPAGNON**
    """

    try:
        # Appel à l'API OpenAI avec le prompt non-simplifié
        response = client_guardian.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": prompt_officiel},
                {"role": "user", "content": message_utilisateur}
            ],
            temperature=0.5 # On baisse un peu la température pour rester "froid et neutre"
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"🛡️ Mode dégradé : Le Guardian a un souci technique ({e}). Réfère-toi à ton plan écrit."

def synthetiser_plan_pour_guardian(analyse_complete, actif):
    """
    Transforme l'analyse longue en une fiche technique pour l'IA n°2.
    """
    prompt_synthese = f"""
    RÉSUME ce trade en 4 points CLÉS pour le Risk Manager (Guardian) :
    ANALYSE : {analyse_complete}
    ACTIF : {actif}

    FORMAT STRICT :
    - BIAIS : (Achat/Vente)
    - INVALIDATION : (Prix ou condition du Stop Loss)
    - OBJECTIF : (Prix ou RR visé)
    - LOGIQUE : (La raison principale en 10 mots)
    """
    try:
        response = client_architect.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt_synthese}],
            temperature=0.3
        )
        return response.choices[0].message.content
    except:
        return "Plan non synthétisé. Se référer à l'analyse brute."
    

def generer_verdict_final_ia(analyse_init, logs_discipline, resultat, prix_cloture):
    """
    Appelle gpt-4o pour générer le rapport final basé sur ton prompt 'Auditeur Final'.
    """
    
    prompt = f"""
    TU ES : L’Auditeur Final de Trade Mind.

    TON RÔLE :
    Tu es un coach de trading institutionnel. Tu analyses la QUALITÉ du processus de décision, PAS le résultat seul.
    Tu dois corriger les biais psychologiques du trader et renforcer les bonnes pratiques.

    ----------------------------------------
    DONNÉES DU TRADE
    ----------------------------------------
    Analyse initiale :
    {analyse_init}

    Alertes du Guardian (discipline) :
    {logs_discipline}

    Résultat :
    {resultat}  (WIN ou LOSS)

    Prix de clôture réel :
    {prix_cloture}

    ----------------------------------------
    TA MÉTHODE D’ANALYSE (OBLIGATOIRE)
    ----------------------------------------

    1. ÉVALUE LE RESPECT DU PLAN
    - Le trader a-t-il respecté son SL, TP, et son plan initial ?
    - Les alertes Guardian indiquent-elles une dérive ?

    2. DISTINGUE LE TYPE DE RÉSULTAT

    SI WIN :
    - Si discipline respectée → "Victoire professionnelle"
    - Si discipline non respectée → "Victoire chanceuse"

    SI LOSS :
    - Si discipline respectée → "Perte saine"
    - Si discipline non respectée → "Perte par indiscipline"

    3. IDENTIFIE LE RISQUE PSYCHOLOGIQUE
    - Peur (sortie prématurée, SL serré)
    - Avidité (TP déplacé, over-risk)
    - Indiscipline (non-respect du plan)

    ----------------------------------------
    FORMAT DE RÉPONSE (STRICT)
    ----------------------------------------

    Tu DOIS répondre exactement avec cette structure :

    VERDICT : [Type de résultat]

    ANALYSE :
    [2 à 4 phrases maximum expliquant clairement ce qui s’est réellement passé]

    POINT FORT :
    [1 seule chose positive, même en cas de perte]

    ERREUR CRITIQUE :
    [1 seule erreur majeure. Si aucune → écrire "Aucune erreur critique"]

    CONSEIL PRIORITAIRE :
    [1 seule action concrète pour le prochain trade]

    ----------------------------------------
    RÈGLES IMPORTANTES
    ----------------------------------------

    - Tu ne dois JAMAIS féliciter sans nuance
    - Tu ne dois JAMAIS dramatiser une perte saine
    - Tu dois être honnête, direct, mais constructif
    - Tu dois corriger les biais mentaux (ego, peur, hasard)
    - Tu dois privilégier le PROCESSUS, pas le résultat

    ----------------------------------------
    OBJECTIF FINAL
    ----------------------------------------

    Ton but est que le trader :
    - reste discipliné après une perte
    - ne devienne pas arrogant après un gain
    - améliore son processus décisionnel

    Réponds maintenant.
    """
    client_guardian = OpenAI(api_key=os.getenv("OPENAI_GUARDIAN_KEY"))
    
    try:
        response = client_guardian.chat.completions.create(
            model="gpt-4o", # Version rapide et peu coûteuse
            messages=[
                {"role": "system", "content": "Tu es un auditeur de fonds d'investissement expert en psychologie du trading."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3, # On garde une température basse pour la rigueur
            max_tokens=500
        )
        
        verdict = response.choices[0].message.content
        return verdict

    except Exception as e:
        print(f"❌ Erreur API OpenAI (Verdict) : {e}")
        return "Erreur lors de la génération du rapport final. Vérifiez vos logs."
    

def logique_decision_mentor(user_settings, risque_saisi, rr_saisi):
    """
    Remplace l'ancienne logique de décision. 
    Renvoie un dictionnaire avec le message et la couleur associée.
    """
    mode = user_settings.get("ia_severite", "Neutre")
    max_risk = user_settings.get("risque_max", 1.0)
    min_rr = user_settings.get("rr_min", 2.0)
    
    # Logique de sévérité (Maintenue intégralement)
    if risque_saisi > max_risk:
        if mode == "Institutionnel":
            return {"message": "🔴 REFUSÉ : Risque hors limites (Standards Institutionnels).", "couleur": "red", "autorise": False}
        elif mode == "Sévère":
            return {"message": "🟠 ALERTE : Tu violes ton plan de gestion des risques.", "couleur": "orange", "autorise": True}
        else:
            return {"message": "🔵 Conseil : Ton exposition est supérieure à ton réglage.", "couleur": "blue", "autorise": True}

    if rr_saisi < min_rr:
        if mode == "Institutionnel":
            return {"message": f"🔴 REJETÉ : RR de {rr_saisi} insuffisant (Min: {min_rr}).", "couleur": "red", "autorise": False}
        return {"message": f"🟡 Attention : Ratio inférieur à ton objectif de {min_rr}.", "couleur": "orange", "autorise": True}

    return {"message": "🟢 Setup Conforme. Analyse validée par le Mentor.", "couleur": "green", "autorise": True}

def lancer_analyse(analyse_actuelle, valeur_conviction, actif_actuel, user_settings, client_architect):
    # 1. Classe simple pour simuler app_instance
    class AppMock:
        def __init__(self, settings):
            self.user_settings = settings

    try:
        # 2. Sécurité
        if len(analyse_actuelle.strip()) < 10:
            return {"statut": "erreur", "message": "Ton analyse est trop courte."}

        # 3. Création de l'instance
        app_mock = AppMock(user_settings)
        mode = user_settings.get("mode", "SWING").upper()

        # 4. AIGUILLAGE (Dispatcher)
        # On appelle la fonction correspondante au mode
        if mode == "SWING":
            score, verdict, couleur = analyser_ia_swing(app_mock, None, analyse_actuelle, actif_actuel, valeur_conviction, client_architect)
        elif mode == "DAILY":
            score, verdict, couleur = analyser_ia_daily(app_mock, None, analyse_actuelle, actif_actuel, valeur_conviction, client_architect)
        elif mode == "SCALP":
            score, verdict, couleur = analyser_ia_scalp(app_mock, None, analyse_actuelle, actif_actuel, valeur_conviction, client_architect)
        else:
            return {"statut": "erreur", "message": f"Mode inconnu : {mode}"}

        return {
            "statut": "success",
            "score": score,
            "verdict": verdict,
            "couleur": couleur,
            "notifications_actives": user_settings.get("notifications_actives", True)
        }

    except Exception as e:
        print(f"CRITIQUE : Erreur lors de l'analyse : {str(e)}")
        return {"statut": "erreur", "message": f"Erreur technique : {str(e)}"}
