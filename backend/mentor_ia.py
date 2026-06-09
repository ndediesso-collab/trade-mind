import logging
import os
import time
import requests
import json
import xml.etree.ElementTree as ET
from openai import OpenAI
import re
import datetime 
from dotenv import load_dotenv

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
import datetime
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
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.polygon.io"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) MentorIA/1.0"
        })
        
        self.storage = {
            "polygon": {"data": None, "timestamp": 0},
            "forex_factory": {"data": None, "timestamp": 0},
            "cnn_fear_greed": {"data": None, "timestamp": 0}
        }
        self.cache_duration = 60 # Cache de 60 secondes pour les données de marché 

    def _est_valide(self, key):
        """Vérifie la fraîcheur de la donnée en cache"""
        return (time.time() - self.storage[key]["timestamp"]) < self.cache_duration

    # --- MODULE : FEAR & GREED (Sentiment) ---
    def fetch_cnn_index(self):
        """Extraction brute avec protection contre les blocages"""
        url = "https://production.dataviz.cnn.io/index/feargreed/static/severity"
        try:
            # On simule une origine pour éviter le rejet par CNN
            headers = {"Origin": "https://www.cnn.com"}
            response = self.session.get(url, headers=headers, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            now = data.get('now', {})
            return {
                "score": round(now.get('value', 50)),
                "rating": now.get('rating', 'Neutral').upper(),
                "label": f"{now.get('rating', 'Neutral').upper()} ({round(now.get('value', 50))}/100)"
            }
        except Exception as e:
            print(f"❌ Erreur Sentiment CNN: {e}")
            return {"score": 50, "rating": "NEUTRAL", "label": "Indisponible"}

    def get_sentiment_data(self):
        """Accès sécurisé au sentiment avec cache"""
        if not self._est_valide("cnn_fear_greed"):
            data = self.fetch_cnn_index()
            self.storage["cnn_fear_greed"] = {"data": data, "timestamp": time.time()}
        return self.storage["cnn_fear_greed"]["data"]

    # --- MODULE : POLYGON (Prix & Snapshot) ---
    def get_market_snapshot(self, ticker):
        """Récupère l'état du marché pour un actif précis"""
        clean_ticker = ticker.replace("/", "").replace(" ", "").upper()
        if not clean_ticker.startswith("C:"):
            clean_ticker = f"C:{clean_ticker}"

        if self._est_valide("polygon"):
            return self.storage["polygon"]["data"]

        url = f"{self.base_url}/v2/snapshot/locale/global/markets/forex/tickers/{clean_ticker}?apiKey={self.api_key}"
        try:
            res = self.session.get(url, timeout=5)
            res.raise_for_status()
            data = res.json()
            self.storage["polygon"] = {"data": data, "timestamp": time.time()}
            return data
        except Exception as e:
            print(f"❌ Erreur Polygon Snapshot: {e}")
            return None

    def _formater_ticker(self, actif):
        """
        Détection intelligente de l'actif (Forex, Crypto, Actions).
        Nettoie 'EUR/USD' ou 'GBP JPY' pour Polygon.
        """
        clean = actif.replace("/", "").replace(" ", "").upper()
        
        # Logique Forex Universelle
        if len(clean) == 6:
            return f"C:{clean}"
            
        # Logique Crypto
        if clean.startswith("BTC") or clean.startswith("ETH"):
            return f"X:{clean}"
            
        # Par défaut (Actions ou indices)
        return clean

    def get_last_price(self, ticker):
        """Récupère le tout dernier prix coté."""
        if self._est_valide("polygon") and self.storage["polygon"]["data"]:
            return self.storage["polygon"]["data"].get("price")

        ticker_poly = self._formater_ticker(ticker)
        url = f"{self.base_url}/v2/last/trade/{ticker_poly}?apiKey={self.api_key}"
        try:
            resp = self.session.get(url, timeout=5).json()
            price = resp.get("results", {}).get("p") or resp.get("last", {}).get("price")
            return price
        except: 
            return None

    def get_volatility_atr(self, ticker):
        """
        Récupère les données de la veille (Previous Close) pour calculer 
        le range et préparer les bornes ADR pour l'IA.
        """
        if self._est_valide("polygon") and self.storage["polygon"]["data"]:
            return self.storage["polygon"]["data"].get("volatility")
        
        ticker_poly = self._formater_ticker(ticker)
        url = f"{self.base_url}/v2/aggs/ticker/{ticker_poly}/prev?apiKey={self.api_key}"
        
        try:
            resp = self.session.get(url, timeout=5).json()
            if resp.get("results"):
                res = resp["results"][0]
                high = res.get("h", 0)
                low = res.get("l", 0)
                close = res.get("c", 0)
                
                daily_range = high - low
                
                self.storage["last_daily_stats"] = {
                    "prev_high": high,
                    "prev_low": low,
                    "prev_close": close,
                    "range": daily_range
                }
                return daily_range
            return 0
        except Exception as e:
            print(f"Erreur Polygon Volatility: {e}")
            return 0

    def get_daily_range_stats(self, ticker):
        """
        Calcule les statistiques ADR glissantes basées sur l'historique 
        récent des 5 derniers jours pour la règle du 'carburant de session'.
        """
        ticker_poly = self._formater_ticker(ticker)
        aujourdhui = datetime.date.today()
        il_ya_dix_jours = aujourdhui - datetime.timedelta(days=10)
        
        url = f"{self.base_url}/v2/aggs/ticker/{ticker_poly}/range/1/day/{il_ya_dix_jours}/{aujourdhui}?sort=desc&limit=5&apiKey={self.api_key}"
        try:
            resp = self.session.get(url, timeout=5).json()
            results = resp.get("results", [])
            if results:
                ranges = [r.get("h", 0) - r.get("l", 0) for r in results]
                avg_adr = sum(ranges) / len(ranges)
                return {
                    "adr_moyenne": round(avg_adr, 5),
                    "dernier_high": results[0].get("h", 0),
                    "dernier_low": results[0].get("l", 0)
                }
            return {"adr_moyenne": 0.00200, "dernier_high": 0, "dernier_low": 0}
        except:
            return {"adr_moyenne": 0.00200, "dernier_high": 0, "dernier_low": 0}

    def get_forex_factory_news(self, actif):
        if self._est_valide("forex_factory"):
            return self.storage["forex_factory"]["data"]

        url_calendar = "https://www.forexfactory.com/ffcal_week_this.xml"
        try:
            response = self.session.get(url_calendar, timeout=5)
            root = ET.fromstring(response.content)
            events_importants = []
            paire = actif.replace("/", "").replace(" ", "").upper()
            devises_concernees = [paire[:3], paire[3:]]
            for event in root.findall('event'):
                devise = event.find('symbol').text.upper() if event.find('symbol') is not None else ""
                impact = event.find('impact').text if event.find('impact') is not None else ""
                title = event.find('title').text if event.find('title') is not None else "News"
                if devise in devises_concernees and impact in ['High', 'Medium']:
                    events_importants.append(f"⚠️ [{impact}] {devise}: {title}")
            
            self.storage["forex_factory"] = {"data": events_importants, "timestamp": time.time()}
            return events_importants
        except: 
            return []
        
    def get_geopolitical_news(self, actif, mode="SCALP"):
        """
        Récupère les news géopolitiques via NewsAPI.
        - mode="SCALP": Tri par fraîcheur (publishedAt) pour réagir vite.
        - mode="SWING": Tri par pertinence (relevancy) pour l'analyse de fond.
        """
        try:
            keywords = "(War OR Geopolitical OR Election OR Crisis OR Sanctions OR Tensions OR Inflation OR Recession)"
            
            # Ajustement dynamique du tri selon le mode
            sort_order = "publishedAt" if mode == "SCALP" else "relevancy"
            
            url = f"https://newsapi.org/v2/everything?q={keywords}&language=en&pageSize=3&sortBy={sort_order}&apiKey={os.getenv('NEWS_API_KEY')}"
            
            response = self.session.get(url, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            articles = data.get("articles", [])
            
            if not articles:
                return ["🌍 Sentiment Géopolitique: Calme (aucune tension majeure détectée)."]
                
            # Ajout du timestamp pour que l'IA sache l'âge de la news (crucial pour le scalp)
            news_list = []
            for a in articles:
                time_str = a.get('publishedAt', 'N/A')
                news_list.append(f"🌍 [GEOPOLITIQUE/RISQUE][{mode}] {a['title']} ({time_str})")
            
            return news_list

        except Exception as e:
            print(f"❌ Erreur flux Géopolitique: {e}")
            return [f"🌍 Sentiment Géopolitique: Flux temporairement indisponible."]    

    def preparer_contexte_marche(self, actif):
        """
        Orchestrateur enrichi pour fournir les données spécifiques 
        aux modes Daily (ADR/Heure) et Investor (Sentiment Long Terme).
        """
        maintenant = datetime.datetime.now()
        heure_serveur = maintenant.strftime("%H:%M")
        
        sentiment = self.get_sentiment_data()

        if not self._est_valide("polygon"):
            prix = self.get_last_price(actif)
            vol = self.get_volatility_atr(actif)
            stats_journalieres = self.get_daily_range_stats(actif) 
            
            self.storage["polygon"] = {
                "data": {
                    "price": prix, 
                    "volatility": vol,
                    "adr_stats": stats_journalieres,
                    "timestamp_str": heure_serveur
                } if prix else {"price": 1.0, "volatility": 0, "adr_stats": {}, "timestamp_str": heure_serveur},
                "timestamp": time.time()
            }

        news = self.get_forex_factory_news(actif)

        return {
            "prix_actuel": self.storage["polygon"]["data"]["price"],
            "volatilite": self.storage["polygon"]["data"]["volatility"],
            "adr_data": self.storage["polygon"]["data"]["adr_stats"], 
            "heure_actuelle": self.storage["polygon"]["data"]["timestamp_str"], 
            "news_impact": news,
            "sentiment": sentiment 
        }

# ====== LOGIQUE MENTOR =======

def get_news(actif="EURUSD", guard=None, POLYGON_API_KEY=None, NEWS_API_KEY=None):
    """
    Synthèse intelligente séparant la Macro-économie de la Géopolitique.
    """
    if guard is None:
        guard = MarketGuard(POLYGON_API_KEY)
    
    # 1. Données brutes
    events_critiques = guard.get_forex_factory_news(actif)
    sentiment_global = guard.get_sentiment_data()
    
    # 2. Récupération des News Géopolitiques (Focus Risque)
    try:
        # On cible uniquement les sujets à fort impact géopolitique
        geo_query = "War OR Geopolitical OR Crisis OR Election OR Sanctions OR Tensions"
        geo_url = f"https://newsapi.org/v2/everything?q={geo_query}&language=en&pageSize=3&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
        r_geo = guard.session.get(geo_url, timeout=5)
        geo_articles = r_geo.json().get("articles", [])
        geo_titles = [f"🌍 {a['title']}" for a in geo_articles]
    except:
        geo_titles = ["🌍 News géopolitiques indisponibles."]

    # 3. Récupération des News Macro-économiques liées à la paire
    try:
        macro_query = f"{actif[:3]} OR {actif[-3:]} AND (Central Bank OR Interest Rate OR CPI OR GDP OR Inflation)"
        macro_url = f"https://newsapi.org/v2/everything?q={macro_query}&language=en&pageSize=2&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
        r_macro = guard.session.get(macro_url, timeout=5)
        macro_articles = r_macro.json().get("articles", [])
        macro_titles = [f"📊 {a['title']}" for a in macro_articles]
    except:
        macro_titles = ["📊 News macro indisponibles."]

    # 4. Construction de la synthèse structurée
    resultat = f"--- 🎭 INDICE SENTIMENT GLOBAL ---\n{sentiment_global['label']}\n\n"
    
    resultat += "--- 📅 CALENDRIER ÉCONOMIQUE (MACRO) ---\n"
    resultat += "\n".join(events_critiques) if events_critiques else "Aucun événement impactant prévu."
    resultat += "\n" + "\n".join(macro_titles)
    
    resultat += "\n\n--- 🌍 FLASH GÉOPOLITIQUE (RISK) ---\n"
    resultat += "\n".join(geo_titles)
    
    return resultat


def analyser_ia_pro(app_instance, ancienne_analyse, nouvelle_analyse, statut_analyse, actif, conviction, guide_etudiant_contenu, guide_expert_contenu, mode="SWING", data_json=None):
    try:
        # TEST DIRECT : On ne passe pas par tes variables complexes
        # On utilise le client global défini en haut du fichier
        response = client_architect.chat.completions.create(
            model="gpt-4o",  # On change pour gpt-4o (plus standard)
            messages=[{"role": "user", "content": "Ping"}]
        )
        return 10, f"Réponse reçue : {response.choices[0].message.content}", "#00FF00"
    except Exception as e:
        # On logue l'erreur complète ici pour voir si c'est une authentification ou un timeout
        logging.error(f"DEBUG CRITIQUE : {str(e)}")
        return 0, f"Erreur OpenAI : {str(e)}", "#FF0000"

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
            model="gpt-4o-mini",
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
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt_synthese}],
            temperature=0.3
        )
        return response.choices[0].message.content
    except:
        return "Plan non synthétisé. Se référer à l'analyse brute."
    

def generer_verdict_final_ia(analyse_init, logs_discipline, resultat, prix_cloture):
    """
    Appelle gpt-4o-mini pour générer le rapport final basé sur ton prompt 'Auditeur Final'.
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
            model="gpt-4o-mini", # Version rapide et peu coûteuse
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
            model="gpt-4o-mini",
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
    
