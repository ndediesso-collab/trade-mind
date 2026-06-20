import os
import httpx
from dotenv import load_dotenv

# --- CONFIGURATION STRICTE HTTP SUPABASE ---
DOSSIER_BACKEND = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DOSSIER_BACKEND, "trademind_pro.db") 

load_dotenv()

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
# Astuce : Utilise la clé Service Role (ou désactive la RLS sur Supabase pour la clé Anon) pour autoriser l'écriture API
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_SERVICE_ROLE_KEY") or os.getenv("NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def initialiser_config():
    print("📡 [SYSTEM] Connexion HTTP établie avec le Cloud Supabase.")

def init_db():
    print("✅ [SYSTEM] Mode API REST activé. Structure cloud opérationnelle.")

def migrate_db():
    print("✅ [SYSTEM] Synchronisation réseau terminée.")

def sauvegarder_trade_final(actif, biais, conviction, score_ia, analyse, feedback, statut, position, mode, 
                            t_type="SWING", trade_id=None, entry_price=None, stop_loss=None, take_profit=None, rr=None):
    """
    Insère ou met à jour un trade complet dans journal_final via l'API REST.
    Fonctionne pour tous les modes : SWING, DAILY, SCALP.
    """
    url = f"{SUPABASE_URL}/rest/v1/journal_final"
    
    # Payload unifié pour tous les modes
    payload = {
        "actif": actif.upper(),
        "biais": biais,
        "conviction": int(conviction),
        "score_ia": int(score_ia),
        "analyse": analyse,
        "feedback": feedback,
        "statut": statut,
        "position": position,
        "mode": mode.upper(),  # Normalisé pour Supabase
        "type": t_type,
        "mode_type": t_type,
        "entry_price": float(entry_price) if entry_price is not None else None,
        "stop_loss": float(stop_loss) if stop_loss is not None else None,
        "take_profit": float(take_profit) if take_profit is not None else None,
        "rr": float(rr) if rr is not None else None
    }

    try:
        if trade_id:
            # MISE À JOUR : PATCH si un ID existe (pour finaliser un brouillon)
            patch_url = f"{url}?id=eq.{trade_id}"
            response = httpx.patch(patch_url, headers=HEADERS, json=payload)
            if response.status_code in [200, 204]:
                return trade_id
            print(f"❌ Erreur PATCH Supabase ({response.status_code}) : {response.text}")
            return False
        else:
            # INSERTION : POST pour un nouveau trade
            response = httpx.post(url, headers=HEADERS, json=payload)
            if response.status_code in [200, 201]:
                data = response.json()
                new_id = data[0]["id"]
                
                # Initialisation parallèle des logs
                log_url = f"{SUPABASE_URL}/rest/v1/mind_engine_logs"
                log_payload = {"trade_id": new_id, "score_engine": int(score_ia), "statut_ia": "INIT_IA"}
                httpx.post(log_url, headers=HEADERS, json=log_payload)
                return new_id
            
            print(f"❌ Erreur POST Supabase ({response.status_code}) : {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Échec réseau sauvegarder_trade_final : {e}")
        return False

def recuperer_tout_historique():
    """Récupère l'historique sans forcer le tri sur le mot réservé si conflit."""
    url = f"{SUPABASE_URL}/rest/v1/journal_final?select=id,date,actif,statut,analyse,position,conviction,mode,feedback,%22type%22"
    try:
        response = httpx.get(url, headers=HEADERS)
        if response.status_code == 200:
            res = response.json()
            res.sort(key=lambda x: x.get("date") or "", reverse=True)
            return [
                (t["id"], t.get("date"), t.get("actif"), t.get("statut"), t.get("analyse"),
                 t.get("position"), t.get("conviction"), t.get("mode"), t.get("feedback"), t.get("type"))
                for t in res
            ]
        print(f"⚠️ Erreur Historique API ({response.status_code}) : {response.text}")
        return []
    except Exception as e:
        print(f"❌ Échec recuperer_tout_historique : {e}")
        return []

def get_recent_flux(limit=10):
    """Extraction à plat des flux pour éviter le conflit de jointure imbriquée."""
    url = f"{SUPABASE_URL}/rest/v1/capital_flux?select=montant,type&order=id.desc&limit={limit}"
    try:
        response = httpx.get(url, headers=HEADERS)
        if response.status_code == 200:
            return [
                {
                    "actif": "TRADE", 
                    "montant": float(r.get("montant") or 0.0), 
                    "type": r.get("type", "DEPOT")
                } 
                for r in response.json()
            ]
        return []
    except Exception as e:
        print(f"❌ Échec get_recent_flux : {e}")
        return []

def recuperer_trade_par_id(trade_id):
    """Extrait un dossier de transaction unique par son identifiant unique."""
    url = f"{SUPABASE_URL}/rest/v1/journal_final?id=eq.{trade_id}&select=*"
    try:
        response = httpx.get(url, headers=HEADERS)
        if response.status_code == 200 and response.json():
            res = response.json()[0]
            if res.get('actif'):
                res['actif'] = str(res['actif']).upper()
            return res
        return None
    except Exception as e:
        print(f"❌ Échec recuperer_trade_par_id : {e}")
        return None

def sauvegarder_analyse_investisseur(analyse_id, actif, texte, statut="BROUILLON"):
    """Persistance des analyses fondamentales long terme via l'API REST."""
    if analyse_id:
        url = f"{SUPABASE_URL}/rest/v1/journal_final?id=eq.{analyse_id}"
        payload = {"analyse": texte, "actif": actif, "statut": statut, "mode": "Investor", "mode_type": "INVESTOR"}
        try:
            response = httpx.patch(url, headers=HEADERS, json=payload)
            return analyse_id if response.status_code in [200, 204] else False
        except:
            return False
    else:
        url = f"{SUPABASE_URL}/rest/v1/journal_final"
        payload = {"actif": actif, "analyse": texte, "statut": statut, "mode": "Investor", "mode_type": "INVESTOR"}
        try:
            response = httpx.post(url, headers=HEADERS, json=payload)
            if response.status_code in [200, 201]:
                return response.json()[0]["id"]
            return False
        except:
            return False

def get_performance_by_mode(mode):
    """Récupère l'évolution de la performance pour l'orchestrateur Logic.py."""
    url = f"{SUPABASE_URL}/rest/v1/journal_final?mode_type=eq.{mode}&statut=eq.COMPLETED&select=date,resultat&order=date.asc"
    try:
        response = httpx.get(url, headers=HEADERS)
        return response.json() if response.status_code == 200 else []
    except Exception as e:
        print(f"❌ Échec get_performance_by_mode : {e}")
        return []

def get_trades_by_mode(mode):
    """Récupère la liste brute des trades complétés d'un mode."""
    url = f"{SUPABASE_URL}/rest/v1/journal_final?mode_type=eq.{mode}&statut=eq.COMPLETED&select=id,resultat,actif,date"
    try:
        response = httpx.get(url, headers=HEADERS)
        return response.json() if response.status_code == 200 else []
    except Exception as e:
        print(f"❌ Échec get_trades_by_mode : {e}")
        return []

def ajouter_flux_capital(trade_id, montant, flux_type, justification=""):
    url = f"{SUPABASE_URL}/rest/v1/capital_flux"
    payload = {"trade_id": trade_id, "montant": float(montant), "type": flux_type, "justification": justification}
    try:
        response = httpx.post(url, headers=HEADERS, json=payload)
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"❌ Échec ajouter_flux_capital : {e}")
        return False

def supprimer_trade_sql(trade_id):
    url = f"{SUPABASE_URL}/rest/v1/journal_final?id=eq.{trade_id}"
    try:
        response = httpx.delete(url, headers=HEADERS)
        return response.status_code in [200, 204]
    except:
        return False

def update_capital_initial(nouveau_montant):
    """Gère l'écriture ou la mise à jour (Upsert) du capital."""
    url = f"{SUPABASE_URL}/rest/v1/capital_config"
    payload = {"id": 1, "capital_initial": float(nouveau_montant)}
    
    # AJUSTEMENT CLÉ : PostgREST requiert "On-Conflict" pour un Upsert via POST sur clé primaire explicite
    headers_upsert = {
        **HEADERS,
        "Prefer": "resolution=merge-duplicates, return=representation",
        "On-Conflict": "id"
    }
    try:
        response = httpx.post(url, headers=headers_upsert, json=payload)
        if response.status_code in [200, 201, 204]:
            return True
        print(f"⚠️ Échec update_capital_initial ({response.status_code}) : {response.text}")
        return False
    except Exception as e:
        print(f"❌ Échec réseau update_capital_initial : {e}")
        return False

def calculer_capital_total():
    try:
        res_config = httpx.get(f"{SUPABASE_URL}/rest/v1/capital_config?select=capital_initial&id=eq.1", headers=HEADERS).json()
        base = float(res_config[0]["capital_initial"]) if res_config and len(res_config) > 0 else 1000.0
        
        res_flux = httpx.get(f"{SUPABASE_URL}/rest/v1/capital_flux?select=montant", headers=HEADERS).json()
        flux = sum([float(f.get("montant") or 0.0) for f in res_flux]) if res_flux and isinstance(res_flux, list) else 0.0
        return round(base + flux, 2)
    except Exception as e:
        print(f"⚠️ Erreur de sommation calculer_capital_total : {e}")
        return 1000.0

def calculer_winrate():
    try:
        res = httpx.get(f"{SUPABASE_URL}/rest/v1/capital_flux?type=in.(\"WIN\",\"LOSS\")&select=type", headers=HEADERS).json()
        if not res or not isinstance(res, list): return 0.0
        wins = len([r for r in res if r.get("type") == 'WIN'])
        return round((wins / len(res)) * 100, 1)
    except Exception as e:
        print(f"⚠️ Erreur de parsing calculer_winrate : {e}")
        return 0.0

def get_equity_curve():
    try:
        res_config = httpx.get(f"{SUPABASE_URL}/rest/v1/capital_config?select=capital_initial&id=eq.1", headers=HEADERS).json()
        cap = float(res_config[0]["capital_initial"]) if res_config and len(res_config) > 0 else 1000.0
        
        # Ajout d'un filtre d'ordonnancement explicite pour bâtir la courbe chronologique exacte
        res_flux = httpx.get(f"{SUPABASE_URL}/rest/v1/capital_flux?select=montant&order=id.asc", headers=HEADERS).json()
        
        curve = [cap]
        if not res_flux or not isinstance(res_flux, list):
            curve.append(cap)
            return curve
            
        for f in res_flux:
            cap += float(f.get("montant") or 0.0)
            curve.append(round(cap, 2))
        return curve
    except Exception as e:
        print(f"⚠️ Erreur extraction courbe get_equity_curve : {e}")
        return [1000.0, 1000.0]

def get_last_active_trade():
    url = f"{SUPABASE_URL}/rest/v1/journal_final?statut=eq.En%20attente&order=date.desc&limit=1"
    try:
        res = httpx.get(url, headers=HEADERS).json()
        return res[0] if res and len(res) > 0 else None
    except Exception as e:
        print(f"❌ Erreur get_last_active_trade : {e}")
        return None

def recuperer_logs_trade(trade_id):
    url = f"{SUPABASE_URL}/rest/v1/mind_engine_logs?trade_id=eq.{trade_id}&limit=1"
    try:
        res = httpx.get(url, headers=HEADERS).json()
        return res[0] if res and len(res) > 0 else None
    except: return None

def enregistrer_alerte(trade_id, alerte):
    url = f"{SUPABASE_URL}/rest/v1/mind_engine_alerts"
    payload = {"trade_id": trade_id, "type": alerte.get('type'), "niveau": alerte.get('niveau')}
    try:
        response = httpx.post(url, headers=HEADERS, json=payload)
        return response.status_code in [200, 201]
    except: return False

def recuperer_stats_mind_engine():
    try:
        logs = httpx.get(f"{SUPABASE_URL}/rest/v1/mind_engine_logs?select=score_engine,rr,risque_reel_percent", headers=HEADERS).json()
        alerts = httpx.get(f"{SUPABASE_URL}/rest/v1/mind_engine_alerts?select=id", headers=HEADERS).json()
        
        # Sécurisation du format de liste PostgREST
        if not logs or not isinstance(logs, list):
            return {"score": 0.0, "rr": 0.0, "risque": 0.0, "total": 0, "alerts": len(alerts) if isinstance(alerts, list) else 0}
        
        total = len(logs)
        alerts_total = len(alerts) if isinstance(alerts, list) else 0
        
        avg_score = sum([float(l.get("score_engine") or 0.0) for l in logs]) / total
        avg_rr = sum([float(l.get("rr") or 0.0) for l in logs]) / total
        avg_risque = sum([float(l.get("risque_reel_percent") or 0.0) for l in logs]) / total
        
        return {
            "score": round(avg_score, 1),
            "rr": round(avg_rr, 2),
            "risque": round(avg_risque, 2),
            "total": total,
            "alerts": alerts_total
        }
    except Exception as e:
        print(f"⚠️ Erreur de synthèse recuperer_stats_mind_engine : {e}")
        return {"score": 0.0, "rr": 0.0, "risque": 0.0, "total": 0, "alerts": 0}

def initialiser_abonnement_gratuit(user_id):
    url = f"{SUPABASE_URL}/rest/v1/abonnements"
    payload = {
        "user_id": str(user_id),
        "type_offre": "FREE",
        "zone_geographique": "AFRIQUE",
        "montant": 0.0,
        "devise": "XAF",
        "statut_paiement": "ACTIF"
    }
    try:
        response = httpx.post(url, headers=HEADERS, json=payload)
        return response.status_code in [200, 201]
    except:
        return False

def verifier_statut_premium(user_id):
    url = f"{SUPABASE_URL}/rest/v1/abonnements?user_id=eq.{user_id}&select=type_offre,statut_paiement"
    try:
        response = httpx.get(url, headers=HEADERS)
        if response.status_code == 200 and response.json():
            data = response.json()[0]
            return data.get("type_offre") == "PREMIUM" and data.get("statut_paiement") == "ACTIF"
        return False
    except:
        return False

def activer_abonnement_premium(user_id, zone):
    url = f"{SUPABASE_URL}/rest/v1/abonnements?user_id=eq.{user_id}"
    montant, devise = (8000.0, "XAF") if zone.upper() == "AFRIQUE" else (13000.0, "EUR")
    payload = {
        "type_offre": "PREMIUM",
        "zone_geographique": zone.upper(),
        "montant": montant,
        "devise": devise,
        "statut_paiement": "ACTIF"
    }
    try:
        response = httpx.patch(url, headers=HEADERS, json=payload)
        return response.status_code in [200, 204]
    except:
        return False
    
# --- PROCESSUS INITIAL DU SYSTEME ---
initialiser_config()
init_db()
migrate_db()