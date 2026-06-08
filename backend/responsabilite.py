import customtkinter as ctk
from tkinter import messagebox
import json
import os
import datetime
import requests
import time
import xml.etree.ElementTree as ET

CONFIG_FILE = "mentor_config.json"

def charger_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"disclaimer_accepted": False, "date_acceptation": None}

def sauvegarder_acceptation():
    config = {
        "disclaimer_accepted": True, 
        "date_acceptation": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

# --- LA POPUP DE DEPART (BLOQUANTE) ---
def verifier_disclaimer(root_callback):
    config = charger_config()
    
    # Si déjà accepté, on lance directement l'application principale
    if config.get("disclaimer_accepted"):
        root_callback()
        return

    # Création de la fenêtre de contrat
    top = ctk.CTk()
    top.title("CONTRAT D'UTILISATION & RESPONSABILITÉ - MentorIA")
    top.geometry("600x650")
    top.resizable(False, False)

    # Titre principal
    ctk.CTkLabel(top, text="⚖️ CLAUSES DE RESPONSABILITÉ", font=("Arial", 20, "bold")).pack(pady=15)
    
    # Zone de texte avec le contenu légal complet
    texte_legal = """
    ⚖️ CLAUSES DE RESPONSABILITÉ & CONFIDENTIALITÉ
    1. Nature du Service (Définition et Limites)

    L’utilisateur reconnaît expressément que "Trade MIND" est un outil pédagogique d’aide à la réflexion et à la structuration d’un raisonnement en trading, basé sur l’utilisation d’algorithmes d’intelligence artificielle.

    À ce titre :

    PAS UN CONSEILLER FINANCIER :
    "Trade MIND" ne fournit aucun conseil en investissement au sens des autorités de régulation financière. Aucune recommandation personnalisée d’achat ou de vente n’est délivrée.
    
    PAS UN FOURNISSEUR DE SIGNAUX :
    L’application ne génère aucun signal de trading. Elle se limite à analyser et auditer la cohérence d’un plan soumis par l’utilisateur.
    
    PAS UN SYSTÈME D’EXÉCUTION :
    "Trade MIND" n’exécute aucune transaction, n’interagit pas avec des marchés financiers, et ne garantit en aucun cas une performance ou une rentabilité.
    
    2. Limitation de Responsabilité

    L’utilisateur reconnaît être l’unique décisionnaire de ses actions de trading et assume pleinement les risques associés.

    Absence de garantie :
    Les données utilisées (via APIs tierces telles que Polygon, NewsAPI, etc.) peuvent contenir des erreurs, retards ou approximations.
    De même, les analyses générées par l’IA sont basées sur des modèles probabilistes et ne constituent en aucun cas une vérité absolue.
    
    Risque de perte en capital :
    Le trading comporte un risque élevé de perte financière.
    En aucun cas le développeur ou le projet "Trade MIND" ne pourront être tenus responsables de pertes, directes ou indirectes, résultant de l’utilisation de l’outil.
    
    Utilisation inappropriée :
    Toute utilisation détournée de l’application (automatisation non prévue, reverse-engineering, ou interprétation des analyses comme des certitudes) annule immédiatement toute responsabilité du concepteur.
    
    3. Confidentialité & Traitement des Données
    
    Traitement des analyses :
    Les données saisies par l’utilisateur (analyses, réponses, etc.) peuvent être transmises à des services tiers (ex : API d’intelligence artificielle) uniquement dans le cadre du traitement fonctionnel de l’application.
    Elles ne sont pas exploitées à des fins commerciales par "Trade MIND".
    
    Clés API :
    L’utilisateur est responsable de la gestion et de la sécurité de ses propres clés API s’il en configure dans l’application.
    
    Respect de la vie privée :
    Aucune donnée personnelle identifiable n’est vendue, cédée ou partagée avec des tiers.
    
    4. Acceptation des Conditions

    En utilisant "Trade MIND", l’utilisateur reconnaît avoir lu, compris et accepté l’ensemble des présentes clauses.
    Il accepte notamment que l’outil soit utilisé uniquement comme support pédagogique et non comme système de prise de décision autonome.
    
    """

    textbox = ctk.CTkTextbox(top, width=540, height=350, font=("Arial", 12))
    textbox.insert("0.0", texte_legal)
    textbox.configure(state="disabled") # Empêche la modification du texte
    textbox.pack(pady=10, padx=20)

    # Case à cocher obligatoire
    check_var = ctk.StringVar(value="off")
    checkbox = ctk.CTkCheckBox(
        top, 
        text="J'accepte les risques et les conditions d'utilisation", 
        variable=check_var, 
        onvalue="on", 
        offvalue="off",
        font=("Arial", 12, "bold")
    )
    checkbox.pack(pady=15)

    def on_accept():
        if check_var.get() == "on":
            sauvegarder_acceptation()
            top.destroy()
            root_callback() # Lance la classe MentorApp
        else:
            messagebox.showwarning("Action requise", "Veuillez cocher la case d'acceptation pour continuer.")

    # Bouton de validation
    btn_access = ctk.CTkButton(
        top, 
        text="ACCÉDER À MENTORIA", 
        command=on_accept,
        fg_color="#2ecc71", 
        hover_color="#27ae60",
        font=("Arial", 14, "bold")
    )
    btn_access.pack(pady=10)

    # Si l'utilisateur ferme la fenêtre sans accepter, on quitte tout
    top.protocol("WM_DELETE_WINDOW", lambda: exit())
    
    top.mainloop()


# --- L'INTERFACE PRINCIPALE ---
class MentorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("MentorIA PRO - Risk Management")
        self.geometry("1100x700")
        
        # Initialisation du Hub de données
        # self.market_guard = MarketGuard(POLYGON_API_KEY) 
        
        self.setup_ui()

    def setup_ui(self):
        # Ici on placera tes onglets et ton bouton "Analyser"
        ctk.CTkLabel(self, text="Bienvenue dans MentorIA", font=("Arial", 24)).pack(pady=50)
        
        # Bouton Paramètres pour voir le statut legal
        ctk.CTkButton(self, text="Paramètres", command=self.afficher_legal).pack()

    def afficher_legal(self):
        # La vue qu'on a codée juste avant
        print("Affichage de la clause de responsabilité...")

# --- LANCEMENT ---
if __name__ == "__responsabilite__":
    # On vérifie le contrat AVANT de lancer la classe principale
    verifier_disclaimer(lambda: MentorApp().mainloop())        