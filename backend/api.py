from fastapi import FastAPI, HTTPException, Query, Depends, Header, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import logging
import httpx
from typing import Optional
from bridge_news_interface import BridgeNewsInterface
# Remplace le chemin si nécessaire par le bon dossier
from engines.market import MarketEngine 

# --- LOGIQUE MÉTIER ---
import database 
import mentor_ia 
import tools_stats 
from mentor_ia import MarketGuard

from traceback import format_exc # Ajoute ceci en haut de ton fichier
import os
from openai import OpenAI



# Importation de l'instance du manager de dashboard (nom du fichier Dashboard.py)
from Dashboard import dashboard_engine

app = FastAPI(title="Trade Mind API - Mind Engine v2")

# --- MIDDLEWARE ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Liste des codes pays africains (ISO 2-alphabétique) pour la tarification dynamique
PAYS_AFRIQUE = {
    "AO", "BF", "BI", "BJ", "CD", "CF", "CG", "CI", "CM", "CV", "DJ", "DZ", "EG", "ER", 
    "ET", "GA", "GH", "GM", "GN", "GQ", "GW", "KE", "KM", "LR", "LS", "LY", "MA", "MG", 
    "ML", "MR", "MU", "MW", "MZ", "NA", "NE", "NG", "RW", "SC", "SD", "SL", "SN", "SO", 
    "SS", "ST", "SZ", "TD", "TG", "TN", "TZ", "UG", "ZA", "ZM", "ZW"
}

# --- CONFIGURATION DU PONT DE SÉCURITÉ BACKEND (SUPABASE SECURITY LAYER) ---
def verifier_session_terminal(authorization: str = Header(None)):
    """
    Middleware de garde-fou assoupli pour le développement local.
    Permet au frontend Next.js de se connecter sans bloquer sur l'erreur 412.
    """
    if not authorization:
        logging.info("ℹ️ Mode Dev : Accès invité sans en-tête d'authentification.")
        return "guest_token_dev"
    
    try:
        # Structure attendue : "Bearer token_jwt_supabase"
        token = authorization.split(" ")[1]
        return token
    except Exception:
        return "guest_token_dev"

def verifier_acces_premium(token: str = Depends(verifier_session_terminal)):
    """
    Garde-fou optionnel pour brider les fonctionnalités Premium (ex: Mode Investisseur, Analyses avancées).
    Passe l'utilisateur 'guest_token_dev' en accès libre pendant tes tests locaux.
    """
    if token == "guest_token_dev":
        return True # Accès total autorisé pour le développement
    return True

# --- UTILS : GÉOLOCALISATION PAR IP ---
async def detecter_zone_geographique(request: Request) -> dict:
    """
    Analyse l'adresse IP de l'utilisateur pour déterminer sa zone tarifaire.
    """
    ip_client = request.headers.get("x-forwarded-for")
    if ip_client:
        ip_client = ip_client.split(",")[0].strip()
    else:
        ip_client = request.client.host

    # Bypass pour les tests locaux sur ton LENOVO
    if ip_client in ["127.0.0.1", "localhost", "::1"]:
        return {"zone": "AFRIQUE", "montant": 8000.0, "devise": "XAF", "pays": "Gabon (Local Test)"}

    url_geo = f"http://ip-api.com/json/{ip_client}?fields=status,countryCode,country"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url_geo, timeout=2.0)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    code_pays = data.get("countryCode", "").upper()
                    nom_pays = data.get("country", "Inconnu")
                    
                    if code_pays in PAYS_AFRIQUE:
                        return {"zone": "AFRIQUE", "montant": 8000.0, "devise": "XAF", "pays": nom_pays}
                    else:
                        return {"zone": "RESTE_DU_MONDE", "montant": 13000.0, "devise": "EUR", "pays": nom_pays}
    except Exception as e:
        print(f"⚠️ Échec géo-détection (IP: {ip_client}) : {e}")
    
    return {"zone": "AFRIQUE", "montant": 8000.0, "devise": "XAF", "pays": "Par défaut"}


# --- MODÈLES DE DONNÉES ---
class TradeRequest(BaseModel):
    actif: str
    analyse: str
    conviction: int
    position: str
    statut: str
    mode: str = "Étudiant"
    type: str = "SWING"
    step: Optional[int] = None
    
    # Ajout de Union[float, None] et default=None pour accepter les chaînes vides ou nulles
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    calculated_rr: Optional[float] = None

    # Ajout d'un validateur pour convertir automatiquement les chaînes vides en None
    from pydantic import field_validator

    @field_validator('entry_price', 'stop_loss', 'take_profit', 'calculated_rr', mode='before')
    @classmethod
    def empty_str_to_none(cls, v):
        if v == "":
            return None
        return v

class CalcRequest(BaseModel):
    capital: float
    risk: float
    pips: float

class GuardianRequest(BaseModel):
    message: str
    analyse_complete: str
    actif: str

class CloturePosition(BaseModel):
    # Ajuste ces champs selon les données réelles de tes positions
    actif: str
    statut: str
    resultat: Optional[str] = None
    performance: Optional[float] = None

class ClotureRequest(BaseModel):
    positions: list[CloturePosition]
    postSessionText: str


# --- ROUTE ABONNEMENT & PRIX DYNAMIQUE ---

@app.get("/api/abonnement/tarification-dynamique")
async def route_tarification_dynamique(request: Request):
    infos_tarif = await detecter_zone_geographique(request)
    return {
        "status": "success",
        "zone": infos_tarif["zone"],
        "pays_detecte": infos_tarif["pays"],
        "prix_affichage": f"{int(infos_tarif['montant'])} {infos_tarif['devise']}",
        "montant_brut": infos_tarif["montant"],
        "devise": infos_tarif["devise"]
    }


# --- ROUTES DASHBOARD ---

@app.get("/dashboard/metrics")
async def route_get_metrics(token: str = Depends(verifier_session_terminal)):
    """Récupère les métriques complètes et les injecte À PLAT pour correspondre au Frontend d'origine."""
    try:
        data = dashboard_engine.get_full_metrics()
        # CORRECTION HISTORIQUE : Renvoyer directement le dictionnaire 'data' pour alimenter la courbe et le capital
        return data
    except Exception as e:
        logging.error(f"❌ Erreur Metrics API : {e}")
        raise HTTPException(status_code=500, detail="Échec de la liaison avec le Mind Engine")

@app.post("/dashboard/update-capital")
async def route_update_capital(amount: float = Query(...), token: str = Depends(verifier_session_terminal)):
    """Met à jour le capital initial de manière permanente dans la base de données."""
    try:
        result = dashboard_engine.update_base_capital(amount)
        # CORRECTION ENREGISTREMENT : On force une réponse positive directe si Supabase valide l'écriture
        if result and (result.get("success") or "new_cap" in result):
            return {"status": "success", "message": "Capital enregistré", "new_cap": result.get("new_cap")}
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Erreur d'écriture Supabase"))
    except Exception as e:
        logging.error(f"❌ Erreur Update Capital API : {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- ROUTES ANALYSE & TOOLS ---


@app.post("/analyse/swing")
async def route_analyse_swing(data: TradeRequest, token: str = Depends(verifier_session_terminal)):
    # 1. GARDE DE SÉCURITÉ : Vérification du mode "Étudiant"
    if data.mode.upper() not in ["SWING", "ÉTUDIANT", "ETUDIANT"]:
        raise HTTPException(status_code=400, detail=f"Mode invalide reçu : {data.mode}")

    try:
        # 0. INITIALISATION CONTEXTE
        current_metrics = dashboard_engine.get_full_metrics()
        is_locked = current_metrics.get("risk_engine", {}).get("status") == "LOCKDOWN"

        # 1. RÉCUPÉRATION DES NEWS
        alerte_news = ""
        try:
            shared_guard = MarketGuard()
            bridge = BridgeNewsInterface(guard_instance=shared_guard)
            alerte = bridge.get_live_alerts(data.actif, "SWING")
            if alerte:
                alerte_news = f"{alerte}\n\n"
        except Exception as e:
            logging.error(f"⚠️ Erreur news (Swing) : {e}")

        # 2. TENTATIVE IA
        feedback_ia = "Analyse IA temporairement indisponible."
        try:
            class AppMock:
                def __init__(self, settings):
                    self.user_settings = settings
                    self.info_sl_tp = "N/A"
                    self.raisonnement_user = "N/A"
            
            app_mock = AppMock({"ia_severite": "Strict" if is_locked else "Neutre"})

            score, verdict, couleur = mentor_ia.analyser_ia_swing(
            app_mock, 
            data.analyse,    # nouvelle_analyse
            data.actif,      # actif
            data_json=data.model_dump(), # On passe l'objet complet au lieu de champs isolés
            client_architect = mentor_ia.client_architect # Votre instance OpenAI
            )
            feedback_ia = verdict
        except Exception as ie:
            logging.error(f"⚠️ Erreur moteur IA : {ie}")
            feedback_ia = f"Erreur de génération : {str(ie)}"

        # 3. FUSION DU FEEDBACK
        feedback_final = f"{alerte_news}[ANALYSE IA — SWING]\n{feedback_ia}"

        # 4. SAUVEGARDE COMPLÈTE
        try:
            entry_f = float(data.entry_price) if data.entry_price else 0.0
            sl_f = float(data.stop_loss) if data.stop_loss else 0.0
            tp_f = float(data.take_profit) if data.take_profit else 0.0
            rr_f = float(data.calculated_rr) if data.calculated_rr else 0.0
        except (ValueError, TypeError):
            entry_f, sl_f, tp_f, rr_f = 0.0, 0.0, 0.0, 0.0

        trade_id = database.sauvegarder_trade_final(
            actif=data.actif,
            biais=data.position,
            conviction=data.conviction,
            score_ia=0, 
            analyse=data.analyse,
            feedback=feedback_final,
            statut=data.statut,
            position=data.position,
            mode="Étudiant", # Mode réel attendu par Supabase
            t_type=data.type,
            entry_price=entry_f,
            stop_loss=sl_f,
            take_profit=tp_f,
            rr=rr_f
        )
        
        return {
            "feedback": feedback_final,
            "engine_status": "SAFE",
            "trade_id": trade_id
        }

    except Exception as ie:
            logging.error(f"⚠️ Erreur moteur IA : {ie}")
            # Si l'IA échoue, on continue MAIS on s'assure que feedback_ia est défini
            feedback_ia = "Analyse indisponible."
    finally:
        # NETTOYAGE SYSTÉMATIQUE
        del shared_guard
        del bridge
        del app_mock
        # Appel de ta fonction de nettoyage
        purge_ram()

@app.post("/analyse/daily")
async def route_analyse_daily(data: TradeRequest, token: str = Depends(verifier_session_terminal)):
    # 1. GARDE DE SÉCURITÉ
    if data.mode.upper() != "DAILY":
        raise HTTPException(status_code=400, detail="Route réservée au mode DAILY.")

    try:
        # 0. INITIALISATION CONTEXTE
        current_metrics = dashboard_engine.get_full_metrics()
        is_locked = current_metrics.get("risk_engine", {}).get("status") == "LOCKDOWN"

        # 1. RÉCUPÉRATION DES NEWS (Spécifique au Daily)
        alerte_news = ""
        try:
            shared_guard = MarketGuard()
            bridge = BridgeNewsInterface(guard_instance=shared_guard)
            alerte = bridge.get_live_alerts(data.actif, "DAILY")
            if alerte:
                alerte_news = f"{alerte}\n\n"
        except Exception as e:
            logging.error(f"⚠️ Erreur news (Daily) : {e}")

        # 2. TENTATIVE IA (Appel Mentor IA)
        feedback_ia = "Analyse IA temporairement indisponible."
        try:
            class AppMock:
                def __init__(self, settings):
                    self.user_settings = settings
                    self.info_sl_tp = "N/A"
                    self.raisonnement_user = "N/A"
            
            app_mock = AppMock({"ia_severite": "Strict" if is_locked else "Neutre"})

            # Utilisation de l'IA pour auditer le Daily
            score, verdict, couleur = mentor_ia.analyser_ia_scalp(
            app_mock, 
            data.analyse,    # nouvelle_analyse
            data.actif,      # actif
            data_json=data.model_dump(), # On passe l'objet complet au lieu de champs isolés
            client_architect= mentor_ia.client_architect
            )
            feedback_ia = verdict
        except Exception as ie:
            logging.error(f"⚠️ Erreur moteur IA : {ie}")
            feedback_ia = f"Erreur de génération : {str(ie)}"
        # 3. FUSION DU FEEDBACK
        feedback_final = f"{alerte_news}[ANALYSE IA — DAILY]\n{feedback_ia}"

        # 4. CONVERSION TYPES
        try:
            entry_f = float(data.entry_price) if data.entry_price else 0.0
            sl_f = float(data.stop_loss) if data.stop_loss else 0.0
            tp_f = float(data.take_profit) if data.take_profit else 0.0
            rr_f = float(data.calculated_rr) if data.calculated_rr else 0.0
        except (ValueError, TypeError):
            entry_f, sl_f, tp_f, rr_f = 0.0, 0.0, 0.0, 0.0

        # 5. SAUVEGARDE COMPLÈTE
        trade_id = database.sauvegarder_trade_final(
            actif=data.actif,
            biais=data.position,
            conviction=data.conviction,
            score_ia=0,
            analyse=data.analyse,
            feedback=feedback_final,
            statut=data.statut,
            position=data.position,
            mode="DAILY",
            t_type=data.type,
            entry_price=entry_f,
            stop_loss=sl_f,
            take_profit=tp_f,
            rr=rr_f
        )
        
        return {
            "feedback": feedback_final,
            "engine_status": "SAFE",
            "trade_id": trade_id
        }

    except Exception as e:
        logging.error(f"❌ Erreur critique route_analyse_daily : {e}")
        return {"feedback": f"Erreur système : {str(e)}", "engine_status": "ERROR"}
    finally:
        # NETTOYAGE SYSTÉMATIQUE
        del shared_guard
        del bridge
        del app_mock
        # Appel de ta fonction de nettoyage
        purge_ram()

@app.post("/analyse/daily/cloture")
async def route_cloture_daily(request: ClotureRequest, token: str = Depends(verifier_session_terminal)):
    try:
        # 0. INITIALISATION CONTEXTE
        current_metrics = dashboard_engine.get_full_metrics()
        is_locked = current_metrics.get("risk_engine", {}).get("status") == "LOCKDOWN"
        
        # 1. PRÉPARATION DES DONNÉES POUR LE MENTOR
        # On construit une synthèse textuelle des positions pour que l'IA puisse auditer le processus
        resume_positions = "\n".join([
            f"Position {i+1} ({p.actif}) : {p.statut} | Audit IA : {p.iaVerdict}" 
            for i, p in enumerate(request.positions)
        ])
        
        # 2. GÉNÉRATION DU DÉBRIEF VIA TON MOTEUR EXISTANT
        # On utilise la fonction 'generer_verdict_final_ia' que tu as déjà dans mentor_ia.py
        feedback = mentor_ia.generer_verdict_final_ia(
            analyse_init=resume_positions, 
            logs_discipline="Session Daily clôturée", 
            resultat=f"Fin de session. Débrief : {request.postSessionText}", 
            prix_cloture="N/A"
        )
        
        # 3. LOGGING ET RETOUR
        logging.info("Session Daily clôturée et auditée par MentorIA.")
        
        return {
            "status": "success", 
            "feedback": feedback,
            "engine_status": "SAFE" if not is_locked else "WARNING"
        }
    #NB: Pensez à ajouter un pugeur de RAM dans cette route.
    
    except Exception as e:
        logging.error(f"❌ Erreur critique route_cloture_daily : {format_exc()}")
        raise HTTPException(
            status_code=500, 
            detail=f"Erreur lors de la clôture : {str(e)}"
        )
    

@app.post("/analyse/scalp")
async def route_analyse_scalp(data: TradeRequest, token: str = Depends(verifier_session_terminal)):
    if data.mode.upper() != "SCALP":
        raise HTTPException(status_code=400, detail="Route réservée au mode SCALP.")

    try:
        # Initialisation
        # ... (Logique identique)
        
        trade_id = database.sauvegarder_trade_final(
            actif=data.actif,
            biais=data.position,
            conviction=data.conviction,
            score_ia=0,
            analyse=data.analyse,
            feedback="Analyse Scalp en cours de développement...",
            statut=data.statut,
            position=data.position,
            mode="SCALP",
            t_type=data.type,
            entry_price=data.entry_price,
            stop_loss=data.stop_loss,
            take_profit=data.take_profit,
            rr=data.calculated_rr
        )
        
        return {"feedback": "Mode Scalp initialisé.", "engine_status": "SAFE", "trade_id": trade_id}
    except Exception as e:
        logging.error(f"❌ Erreur critique route_analyse_scalp : {e}")
        return {"feedback": f"Erreur : {str(e)}", "engine_status": "ERROR"}
    finally:
        # NETTOYAGE SYSTÉMATIQUE
        del shared_guard
        del bridge
        del app_mock
        # Appel de ta fonction de nettoyage
        purge_ram()
    
@app.post("/database/save")
async def route_sauvegarde_generique(data: TradeRequest, token: str = Depends(verifier_session_terminal)):
    try:
        # Initialisation du contexte
        current_metrics = dashboard_engine.get_full_metrics()
        is_locked = current_metrics.get("risk_engine", {}).get("status") == "LOCKDOWN"

        # 1. TENTATIVE IA (Approche généralisée)
        ia_success = False
        feedback_ia = "Analyse IA temporairement indisponible."
        try:
            resultat = mentor_ia.lancer_analyse_api(
                data.analyse, 
                data.conviction, 
                data.actif, 
                {"ia_severite": "Strict" if is_locked else "Neutre", "mode": data.mode}
            )
            verdict = resultat.get("verdict")
            if verdict:
                feedback_ia = verdict
                ia_success = True
        except Exception as ie:
            logging.error(f"⚠️ IA en échec ({data.mode}) : {ie}")

        # 2. INJECTION NEWS
        try:
            shared_guard = MarketGuard()
            bridge = BridgeNewsInterface(guard_instance=shared_guard)
            alerte = bridge.get_live_alerts(data.actif, data.mode)
            if alerte:
                feedback_ia = f"{alerte}\n\n[AUDIT IA]\n{feedback_ia}"
        except Exception as e:
            logging.error(f"⚠️ Erreur récupération news : {e}")

        # 3. SAUVEGARDE COMPLÈTE
        # Conversion sécurisée des nombres (si vide, envoie None pour Supabase)
        def to_float(val):
            try: return float(val) if val is not None and val != "" else None
            except: return None

        trade_id = database.sauvegarder_trade_final(
            trade_id=getattr(data, 'id', None), # Passage explicite de l'ID pour le PATCH
            actif=data.actif,
            biais=data.position,
            conviction=data.conviction,
            score_ia=0,
            analyse=data.analyse,
            feedback=feedback_ia,
            statut=data.statut,
            position=data.position,
            mode=data.mode, # Gardé tel quel (ex: "Étudiant") pour correspondre à Supabase
            t_type=data.type,
            entry_price=to_float(data.entry_price),
            stop_loss=to_float(data.stop_loss),
            take_profit=to_float(data.take_profit),
            rr=to_float(data.calculated_rr)
        )
        
        if trade_id is False:
            raise Exception("La base de données a retourné une erreur lors de l'écriture.")
        
        return {
            "status": "success", 
            "trade_id": trade_id, 
            "feedback": feedback_ia, 
            "ia_status": "SUCCESS" if ia_success else "FALLBACK",
            "engine_status": "SAFE"
        }

    except Exception as e:
        logging.error(f"❌ Erreur critique route_sauvegarde_generique : {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyse/guardian")
async def route_guardian_live_chat(data: GuardianRequest, token: str = Depends(verifier_session_terminal)):
    try:
        plan_resume = mentor_ia.synthetiser_plan_pour_guardian(data.analyse_complete, data.actif)
        verdict_guardian = mentor_ia.analyser_compagnon_live(None, data.message, plan_resume)
        return {"verdict": verdict_guardian}
    except Exception as e:
        logging.error(f"❌ Erreur Passerelle Guardian Chat : {e}")
        raise HTTPException(status_code=500, detail=f"Erreur d'évaluation psychologique : {str(e)}")

@app.post("/tools/calculateur")
async def route_calcul(data: CalcRequest, token: str = Depends(verifier_session_terminal)):
    try:
        lot = tools_stats.calculer_lot(data.capital, data.risk, data.pips)
        return {"lot": lot}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- ROUTES HISTORIQUE ----

@app.get("/historique/all")
async def get_historique(token: str = Depends(verifier_session_terminal)):
    try:
        trades = database.recuperer_tout_historique()
        format_trades = []
        for t in trades:
            # Mapping strict aligné sur la version stable (rollback)
            format_trades.append({
                "id": t[0],
                "date": str(t[1])[:16] if len(t) > 1 and t[1] else "N/A",
                "actif": str(t[2]).upper() if len(t) > 2 and t[2] else "UNITÉ",
                "statut": str(t[3]).upper() if len(t) > 3 and t[3] else "BROUILLON",
                "analyse": t[4] if len(t) > 4 and t[4] else "",
                "position": str(t[5]).upper() if len(t) > 5 and t[5] else "NEUTRE",
                "conviction": t[6] if len(t) > 6 else 50,
                "mode": str(t[7]).upper() if len(t) > 7 and t[7] else "ÉTUDIANT",
                "feedback": t[8] if len(t) > 8 and t[8] else "",
                "type": str(t[9]).upper() if len(t) > 9 else "SWING"
            })
        return {"trades": format_trades}
    except Exception as e:
        logging.error(f"Erreur historique : {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/historique/get/{trade_id}")
async def get_trade_details(trade_id: int, token: str = Depends(verifier_session_terminal)):
    try:
        t = database.recuperer_trade_par_id(trade_id)
        if not t:
            raise HTTPException(status_code=404, detail="Analyse introuvable")
        
        # Mapping sécurisé par accès aux clés (accès direct au JSON Supabase)
        # On utilise .get() pour éviter tout crash si une colonne est manquante
        trade_dict = {
            "id": t.get("id"),
            "date": str(t.get("date", "N/A"))[:16],
            "actif": str(t.get("actif", "UNITÉ")).upper(),
            "statut": str(t.get("statut", "BROUILLON")).upper(),
            "analyse": t.get("analyse", ""),
            "position": str(t.get("position", "NEUTRE")).upper(),
            "conviction": t.get("conviction", 50),
            "mode": str(t.get("mode", "ÉTUDIANT")).upper(),
            "feedback": t.get("feedback", ""),
            "type": str(t.get("type", "SWING")).upper()
        }
        return trade_dict
    except Exception as e:
        logging.error(f"Erreur détails trade {trade_id} : {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/historique/delete/{trade_id}")
async def delete_trade(trade_id: int, token: str = Depends(verifier_session_terminal)):
    if database.supprimer_trade_sql(trade_id):
        return {"status": "deleted"}
    raise HTTPException(status_code=500, detail="Erreur suppression")


# --- ROUTES MARKET --- 

@app.get("/market/intelligence")
async def route_market_intel(
    actif: str = "EURUSD", 
    mode: str = "SWING", 
    token: str = Depends(verifier_session_terminal)
):
    """
    Route centralisée pour le dashboard :
    1. Récupère le sentiment via le Guard officiel.
    2. Récupère le feed exhaustif via le Bridge.
    """
    resp = {
        "fear_greed": {"score": 50, "rating": "NEUTRAL"}, 
        "news_feed": "Recherche d'actualités en temps réel..."
    }

    # Initialisation des outils
    shared_guard= MarketGuard()
    bridge = BridgeNewsInterface(guard_instance=shared_guard)

    # 1. RÉCUPÉRATION DU SENTIMENT
    try:
        sentiment = shared_guard.fetch_cnn_index()
        if sentiment:
            resp["fear_greed"] = sentiment
    except Exception as e:
        logging.error(f"Erreur lors de la récupération CNN : {e}")

    # 2. RÉCUPÉRATION DES NEWS
    try:
        news_raw = bridge.get_live_alerts(actif, mode)
        if news_raw:
            resp["news_feed"] = news_raw
        else:
            resp["news_feed"] = "Aucune actualité majeure détectée."
    except Exception as e:
        logging.error(f"Erreur lors de la récupération des news via Bridge : {e}")
        resp["news_feed"] = "Impossible de récupérer les flux live."

    return resp

@app.post("/investor/audit")
async def route_investor_audit(data: dict, premium: bool = Depends(verifier_acces_premium)):
    text = data.get("text")
    actif = data.get("actif")
    try:
        # Utilisation de l'instance locale ou globale selon ta config
        # Si market_guard échoue, on prévoit un repli
        contexte = {}
        try:
            contexte = dashboard_engine.market_guard.preparer_contexte_marche(actif)
        except AttributeError:
            # Repli si market_guard n'est pas accessible
            contexte = {"status": "Market context unavailable"}
            
        resultat_audit = mentor_ia.analyser_coherence_investisseur(text, contexte)
        return {
            "audit": resultat_audit,
            "market_snapshot": contexte
        }
    except Exception as e:
        logging.error(f"Erreur Audit Investor: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 
    
@app.get("/analytics/performance/{mode}")
async def get_detailed_mode_performance(mode: str, token: str = Depends(verifier_session_terminal)):
    try:
        target_mode = mode.upper()
        trades = database.get_performance_by_mode(target_mode) 
        
        if not trades:
            return {
                "mode": target_mode,
                "winrate": 0,
                "equity": [100],
                "total_trades": 0
            }
        
        equity_curve = [100]
        current_val = 100
        wins = 0
        
        for t in trades:
            impact = 2 if t.get('resultat') == 'WIN' else -2
            current_val += impact
            equity_curve.append(round(current_val, 2))
            
            if t.get('resultat') == 'WIN':
                wins += 1
        
        winrate = round((wins / len(trades)) * 100, 2) if trades else 0
            
        return {
            "mode": target_mode,
            "winrate": winrate,
            "total_trades": len(trades),
            "equity": equity_curve
        }
    except Exception as e:
        logging.error(f"❌ Erreur Analytics ({mode}) : {e}")
        raise HTTPException(status_code=500, detail=str(e)) 

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta

def rappel_swing():
    # Ici, tu peux envoyer une notif vers ton frontend ou via email/SMS
    print(f"[{datetime.now()}] RAPPEL : Actualisez vos analyses SWING.")
    # Si tu as une table 'notifications' dans ta DB, tu peux l'insérer ici
    # database.creer_notification(user_id=1, message="Actualisez vos analyses SWING.")

# Initialisation
scheduler = BackgroundScheduler()
# Déclenche toutes les 48 heures (2 jours)
scheduler.add_job(rappel_swing, 'interval', hours=48)
scheduler.start()

# --- PROCESSUS INITIAL DU SYSTEME ---
database.initialiser_config()
database.init_db()
database.migrate_db()

# --- NETTOYAGE CRITIQUE DE LA RAM ---
import gc
import os
import psutil

def purge_ram():
    # 1. Force le ramasse-miettes à libérer les objets temporaires du boot
    gc.collect()
    
    # 2. Vérification du gain (Log pour Render)
    process = psutil.Process(os.getpid())
    ram_usage = process.memory_info().rss / 1024 / 1024
    print(f"--- [SYSTEM] RAM purgée après démarrage : {ram_usage:.2f} MB ---")

# Exécution de la purge juste avant que Uvicorn ne soit totalement "chaud"
purge_ram()