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

GUIDES_QUESTIONNAIRES = {
    "SWING_ETUDIANT": """[QUESTIONNAIRE SWING - ÉTUDIANT]
    A - IDENTITÉ & CONVICTION: Actif défini? Biais unique? Conviction justifiée?
    B - MACRO: Sentiment? Yields? Taux? Inflation? Géopolitique? Corrélations? Événements?
    C - CONCLUSION: Devise dominante?
    D - TECHNIQUE: Structure HTF? Momentum? Zones clés? Liquidité?
    E - RISQUE: Pourquoi maintenant? SL Logique? RR >= 1:2? Confirmation?""",
    
    "SWING_EXPERT": """[QUESTIONNAIRE SWING - EXPERT]
    1. YIELDS: Confirmation biais? 2. LIQUIDITÉ: Sweep effectué? 3. STRUCTURE: BOS ou ChoCh? 
    4. ZONE: FVG ou OB? 5. RISK: RR >= 1:2? 6. DISCIPLINE: Plan strict?""",
    
    "DAILY_DEBUT": """[QUESTIONNAIRE DAILY - PENDANT SESSION]
    1. CONTEXTE: Tendance? État du marché? News prévues? Fondamentaux passés?
    2. SETUP: Quel setup? Confirmation entrée? Invalidation logique? Session ciblée?""",
    
    "DAILY_FIN": """[QUESTIONNAIRE DAILY - APRÈS SESSION]
    1. AUDIT: Déviances psychologiques majeures?
    2. PERFORMANCE: Gains issus du plan ou impulsion heureuse?""",

    "SCALP_DEBUT": """[QUESTIONNAIRE SCALP - DÉBUT SESSION]
    1. TECHNIQUE: Quel setup ciblé? Trades max? Perte max (stop)?
    2. COGNITIF: Clarté mentale? Session? """,

    "SCALP_FIN": """[QUESTIONNAIRE SCALP - FIN SESSION]
    1. RÉSULTATS: Micro-scalps exécutés? Ratio W/L?
    2. AUDIT: Respect plan/tailles/drawdown? Sur-trading/Impulsivité? Note exécution (0-10)?"""
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
            "market_data": {"data": None, "timestamp": 0},
            "forex_factory": {"data": None, "timestamp": 0},
            "sentiment": {"data": None, "timestamp": 0}
        }
        
        # Cache de 5 minutes pour éviter toute limitation inutile des sources gratuites
        self.cache_duration = 300 


    def _est_valide(self, key):
        """Vérifie la fraîcheur de la donnée en cache"""
        return (time.time() - self.storage[key]["timestamp"]) < self.cache_duration

    # --- MODULE : FEAR & GREED (Sentiment) ---

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
        """Récupération ultra-rapide du prix."""
        ticker_key = f"market_data_{ticker.replace('/', '_')}"
        
        # 1. Vérification du cache
        if self._est_valide(ticker_key):
            return self.storage[ticker_key]["data"].get("price")

        # 2. Fallback direct si le cache est vide
        snapshot = self.get_market_snapshot(ticker)
        return snapshot["price"] if snapshot else None

    def get_volatility_atr(self, ticker):
        """Récupère le range quotidien avec cache spécifique par actif."""
        ticker_key = f"daily_stats_{ticker.replace('/', '_')}"
        
        # 1. Vérification du cache spécifique
        if self._est_valide(ticker_key):
            return self.storage[ticker_key].get("range")
        
        try:
            ticker_yf = self._formater_ticker(ticker)
            stock = yf.Ticker(ticker_yf)
            hist = stock.history(period="2d")
            
            if len(hist) < 2: return 0
                
            yesterday = hist.iloc[-2]
            daily_range = float(yesterday['High'] - yesterday['Low'])
            
            # 2. Mise en cache avec la clé unique
            self.storage[ticker_key] = {
                "range": daily_range,
                "timestamp": time.time()
            }
            return daily_range
            
        except Exception as e:
            print(f"❌ Erreur YFinance Volatility pour {ticker}: {e}")
            return 0

    def get_daily_range_stats(self, ticker):
        """Calcule l'ADR glissant (5 jours) avec cache propre."""
        ticker_key = f"adr_stats_{ticker.replace('/', '_')}"
        
        if self._est_valide(ticker_key):
            return self.storage[ticker_key]["data"]

        try:
            ticker_yf = self._formater_ticker(ticker)
            stock = yf.Ticker(ticker_yf)
            # On demande 6 jours pour avoir une moyenne glissante sur 5 jours complets
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
            
            # Mise en cache
            self.storage[ticker_key] = {"data": stats, "timestamp": time.time()}
            return stats
            
        except Exception as e:
            print(f"❌ Erreur YFinance ADR pour {ticker}: {e}")
            return {"adr_moyenne": 0.002, "dernier_high": 0, "dernier_low": 0}

    def get_forex_factory_news(self, actif):
        """Récupère l'intégralité des news (Lun-Ven) via le flux miroir sécurisé avec cache 1h."""
        url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
        
        # --- VÉRIFICATION DU CACHE ---
        cache = self.storage["market_data"].get("forex_factory")
        if cache and (time.time() - cache["timestamp"] < 3600):
            return cache["data"]

        all_events = []
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                # Filtrage Lundi (0) à Vendredi (4)
                for event in data:
                    try:
                        date_part = event.get('date', '').split('T')[0]
                        if datetime.strptime(date_part, '%Y-%m-%d').weekday() <= 4:
                            all_events.append(event)
                    except:
                        continue
                
                # Stockage dans le cache pour éviter les appels inutiles (avec timestamp)
                self.storage["market_data"]["forex_factory"] = {"data": all_events, "timestamp": time.time()}
                return all_events
                
            else:
                print(f"❌ Erreur Forex Factory : {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Erreur de connexion Forex Factory : {e}")
            return []
        
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
        maintenant = datetime.datetime.utcnow()
        heure_serveur = maintenant.strftime("%H:%M")
        
        # 1. Récupération des données brutes
        sentiment = self.fetch_cnn_index()
        news_macro = self.get_forex_factory_news(actif)
        news_geo_brutes = self.get_geopolitical_news(actif)
        
        # 2. Filtrage intelligent (si tu veux garder ta méthode IA, on la laisse)
        # Note: Si filtrer_news_par_ia n'est pas nécessaire car ton RSS est déjà filtré, 
        # tu peux simplifier cette ligne.
        news_geo_filtrees = self.filtrer_news_par_ia(news_geo_brutes) if hasattr(self, 'filtrer_news_par_ia') else news_geo_brutes
        
        # 3. Mise à jour cache market_data (données techniques)
        if not self._est_valide("market_data"):
            prix = self.get_last_price(actif)
            vol = self.get_volatility_atr(actif)
            stats_adr = self.get_daily_range_stats(actif)
            
            self.storage["market_data"] = {
                "data": {
                    "price": prix,
                    "volatility": vol,
                    "adr_stats": stats_adr,
                    "timestamp_str": heure_serveur
                },
                "timestamp": time.time()
            }

        # 4. Synthèse finale pour le Prompt IA
        data = self.storage["market_data"]["data"]
        
        # Conversion des listes de news en chaînes lisibles pour l'IA
        str_news_macro = "\n".join(news_macro) if isinstance(news_macro, list) else str(news_macro)
        str_news_geo = "\n".join(news_geo_filtrees) if isinstance(news_geo_filtrees, list) else str(news_geo_filtrees)
        
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
    
    # 1. Données brutes
    events_critiques = guard.get_forex_factory_news(actif)
    sentiment_global = guard.fetch_cnn_index()
    
    # 2. Récupération sécurisée du score
    # Si sentiment_global est un dict, on extrait le score, sinon on passe None
    cnn_score = sentiment_global.get('score') if isinstance(sentiment_global, dict) else None
    
    # 3. Appel avec la valeur réelle (ou None)
    # L'IA est capable de gérer une absence de score, mais pas un score faux (50)
    geo_titles = guard.get_geopolitical_news(actif, sentiment=cnn_score)
    
    # 3. Construction de la synthèse structurée
    resultat = f"--- 🎭 INDICE SENTIMENT GLOBAL ---\n{sentiment_global.get('label', 'Neutre')}\n\n"
    
    resultat += "--- 📅 CALENDRIER ÉCONOMIQUE (MACRO) ---\n"
    resultat += "\n".join(events_critiques) if events_critiques else "Aucun événement impactant prévu."
    
    resultat += "\n\n--- 🌍 FLASH GÉOPOLITIQUE (RISK) ---\n"
    resultat += "\n".join(geo_titles)
    
    return resultat


def analyser_ia_pro(app_instance, ancienne_analyse, nouvelle_analyse, statut_analyse, actif, conviction, guide_etudiant_contenu, guide_expert_contenu, mode="SWING",data_json=None):
    """
    Fonction principale d'appel à l'API OpenAI avec spécialisation dynamique par mode.
    Conserve le prompt original pour le mode SWING.
    """
    user_settings = getattr(app_instance, 'user_settings', {})
    severite = user_settings.get("ia_severite", "Neutre")
    
    # 2. RÉCUPÉRATION DYNAMIQUE DU GUIDE
    guide_contenu = GUIDES_QUESTIONNAIRES.get(mode.upper(), "1. Analyse structurelle. 2. Gestion risque.")
    
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

    # 2. DÉFINITION DU TEMPÉRAMENT (Pour GPT-4o)
    instructions_severite = {
        "Doux": "Sois un mentor bienveillant. Encourage le trader même en cas d'erreur.",
        "Neutre": "Sois un analyste pro et factuel. Rappelle les règles sans détour.",
        "Sévère": "Sois un coach strict. Ne laisse passer aucun écart de discipline.",
        "Institutionnel": "Agis comme un Head of Desk en banque. Rejette froidement tout trade hors-cadre."
    }
    
    instructions_pedagogiques = {
        "Doux": "Explique l'erreur comme un professeur. Valorise ce qui est bon.",
        "Neutre": "Factuel et constructif. Donne la raison mathématique sans jugement.",
        "Sévère": "Direct et exigeant. Souligne le manque de rigueur.",
        "Institutionnel": "Froid, professionnel. Analyse le trade comme un coût d'opportunité."
    }

    # 3. LOGIQUE DE SÉLECTION DU MODE (SQUELETTE DYNAMIQUE)
    mode_upper = mode.upper()
    
    if mode_upper == "DAILY":
        role_titre = "Auditeur Intraday & Risk Manager de Session"
        mission_specifique = (
            "Évaluer la cohérence du plan intraday avant exécution, "
            "détecter les risques immédiats de marché et améliorer "
            "la qualité décisionnelle du trader."
        )
        instructions_mode = """
        [LOGIQUE DAILY - AUDIT INTRADAY]

        CONTEXTE :
        Le trader opère en Day Trading. Toutes les positions doivent être clôturées avant minuit.
        Ton rôle : Auditer la logique, le timing et la qualité du processus.

        ═══════════════════════
        1. VALIDATION DU CONTEXTE & ADR (CARBURANT)
        ═══════════════════════
        - Cohérence Biais : Structure HTF, Momentum et Session active.
        - ANALYSE ADR (Average Daily Range) : 
        • Vérifie si l'actif n'a pas déjà atteint son extension moyenne journalière. 
        • Si l'extension est > 80% de l'ADR, avertis : "Potentiel de mouvement épuisé. Objectif (TP) statistiquement difficile à atteindre."

        ═══════════════════════
        2. AUDIT DU TIMING & CLÔTURE PROCHE
        ═══════════════════════
        - Analyse de Session : Open Londres/NY, Killzones.
        - PROXIMITÉ DE CLÔTURE : Si l'entrée est tentée après 16h30 (clôture Londres) :
        • Avertis : "Timing risqué : la volatilité va chuter, le potentiel diminue et les frais de swap approchent."
        - Timing vs Exécution : Distingue si le plan est bon mais l'entrée trop tardive (chasser le prix).

        ═══════════════════════
        3. RISQUE & VOLATILITÉ
        ═══════════════════════
        - News : Si une news majeure approche (< 30 min), suggère d'attendre la stabilisation.
        - Cohérence SL : Doit être aligné avec l'ATR actuel et la structure intraday.

        ═══════════════════════
        4. DISCIPLINE & PSYCHOLOGIE
        ═══════════════════════
        - Détecte le FOMO, l'impulsivité ou l'anticipation sans confirmation.
        - Un “non-trade” intelligent vaut mieux qu'une position forcée.

        ═══════════════════════
        5. VERDICT FINAL (LES 3 NOTES)
        ═══════════════════════
        Tu dois impérativement noter séparément :
        - [NOTE SETUP] : Qualité de la stratégie et du plan (sur 10).
        - [NOTE TIMING] : Précision de l'entrée par rapport aux sessions/news (sur 10).
        - [NOTE DISCIPLINE] : Respect des règles et absence d'émotion (sur 10).

        IMPORTANT : Valorise le PROCESSUS. Un trade perdant mais exécuté selon le plan peut avoir 10/10 partout.

        [ORIENTATIONS STRATÉGIQUES]
        Si le taux de réussite en DAILY est instable, conseille à l'utilisateur de passer temporairement en mode SWING pour filtrer le bruit, ou à l'inverse, si l'impulsivité est trop forte, suggère de pratiquer en mode SCALP pour forcer une exécution ultra-calibrée sur micro-timeframes.
        """
    
    elif mode_upper == "SCALP":
        role_titre = "Coach de Performance Scalping & Analyste d’Exécution"
        mission_specifique = (
            "Débriefing de fin de session : analyser la discipline, "
            "la qualité d’exécution et les comportements du trader "
            "afin d’améliorer sa constance sur les micro-timeframes."
        )
        instructions_mode = """
        [MODE SCALPING — DÉBRIEFING POST-SESSION]

        IMPORTANT :
        Tu n’es PAS ici pour prédire le marché.
        Tu es un coach de performance spécialisé en scalping.

        Le trader fournit :
        - le résumé de sa session,
        - ses entrées/sorties,
        - ses erreurs,
        - ses émotions,
        - ses décisions,
        - ses statistiques éventuelles.

        TON OBJECTIF :
        Identifier les comportements qui empêchent la régularité.

        TU DOIS ANALYSER :

        1. DISCIPLINE
        - Le trader a-t-il respecté son plan ?
        - A-t-il forcé des trades ?
        - A-t-il surtradé après une perte ou une série de gains ?
        - A-t-il respecté ses confirmations ?

        2. QUALITÉ D’EXÉCUTION
        - Les entrées étaient-elles précises ou impulsives ?
        - Les sorties étaient-elles cohérentes ?
        - Le trader coupe-t-il trop tôt ses gains ?
        - Les stoploss étaient-ils respectés ?

        3. GESTION ÉMOTIONNELLE
        - Présence de frustration, FOMO, revenge trading ou euphorie ?
        - Les émotions ont-elles influencé les décisions ?
        - Le trader est-il devenu agressif après une perte ?

        4. GESTION DU RISQUE
        - Risque constant par trade ?
        - Taille de position cohérente ?
        - Accumulation de pertes inutile ?
        - Impact des spreads/frais sur la rentabilité ?

        5. EFFICACITÉ DE SESSION
        - Quels setups ont réellement fonctionné ?
        - Quels trades étaient inutiles ?
        - Quels comportements doivent être supprimés immédiatement ?

        RÈGLES :
        - Ignore la macroéconomie long terme.
        - Ignore les prévisions swing/investissement.
        - Concentre-toi sur la discipline opérationnelle.
        - Priorité absolue : constance et survie du capital.

        FIN DE RÉPONSE OBLIGATOIRE :
        Donne :
        - 3 erreurs principales maximum
        - 3 points forts maximum
        - 1 objectif concret pour la prochaine session

        TON :
        Direct. Professionnel. Sans complaisance.
        Comme un coach de desk propriétaire.

        [ORIENTATIONS STRATÉGIQUES]
        Si la charge émotionnelle ou l'impulsivité est trop élevée, conseille à l'utilisateur de basculer vers le mode DAILY pour réduire la fréquence des décisions et retrouver une perspective plus sereine.
        """

    elif mode_upper == "INVESTOR":
        role_titre = "Senior Macro Strategist & Investment Research Partner"
        mission_specifique = (
            "Accompagner un investisseur long terme dans l'évaluation de sa thèse "
            "d'investissement en confrontant son raisonnement aux réalités macroéconomiques, "
            "au sentiment de marché et aux risques structurels."
        )
        instructions_mode = f"""
        [LOGIQUE INVESTOR — STRATEGIC THESIS AUDIT]

        PHILOSOPHIE GÉNÉRALE :
        L'utilisateur est un investisseur autonome et expérimenté.
        Tu n'es PAS un mentor disciplinaire ni un système de validation autoritaire.
        Tu es un partenaire stratégique de réflexion.

        Ton objectif :
        - enrichir le raisonnement,
        - identifier les angles morts,
        - nuancer les hypothèses,
        - apporter du contexte macro et stratégique,
        - challenger la cohérence globale de la thèse.

        IMPORTANT :
        - La décision finale appartient toujours à l'investisseur.
        - Tu ne donnes jamais d'ordre direct.
        - Tu utilises un ton calme, analytique, institutionnel et nuancé.
        - Ignore totalement le bruit intraday et les micro-variations de prix.
        - Concentre-toi sur le moyen / long terme.

        --------------------------------------------------

        [AXES D'ANALYSE OBLIGATOIRES]

        1. COHÉRENCE MACROÉCONOMIQUE
        - Vérifie si la thèse est alignée avec :
        • le cycle économique actuel,
        • les politiques monétaires,
        • les taux d'intérêt,
        • l'inflation,
        • les flux de capitaux,
        • le sentiment global de marché.

        - Appuie-toi sur :
        • Sentiment CNN Fear & Greed : {sentiment.get('score')}
        • Données macro disponibles
        • Contexte global actuel

        - Exemple :
        Si l'investisseur veut accumuler massivement dans une phase d'euphorie,
        suggère que le timing pourrait historiquement réduire la marge de sécurité.

        --------------------------------------------------

        2. AUDIT DE LA THÈSE D'INVESTISSEMENT
        Analyse :
        - la logique interne du raisonnement,
        - la cohérence entre les arguments,
        - la solidité des hypothèses utilisées,
        - les liens de causalité.

        Vérifie notamment :
        - si les conclusions découlent réellement des arguments,
        - si certaines hypothèses sont implicites ou fragiles,
        - si certains scénarios importants sont ignorés.

        Tu dois détecter :
        - excès de confiance,
        - biais de confirmation,
        - optimisme non justifié,
        - extrapolation excessive.

        --------------------------------------------------

        3. RÉALITÉ DES NEWS & DU CONTEXTE
        Croise la thèse avec :
        {market_data.get("news", [])}

        Objectif :
        - détecter les contradictions potentielles,
        - confirmer ou nuancer certains arguments,
        - identifier les éléments macro susceptibles d'invalider le scénario.

        Tu peux signaler :
        - un changement de régime économique,
        - une divergence entre sentiment et fondamentaux,
        - une incohérence entre le scénario présenté et les données récentes.

        --------------------------------------------------

        4. ANALYSE DU RISQUE STRUCTUREL
        Évalue les risques liés :
        - à la valorisation,
        - au contexte macro,
        - au cycle de liquidité,
        - aux taux,
        - à la volatilité structurelle,
        - aux événements géopolitiques,
        - au secteur concerné.

        Vérifie également :
        - si la thèse possède une marge de sécurité raisonnable,
        - si le prix actuel laisse une place à l'erreur,
        - si le scénario dépend d'hypothèses trop optimistes.

        --------------------------------------------------

        5. PERSPECTIVE STRATÉGIQUE
        Ton rôle est d'apporter :
        - des nuances,
        - des pistes de réflexion,
        - des scénarios alternatifs,
        - des éléments que l'investisseur pourrait approfondir.

        Tu peux proposer :
        - des facteurs à surveiller,
        - des risques sous-estimés,
        - des variables macro importantes,
        - des éléments pouvant renforcer ou fragiliser la thèse.

        --------------------------------------------------

        [STYLE DE RÉPONSE OBLIGATOIRE]

        INTERDICTIONS :
        - Ne dis jamais :
        • "Trade validé"
        • "Mauvais investissement"
        • "Achetez"
        • "Vendez"
        • "Entrée parfaite"

        AUTORISÉ :
        - "La thèse semble cohérente avec..."
        - "Le raisonnement paraît partiellement aligné..."
        - "Une divergence apparaît entre..."
        - "Il pourrait être pertinent d'approfondir..."
        - "Le scénario semble dépendre fortement de..."

        --------------------------------------------------

        [FORMAT DE SORTIE]

        [NOTE]
        - Donne une note de cohérence stratégique sur 10.
        - Cette note évalue la qualité du raisonnement,
        PAS la probabilité de gain.

        [STATUT]
        Utilise uniquement :
        - COHÉRENT
        - NUANCÉ
        - DIVERGENT

        [DÉCISION]
        Ne donne jamais une décision de trading.
        Utilise plutôt :
        - APPROFONDIR L'ANALYSE
        - SURVEILLER LE CONTEXTE MACRO
        - ATTENDRE PLUS DE CONFIRMATIONS
        - THÈSE STRUCTURÉE MAIS À NUANCER
        - SCÉNARIO À RÉÉVALUER

        --------------------------------------------------

        [ORIENTATIONS STRATÉGIQUES]
        Si la thèse d'investissement semble trop corrélée à des événements à court terme, conseille à l'utilisateur de repasser en revue ses fondamentaux (DAILY) pour s'assurer que ses convictions ne sont pas biaisées par le bruit du marché.

        RÈGLE FINALE :
        Un investissement solide n'est pas une certitude.
        C'est une thèse cohérente capable de survivre à plusieurs scénarios.
        """

    else: # PAR DÉFAUT : MODE SWING (PROMPT ORIGINAL CONSERVÉ AUX MOTS PRÈS)
        role_titre = "Head of Risk Management dans un Hedge Fund + Mentor Trading institutionnel"
        mission_specifique = "PROTÉGER LE CAPITAL et IMPOSER LA DISCIPLINE."
        instructions_mode = "Tu n’es PAS un analyste classique, tu es le FILTRE FINAL avant exécution. Tu analyses exclusivement la STRUCTURE LOGIQUE, la COHÉRENCE et les DONNÉES OBJECTIVES. Tu ne fournis JAMAIS de signaux."

    # 4. LE PROMPT FINAL FUSIONNÉ (Structure originale respectée)
    prompt = f"""
    TU ES : {role_titre}. 
    Ta mission principale : {mission_specifique}
    GUIDE DE RÉFÉRENCE POUR CE MODE : {guide_contenu}
    [DONNÉES ISOLÉES DU FRONTEND]
    {donnees_techniques}
    
    {instructions_mode}

    Tu as accès à des DONNÉES DE MARCHÉ via API (ex: polygon.io) : prix actuel, historique, volatilité, RSI, variations, etc.
    Tu ne vois PAS les graphiques visuellement : tu analyses exclusivement la STRUCTURE LOGIQUE, la COHÉRENCE et les DONNÉES OBJECTIVES.
    Tu ne fournis JAMAIS de signaux ou d’analyses techniques. Ton rôle est de VALIDER ou REJETER un plan de trading basé sur des règles strictes.
    ═══════════════════════════════
    RÉFÉRENTIELS UTILISATEUR
    ═══════════════════════════════
    {guide_contenu}

    ═══════════════════════════════
    CONTEXTE TRADER
    ═══════════════════════════════
    - Style : {style}
    - Marché : {marche}
    - Objectif : {objectif}
    - Niveau : {niveau}
    - Risque max : {max_risk}%
    - RR minimum : {rr_min}
    - Sévérité : {severite}

    # ═══════════════════════════════
    # DONNÉES MARCHÉ (Connectées API)
    # ═══════════════════════════════
    - Prix Actuel : {market_data.get('prix_actuel', 'N/A')}
    - Volatilité (ATR 5j) : {market_data.get('volatilite', 'N/A')}
    - Bornes ADR (High/Low) : {market_data.get('adr_stats', {}).get('dernier_high', 'N/A')} / {market_data.get('adr_stats', {}).get('dernier_low', 'N/A')}
    - News (Macro & Géo) : {', '.join(market_data.get('news', [])) if market_data.get('news') else 'Aucune news majeure détectée.'}
    - Sentiment (Fear & Greed) : {sentiment.get('rating', 'INDISPONIBLE')} ({sentiment.get('score', 'N/A')}/100)
    
    ═══════════════════════════════
    TRADE & ANALYSE
    ═══════════════════════════════
    - Actif : {actif}
    - Conviction : {conviction}%
    - SL/TP : {app_instance.info_sl_tp if hasattr(app_instance, 'info_sl_tp') else 'N/A'}
    - Invalidation : {app_instance.raisonnement_user if hasattr(app_instance, 'raisonnement_user') else 'N/A'}
    ANALYSE :
    {nouvelle_analyse}

    RÈGLE D’OR :
    Toute contradiction entre :
    → analyse écrite
    → checklist
    → données marché
    = INCOHÉRENCE CRITIQUE

    ═══════════════════════════════
    AUDIT HIÉRARCHIQUE (OBLIGATOIRE)
    ═══════════════════════════════

    1. RISQUE & RR (BLOQUANT)
    - RR ≥ {rr_min} ?
    - Risque ≤ {max_risk}% ?
    → Si NON : ERREUR CRITIQUE

    2. COHÉRENCE LOGIQUE
    - Alignement complet ?
    → Sinon : ERREUR MAJEURE

    3. STRUCTURE & LIQUIDITÉ
    → Si faible : ERREUR MAJEURE

    4. ADAPTATION AU MARCHÉ
    → SL vs volatilité
    → Style vs setup

    5. PSYCHOLOGIE (OBLIGATOIRE)
    Analyse conviction {conviction}% :
    - Excès de confiance
    - Manque de conviction
    - Impulsivité

    6. SENTIMENT : Le setup est-il cohérent avec un Fear & Greed à {sentiment.get('score')} ? (Ex: Achat en Extreme Greed = Danger, envisager un retracement (correction)).

    ═══════════════════════════════
    CLASSIFICATION DES ERREURS
    ═══════════════════════════════
    - CRITIQUE : invalide le trade (RR, risque, incohérence)
    - MAJEURE : fragilise fortement
    - MINEURE : améliorable

    ═══════════════════════════════
    RÈGLES DE SANCTION
    ═══════════════════════════════
    - RR < {rr_min} → INCORRECT
    - Risque > {max_risk}% → INCORRECT
    - Incohérence logique → INCORRECT

    ⚠️ AUCUNE compensation possible.

    ═══════════════════════════════
    DÉCISION FINALE (OBLIGATOIRE)
    ═══════════════════════════════
    Tu DOIS trancher :

    - VALIDÉ → Trade exploitable immédiatement
    - PARTIEL → Trade exploitable sous conditions
    - INCORRECT → Trade à REFUSER

    ═══════════════════════════════
    FORMAT DE SORTIE (STRICT)
    ═══════════════════════════════

    [NOTE] : X/10
    [STATUT] : VALIDÉ / PARTIEL / INCORRECT
    [DÉCISION] : EXÉCUTER / AJUSTER / REFUSER

    [AUDIT] :
    - Risque & RR :
    - Cohérence :
    - Structure :
    - Psychologie :

    [ERREURS] :
    - (Type : CRITIQUE / MAJEURE / MINEURE)

    [HEATMAP] :
    #XXXXXX

    [GESTION] :
    1 action unique, claire et prioritaire

    ═══════════════════════════════
    TON
    ═══════════════════════════════
    {instructions_severite[severite]}
    {instructions_pedagogiques[severite]}
    Institutionnel. Froid. Direct.
    Aucune émotion. Aucun encouragement inutile.
    Utilise des formulations comme :
    "Le plan présente une incohérence entre X et Y"
    - "Le trade est refusé pour non-respect du cadre de risque."
    - "La conviction n’est pas justifiée par les données."
    - "Le plan est exploitable sous ajustement."
    """
    
    try:
        response = client_architect.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"Tu es un Mentor IA spécialisé en Risk Management ({mode_upper}). Niveau : {severite}."}, 
                {"role": "user", "content": prompt}
            ]
        )
        
        reponse_ia = response.choices[0].message.content 
        
        # --- EXTRACTION ---
        match = re.search(r'#(?:[0-9a-fA-F]{3}){1,2}', reponse_ia)
        couleur = match.group(0) if match else "#2B2B2B"
        note_match = re.search(r'\d+', reponse_ia)
        score = int(note_match.group()) if note_match else 5
                
        return score, reponse_ia, couleur 
    
    except Exception as e:
        return 0, f"Erreur : {e}", "#34495E"

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

def lancer_analyse(analyse_actuelle, valeur_conviction, actif_actuel, user_settings): 
    """
    Version API de 'lancer_analyse'.
    Ne contient plus de 'self' ni de 'messagebox'.
    Prend les données brutes et renvoie le verdict final.
    """
    try:
        severite = user_settings.get("ia_severite", "Neutre")
        
        # 1. Sécurité (Maintenue)
        if len(analyse_actuelle.strip()) < 10:
            return {
                "statut": "erreur",
                "titre": "IA",
                "message": "Ton analyse est trop courte pour être auditée par le Mentor."
            }

        # 2. Appel de l'IA (On utilise la fonction de calcul existante)
        # On passe les arguments nécessaires à analyser_ia_pro
        score, verdict, couleur = analyser_ia_pro(
            None, # app_instance remplacé par None car géré par API
            "", # ancienne_analyse
            analyse_actuelle, 
            "EN_COURS", 
            actif_actuel, 
            valeur_conviction,
            "", # guide_etudiant (à fournir via settings si besoin)
            ""  # guide_expert
        )

        # 3. Construction du retour (Remplace l'UI update)
        return {
            "statut": "success",
            "score": score,
            "verdict": verdict,
            "couleur": couleur,
            "notifications_actives": user_settings.get("notifications_actives", True)
        }

    except Exception as e:
        return {
            "statut": "erreur",
            "message": f"Le moteur d'analyse a rencontré une erreur technique : {str(e)}"
        }

def analyser_question_suivi(etape_nom, question, reponse_user, user_settings):
    """
    Version API de 'analyser_question_suivi'.
    Analyse une étape avec 3 modes : VALIDE, PARTIEL, INCORRECT.
    """
    try:
        severite = user_settings.get("ia_severite", "Neutre")
        
        # Le prompt reste identique, mot pour mot
        prompt = f"""
        Tu es le Mentor IA (Sévérité : {severite}). Analyse la réponse du trader.
        
        ÉTAPE : {etape_nom}
        QUESTION : {question}
        RÉPONSE DU TRADER : {reponse_user}
        
        MISSION : Réponds selon l'un de ces 3 modes :
        1. [VALIDÉ] : Réponse courte, précise et cohérente. (Explication courte mais complète).

        2. [PARTIEL] : C'est le mode "Oui... mais". La réponse est sur la bonne voie mais manque de profondeur ou de prudence. 
           Action : Valide avec réserve + suggère une amélioration + termine par [PARTIEL].

        3. [INCORRECT] : Erreur de logique, oubli majeur ou risque ignoré. 
           Action : Bloque le passage + explique l'erreur clairement + termine par [INCORRECT].
        """
        
        response = client_architect.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"Tu es un Mentor Trading expert et {severite}."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4 
        )
        
        # On renvoie le texte brut de l'IA à l'API
        return response.choices[0].message.content

    except Exception as e:
        return f"❌ Erreur de liaison neuronale : {str(e)}"
    
