import email
from turtle import reset
import customtkinter as ctk
import json
import datetime
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import re
from openai import OpenAI
import requests
from tkinter import NO, filedialog
import PIL.Image
import webbrowser 
import pytz 
from fpdf import FPDF
from tkinter import filedialog 
from tkinter import messagebox, filedialog 
import sqlite3 
import hashlib
import cv2 
from PIL import Image 
import PIL.Image
import os
import backend.database as database 
import backend.mentor_ia as mentor_ia 
import backend.tools_stats as tools_stats 
import backend.media_manager as media_manager 
import backend.Logic as Logic 
import backend.Dashboard as Dashboard
from backend.MindEngine import MindEngine
from backend.savoir import SavoirView
from backend.licence_manager import LicenceManager 
import backend.responsabilite as responsabilite
import turtle 
import logging 

ctk.set_appearance_mode("dark")  

BG = "#0B0E14"
CARD = "#151921"
ACCENT = "#08090A"
ACCENT_COLOR = "#007AFF"
TEXT_MAIN = "#FFFFFF"
TEXT_SUB = "#70778C"
couleur =  "#2B2B2B"


# ==== APP ====

app = ctk.CTk() 
app.geometry("1100x720")
app.title("Trade Mind")

top_bar = ctk.CTkFrame(app, fg_color=CARD, height=50, corner_radius=0) 
turtle.setup(width=0, height=0) # Initialise mais cache
turtle.hideturtle()

class TradeMindApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- CONFIGURATION GLOBALE (La mémoire de l'app) ---
        self.user_settings = {
            "style": "Day Trading",
            "objectif": "Croissance",
            "niveau": "Intermédiaire", 
            "marche": "Forex",
            "notif_analyses": True,
            "notif_objectifs": False,
            "notif_motivation": True,
            "notif_resume": False,
            "taille_texte": 14,
            "ia_severite": "Neutre", # Priorité sur le doublon
            "ia_active": True,
            "risque_max": 1.0,
            "rr_min": 2.0,
            "theme": "Dark"

        }
        self.charger_donnees_sql()
        
       
        self.title("Trading Mind Pro")
        self.geometry("1200x800")
        self.media_manager = media_manager # On crée une instance de media_manager pour accéder à ses fonctions
        self.tools_stats = tools_stats # Idem pour tools_stats, notamment pour la fonction d'export PDF
        self.licence_mgr = LicenceManager(self) # On connecte le manager à l'app
        self.engine = MindEngine()
        self.question_label = None
        self.statut_var = ctk.StringVar(value="Brouillon")
        self.position_var = ctk.StringVar(value="Neutre")
        database.initialiser_config()
        params_sauvegardes = database.charger_parametres()
    
        # On écrase les valeurs par défaut par celles de la base de données
        if "risque_max" in params_sauvegardes:
            self.user_settings["risque_max"] = float(params_sauvegardes["risque_max"])

        if "rr_min" in params_sauvegardes:
            self.user_settings["rr_min"] = float(params_sauvegardes["rr_min"])

        if "ia_severite" in params_sauvegardes:
            self.user_settings["ia_severite"] = params_sauvegardes["ia_severite"]
        
        # 2. IMPORTS ET MODULES
        self.detail = None
        self.txt_savoir = None
        self.delete = None
        self.ent_risk_glob = None
        self.ent_rr_glob = None
        self.seg_ia_glob = None
        self.frame_list = None
        self.right_frame = None
        self.left_frame = None
        self.buttons_menu = None
        self.btn_save = None
        self.btn_profil = None
        self.btn_reset = None
        self.retour = None
        self.btn_calc = None
        self.btn_delete = None
        self.entry_recherche = None
        self.btn_parametres = None
        self.btn_stats = None
        self.slider_conviction = None
        self.entry_actif = None
        self.entry_biais = None
        self.texte_analyse = None
        self.btn_biblio = None
        self.btn_txt = None
        self.frame_actions = None
        self.texte_reponse_ia = None
        self.main_container = None
        self.btn_ia = None
        self.frame_score = None
        self.historique_frame = None
        self.ia_feedback_area = None
        self.trade_en_cours_id = None
        
        self.logo_img = None
        self.template = None
        self.btn_export = None
        self.guide_expert_contenu = None
        self.guide_etudiant_contenu = None
        self.login_frame = None
        self.menu_frame = None
        self.outils_frame = None
        self.profil_frame = None
        self.parametre_frame = None
        self.top_bar = None # Initialisé à None, sera créé dans setup_ui
        self.menu_buttons = None
        self.menu_marche = None
        self.menu_obj = None
        self.menu_style = None
        self.menu_niveau = None
        self.analyse_frame = None
        self.frame_opt = None
        self.savoir_frame = None
        self.mode_menu = None
        self.mode = "Étudiant"
        self.guide_texte = None
        self.savoir_contenu = None
        self.info_sl_tp = "Non défini"
        self.raisonnement_user = "Non défini"
        self.analyse_en_cours = ""
        self.trade_actif = False
        self.plan_synthetise = ""  # Le contrat que l'IA 2 va protéger
        self.historique_chat_guardian = [] # Pour que l'IA 2 se souvienne de la discussion
        # États possibles : "verrouillé", "actif", "validé", "partiel", "incorrect"
        self.etats_progression = ["actif", "verrouillé", "verrouillé", "verrouillé"]

   
        
        
        # --- LOGIQUE D'ANALYSE STEP-BY-STEP (V5.2) ---
        self.current_step = 0
        self.etapes_analyse = [
            {
                "id": "macro", 
                "titre": "🌍 MACRO", 
                "questions": [
                
                    "1 - Sentiment global : Risk-on (appétit) ou Risk-off (peur)"
                    "→ Justification obligatoire basée sur des éléments concrets (indices, flux, news)."
                    "→ ⚠️ Une réponse sans justification = invalide.",

                    "2 - Rendements (Yields) : Que fait le rendement de référence (ex: US02Y/GB10Y/...) ?"
                    "→ Direction claire : hausse / baisse / stagnation."
                    "→ Impact direct sur la devise analysée."
                    "→ ⚠️ Si non relié à ton biais → incohérence macro.",

                    "3 - Différentiel de taux : Quelle devise a le taux d’intérêt et la politique monétaire les plus attractifs ? Justifiez votre réponse."
                    "→ Comparaison OBLIGATOIRE entre les deux devises de la paire."
                    "→ ⚠️ Si aucune dominance claire → biais fragile.",

                    "4 - Inflation & Emploi : Selon les dernières news, quelle économie est la plus forte ? Justifiez votre réponse."
                    "→ Basé uniquement sur données récentes (pas d’hypothèse)."
                    "→ ⚠️ Si contradiction avec le biais → incohérence critique.",

                    "5 - Événement à venir ?"
                    "→ Identifier les news importantes (high impact)."
                    "→ ⚠️ Si événement imminent non pris en compte → erreur de gestion.",

                    "🔎 Conclusion partielle 1"

                    "Rédigez une conclusion incluant la devise soutenue par la macroéconomie et le différentiel de taux sur le long terme."

                    "→ Une seule devise doit ressortir clairement dominante."
                    "→ ⚠️ Si conclusion neutre ou hésitante → pas de direction exploitable → trade interdit.",
                ]
            },
            {
                "id": "contexte", 
                "titre": "🗺️ CONTEXTE", 
                "questions": [
                    "1 - Situation du marché : Selon la paire analysée, qu’observe-t-on actuellement sur le marché forex ?"
                    "→ Décrire un contexte clair (tendance, incertitude, compression…)."
                    "→ ⚠️ Réponse vague = analyse invalide.",

                    "2 - Géopolitique : Quel est le contexte géopolitique actuel ?"
                    "→ Identifier si cela soutient ou affaiblit une devise."
                    "→ ⚠️ Ignorer ce facteur = vision incomplète.",

                    "3 - Corrélations : Y a-t-il des corrélations fortes avec d'autres marchés (indices, matières premières, autres devises) ?"
                    "→ Exemple : USD / Or / Indices / pétrole…"
                    "→ ⚠️ Si corrélations ignorées → analyse partielle.",

                    "🔎 Conclusion partielle 2"

                    "Rédigez une conclusion précisant quelle devise est soutenue par le contexte."

                    "→ Doit confirmer ou invalider la conclusion macro."
                    "→ ⚠️ Si contradiction entre macro et contexte → signal faible → prudence ou abstention.",
                ]
            },
            {
                "id": "technique", 
                "titre": "📊 TECHNIQUE", 
                "questions": [
                    "1 - Structure : Quelle est la tendance sur l’unité de temps supérieure ? Y a-t-il un range ?"
                    "→ Doit être clairement définie (pas d’ambiguïté)."
                    "→ ⚠️ Pas de structure claire = pas de trade.",

                    "2 - Momentum : Les bougies montrent-elles de la force (impulsion) ou de l’hésitation ?"
                    "→ Justifier avec comportement du prix."
                    "→ ⚠️ Momentum faible = entrée risquée.",

                    "3 - Zones institutionnelles & Zones clés : Sommes-nous dans un Order Block ou un Fair Value Gap ? Y a-t-il un support et une résistance ?"
                    "→ La zone doit être identifiée ET cohérente avec le biais."
                    "→ ⚠️ Zone mal définie = SL fragile.",

                    "4 - Liquidité : Le marché a-t-il déjà “nettoyé” les sommets/bas précédents avant mon entrée ?"
                    "→ Réponse claire : Oui / Non + justification."
                    "→ ⚠️ Si non → risque de sweep contre ta position.",
                ]
            },
            {
                "id": "risque", 
                "titre": "🛡️ RISQUE", 
                "questions": [                   
                    "1 - Pourquoi j’entre maintenant ?"
                    "→ Timing précis (pas de réponse vague)."
                    "→ ⚠️ “Parce que ça monte” = invalide.",

                    "2 - Où est mon stop loss de sécurité ?"
                    "→ Doit correspondre à une invalidation logique du scénario."
                    "→ ⚠️ SL arbitraire = erreur critique.",

                    "3 - Quel est mon ratio Risque/Récompense (RR) ? (Minimum 1:2 conseillé.)"
                    "→ Calcul réel obligatoire."
                    "→ ⚠️ RR < 1:2 = trade refusé automatiquement.",

                    "4 - Confirmation ? (oui/non)"
                    "→ Basée sur structure + liquidité + timing."
                    "→ ⚠️ Si NON → trade non validé.",
                    
                ]
            }
        ]
        
        # Dictionnaire pour stocker les textes de chaque étape en cours de saisie
        self.reponses_temporaires = {e["id"]: "" for e in self.etapes_analyse}
        # À ajouter dans votre setup_ui ou __init__
        self.savoir_frame = SavoirView(
            master=self.main_container, 
            back_command=lambda: self.show_frame("menu_principal")
)

        # 3. LANCEMENT DE L'INTERFACE (MAINTENANT QUE TOUT EST PRÊT)
        self.setup_ui()
        # Lancer la base au démarrage
        database.init_db()

    def charger_donnees_sql(self):
        try:
            import backend.database as database
            data_recuperee = database.charger_parametres()
            if data_recuperee:
                # On met à jour notre dictionnaire interne avec les vraies valeurs SQL
                for cle, valeur in data_recuperee.items():
                    # Conversion des booléens (SQLite stocke souvent en string ou int)
                    if valeur in ["True", "False", 1, 0, "1", "0"]:
                        self.user_settings[cle] = str(valeur).lower() in ["true", "1"]
                    else:
                        self.user_settings[cle] = valeur
                print("✅ RAM synchronisée avec le SQL au démarrage.")
        except Exception as e:
            print(f"⚠️ Erreur de chargement SQL : {e}")

    def show_frame(self, frame_cible):
        """Protocole de réinitialisation totale du conteneur - Version Omnisciente avec Mémoire"""
        print(f"🔥 [WARP] Transition vers : {frame_cible}")

        # --- ÉTAPE 0 : SAUVEGARDE VOLATILE (Le Fix Sécurisé) ---
        # On vérifie : 1. Si l'attribut existe, 2. S'il n'est pas None, 3. S'il existe dans l'interface
        if hasattr(self, 'texte_analyse') and self.texte_analyse is not None:
            try:
                if self.texte_analyse.winfo_exists():
                    self.temp_analyse_buffer = self.texte_analyse.get("1.0", "end-1c")
                    self.temp_actif_buffer = self.entry_actif.get()
                    print("💾 [MEM] Analyse mise en mémoire tampon.")
            except:
                # Au cas où le widget est en cours de destruction, on ignore pour éviter le crash
                pass

        # 1. PURGE RADICALE : Nettoyage du conteneur principal
        for widget in self.main_container.winfo_children():
            widget.destroy()

        # 2. ISOLATION : Création de la nouvelle surface de travail
        surface_neuve = ctk.CTkFrame(self.main_container, fg_color="#0B0E14")
        surface_neuve.pack(fill="both", expand=True)

        # 3. ROUTAGE PAR INJECTION : Branchement vers les fonctions de construction
        if frame_cible == "menu_principal":
            self.menu_principal = surface_neuve
            self.creer_menu()

        elif frame_cible == "analyse_frame":
            self.analyse_frame = surface_neuve
            self.creer_analyse()
            
            # --- RÉINJECTION DE LA MÉMOIRE ---
            # Si on revient sur l'analyse et qu'on a un buffer, on le remet
            if hasattr(self, 'temp_analyse_buffer'):
                self.texte_analyse.insert("1.0", self.temp_analyse_buffer)
                self.entry_actif.delete(0, "end")
                self.entry_actif.insert(0, self.temp_actif_buffer)
                print("🧠 [MEM] Analyse restaurée avec succès.")

        elif frame_cible == "historique_frame":
            self.historique_frame = surface_neuve
            self.creer_historique() 

        elif frame_cible == "outils_frame":
            self.outils_frame = surface_neuve
            self.ouvrir_outils()

        elif frame_cible == "bibliotheque_frame":
            self.savoir_view = SavoirView(
                master=surface_neuve, 
                back_command=lambda: self.show_frame("menu_principal"),
                fg_color="transparent"
            )
            self.savoir_view.pack(fill="both", expand=True)

        elif frame_cible == "parametre_frame":
            self.parametre_frame = surface_neuve
            self.ouvrir_parametres()

        elif frame_cible == "mind_frame":
            self.mind_dashboard = Dashboard.MindEngineDashboard(
                master=surface_neuve, 
                back_command=lambda: self.show_frame("menu_principal")
            )
            self.mind_dashboard.pack(fill="both", expand=True)
            print("🔥 [WARP] Mind Engine Dashboard activé (Mode Autonome)")

        # 4. FORÇAGE DU RENDU
        self.update_idletasks()
        self.main_container.update()
        print(f"✅ Injection terminée pour : {frame_cible}")
       
        
    def verifier_login(self, email, password):
        # --- 1. CONNEXION BDD ---
        try:
            conn = sqlite3.connect("trademind_pro.db")
            cursor = conn.cursor()
            # On utilise ta fonction de cryptage pour comparer les hashs
            cursor.execute("SELECT * FROM users WHERE email=? AND password=?", 
                        (email, database.crypter_password(password)))
            user = cursor.fetchone()
            conn.close()
        except Exception as e:
            messagebox.showerror("Erreur BDD", f"Impossible de vérifier les identifiants : {e}")
            return

        # --- 2. TRAITEMENT DU RÉSULTAT ---
        if user: 
            # On stocke l'ID utilisateur pour les futures requêtes (optionnel mais utile)
            self.current_user_id = user[0]

            # NETTOYAGE : On retire l'écran de login mis avec .place()
            if hasattr(self, 'login_frame'):
                self.login_frame.place_forget()

            # On affiche le conteneur principal
            self.main_container.pack(side="bottom", fill="both", expand=True)
            # AFFICHAGE DE LA STRUCTURE :
            # On ne recrée pas la top_bar, on affiche celle qui existe déjà (créée dans setup_ui)
            if hasattr(self, 'top_bar'):
                self.top_bar.pack(side="top", fill="x")

            # On affiche le conteneur principal qui contient le menu et le dashboard
            if hasattr(self, 'main_container'):
                self.main_container.pack(side="bottom", fill="both", expand=True)

            # NAVIGATION : On lance enfin l'affichage du menu
            self.show_frame(self.menu_frame)
            
        else:
            # Échec de connexion
            messagebox.showerror("Accès refusé", "Identifiants ou mot de passe incorrects.")

    def enregistrer_utilisateur(self, email, password):
        """Crée la table si elle n'existe pas et enregistre le nouvel utilisateur"""
        if not email or not password:
            messagebox.showwarning("Champs vides", "Remplissez l'email et le mot de passe.")
            return
            
        try:
            conn = sqlite3.connect("trademind_pro.db")
            cursor = conn.cursor()
            
            # SÉCURITÉ : On s'assure que la table existe (Règle le message 'no table user')
            cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                            email TEXT UNIQUE, 
                            password TEXT)''')
            
            # Hachage du mot de passe via ton module database
            pwd_crypte = database.crypter_password(password)
            
            try:
                cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, pwd_crypte))
                conn.commit()
                messagebox.showinfo("Succès", "Compte créé ! Vous pouvez maintenant vous connecter.")
            except sqlite3.IntegrityError:
                messagebox.showerror("Erreur", "Cet email est déjà enregistré.")
                
            conn.close()
        except Exception as e:
            messagebox.showerror("Erreur BDD", f"Erreur technique : {e}")

    def setup_ui(self):
        """Initialise l'interface, le menu et gère le login"""
        
        # Couleurs de ton thème
        CARD_COLOR = getattr(self, 'CARD', "#1C222D")

        # 1. TOP BAR (Fixe pour toute l'application)
        self.top_bar = ctk.CTkFrame(self, height=50, fg_color=CARD_COLOR, corner_radius=0)
        self.top_bar.pack(side="top", fill="x")

        self.btn_profil = ctk.CTkButton(self.top_bar, text="👤", width=40, fg_color="transparent") 
        self.btn_profil.pack(side="right", padx=15, pady=5)

        # 2. CONTENEUR MAÎTRE (Où les frames vont s'afficher)
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(side="top", fill="both", expand=True)

        # --- ERREUR CORRIGÉE ICI ---
        # On ne pack pas le Capital ici ! 
        # Il appartient au MindEngineDashboard.py que nous avons codé ensemble.
        
        # 3. AFFICHAGE DU MENU (Charge le frame par défaut)
        self.show_frame("menu_principal")
        
        # 4. ÉCRAN DE LOGIN
        if hasattr(self, 'login_frame') and self.login_frame:
            self.login_frame.tkraise()
            
    # --- ÉCRAN LOGIN (AVEC LOGO AGRANDI) ---
    def login_ui(self):
        # --- 1. NETTOYAGE ---
        for widget in self.login_frame.winfo_children():
            widget.destroy()

        # --- 2. GESTION DU LOGO & TITRE ---
        logo_reussi = False
        try:
            current_path = os.path.dirname(os.path.abspath(__file__))
            logo_path = os.path.join(current_path, "logo.jpg")
            
            if os.path.exists(logo_path):
                raw_img = Image.open(logo_path)
                # On stocke l'image dans self pour la survie en mémoire
                self.logo_img = ctk.CTkImage(light_image=raw_img, dark_image=raw_img, size=(120, 120))
                
                logo_label = ctk.CTkLabel(self.login_frame, image=self.logo_img, text="")
                # ANCRE CRITIQUE : Empêche le bug "pyimage2"
                logo_label.image = self.logo_img 
                logo_label.pack(pady=(30, 10))
                logo_reussi = True
        except Exception as e:
            print(f"DEBUG: Erreur logo (basculement texte) : {e}")

        # --- 3. TITRE (Conditionnel pour éviter les doublons) ---
        if not logo_reussi:
            # Si pas de logo, on met un gros titre pour combler l'espace
            ctk.CTkLabel(self.login_frame, text="TRADE MIND", 
                        font=("Inter", 35, "bold"), 
                        text_color=ACCENT).pack(pady=(50, 5))
        else:
            # Si logo présent, on met le titre juste en dessous plus petit ou standard
            ctk.CTkLabel(self.login_frame, text="TRADE MIND", 
                        font=("Inter", 30, "bold"), 
                        text_color=ACCENT).pack()

        ctk.CTkLabel(self.login_frame, text="CONNEXION SÉCURISÉE", 
                    font=("Inter", 12), text_color=TEXT_SUB).pack(pady=(0, 30))

        # --- 4. CHAMPS DE SAISIE ---
        self.email_ent = ctk.CTkEntry(self.login_frame, placeholder_text="Email", width=320, height=45)
        self.email_ent.pack(pady=10)
        
        self.pass_ent = ctk.CTkEntry(self.login_frame, placeholder_text="Mot de passe", show="*", width=320, height=45)
        self.pass_ent.pack(pady=10)

        # --- 5. BOUTON DE CONNEXION ---
        ctk.CTkButton(
            self.login_frame, 
            text="SE CONNECTER", 
            width=320, height=50, 
            font=("Inter", 15, "bold"),
            fg_color=ACCENT,
            hover_color="#2980b9",
            command=lambda: self.verifier_login(self.email_ent.get(), self.pass_ent.get())
        ).pack(pady=(25, 10))

        # --- 6. BOUTON D'INSCRIPTION ---
        ctk.CTkButton(
            self.login_frame, 
            text="Créer un nouveau compte", 
            fg_color="transparent", 
            text_color=ACCENT,
            hover_color="#f0f0f0", # Ou une couleur sombre si tu es en mode Dark
            command=lambda: self.enregistrer_utilisateur(self.email_ent.get(), self.pass_ent.get()) 
        ).pack()
        
    def ouvrir_outils(self):
        """Nettoie et construit la vue outils - Version Dashboard Pro"""
        for w in self.outils_frame.winfo_children():
            w.destroy()
            
        # --- CONFIG STYLE ---
        ACCENT_OUTILS = "#3498db"
        BG_CARD = "#151921"
        BORDER_COLOR = "#2C3E50"

        # Header
        header_frame = ctk.CTkFrame(self.outils_frame, fg_color="Black")
        header_frame.pack(pady=(30, 20), fill="x")

        ctk.CTkLabel(header_frame, text="🚀 RESSOURCES INSTITUTIONNELLES", 
                    font=("Inter", 28, "bold"), text_color=ACCENT_OUTILS).pack()
        ctk.CTkLabel(header_frame, text="Données flux tendu et analyses macro-économiques de rang A.", 
                    font=("Inter", 13, "italic"), text_color="#7F8C8D").pack()

        # Conteneur principal scrollable
        scroll_container = ctk.CTkScrollableFrame(self.outils_frame, fg_color="Black", border_width=0)
        scroll_container.pack(pady=10, padx=40, fill="both", expand=True)

        # Utilitaire pour créer des "Sections" proprement
        def creer_section(parent, titre, icone):
            section_frame = ctk.CTkFrame(parent, fg_color="transparent")
            section_frame.pack(fill="x", pady=15)
            ctk.CTkLabel(section_frame, text=f"{icone} {titre}", 
                        font=("Inter", 18, "bold"), text_color=ACCENT_OUTILS).pack(anchor="w", padx=10)
            ctk.CTkFrame(section_frame, fg_color=BORDER_COLOR, height=1).pack(fill="x", pady=5)
            return section_frame

        # --- CATEGORIE 1 : DIRECT & NEWS ---
        news_section = creer_section(scroll_container, "FLUX DIRECT & ACTUALITÉS", "📺")
        
        # Grid pour les boutons News (2 par ligne)
        grid_news = ctk.CTkFrame(news_section, fg_color="transparent")
        grid_news.pack(fill="x")
        grid_news.grid_columnconfigure((0, 1), weight=1, pad=10)

        # Bouton Live (Rouge Alerte)
        ctk.CTkButton(grid_news, text="🔴 InvestingLive\n(Vidéo & Audio)", 
                    fg_color="#D32F2F", hover_color="#B71C1C", height=60, font=("Inter", 12, "bold"),
                    command=lambda: webbrowser.open("https://fr.investing.com/live-video/")).grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        ctk.CTkButton(grid_news, text="📰 Investing.com\n(Portail Global)", 
                    fg_color=BG_CARD, border_width=1, border_color=BORDER_COLOR, height=60,
                    command=lambda: webbrowser.open("https://fr.investing.com/")).grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        ctk.CTkButton(grid_news, text="📉 Bloomberg Markets\n(Flux Pro)", 
                    fg_color=BG_CARD, border_width=1, border_color=BORDER_COLOR, height=50,
                    command=lambda: webbrowser.open("https://www.bloomberg.com/markets")).grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        # --- CATEGORIE 2 : ANALYSE & MACRO ---
        macro_section = creer_section(scroll_container, "ANALYSE FONDAMENTALE", "🧠")
        
        btns_macro = [
            ("📅 Forex Factory", "Calendrier Économique", "https://www.forexfactory.com/calendar"),
            ("🏦 CME FedWatch", "Prévisions Taux US", "https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html"),
            ("🌍 Trading Economics", "Statistiques Mondiales", "https://tradingeconomics.com")
        ]

        for titre, desc, url in btns_macro:
            f = ctk.CTkFrame(macro_section, fg_color=BG_CARD, height=55, border_width=1, border_color=BORDER_COLOR)
            f.pack(fill="x", pady=3)
            f.pack_propagate(False)
            
            ctk.CTkLabel(f, text=titre, font=("Inter", 13, "bold")).pack(side="left", padx=15)
            ctk.CTkLabel(f, text=f"|  {desc}", font=("Inter", 11), text_color="#7F8C8D").pack(side="left")
            
            ctk.CTkButton(f, text="OUVRIR 🔗", width=80, height=28, fg_color=ACCENT_OUTILS, font=("Inter", 10, "bold"),
                        command=lambda u=url: webbrowser.open(u)).pack(side="right", padx=10)

        # --- CATEGORIE 3 : SENTIMENT ---
        sent_section = creer_section(scroll_container, "SENTIMENT DE MARCHÉ", "📊")
        
        grid_sent = ctk.CTkFrame(sent_section, fg_color="transparent")
        grid_sent.pack(fill="x")
        grid_sent.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(grid_sent, text="📈 TradingView\n(Charting)", 
                    fg_color=BG_CARD, border_width=1, border_color=BORDER_COLOR, height=70,
                    command=lambda: webbrowser.open("https://www.tradingview.com")).grid(row=0, column=0, sticky="ew", padx=5)
        
        ctk.CTkButton(grid_sent, text="😨 Fear & Greed\n(CNN Index)", 
                    fg_color=BG_CARD, border_width=1, border_color=BORDER_COLOR, height=70,
                    command=lambda: webbrowser.open("https://edition.cnn.com/markets/fear-and-greed")).grid(row=0, column=1, sticky="ew", padx=5)

        # Bouton Retour (En bas, fixe)
        ctk.CTkButton(self.outils_frame, text="⬅ RETOUR AU MENU", 
              command=lambda: self.show_frame("menu_principal")).pack(pady=25)

    def sauvegarde(self):
        print("\n--- [SYNCHRONISATION SQL FORCEE] ---")
        try:
            # 1. Récupération de l'actif
            actif = getattr(self, 'entry_actif', None)
            actif_val = actif.get().strip() if actif else "Inconnu"
            
            # 2. Capture de la CONVICTION
            try:
                valeur_conviction = int(self.slider_conviction.get())
            except:
                valeur_conviction = 50

            # 3. LE MODE (C'est ta balise GPS pour l'historique)
            mode_actuel = getattr(self, 'mode', 'Étudiant')
            if not mode_actuel: mode_actuel = "Étudiant"

           # 4. CAPTURE DU TEXTE (Priorité Suivi IA)
            analyse_texte = "Aucune analyse saisie"
            texte_suivi = self.guide_texte.get("1.0", "end-1c").strip() if hasattr(self, 'guide_texte') else ""
            texte_classique = self.texte_analyse.get("1.0", "end-1c").strip() if hasattr(self, 'texte_analyse') else ""

            if mode_actuel == "Suivi IA":
                analyse_texte = texte_suivi if len(texte_suivi) > 5 else "Analyse Suivi IA vide"
            else:
                analyse_texte = texte_classique if len(texte_classique) > 5 else "Analyse classique vide"

            # 5. Récupération du Plan et du Statut
            plan_final = getattr(self, 'plan_synthetise', "Plan non généré")
            statut_actuel = self.statut_var.get()

            # --- [NOUVEAU] LOGIQUE AUDITEUR FINAL ---
            # On initialise le feedback par défaut
            feedback_final = "Pas de feedback"

            # Si le trade est terminé (WIN ou LOSS), on demande le verdict à l'IA
            if statut_actuel.upper() in ["WIN", "LOSS"]:
                print(f"🧠 {statut_actuel} détecté. Appel de l'Auditeur Final...")
                
                # On récupère le prix de clôture si le champ existe
                prix_cloture = getattr(self, 'entry_prix_cloture', None)
                prix_val = prix_cloture.get() if prix_cloture else "Non spécifié"

                # Appel de l'IA (On utilise ton instance mentor_ia)
                # On passe l'analyse, les logs (optionnel ici), le résultat et le prix
                
                verdict = mentor_ia.generer_verdict_final_ia(
                    analyse_texte, 
                    "Analyse de discipline en cours...", 
                    statut_actuel, 
                    prix_val
                )
                
                feedback_final = verdict

                # Mise à jour visuelle immédiate dans la Textbox de l'IA
                if hasattr(self, 'texte_reponse_ia'):
                    self.texte_reponse_ia.configure(state="normal")
                    self.texte_reponse_ia.delete("1.0", "end")
                    self.texte_reponse_ia.insert("1.0", verdict)
                    self.texte_reponse_ia.configure(state="disabled")

            import backend.database as database
            
            # 6. APPEL SQL (On injecte feedback_final au lieu de "Pas de feedback")
            succes = database.sauvegarder_trade_final(
                actif_val,                      # 1. actif
                mode_actuel,                    # 2. biais
                valeur_conviction,              # 3. conviction
                0,                              # 4. score_ia
                analyse_texte,                  # 5. analyse
                feedback_final,                 # 6. feedback (Contient le Verdict IA)
                statut_actuel,                  # 7. statut
                self.position_var.get(),        # 8. position
                plan_final                      # 9. plan
            )

            if succes: 
                print(f"✅ Trade {succes} scellé [Mode: {mode_actuel}] avec Verdict IA.")
                
                self.trades = database.recuperer_tout_historique() 
                
                def rafraichir_et_partir():
                    try:
                        # On récupère le widget de manière sécurisée
                        f_list = getattr(self, 'frame_list', None)
                        
                        # Si le widget existe et est affiché, on rafraîchit les données
                        if f_list is not None and f_list.winfo_exists():
                            if hasattr(self, 'charger_historique'): 
                                self.charger_historique()
                                print("🔄 Historique mis à jour avec succès.")
                        
                        # Transition forcée vers la page historique
                        self.show_frame("historique_frame")
                        print("⚡ Navigation vers Historique terminée.")
                        
                    except Exception as e_ui:
                        # En cas de pépin sur l'UI, on bascule quand même sur l'historique
                        print(f"⚠️ Note UI : Redirection forcée suite à une instabilité ({e_ui})")
                        self.show_frame("historique_frame")

                # On laisse 200ms pour que le SQL finisse de respirer avant de changer de vue
                self.after(200, rafraichir_et_partir)
                    
        except Exception as e:
            print(f"❌ Erreur critique sauvegarde : {e}")
    
    def sauvegarder_json_backup(self, actif, biais, conviction, score_ia, texte, com, score_final, statut, position):
        """Sous-fonction utilitaire mise à jour pour inclure le statut et la position"""
        import json
        import os
        from datetime import datetime
        
        journal = []
        if os.path.exists("journal.json"):
            try:
                with open("journal.json", "r", encoding="utf-8") as f:
                    journal = json.load(f)
            except: journal = []
        
        data_json = {
            "id": str(datetime.now().timestamp()),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "actif": actif,
            "biais": biais,
            "position": position,  # Ajouté
            "statut": statut,      # Ajouté
            "conviction": conviction,
            "analyse": texte,
            "score_ia": score_ia,
            "score_final": score_final,
            "ia": com
        }
        journal.append(data_json)
        with open("journal.json", "w", encoding="utf-8") as f:
            json.dump(journal, f, indent=4, ensure_ascii=False)


    def charger_historique(self):
        """Injecte UNIQUEMENT les données sans détruire la structure globale (Aperçu + Titre)."""
        print("\n[DEBUG] Injection des données dans le Journal...")

        # Sécurité : On vérifie que la liste existe avant d'essayer de la remplir
        if not hasattr(self, 'frame_list') or self.frame_list is None:
            print("⚠️ [DEBUG] frame_list introuvable. Construction initiale requise.")
            return

        import backend.database as database
        try:
            trades = database.recuperer_tout_historique()
        except Exception as e:
            print(f"❌ Erreur SQL : {e}")
            return

        # 1. NETTOYAGE : On ne vide que le contenu de la liste scrollable
        # On laisse le titre et la zone d'aperçu intacts
        for w in self.frame_list.winfo_children():
            w.destroy()

        if not trades:
            ctk.CTkLabel(self.frame_list, text="📂 Aucune trace de trade détectée...", 
                        font=("Inter", 13, "italic"), text_color="#566573").pack(pady=40)
            return

        # 2. INJECTION DES LIGNES
        for t in trades:
            # CORRECTION : On utilise self.frame_list au lieu de self.scroll_h
            ligne = ctk.CTkFrame(self.frame_list, fg_color="#151921", height=55, corner_radius=8)
            ligne.pack(fill="x", pady=5, padx=10)
            ligne.pack_propagate(False)

            # Affichage des infos
            date_txt = str(t[1])[:16] if t[1] else "Date N/A"
            actif_txt = str(t[2]).upper() if t[2] else "UNITÉ"
            
            ctk.CTkLabel(ligne, text=f"📅 {date_txt}  |  📊 {actif_txt}", 
                        font=("Inter", 12), text_color="#ECF0F1").pack(side="left", padx=15)
            
            # Groupe de boutons (Action)
            btn_f = ctk.CTkFrame(ligne, fg_color="transparent")
            btn_f.pack(side="right", padx=10)

            # Bouton Voir (👁️)
            ctk.CTkButton(btn_f, text="👁️", width=35, height=35, fg_color="#273746",
                        command=lambda d=t: self.show_detail(d)).pack(side="left", padx=2)
            
            # Bouton Supprimer (🗑️) - Optionnel mais recommandé
            ctk.CTkButton(btn_f, text="🗑️", width=35, height=35, fg_color="#273746", hover_color="#C0392B",
                        command=lambda i=t[0]: self.supprimer_trade_action(i)).pack(side="left", padx=2)

        # 3. RAFRAÎCHISSEMENT VISUEL
        self.update_idletasks()
        print(f"✅ {len(trades)} lignes de trades injectées proprement.")

    def reset(self):
        """Remise à zéro complète de l'interface d'analyse"""
        self.template = "Exemple :\n\nActif : EUR/USD\nBiais : Baissier\nAnalyse : ..."
        
        # Reset des entrées texte
        if hasattr(self, 'entry_actif') and self.entry_actif:
            self.entry_actif.delete(0, "end")
        if hasattr(self, 'entry_biais') and self.entry_biais:
            self.entry_biais.delete(0, "end")
            
        if hasattr(self, 'texte_analyse') and self.texte_analyse:
            self.texte_analyse.delete("1.0", "end")
            self.texte_analyse.insert("1.0", self.template)

        # Reset des statuts et conviction
        if hasattr(self, 'statut_var'):
            self.statut_var.set("Brouillon")
        if hasattr(self, 'position_var'):
            self.position_var.set("Neutre")
        if hasattr(self, 'slider_conviction'):
            self.slider_conviction.set(50)
            
        if hasattr(self, 'texte_reponse_ia'):
            self.texte_reponse_ia.delete("1.0", "end")
            
        print("🧹 Interface réinitialisée.")
            

    def executer_analyse_complete(self):
        """Lance l'audit complet du Mentor avec le contexte du statut"""
        nom_actif = self.entry_actif.get()
        contenu_analyse = self.texte_analyse.get("1.0", "end")
        # On récupère le statut et la position depuis les menus créés précédemment
        statut_actuel = self.statut_var.get() if hasattr(self, 'statut_var') else "Brouillon"
        conviction = int(self.slider_conviction.get()) if hasattr(self, 'slider_conviction') else 50

        # UI Feedback
        self.texte_reponse_ia.delete("1.0", "end")
        self.texte_reponse_ia.insert("1.0", "Le Mentor analyse ton plan... 🧠")
        self.update() 

        # Appel au mentor avec le nouveau système
        import backend.mentor_ia as mentor_ia
        # On utilise la fonction pro qui gère les APIs de marché (Polygon/News)
        score, feedback, couleur = mentor_ia.analyser_ia_pro(
            self, 
            "Analyse Initiale", 
            contenu_analyse, 
            statut_actuel, 
            nom_actif, 
            conviction
        )
            
        self.texte_reponse_ia.delete("1.0", "end")
        self.texte_reponse_ia.insert("1.0", feedback)
        
        # Mise à jour visuelle du score si tu as un label dédié
        if hasattr(self, 'label_score'):
            self.label_score.configure(text=f"Score: {score}/10", text_color=couleur)

    def engager_le_trade(self):
        """Bascule de l'analyse vers le suivi live avec le Guardian."""
        verdict_ia1 = self.texte_reponse_ia.get("1.0", "end-1c")
        actif = self.entry_actif.get()

        if not verdict_ia1 or len(verdict_ia1) < 20:
            messagebox.showwarning("Action requise", "Tu dois d'abord obtenir l'avis de l'IA Architecte.")
            return

        # 1. On génère la fiche de mission (IA 1 -> Synthèse)
        self.plan_synthetise = mentor_ia.synthetiser_plan_pour_guardian(verdict_ia1, actif)
        
        # 2. On prépare l'UI du Cockpit
        self.label_contrat_details.configure(text=self.plan_synthetise)
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", "🛡️ [SYSTEM] : Le Guardian est en ligne. Ton plan est verrouillé. Ta seule mission est de le respecter.\n\n")
        self.chat_display.configure(state="disabled")
        
        # 3. On affiche la frame (On suppose que tu as une fonction show_frame)
        self.cockpit_frame.tkraise()
        self.trade_actif = True

    def parler_au_guardian(self):
        message_user = self.input_chat.get().strip()
        if not message_user: 
            return

        # Affichage immédiat du message utilisateur
        self.update_chat_view(f"👤 Trader : {message_user}")
        self.input_chat.delete(0, 'end')

        # Appel de l'IA 2 (The Guardian)
        # On lui passe le plan synthétisé pour qu'il reste dans son cadre
        reponse_guardian = mentor_ia.analyser_compagnon_live(self, message_user, self.plan_synthetise)
        
        # Affichage de la réponse
        self.update_chat_view(f"🛡️ Guardian : {reponse_guardian}")
 
    def update_chat_view(self, texte):
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", texte + "\n\n")
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")        

    def ouvrir_guardian(self):
        # 1. Vérification si un trade est analysé
        # J'utilise self.texte_reponse_ia comme convenu
        verdict_ia1 = self.texte_reponse_ia.get("1.0", "end-1c").strip()
        
        if len(verdict_ia1) < 20:
            messagebox.showwarning("Guardian", "L'IA Architecte doit d'abord valider un plan avant d'activer le Guardian.")
            return

        # 2. Synthèse du plan (Une seule fois par trade)
        if not hasattr(self, 'plan_synthetise') or not self.plan_synthetise:
            self.plan_synthetise = mentor_ia.synthetiser_plan_pour_guardian(verdict_ia1, self.entry_actif.get())

        # 3. Création de la fenêtre flottante
        guard_win = ctk.CTkToplevel(self)
        guard_win.title("The Guardian - Discipline Live")
        guard_win.geometry("400x550")
        guard_win.attributes('-topmost', True) 
        guard_win.configure(fg_color="#0B0E14")
        guard_win.lift()  # Force le focus au premier plan

        # --- UI INTERNE ---
        ctk.CTkLabel(guard_win, text="🛡️ THE GUARDIAN", font=("Inter", 16, "bold"), text_color="#2ECC71").pack(pady=15)

        # Zone de chat
        chat_box = ctk.CTkTextbox(guard_win, fg_color="#151921", font=("Inter", 12), corner_radius=10)
        chat_box.pack(fill="both", expand=True, padx=15, pady=10)
        chat_box.insert("end", "🛡️ Guardian : Plan reçu. Je surveille tes émotions. Comment se passe le trade ?\n\n")
        chat_box.configure(state="disabled")

        # Zone de saisie
        entry_msg = ctk.CTkEntry(guard_win, placeholder_text="Parle à ton Guardian...", height=40)
        entry_msg.pack(fill="x", padx=15, pady=(0, 10))

        # 4. Logique d'envoi
        def envoyer_au_guardian(event=None):
            msg = entry_msg.get().strip()
            if not msg: 
                return
            
            # Affichage Trader
            chat_box.configure(state="normal")
            chat_box.insert("end", f"👤 Vous : {msg}\n\n")
            entry_msg.delete(0, 'end')
            chat_box.configure(state="disabled")
            chat_box.see("end")
            
            # Appel IA 2 (Guardian)
            # On affiche un petit message d'attente
            chat_box.configure(state="normal")
            
            reponse = mentor_ia.analyser_compagnon_live(self, msg, self.plan_synthetise)
            
            # Affichage Guardian
            chat_box.insert("end", f"🛡️ Guardian : {reponse}\n\n")
            chat_box.configure(state="disabled")
            chat_box.see("end")

        # --- BINDINGS ET BOUTON ---
        # On lie la touche Entrée à l'entry_msg
        entry_msg.bind("<Return>", envoyer_au_guardian)
        
        btn_envoyer = ctk.CTkButton(guard_win, text="Envoyer", fg_color="#2ECC71", hover_color="#27AE60", command=envoyer_au_guardian)
        btn_envoyer.pack(pady=(0, 15))

    def fermer_position(self):
        # 1. Demander confirmation (Optionnel, mais évite les miss-clics fatals)
        if not messagebox.askyesno("Clôture", "Confirmes-tu la clôture de la position ?"):
            return

        # 2. Reset des variables logiques
        self.trade_actif = False
        self.plan_synthetise = None
        
        # 3. Fermeture propre de la fenêtre du Guardian
        try:
            if hasattr(self, 'guard_win') and self.guard_win.winfo_exists():
                self.guard_win.destroy()
        except Exception:
            pass # La fenêtre était déjà fermée

        # 4. Nettoyage de l'interface principale pour le prochain trade
        self.texte_reponse_ia.configure(state="normal")
        self.texte_reponse_ia.delete("1.0", "end")
        self.texte_reponse_ia.insert("1.0", "Prêt pour une nouvelle analyse...")
        self.texte_reponse_ia.configure(state="disabled")

        # 5. Reset des champs de saisie (Optionnel)
        # self.entry_actif.delete(0, 'end') 

        print("✅ Session de trade archivée. Système réinitialisé.")

    def appliquer_sauvegarde(self, nom_section):
        try:
            import backend.database as database
            
            if nom_section == "Trading":
                risque = float(self.ent_risk_glob.get())
                rr = float(self.ent_rr_glob.get())
                self.user_settings["risque_max"] = risque
                self.user_settings["rr_min"] = rr
                database.sauvegarder_parametre("risque_max", risque)
                database.sauvegarder_parametre("rr_min", rr)

            elif nom_section == "Mentor IA":
                severite = self.seg_ia_glob.get()
                self.user_settings["ia_severite"] = severite
                database.sauvegarder_parametre("ia_severite", severite)

            elif nom_section == "Profil":
                for key in ["style", "objectif", "niveau"]:
                    val = self.user_settings.get(key)
                    database.sauvegarder_parametre(key, val)

            elif nom_section == "Notifications":
                for key in ["notif_analyses", "notif_objectifs", "notif_motivation", "notif_resume"]:
                    val = self.user_settings.get(key)
                    database.sauvegarder_parametre(key, str(val))

            # --- AJOUT : IDENTIFIANTS ---
            elif nom_section == "Identifiants":
                # Ici on pourrait ajouter la logique de hachage de mot de passe
                # Pour l'instant, on confirme juste la réception des données
                print("🔒 [SECURE] Tentative de mise à jour des identifiants.")
                # database.maj_credentials(email, password) # Exemple futur

            # --- AJOUT : APPARENCE ---
            elif nom_section == "Apparence":
                # On s'assure que le thème est bien en base
                theme_actuel = self.user_settings.get("theme", "Dark")
                database.sauvegarder_parametre("theme", theme_actuel)
                print(f"🎨 [STYLE] Thème {theme_actuel} confirmé en base.")

            messagebox.showinfo("Succès", f"Paramètres {nom_section} enregistrés de manière permanente !")
            print(f"💾 [SQL] Paramètres {nom_section} synchronisés en base de données.")

        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer des valeurs numériques valides.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Échec de la sauvegarde : {e}")

    def create_main_btn(self, texte, icone, commande, special=False):
        # IMPORTANT : Le parent doit être self.menu_buttons_container (celui qu'on a créé dans creer_menu)
        couleur = ACCENT_COLOR if special else CARD
        
        btn = ctk.CTkButton(self.menu_buttons_container, # Vérifie bien ce parent !
                            text=f"{icone} {texte}",
                            command=commande,
                            fg_color=couleur,
                            width=300,
                            height=60,
                            font=("Inter", 16, "bold"))
        btn.pack(pady=10, padx=20, fill="x")

    def maj_profil(self, cle, valeur):
        """Sauvegarde Style, Objectif, Niveau, etc."""
        # Mise à jour RAM
        self.user_settings[cle] = valeur
        # Persistance SQL
        try:
            import backend.database as database
            database.sauvegarder_parametre(cle, valeur)
            print(f"💾 [SQL] Profil {cle} sauvegardé : {valeur}")
        except Exception as e:
            print(f"❌ Erreur SQL Profil : {e}")

    def toggle_specifique(self, cle):
        """Sauvegarde les switches (True/False)."""
        if cle in self.user_settings:
            # Inversion de l'état actuel
            nouvelle_val = not self.user_settings[cle]
            self.user_settings[cle] = nouvelle_val
            
            try:
                import backend.database as database
                # On force en string "True"/"False" pour SQLite
                database.sauvegarder_parametre(cle, str(nouvelle_val))
                print(f"💾 [SQL] Switch {cle} -> {nouvelle_val}")
            except Exception as e:
                print(f"❌ Erreur SQL Switch : {e}")

    def maj_ia_severite(self, valeur):
        """Mise à jour instantanée de la sévérité IA."""
        self.user_settings["ia_severite"] = valeur
        try:
            import backend.database as database
            database.sauvegarder_parametre("ia_severite", valeur)
            print(f"💾 [SQL] Sévérité IA scellée : {valeur}")
        except Exception as e:
            print(f"❌ Erreur SQL IA : {e}")

    def sauvegarder_details_marche(self):
        """Récupère les saisies manuelles et force l'écriture en SQL"""
        print("DEBUG: Lancement de la sauvegarde manuelle...") # Pour voir si ça passe
        
        try:
            # 1. Récupération des valeurs depuis les widgets
            spread = self.spread_entry.get()
            session = self.session_menu.get()
            correlation = self.correlation_entry.get()

            # 2. Envoi vers ta logique SQL existante (maj_profil)
            self.maj_profil("spread_moyen", spread)
            self.maj_profil("session_pref", session)
            self.maj_profil("correlation_defaut", correlation)

            # 3. Message de succès (si tu as cette méthode)
            if hasattr(self, 'appliquer_sauvegarde'):
                self.appliquer_sauvegarde("Marche")
                
            print(f"💾 [SQL] Paramètres Marche synchronisés : {spread}, {session}")

        except AttributeError as e:
            print(f"❌ Erreur : Un widget n'est pas encore créé ou accessible : {e}")

    def ouvrir_parametres(self):
        """Initialise la structure avec un design Deep Black & Minimaliste"""
        
        # --- INITIALISATION DU MANAGER ---
        if not hasattr(self, 'licence'):
            self.licence = LicenceManager(self)

        # Nettoyage
        for w in self.parametre_frame.winfo_children():
            w.destroy()

        # --- ARCHITECTURE ---
        # Sidebar : On reste sur un bleu très sombre ou un gris presque noir pour détacher un peu du fond
        self.side_panel = ctk.CTkFrame(self.parametre_frame, width=240, fg_color="#0A0A0A", corner_radius=0)
        self.side_panel.pack(side="left", fill="y")
        self.side_panel.pack_propagate(False) 
        
        # Zone de contenu : NOIR TOTAL
        self.content_area = ctk.CTkFrame(self.parametre_frame, fg_color="#000000")
        self.content_area.pack(side="right", fill="both", expand=True, padx=30, pady=20)

        # --- CONTENU DE LA SIDEBAR ---
        ctk.CTkLabel(self.side_panel, text="PARAMÈTRES", 
                    font=("Inter", 18, "bold"), 
                    text_color="#14254C").pack(pady=30)
        
        # Menu standard
        menu_items = [
            ("👤 Identifiants", "Identifiants"),
            ("👨‍💼 Profil Trader", "Profil"),
            ("📊 Type Marche", "Marche"),
            ("⚖️ Trading & Risque", "Trading"),
            ("🤖 Mentor IA", "Mentor IA"),
            ("🔔 Notifications", "Notifications"),
            ("🎨 Apparence", "Apparence"),
            ("⚖️ Responsabité", "Responsabilite") # Nouvelle section pour la responsabilité et les limites de l'IA 
        ]

        for label, view in menu_items:
            ctk.CTkButton(
                self.side_panel, text=label, 
                fg_color="transparent", # Transparent pour laisser voir le fond de la sidebar
                text_color="white",      # Texte Blanc
                anchor="w", 
                height=40, 
                hover_color="#1A1A1A",   # Gris très sombre au survol
                command=lambda v=view: self.charger_vue(v)
            ).pack(fill="x", padx=10, pady=2)
        
        # Séparateur subtil
        ctk.CTkFrame(self.side_panel, fg_color="#1A1A1A", height=1).pack(fill="x", padx=20, pady=15)
        
        # --- BOUTON ABONNEMENT PRO ---
        ctk.CTkButton(
            self.side_panel, text="💎 Abonnement Pro", 
            fg_color="transparent", 
            text_color="#F1C40F", # Or pour le premium
            anchor="w", height=40,
            hover_color="#1A1A1A",
            command=lambda: self.charger_vue("Abonnement")
        ).pack(fill="x", padx=10)
        
        # Option Réinitialiser
        ctk.CTkButton(
            self.side_panel, text="⚠️ Réinitialiser", 
            fg_color="transparent", 
            text_color="#E74C3C", 
            anchor="w", height=40,
            hover_color="#1A1A1A",
            command=lambda: print("Reset futur")
        ).pack(fill="x", padx=10)

        # Bouton Retour Menu
        ctk.CTkButton(
            self.side_panel, text="⬅ Retour Menu", 
            command=lambda: self.show_frame("menu_principal"), 
            fg_color="#1A1A1A", # Bouton discret
            text_color="white",
            border_width=1, 
            border_color="#333333"
        ).pack(side="bottom", fill="x", padx=20, pady=20)

        # Vue par défaut
        self.charger_vue("Identifiants")

    def charger_vue(self, nom_vue):
        """Nettoie et reconstruit la zone de contenu avec le design Deep Black"""
        self.nom_vue = nom_vue
        
        # Sécurité : vérification que content_area existe
        if not hasattr(self, 'content_area') or not self.content_area.winfo_exists():
            return

        # Nettoyage de la zone de droite uniquement
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        # --- PALETTE DE COULEURS DEEP BLACK ---
        ACCENT_COLOR = "#081E58"
        BG_CARD = "#0A0A0A"      # Noir très profond pour les cartes
        BORDER_COL = "#1A1A1A"   # Bordure subtile
        INPUT_BG = "#333333"     # Gris anthracite pour les champs selon ta demande
        TEXT_MAIN = "white"

       # 2. VÉRIFICATION DU STATUT VIA LE SERVEUR
        # On interroge le manager qui regarde si le ticket en RAM est valide
        statut = self.licence_mgr.verifier_statut_abonnement()
        
        # 3. VERROU DE SÉCURITÉ INSTITUTIONNEL
        # Vues autorisées même sans licence (pour que l'utilisateur puisse payer ou changer le look)
        vues_libres = ["Abonnement", "Apparence", "Identifiants"]

        # Si l'abonnement est expiré et qu'il tente d'aller ailleurs que dans les vues libres
        if statut == "EXPIRED" and self.nom_vue not in vues_libres:
            self.licence_mgr.afficher_paywall(self.content_area)
            return

        # --- CAS SPÉCIFIQUE : ONGLET ABONNEMENT ---
        # On affiche TOUJOURS le paywall ici (soit pour activer, soit pour voir son statut)
        if self.nom_vue == "Abonnement":
            self.licence_mgr.afficher_paywall(self.content_area)
            return

        # --- DESIGN STANDARD ---
        header = ctk.CTkFrame(self.content_area, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(header, text=self.nom_vue.upper(), font=("Inter", 24, "bold"), text_color=ACCENT_COLOR).pack(side="left")

        scroll = ctk.CTkScrollableFrame(self.content_area, fg_color="transparent")
        scroll.pack(fill="both", expand=True) 

        # --- LOGIQUE DE VUES ---
        
        if self.nom_vue == "Identifiants":
            s = ctk.CTkFrame(scroll, fg_color=BG_CARD, border_width=1, border_color=BORDER_COL, corner_radius=12)
            s.pack(fill="x", pady=10, padx=5)
            ctk.CTkLabel(s, text="Email actuel:", font=("Inter", 12, "bold"), text_color=TEXT_MAIN).pack(pady=(15,0))
            ctk.CTkEntry(s, width=350, height=40, fg_color=INPUT_BG, border_color=BORDER_COL, text_color=TEXT_MAIN).pack(pady=10)
            ctk.CTkLabel(s, text="Nouveau mot de passe:", font=("Inter", 12, "bold"), text_color=TEXT_MAIN).pack(pady=(5,0))
            ctk.CTkEntry(s, show="*", width=350, height=40, fg_color=INPUT_BG, border_color=BORDER_COL, text_color=TEXT_MAIN).pack(pady=10)

        elif self.nom_vue == "Profil":
            s = ctk.CTkFrame(scroll, fg_color=BG_CARD, border_width=1, border_color=BORDER_COL, corner_radius=12)
            s.pack(fill="x", pady=10, padx=5)
            ctk.CTkLabel(s, text="Configuration du Style de Trading", font=("Inter", 13, "bold"), text_color=ACCENT_COLOR).pack(pady=15)

            # Menus avec fond anthracite
            for attr, key, vals in [("menu_style", "style", ["Scalping", "Day Trading", "Swing"]), 
                                    ("menu_obj", "objectif", ["Revenu Passif", "Prop Firm", "Croissance"]),
                                    ("menu_niveau", "niveau", ["Débutant", "Intermédiaire", "Expert/Institutionnel"])]:
                m = ctk.CTkOptionMenu(s, values=vals, width=250, fg_color=INPUT_BG, button_color="#444444", 
                                    text_color=TEXT_MAIN, command=lambda v, k=key: self.maj_profil(k, v))
                m.set(self.user_settings.get(key, vals[1]))
                m.pack(pady=8)
                setattr(self, attr, m)

        elif self.nom_vue == "Marche": 
            s = ctk.CTkFrame(scroll, fg_color=BG_CARD, border_width=1, border_color=BORDER_COL, corner_radius=12)
            s.pack(fill="x", pady=10, padx=5)
            ctk.CTkLabel(s, text="PARAMÈTRES DE MARCHÉ", font=("Inter", 14, "bold"), text_color=ACCENT_COLOR).pack(pady=15)

            ctk.CTkLabel(s, text="Type de Marché :", font=("Inter", 12), text_color=TEXT_MAIN).pack(anchor="w", padx=20)
            self.market_type_var = ctk.StringVar(value="Forex")
            self.market_type_menu = ctk.CTkSegmentedButton(s, values=["Forex", "Indices", "Crypto", "Matières Premières"],
                                                        variable=self.market_type_var, selected_color=ACCENT_COLOR,
                                                        unselected_color=INPUT_BG, text_color=TEXT_MAIN)
            self.market_type_menu.pack(fill="x", padx=20, pady=(5, 15))

            grid_frame = ctk.CTkFrame(s, fg_color="transparent")
            grid_frame.pack(fill="x", padx=20, pady=10)
            grid_frame.columnconfigure((0, 1), weight=1)

            ctk.CTkLabel(grid_frame, text="Spread (Pips/Points) :", font=("Inter", 12), text_color=TEXT_MAIN).grid(row=0, column=0, sticky="w", pady=5)
            self.spread_entry = ctk.CTkEntry(grid_frame, placeholder_text="ex: 0.8", height=35, fg_color=INPUT_BG, border_color=BORDER_COL, text_color=TEXT_MAIN)
            self.spread_entry.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=(0, 10))

            ctk.CTkLabel(grid_frame, text="Session Actuelle :", font=("Inter", 12), text_color=TEXT_MAIN).grid(row=0, column=1, sticky="w", pady=5)
            self.session_menu = ctk.CTkComboBox(grid_frame, values=["Londres", "New York", "Asie", "Overlap L/NY"], height=35, 
                                            fg_color=INPUT_BG, border_color=BORDER_COL, text_color=TEXT_MAIN)
            self.session_menu.grid(row=1, column=1, sticky="ew", pady=(0, 10))

            ctk.CTkLabel(s, text="Corrélation majeure (DXY, Yields, etc.) :", font=("Inter", 12), text_color=TEXT_MAIN).pack(anchor="w", padx=20, pady=(10, 5))
            self.correlation_entry = ctk.CTkEntry(s, placeholder_text="ex: DXY haussier, US10Y stable", height=35, fg_color=INPUT_BG, border_color=BORDER_COL, text_color=TEXT_MAIN)
            self.correlation_entry.pack(fill="x", padx=20, pady=(0, 15))

            self.save_market_btn = ctk.CTkButton(s, text="ACTUALISER LES PARAMÈTRES", font=("Inter", 12, "bold"), fg_color=ACCENT_COLOR, height=40)
            self.save_market_btn.pack(fill="x", padx=20, pady=20)

        elif self.nom_vue == "Trading":
            s = ctk.CTkFrame(scroll, fg_color=BG_CARD, border_width=1, border_color=BORDER_COL, corner_radius=12)
            s.pack(fill="x", pady=10, padx=5)
            ctk.CTkLabel(s, text="PROTOCOLES DE GESTION DU RISQUE", font=("Inter", 14, "bold"), text_color=ACCENT_COLOR).pack(pady=15)

            ctk.CTkLabel(s, text="Risque (%) :", font=("Inter", 12), text_color=TEXT_MAIN).pack(pady=(5,0))
            self.ent_risk_glob = ctk.CTkEntry(s, width=280, height=40, fg_color=INPUT_BG, border_color=BORDER_COL, text_color=TEXT_MAIN)
            self.ent_risk_glob.insert(0, str(self.user_settings["risque_max"]))
            self.ent_risk_glob.pack(pady=10)

            ctk.CTkLabel(s, text="RR minimum :", font=("Inter", 12), text_color=TEXT_MAIN).pack(pady=(5,0))
            self.ent_rr_glob = ctk.CTkEntry(s, width=280, height=40, fg_color=INPUT_BG, border_color=BORDER_COL, text_color=TEXT_MAIN)
            self.ent_rr_glob.insert(0, str(self.user_settings["rr_min"]))
            self.ent_rr_glob.pack(pady=10)

            ctk.CTkButton(s, text="METTRE À JOUR LE RISQUE", fg_color="#1A1A1A", border_width=1, border_color=ACCENT_COLOR, text_color=TEXT_MAIN,
                        command=lambda: self.appliquer_sauvegarde("Trading")).pack(pady=20, padx=20, fill="x")

        elif self.nom_vue == "Mentor IA":
            s = ctk.CTkFrame(scroll, fg_color=BG_CARD, border_width=1, border_color=BORDER_COL, corner_radius=12)
            s.pack(fill="x", pady=10, padx=5)
            ctk.CTkLabel(s, text="PERSONNALITÉ DE L'ARCHITECTE", font=("Inter", 14, "bold"), text_color=ACCENT_COLOR).pack(pady=15)
            
            self.seg_ia_glob = ctk.CTkSegmentedButton(s, values=["Doux", "Neutre", "Sévère", "Institutionnel"],
                                                selected_color=ACCENT_COLOR, unselected_color=INPUT_BG,
                                                text_color=TEXT_MAIN, height=40, command=self.maj_ia_severite)
            self.seg_ia_glob.set(self.user_settings.get("ia_severite", "Neutre"))
            self.seg_ia_glob.pack(pady=20, padx=20, fill="x")

            ctk.CTkButton(s, text="CONFIRMER LE TEMPÉRAMENT", fg_color="#1A1A1A", border_width=1, border_color=ACCENT_COLOR, text_color=TEXT_MAIN,
                        command=lambda: self.appliquer_sauvegarde("Mentor IA")).pack(pady=(0, 20), padx=20, fill="x")

        elif self.nom_vue == "Notifications":
            s = ctk.CTkFrame(scroll, fg_color=BG_CARD, border_width=1, border_color=BORDER_COL, corner_radius=12)
            s.pack(fill="x", pady=10, padx=5)
            ctk.CTkLabel(s, text="ALERTES & RAPPELS SYSTÈME", font=("Inter", 14, "bold"), text_color=ACCENT_COLOR).pack(pady=15)

            options = [("Rappel d'analyses", "notif_analyses"), ("Rappel d'objectifs", "notif_objectifs"),
                    ("Motivation quotidienne", "notif_motivation"), ("Résumé hebdomadaire", "notif_resume")]

            for texte, cle_fixe in options:
                f_opt = ctk.CTkFrame(s, fg_color="transparent")
                f_opt.pack(fill="x", pady=8, padx=25)
                ctk.CTkLabel(f_opt, text=texte, font=("Inter", 13), text_color=TEXT_MAIN).pack(side="left")
                sw = ctk.CTkSwitch(f_opt, text="", progress_color=ACCENT_COLOR, command=lambda c=cle_fixe: self.toggle_specifique(c))
                if self.user_settings.get(cle_fixe, False): sw.select()
                sw.pack(side="right")

        elif self.nom_vue == "Apparence":
            s = ctk.CTkFrame(scroll, fg_color=BG_CARD, border_width=1, border_color=BORDER_COL, corner_radius=12)
            s.pack(fill="x", pady=10, padx=5)
            ctk.CTkLabel(s, text="INTERFACE VISUELLE", font=("Inter", 14, "bold"), text_color=ACCENT_COLOR).pack(pady=15)
            theme_menu = ctk.CTkOptionMenu(s, values=["Dark", "Light"], fg_color=INPUT_BG, button_color="#444444", text_color=TEXT_MAIN,
                                        command=lambda v: [ctk.set_appearance_mode(v), self.maj_profil("theme", v)])
            theme_menu.set(self.user_settings.get("theme", "Dark"))
            theme_menu.pack(pady=10)

        elif self.nom_vue == "Responsabilite":
            # --- RÉCUPÉRATION DES INFOS DE CONFIG ---
            config = responsabilite.charger_config() # Assure-toi que cette fonction est accessible
            acceptation_date = config.get("date_acceptation", "Non définie")

            s = ctk.CTkFrame(scroll, fg_color=BG_CARD, border_width=1, border_color=BORDER_COL, corner_radius=12)
            s.pack(fill="both", expand=True, pady=10, padx=5)

            ctk.CTkLabel(s, text="CONTRAT D'UTILISATION & DÉCHARGE", 
                        font=("Inter", 14, "bold"), text_color=ACCENT_COLOR).pack(pady=15)

            # Zone de texte avec rappel des clauses
            clauses = """⚖️ CLAUSES DE RESPONSABILITÉ & CONFIDENTIALITÉ
            
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
                
            
            txt_box = ctk.CTkTextbox(s, height=400, fg_color="#000000", border_color=BORDER_COL, 
                                     border_width=1, text_color="gray", font=("Inter", 12))
            txt_box.insert("0.0", clauses)
            txt_box.configure(state="disabled")
            
            # fill="both" et expand=True permettent au cadre de prendre toute la largeur
            txt_box.pack(fill="both", expand=True, padx=20, pady=10)

            # Preuve de validation (Trace indélébile)
            preuve_frame = ctk.CTkFrame(s, fg_color="#050505", corner_radius=8)
            preuve_frame.pack(fill="x", padx=20, pady=20)

            ctk.CTkLabel(preuve_frame, 
                        text=f"✅ Accepté par l'utilisateur le : {acceptation_date}", 
                        font=("Inter", 12, "italic"), 
                        text_color="#2ecc71").pack(pady=15)

            ctk.CTkLabel(s, text="Note : Cette acceptation est liée à votre installation locale.", 
                        font=("Inter", 10), text_color="#555555").pack(pady=5)

        # --- PIED DE PAGE ---
        ctk.CTkButton(scroll, text="SAUVEGARDER LES MODIFICATIONS", 
                    fg_color=ACCENT_COLOR, hover_color="#0F2116", 
                    height=45, font=("Inter", 13, "bold"), text_color="white",
                    command=lambda: self.appliquer_sauvegarde(self.nom_vue)).pack(pady=30, padx=10, fill="x")

    def changer_taille_texte(self, nouvelle_taille):
        """Sauvegarde la taille du texte."""
        try:
            taille = int(nouvelle_taille)
            self.user_settings["taille_texte"] = taille
            database.sauvegarder_parametre("taille_texte", taille)
            
            # Mise à jour visuelle immédiate
            nouvelle_police = ("Inter", taille)
            if hasattr(self, 'texte_analyse'):
                self.texte_analyse.configure(font=nouvelle_police)
            print(f"💾 [SQL] Taille texte : {taille}px")
        except:
            pass

    def update_heatmap(self, val):
        global slider_conviction 
        # Change la couleur du slider ou d'un label selon la conviction
        v = float(val)
        if v < 30: color = "#E74C3C" # Rouge (Peu sûr)
        elif v < 70: color = "#F1C40F" # Jaune (Moyen)
        else: color = "#27AE60" # Vert (Confiant)
        self.slider_conviction.configure(progress_color=color, button_color=color)
        pass # Fin de la fonction update_heatmap

    def activer_ui_suivi(self):
        """Prépare la colonne de droite pour le mode interactif"""
        # 1. On affiche le label de question (placé juste au-dessus de la saisie)
        self.question_label.pack(pady=5, before=self.texte_analyse)
        
        # 2. On change la fonction du bouton IA
        self.btn_ia.configure(
            text="✅ VALIDER CETTE ÉTAPE", 
            command=self.valider_etape_suivi,
            fg_color="#1F538D" # Bleu institutionnel pour différencier
        )
        
        # 3. On affiche la première question
        self.maj_interface_suivi()
            
    def creer_analyse(self):
        """Interface d'Analyse : Design Deep Black avec accents Bleu Foncé"""
        if hasattr(self, 'entry_actif') and self.entry_actif is not None:
            if self.entry_actif.winfo_exists():
                return 

        for w in self.analyse_frame.winfo_children():
            w.destroy()

        # --- PALETTE DE COULEURS (MAINTENUE MAIS AFFINÉE) ---
        BG_PRINCIPAL = "#000000"
        CARD_DARK = "#080808"       # Un noir très légèrement bleuté/profond
        INPUT_BG = "#0D0D0D"        # Noir input pour effet "Apple"
        BORDER_COL = "#151515"      # Bordure ultra-subtile
        ACCENT_COLOR = "#1B2542"
        DEEP_BLUE = "#1B365D"
        TEXT_WHITE = "white"

        self.analyse_frame.configure(fg_color=BG_PRINCIPAL)

        # --- CONTAINER SUPÉRIEUR ---
        self.upper_container = ctk.CTkFrame(self.analyse_frame, fg_color="transparent")
        self.upper_container.pack(fill="x", padx=20, pady=(15, 0))

        # --- GAUCHE (Guide) ---
        self.left_frame = ctk.CTkFrame(self.upper_container, fg_color=CARD_DARK, corner_radius=12, border_width=1, border_color=BORDER_COL)
        self.left_frame.pack(side="left", fill="both", expand=True, padx=10)

        ctk.CTkLabel(self.left_frame, text="📖 GUIDE DE SESSION", font=("Inter", 15, "bold"), text_color="White").pack(pady=15)

        self.mode_menu = ctk.CTkSegmentedButton(self.left_frame, values=["Étudiant", "Expert", "Suivi IA"], 
                                                command=self.switch_mode, selected_color=DEEP_BLUE,
                                                unselected_color=INPUT_BG, text_color=TEXT_WHITE)
        self.mode_menu.pack(pady=10, padx=15, fill="x")

        self.guide_texte = ctk.CTkTextbox(self.left_frame, font=("Inter", 12), fg_color="#050505", 
                                        border_width=1, border_color=BORDER_COL, text_color=TEXT_WHITE)
        self.guide_texte.pack(fill="both", expand=True, padx=15, pady=15)

        
        # --- DROITE (Contrôles) ---
        self.right_frame = ctk.CTkFrame(self.upper_container, fg_color=CARD_DARK, corner_radius=12, border_width=1, border_color=BORDER_COL)
        self.right_frame.pack(side="right", fill="both", expand=True, padx=10)

        # Label question en Bleu Foncé
        self.question_label = ctk.CTkLabel(self.right_frame, text="", font=("Inter", 13, "bold"), text_color=DEEP_BLUE, wraplength=350)
        self.question_label.pack(pady=5)

        self.btn_calc = ctk.CTkButton(self.right_frame, text="🧮 Calculateur de Lot", command=lambda: tools_stats.ouvrir_calculateur(self), 
                                    fg_color="transparent", hover_color=INPUT_BG, height=40, border_width=1, border_color=BORDER_COL, text_color=TEXT_WHITE) 
        self.btn_calc.pack(pady=5, padx=20, fill="x")

        self.mini_barre_configs = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        self.mini_barre_configs.pack(fill="x", padx=15, pady=5)

        self.statut_menu = ctk.CTkSegmentedButton(self.mini_barre_configs, values=["Brouillon", "En attente", "Win", "Loss"],
                                                variable=self.statut_var, height=35, selected_color=ACCENT_COLOR,
                                                unselected_color=INPUT_BG, text_color=TEXT_WHITE)
        self.statut_menu.pack(fill="x", pady=5)

        self.position_menu = ctk.CTkSegmentedButton(self.right_frame, values=["Achat", "Vente", "Neutre"], 
                                                    variable=self.position_var, height=30, 
                                                    selected_color=DEEP_BLUE, unselected_color=INPUT_BG)
        self.position_menu.pack(fill="x", padx=20, pady=5)

        # Slider avec accent Bleu Foncé
        self.slider_conviction = ctk.CTkSlider(self.right_frame, from_=0, to=100, command=self.update_heatmap, 
                                            button_color=DEEP_BLUE, progress_color=DEEP_BLUE, fg_color=INPUT_BG)
        self.slider_conviction.pack(pady=5, padx=20, fill="x")

        # BARRE D'ACTIONS
        STYLE_BTN = {"height": 32, "corner_radius": 10, "font": ("Inter", 11, "bold"), "border_width": 1, "text_color": TEXT_WHITE}
        self.mini_barre_boutons = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        self.mini_barre_boutons.pack(fill="x", padx=15, pady=10)

        ctk.CTkButton(self.mini_barre_boutons, text="💾 Sauver", command=self.sauvegarde, fg_color="#1B4D2E", border_color="#27AE60", **STYLE_BTN).pack(side="left", padx=2, expand=True, fill="x")
        ctk.CTkButton(self.mini_barre_boutons, text="🔄 Reset", command=self.reset_interface, fg_color="#4D1B1B", border_color="#C0392B", **STYLE_BTN).pack(side="left", padx=2, expand=True, fill="x")
        ctk.CTkButton(self.mini_barre_boutons, text="⬅ Menu", command=lambda: self.show_frame("menu_principal"), fg_color="#111111", border_color=BORDER_COL, **STYLE_BTN).pack(side="left", padx=2, expand=True, fill="x")

        self.texte_reponse_ia = ctk.CTkTextbox(self.right_frame, height=100, fg_color="#050505", border_width=1, border_color=BORDER_COL, text_color="#2ecc71", font=("Consolas", 11))
        self.texte_reponse_ia.pack(pady=5, padx=20, fill="x")

        self.btn_ia = ctk.CTkButton(self.right_frame, text="🧠 ANALYSER & AUDITER", command=lambda: mentor_ia.lancer_analyse(self), 
                                fg_color=DEEP_BLUE, hover_color="#254A7F", height=50, font=("Inter", 13, "bold"), text_color=TEXT_WHITE)
        self.btn_ia.pack(pady=(5, 10), padx=20, fill="x")

       # --- ZONE DE SAISIE BASSE (Header Aligné) ---
        self.low_header = ctk.CTkFrame(self.analyse_frame, fg_color="transparent")
        self.low_header.pack(fill="x", padx=30, pady=(15, 5))
        
        # 1. Label à gauche
        self.label_votre_analyse = ctk.CTkLabel(self.low_header, text="VOTRE ANALYSE", 
                                                font=("Inter", 12, "bold"), text_color=DEEP_BLUE)
        self.label_votre_analyse.pack(side="left")
        
        # 2. L'entrée d'ACTIF à l'extrême droite
        self.entry_actif = ctk.CTkEntry(self.low_header, width=120, height=30, 
                                        placeholder_text="Actif...", 
                                        fg_color=INPUT_BG, border_color=BORDER_COL, 
                                        text_color=TEXT_WHITE, corner_radius=6,
                                        font=("Inter", 11))
        self.entry_actif.pack(side="right", padx=(10, 0)) # Petit espace à gauche de la case

        # 3. Le bouton GUARDIAN juste à côté de l'actif
        # On réduit un peu la taille (30x30) pour qu'il s'aligne parfaitement avec la hauteur de l'entry
        self.btn_guardian = ctk.CTkButton(self.low_header, text="🛡️", command=self.ouvrir_guardian,
                                        width=30, height=30, corner_radius=6, 
                                        fg_color=ACCENT_COLOR, hover_color=DEEP_BLUE,
                                        font=("Inter", 14))
        self.btn_guardian.pack(side="right")
        
        self.texte_analyse = ctk.CTkTextbox(self.analyse_frame, fg_color=CARD_DARK, border_width=1, 
                                            border_color=BORDER_COL, text_color=TEXT_WHITE, font=("Inter", 13))
        self.texte_analyse.pack(pady=(0, 20), padx=30, fill="both", expand=True) 

        self.btn_suivant = ctk.CTkButton(self.right_frame, text="BLOQUÉ 🔒", state="disabled", fg_color="transparent", text_color="gray")
        
        self.mode_menu.set("Étudiant")
        self.switch_mode("Étudiant")
            
        
    def bouton_analyser_click(self):
        statut = self.statut_var.get() # Récupère 'Brouillon', 'En attente', etc.
        actif = self.actif_var.get()
        
        # Si on est en mode 'En attente', on passe aussi l'historique
        if statut == "En attente":
            # On va chercher l'analyse précédente dans la DB pour l'envoyer à l'IA
            ancienne = self.get_last_analysis_from_db(actif)
            score, feedback, color = mentor_ia.analyser_ia_pro(self, ancienne, self.nouvelle_analyse, statut, actif, self.conviction)
        else:
            # Analyse standard
            score, feedback, color = mentor_ia.analyser_ia_pro(self, None, self.nouvelle_analyse, statut, actif, self.conviction)

        # Mise à jour de l'UI et de la DB
        self.afficher_feedback(feedback, color)

        texte_a_sauvegarder = self.nouvelle_analyse.get("1.0", "end-1c").strip()

        # --- 2. VÉRIFICATION DEBUG ---
        print(f"🔍 DEBUG TEXTE : Je m'apprête à sauver : '{texte_a_sauvegarder}'")
        
        # --- ON ALIGNE STRICTEMENT SUR LES 8 ARGUMENTS DE DATABASE.PY ---
        database.sauvegarder_trade_final(
            actif,                  # 1. actif
            self.position_var.get(),# 2. biais (on utilise la position ici)
            self.conviction,        # 3. conviction
            score,                  # 4. score_ia (utilise la variable 'score' de l'IA)
            texte_a_sauvegarder,    # 5. analyse (C'est ICI que ton texte doit être)
            feedback,               # 6. feedback
            statut,                 # 7. statut
            self.position_var.get() # 8. position
        )

    def update_fil_ariane_interactif(self):
        noms = ["🌍 MACRO", "🗺️ CONTEXTE", "📊 TECHNIQUE", "🛡️ RISQUE"]
        couleurs = {
            "verrouillé": "⚪ (Gris) ",
            "actif": "🔵 (Bleu) ",
            "validé": "🟢 (Vert) ",
            "partiel": "🟠 (Orange) ",
            "incorrect": "🔴 (Rouge) "
        }
        
        txt = "📍 PROGRESSION :\n\n"
        for i, nom in enumerate(noms):
            etat = self.etats_progression[i]
            txt += f"{couleurs[etat]}{nom}\n"
        
        if hasattr(self, 'question_label'):
            self.question_label.configure(text=txt)

    
    def maj_interface_suivi(self):
        """Affiche UNE SEULE question à la fois et gère le verrouillage du Papa"""
        
        # --- 1. NETTOYAGE CHIRURGICAL ---
        # Pour le mode "Papa", on veut que l'élève se concentre sur UNE question.
        # On efface le contenu précédent pour afficher la nouvelle étape proprement.
        self.guide_texte.configure(state="normal")
        self.guide_texte.delete("1.0", "end") 
        
        # --- 2. RÉCUPÉRATION DE LA DONNÉE ---
        bloc = self.etapes_analyse[self.current_step]
        question_actuelle = bloc["questions"][self.sub_step]

        # --- 3. AFFICHAGE STYLE 'CONVERSATION' ---
        self.guide_texte.insert("end", f"📍 ÉTAPE : {bloc['titre']}\n", "header")
        self.guide_texte.insert("end", f"{'━'*40}\n\n", "sep")
        
        # Le Mentor pose la question
        self.guide_texte.insert("end", f"🤖 MENTOR : {question_actuelle}\n\n", "question")
        
        # Zone d'instruction pour l'utilisateur
        self.guide_texte.insert("end", "✍️ TA RÉPONSE ICI :\n", "hint")
        self.guide_texte.insert("end", "------------------------------------------\n", "sep")
        
        # --- 4. FOCUS ET SÉCURITÉ ---
        # On place le curseur tout en bas pour que l'utilisateur tape au bon endroit
        self.guide_texte.mark_set("insert", "end")
        self.guide_texte.focus()
        self.guide_texte.see("end")

        # Mise à jour visuelle du progrès (Barre de progression)
        self.update_fil_ariane_interactif()

        # --- 5. CONFIGURATION DES BOUTONS (LE VERROU) ---
        # On réinitialise le bouton IA pour la validation de cette question précise
        self.btn_ia.configure(
            text="🧐 VÉRIFIER MA RÉPONSE", 
            command=self.valider_reponse_ia, 
            fg_color="#3498db", 
            state="normal"
        )
        
        # Le bouton "SUIVANT" reste bloqué. Seule l'IA peut le débloquer via valider_reponse_ia
        self.btn_suivant.configure(
            state="disabled", 
            text="🔒 ATTENTE DE VALIDATION IA", 
            fg_color="#555555"
        )

    def valider_reponse_ia(self):
        """Récupère la réponse, appelle l'IA et gère les 3 modes (Valide, Partiel, Incorrect)"""
        contenu = self.guide_texte.get("1.0", "end-1c")
        lignes = contenu.split("✍️ TAPE TA RÉPONSE CI-DESSOUS :\n")
        
        if len(lignes) < 2 or not lignes[-1].strip():
            return 

        reponse_user = lignes[-1].strip()
        bloc = self.etapes_analyse[self.current_step]
        question_actuelle = bloc["questions"][self.sub_step]

        # --- CAPTURE DES VARIABLES POUR L'IA ---
        # Si on est dans le bloc Risque, on enregistre les réponses précieuses
        if bloc["titre"] == "🛡️ RISQUE":
            if "niveaux précis" in question_actuelle.lower():
                self.info_sl_tp = reponse_user # On vient de créer info_sl_tp !
            elif "Justifie" in question_actuelle:
                self.raisonnement_user = reponse_user # On vient de créer raisonnement_user !
        
        # État de chargement
        self.btn_ia.configure(text="⌛ MENTOR RÉFLÉCHIT...", state="disabled")
        self.update()

        bloc = self.etapes_analyse[self.current_step]
        question_actuelle = bloc["questions"][self.sub_step]
        
        verdict = mentor_ia.analyser_question_suivi(self, bloc["titre"], question_actuelle, reponse_user)

        # Affichage du verdict
        self.guide_texte.configure(state="normal")
        self.guide_texte.insert("end", f"\n\n{verdict}\n", "ia_style")
        self.guide_texte.configure(state="disabled")
        self.guide_texte.see("end")

        v_upper = verdict.upper()

        # --- LOGIQUE DES 3 MODES ---
        
        # MODE 1 : VALIDÉ (Tout est vert)
        if "[VALIDÉ]" in v_upper or "VALIDÉ" in v_upper and "[INCORRECT]" not in v_upper:
            if self.sub_step + 1 < len(bloc["questions"]):
                self.btn_ia.configure(text="➡️ QUESTION SUIVANTE", command=self.prochaine_sous_question, fg_color="#27AE60", state="normal")
            else:
                self.btn_ia.configure(text="NIVEAU COMPLÉTÉ ✅", state="disabled")
                self.debloquer_bouton_suivant(bloc)

        # MODE 2 : PARTIEL (Le "Oui... mais" -> Orange)
        elif "[PARTIEL]" in v_upper or "PARTIEL" in v_upper:
            # On laisse passer car c'est une validation avec réserve
            if self.sub_step + 1 < len(bloc["questions"]):
                self.btn_ia.configure(text="➡️ SUIVRE (AVEC RÉSERVE 🟠)", command=self.prochaine_sous_question, fg_color="#E67E22", state="normal")
            else:
                self.btn_ia.configure(text="NIVEAU COMPLÉTÉ (PARTIEL) 🟠", state="disabled")
                self.debloquer_bouton_suivant(bloc)

        # MODE 3 : INCORRECT (Blocage -> Rouge)
        else:
            self.btn_ia.configure(text="❌ CORRIGER MON ANALYSE", command=self.valider_reponse_ia, state="normal", fg_color="#E74C3C")

        # Gestion de la fin absolue (Mauve)
        if (self.current_step + 1 == len(self.etapes_analyse) and 
            self.sub_step + 1 == len(bloc["questions"]) and 
            ("[VALIDÉ]" in v_upper or "[PARTIEL]" in v_upper)):
            
            self.btn_ia.configure(text="📊 GÉNÉRER MON PLAN DE TRADE", command=self.finaliser_analyse_complete, fg_color="#9B59B6", state="normal")

    def debloquer_bouton_suivant(self, bloc):
        """Utilitaire pour éviter la répétition de code"""
        if self.current_step + 1 < len(self.etapes_analyse):
            prochain = self.etapes_analyse[self.current_step+1]['titre']
            self.btn_suivant.configure(state="normal", text=f"🚀 PASSER À : {prochain}", command=self.prochain_bloc, fg_color="#E67E22")

    def prochaine_sous_question(self):
        self.sub_step += 1
        self.maj_interface_suivi()

    def prochain_bloc(self):
        self.sub_step = 0
        self.current_step += 1
        self.maj_interface_suivi()

    def finaliser_analyse_complete(self):
        """Récupère l'historique de la console et prépare l'enregistrement"""
        full_text = self.guide_texte.get("1.0", "end-1c")
        
        # On peut imaginer une petite animation ou un message de félicitations
        self.guide_texte.configure(state="normal")
        self.guide_texte.insert("end", f"\n\n{'='*20} PLAN DE TRADE TERMINÉ {'='*20}\n", "sep")
        self.guide_texte.insert("end", "✅ Ton plan est prêt. Tu peux maintenant l'enregistrer dans ton journal de bord.", "question")
        self.guide_texte.configure(state="disabled")
        
        # Ici on pourrait ouvrir automatiquement l'onglet 'Journal' ou 'Dashboard'
        messagebox.showinfo("Félicitations", "Plan de trade complété avec succès !")     

    def switch_mode(self, nouveau_mode):
        # 1. INITIALISATION DES VARIABLES SI ABSENTES (Anti-Crash)
        if not hasattr(self, 'current_step'): self.current_step = 0
        if not hasattr(self, 'sub_step'): self.sub_step = 0
        if not hasattr(self, 'analyse_suivi_ia'): self.analyse_suivi_ia = ""
        if not hasattr(self, 'analyse_classique_temp'): self.analyse_classique_temp = ""

        # 2. SAUVEGARDE DU TEXTE ACTUEL AVANT DE QUITTER LE MODE
        if hasattr(self, 'mode'):
            if self.mode == "Suivi IA" and hasattr(self, 'guide_texte'):
                # On ne sauvegarde que si c'est l'utilisateur qui a écrit (pas juste les questions 🤖)
                content = self.guide_texte.get("1.0", "end-1c").strip()
                if len(content) > 10: self.analyse_suivi_ia = content
            elif hasattr(self, 'texte_analyse'):
                self.analyse_classique_temp = self.texte_analyse.get("1.0", "end-1c").strip()

        self.mode = nouveau_mode
        if not hasattr(self, 'guide_texte'): return 

        self.guide_texte.configure(state="normal")
        
        # 3. NETTOYAGE DE L'AFFICHAGE
        self.texte_analyse.pack_forget()
        self.label_votre_analyse.pack_forget()
        self.entry_actif.pack_forget()
        self.texte_reponse_ia.pack_forget()
        if hasattr(self, 'question_label'): self.question_label.pack_forget()
        if hasattr(self, 'btn_suivant'): self.btn_suivant.pack_forget()

        # 4. RECONSTRUCTION SELON LE MODE
        if self.mode == "Suivi IA":
            self.guide_texte.configure(height=350) 
            self.entry_actif.pack( pady=10, padx=20, fill="x")
            
            if hasattr(self, 'question_label'): self.question_label.pack(pady=10, before=self.btn_ia)
            if hasattr(self, 'btn_suivant'): self.btn_suivant.pack(pady=5, padx=20, fill="x")

            # --- LOGIQUE DE MÉMOIRE ---
            # Si on a déjà du texte (venant d'une reprise ou d'un switch précédent)
            if len(self.analyse_suivi_ia) > 20:
                self.guide_texte.delete("1.0", "end")
                self.guide_texte.insert("1.0", self.analyse_suivi_ia)
                self.guide_texte.see("end")
            else:
                # Sinon on lance le processus de questions par défaut
                self.current_step = 0
                self.sub_step = 0
                self.maj_interface_suivi() 
                
        else:
            # --- MODES ÉTUDIANT / EXPERT ---
            self.guide_texte.configure(height=140) 
            self.label_votre_analyse.pack(pady=(10, 2))
            self.entry_actif.pack(pady=5, padx=100, fill="x")
            self.texte_analyse.pack(pady=(0, 20), padx=30, fill="both", expand=True)
            self.texte_reponse_ia.pack(pady=5, padx=20, fill="x")
            
            # Restauration du texte si présent
            if len(self.analyse_classique_temp) > 5:
                self.texte_analyse.delete("1.0", "end")
                self.texte_analyse.insert("1.0", self.analyse_classique_temp)

            # Mise à jour des instructions du guide (haut)
            contenu = getattr(self, 'guide_etudiant_contenu', "") if self.mode == "Étudiant" else getattr(self, 'guide_expert_contenu', "")
            self.guide_texte.delete("1.0", "end")
            self.guide_texte.insert("1.0", str(contenu))
            
            # On change la commande du bouton pour l'analyse classique
            import backend.mentor_ia as mentor_ia
            self.btn_ia.configure(text="🧠 ANALYSER PAR L'IA", command=lambda: mentor_ia.lancer_analyse(self), state="normal")

        self.guide_texte.see("end")
        
        self.guide_etudiant_contenu = """
        
       A - IDENTITÉ & CONVICTION

        (À inscrire également dans la case avec l'inscription "Actif" — cohérence obligatoire)

        1 - Actif analysé :
        → L’actif doit être clairement défini (paire précise).
        → ⚠️ Interdiction d’analyser plusieurs actifs simultanément.

        2 - Biais (Long / Short / Aucun) et score de conviction ?
        → Le biais doit être UNIQUE (pas de neutralité floue).
        → Le score de conviction doit être justifié par au moins 2 éléments concrets (macro + technique).
        → ⚠️ Si conviction > 70% sans justification solide → biais psychologique (excès de confiance).
        → ⚠️ Si conviction < 50% → absence de clarté → trade interdit.

        B - ANALYSE MACRO & RENDEMENTS

        1 - Sentiment global : Risk-on (appétit) ou Risk-off (peur)
        → Justification obligatoire basée sur des éléments concrets (indices, flux, news).
        → ⚠️ Une réponse sans justification = invalide.

        2 - Rendements (Yields) : Que fait le rendement de référence (ex: US02Y/GB10Y/...) ?
        → Direction claire : hausse / baisse / stagnation.
        → Impact direct sur la devise analysée.
        → ⚠️ Si non relié à ton biais → incohérence macro.

        3 - Différentiel de taux : Quelle devise a le taux d’intérêt et la politique monétaire les plus attractifs ? Justifiez votre réponse.
        → Comparaison OBLIGATOIRE entre les deux devises de la paire.
        → ⚠️ Si aucune dominance claire → biais fragile.

        4 - Inflation & Emploi : Selon les dernières news, quelle économie est la plus forte ? Justifiez votre réponse.
        → Basé uniquement sur données récentes (pas d’hypothèse).
        → ⚠️ Si contradiction avec le biais → incohérence critique.

        5 - Événement à venir ?
        → Identifier les news importantes (high impact).
        → ⚠️ Si événement imminent non pris en compte → erreur de gestion.

        🔎 Conclusion partielle 1

        Rédigez une conclusion incluant la devise soutenue par la macroéconomie et le différentiel de taux sur le long terme.

        → Une seule devise doit ressortir clairement dominante.
        → ⚠️ Si conclusion neutre ou hésitante → pas de direction exploitable → trade interdit.

        C - CONTEXTE FX & GÉOPOLITIQUE

        1 - Situation du marché : Selon la paire analysée, qu’observe-t-on actuellement sur le marché forex ?
        → Décrire un contexte clair (tendance, incertitude, compression…).
        → ⚠️ Réponse vague = analyse invalide.

        2 - Géopolitique : Quel est le contexte géopolitique actuel ?
        → Identifier si cela soutient ou affaiblit une devise.
        → ⚠️ Ignorer ce facteur = vision incomplète.

        3 - Corrélations : Y a-t-il des corrélations fortes avec d'autres marchés (indices, matières premières, autres devises) ?
        → Exemple : USD / Or / Indices / pétrole…
        → ⚠️ Si corrélations ignorées → analyse partielle.

        🔎 Conclusion partielle 2

        Rédigez une conclusion précisant quelle devise est soutenue par le contexte.

        → Doit confirmer ou invalider la conclusion macro.
        → ⚠️ Si contradiction entre macro et contexte → signal faible → prudence ou abstention.

        D - ANALYSE TECHNIQUE

        1 - Structure : Quelle est la tendance sur l’unité de temps supérieure ? Y a-t-il un range ?
        → Doit être clairement définie (pas d’ambiguïté).
        → ⚠️ Pas de structure claire = pas de trade.

        2 - Momentum : Les bougies montrent-elles de la force (impulsion) ou de l’hésitation ?
        → Justifier avec comportement du prix.
        → ⚠️ Momentum faible = entrée risquée.

        3 - Zones institutionnelles & Zones clés : Sommes-nous dans un Order Block ou un Fair Value Gap ? Y a-t-il un support et une résistance ?
        → La zone doit être identifiée ET cohérente avec le biais.
        → ⚠️ Zone mal définie = SL fragile.

        4 - Liquidité : Le marché a-t-il déjà “nettoyé” les sommets/bas précédents avant mon entrée ?
        → Réponse claire : Oui / Non + justification.
        → ⚠️ Si non → risque de sweep contre ta position.

        E - GESTION DU RISQUE

        1 - Pourquoi j’entre maintenant ?
        → Timing précis (pas de réponse vague).
        → ⚠️ “Parce que ça monte” = invalide.

        2 - Où est mon stop loss de sécurité ?
        → Doit correspondre à une invalidation logique du scénario.
        → ⚠️ SL arbitraire = erreur critique.

        3 - Quel est mon ratio Risque/Récompense (RR) ? (Minimum 1:2 conseillé.)
        → Calcul réel obligatoire.
        → ⚠️ RR < 1:2 = trade refusé automatiquement.

        4 - Confirmation ? (oui/non)
        → Basée sur structure + liquidité + timing.
        → ⚠️ Si NON → trade non validé.

        F - RÉSUMÉ & DÉCISION

        “Si toutes les cases ne sont pas cochées, je reste observateur.”


        --------------------------------------

        🎯 DÉCISION FINALE (NON NÉGOCIABLE)
        
        TOUTES les conditions validées → TRADE AUTORISÉ
        1 incohérence → TRADE À AJUSTER
        Plusieurs incohérences → TRADE REFUSÉ
        
        ⚠️ RÈGLE FINALE

        Un trade n’est pas validé parce qu’il “semble bon”,
        mais parce qu’il respecte un cadre strict.
        """
        self.guide_expert_contenu = """🔥 MODE EXPERT (QUICK CHECK)
        
        ---------------------------
        1. YIELDS (Macro Flow)
        → Le US10Y confirme-t-il ton biais directionnel ?
        Aligné?    Neutre?    Contradictoire?

        2. LIQUIDITÉ (Market Intent)
        → Un sweep de liquidité clair a-t-il été effectué avant ton entrée ?
        Oui?    Non?

        3. STRUCTURE (Market Structure)
        → As-tu une confirmation structurelle valide (BOS ou ChoCh) ?
        BOS?    ChoCh?    Aucune?

        4. ZONE (Execution Precision)
        → Ton entrée est-elle basée sur une zone institutionnelle claire ?
        FVG?    Order Block?    Autre?    Aucune?

        5. RISK MANAGEMENT (Survie)
        → Ton Risk/Reward est-il ≥ 1:2 ?
        Oui?    Non?

        6. DISCIPLINE
        → Respectes-tu STRICTEMENT ton plan sans ajustement émotionnel ?
        Oui?    Non?
        ---------------------------


        🎯 DÉCISION FINALE (NON NÉGOCIABLE)
        
        TOUTES les conditions validées → TRADE AUTORISÉ
        1 incohérence → TRADE À AJUSTER
        Plusieurs incohérences → TRADE REFUSÉ
        
        ⚠️ RÈGLE FINALE

        Un trade n’est pas validé parce qu’il “semble bon”,
        mais parce qu’il respecte un cadre strict.
        """ 

        # Ton template doit aussi être défini en haut pour être accessible partout
        self.template = "ANALYSE MACROECONOMIQUE - CONTEXTE - ANALYSE TECHNIQUE - DECISION\n"

    def creer_menu(self):
        """Vue Dashboard : Sidebar à GAUCHE (tous les boutons), Texte à DROITE"""
        
        # 0. Nettoyage du conteneur
        for widget in self.main_container.winfo_children():
            widget.destroy()

        # --- 1. SIDEBAR (À GAUCHE) ---
        self.menu_frame = ctk.CTkFrame(self.main_container, fg_color="#333333", width=280)
        self.menu_frame.pack(side="left", fill="y")
        self.menu_frame.pack_propagate(False)

        ctk.CTkLabel(self.menu_frame, text="NAVIGATION", font=("Inter", 12, "bold"), 
                    text_color="#0F0F26").pack(pady=(40, 20))

        # Style des boutons
        BTN_STYLE = {"anchor": "w", "height": 55, "corner_radius": 12, 
                    "fg_color": "transparent", "text_color": "#FBFBFB", "font": ("Inter", 16, "bold")}
        
        # --- BOUTONS DE NAVIGATION ---
        self.btn_new = ctk.CTkButton(self.menu_frame, text= "➕"  "Nouvelle Analyse", 
                                    command=lambda: self.show_frame("analyse_frame"), **BTN_STYLE)
        self.btn_new.pack(fill="x", padx=15, pady=5)

        self.btn_mind = ctk.CTkButton(self.menu_frame, text=  "🧠"  "MIND Engine", 
                                    command=lambda: self.show_frame("mind_frame"), **BTN_STYLE)
        self.btn_mind.pack(fill="x", padx=15, pady=5)

        self.btn_hist = ctk.CTkButton(self.menu_frame, text="  📜"  "Journal Des Trades ", 
                                    command=lambda: self.show_frame("historique_frame"), **BTN_STYLE)
        self.btn_hist.pack(fill="x", padx=15, pady=5)

        self.btn_tools = ctk.CTkButton(self.menu_frame, text="  🚀"  "Ressources Pro", 
                                    command=lambda: self.show_frame("outils_frame"), **BTN_STYLE)
        self.btn_tools.pack(fill="x", padx=15, pady=5)

        # AJOUT : Bouton Bibliothèque
        self.btn_know = ctk.CTkButton(self.menu_frame, text="  📚"  "Bibliothèque", 
                                    command=self.aller_au_savoir, **BTN_STYLE)
        self.btn_know.pack(fill="x", padx=15, pady=5)

        # Zone basse pour Paramètres et Stats
        spacer = ctk.CTkFrame(self.menu_frame, fg_color="transparent")
        spacer.pack(fill="both", expand=True)

        

        # Paramètres réintégré proprement
        self.btn_param = ctk.CTkButton(self.menu_frame, text="  ⚙️  Paramètres", 
                                    command=lambda: self.show_frame("parametre_frame"),
                                    **BTN_STYLE)
        self.btn_param.pack(fill="x", padx=15, pady=(0, 25))

        # --- 2. ZONE DE DROITE (PRÉSENTATION) ---
        right_zone = ctk.CTkFrame(self.main_container, fg_color="Black")
        right_zone.pack(side="right", fill="both", expand=True)

        txt_center = ctk.CTkFrame(right_zone, fg_color="transparent")
        txt_center.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(txt_center, text="Trade Mind", font=("Inter", 80, "bold"), text_color="#f7f9fa").pack()
        ctk.CTkLabel(txt_center, text="Précision  •  Discipline  •  Performance", 
                    font=("Inter", 22, "italic"), text_color="#f7f9fa").pack(pady=10)
    
    # Dans ton menu, le bouton Savoir doit faire ça :
    def aller_au_savoir(self):
        print("🚀 Direction la Bibliothèque...")
        self.show_frame("bibliotheque_frame") # Utilise le nom en STRING

    def reset_interface(self):
        """Vide tous les champs de saisie de l'écran d'analyse"""
        # Nettoyage de l'actif (Entry)
        if hasattr(self, 'entry_actif'):
            self.entry_actif.delete(0, 'end')
        
        # Nettoyage de l'analyse (Textbox)
        if hasattr(self, 'texte_analyse'):
            self.texte_analyse.delete("1.0", "end")
            
        # Nettoyage de la réponse IA (Textbox)
        if hasattr(self, 'texte_reponse_ia'):
            self.texte_reponse_ia.delete("1.0", "end")
            
        # Remise à zéro du slider
        if hasattr(self, 'slider_conviction'):
            self.slider_conviction.set(50)
            
        print("Interface réinitialisée.")        

    def reset_journal_complet(self):
        from tkinter import messagebox
        # Sécurité maximale avant de tout supprimer
        if messagebox.askyesno("⚠️ Action Irréversible", "Voulez-vous supprimer TOUT l'historique de la base de données ?"):
            conn = sqlite3.connect("trademind_pro.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM journal_final") # On vide la table SQL
            conn.commit()
            conn.close()
            
            # Une fois la base vidée, on nettoie l'écran avec TA fonction
            reset() 
            
        # Et on vide le widget qui affiche l'historique (ton widget 'detail')
        self.delete("1.0", "end") 
            
        messagebox.showinfo("Reset", "Le journal a été entièrement vidé.")
        pass # Fin de la fonction reset_journal_complet

    # ========= HISTORIQUE FONCTIONS =========
        
    def reset_detail_view(self):
        """Réinitialise l'écran de détail du bas avec le message par défaut"""
        # On vérifie si self.detail existe pour éviter un nouveau crash
        if hasattr(self, 'detail') and self.detail is not None:
            try:
                self.detail.configure(state="normal") # On déverrouille
                self.detail.delete("1.0", "end")      # On vide
                self.detail.insert("1.0", "Cliquez sur l'icône 👁️ d'un trade pour voir les détails ici...")
                self.detail.configure(state="disabled") # On verrouille
                print("🧹 Aperçu de l'historique nettoyé.")
            except Exception as e:
                print(f"⚠️ Erreur lors du reset : {e}")

    def creer_historique(self):
        """Design Premium - Trading Mind Dashboard Edition"""
        
        # 1. NETTOYAGE & INITIALISATION
        self.historique_frame.pack_propagate(False)
        for child in self.historique_frame.winfo_children():
            child.destroy()
        
        # --- PALETTE DE COULEURS ---
        BG_MAIN = "#0B0E14"       # Fond ultra sombre
        CARD_BG = "#161B22"       # Cartes gris anthracite
        ACCENT = "#3498db"        # Bleu Trading
        TEXT_DIM = "#8B949E"      # Texte secondaire
        TEXT_BRIGHT = "#F0F6FC"   # Texte principal
        BORDER = "#30363D"        # Bordures subtiles

        # 2. HEADER PRO
        header = ctk.CTkFrame(self.historique_frame, fg_color="transparent")
        header.pack(fill="x", pady=(25, 15), padx=30)

        ctk.CTkLabel(header, text="JOURNAL DE TRADING", 
                    font=("Inter", 26, "bold"), text_color=TEXT_BRIGHT).pack(side="left")
        
        # Badge de stats (Optionnel visuellement)
        badge = ctk.CTkFrame(header, fg_color="#238636", corner_radius=12)
        badge.pack(side="right")
        ctk.CTkLabel(badge, text="LIVE SQL", font=("Inter", 10, "bold"), padx=10).pack()

        # 3. LISTE DES ANALYSES (Scrollable)
        self.frame_list = ctk.CTkScrollableFrame(
            self.historique_frame, 
            fg_color="transparent", # On laisse voir le fond
            scrollbar_button_color="#30363D",
            scrollbar_button_hover_color="#484F58",
            corner_radius=0
        )
        self.frame_list.pack(fill="both", expand=True, padx=25)

        # 4. ZONE D'APERÇU (Refonte style terminal de luxe)
        preview_container = ctk.CTkFrame(self.historique_frame, fg_color=CARD_BG, 
                                       height=180, corner_radius=15, 
                                       border_width=1, border_color=BORDER)
        preview_container.pack(fill="x", padx=30, pady=(10, 15))
        preview_container.pack_propagate(False)

        # Petit bandeau de titre pour l'aperçu
        p_header = ctk.CTkFrame(preview_container, fg_color="#1F242C", height=30, corner_radius=0)
        p_header.pack(fill="x")
        ctk.CTkLabel(p_header, text="DETAILED ANALYTICS", font=("Consolas", 11, "bold"), 
                    text_color=ACCENT).pack(side="left", padx=15)

        self.detail_view = ctk.CTkTextbox(preview_container, fg_color="transparent", 
                                       font=("Consolas", 12), text_color=TEXT_DIM)
        self.detail_view.pack(fill="both", expand=True, padx=15, pady=10)
        self.detail_view.insert("1.0", "> En attente de sélection...")
        self.detail_view.configure(state="disabled")

        # 5. INJECTION DES TRADES AVEC DESIGN "CARD"
        import backend.database as database
        trades = database.recuperer_tout_historique() or []

        if not trades:
            ctk.CTkLabel(self.frame_list, text="Aucune analyse enregistrée.", 
                        font=("Inter", 14), text_color=TEXT_DIM).pack(pady=100)
        else:
            for t in trades:
                # La Carte
                card = ctk.CTkFrame(self.frame_list, fg_color=CARD_BG, height=80, 
                                  corner_radius=12, border_width=1, border_color=BORDER)
                card.pack(fill="x", pady=6, padx=5)
                card.pack_propagate(False)

                # --- CONTENU GAUCHE ---
                left_side = ctk.CTkFrame(card, fg_color="transparent")
                left_side.pack(side="left", fill="y", padx=20)
                
                # Date avec petit style
                date_str = str(t[1])[:10] if t[1] else "ID: " + str(t[0])
                ctk.CTkLabel(left_side, text=date_str, font=("Inter", 11), 
                            text_color=TEXT_DIM).pack(anchor="w", pady=(12, 0))
                
                # Actif (En gros)
                ctk.CTkLabel(left_side, text=str(t[2]).upper(), font=("Inter", 18, "bold"), 
                            text_color=ACCENT).pack(anchor="w")

                # --- CONTENU DROITE (BOUTONS) ---
                btn_side = ctk.CTkFrame(card, fg_color="transparent")
                btn_side.pack(side="right", padx=15)

                # Style commun des boutons ronds
                b_cfg = {"width": 38, "height": 38, "corner_radius": 10, "font": ("Inter", 14)}
                
                # Voir
                ctk.CTkButton(btn_side, text="👁", fg_color="#21262D", hover_color="#30363D",
                             command=lambda d=t: self.show_detail(d), **b_cfg).pack(side="left", padx=4)
                
                # Éditer
                ctk.CTkButton(btn_side, text="📝", fg_color="#21262D", hover_color="#B48E00",
                             command=lambda d=t: self.continuer_trade(d), **b_cfg).pack(side="left", padx=4)
                
                # Supprimer
                ctk.CTkButton(btn_side, text="×", fg_color="#21262D", hover_color="#842029",
                             command=lambda i=t[0]: self.supprimer_trade_action(i), **b_cfg).pack(side="left", padx=4)

        # 6. NAVIGATION BASSE
        footer = ctk.CTkFrame(self.historique_frame, fg_color="transparent")
        footer.pack(fill="x", pady=(0, 15))

        ctk.CTkButton(footer, text="BACK TO TERMINAL", 
                    fg_color="transparent", border_width=1, border_color=BORDER,
                    hover_color="#1F242C", width=200, height=40,
                    command=lambda: self.show_frame("menu_principal")).pack()

        self.update_idletasks()
        return
            
    def show_detail(self, trade_data):
        try:
            # 1. RÉCUPÉRATION SÉCURISÉE
            actif = str(trade_data[2]) if len(trade_data) > 2 else "Inconnu"
            date_brute = str(trade_data[1])[:16] if len(trade_data) > 1 else "Date inconnue"
            mode_sauvegarde = str(trade_data[3]) if len(trade_data) > 3 else "Étudiant"
            if mode_sauvegarde == "N/A": mode_sauvegarde = "Ancien Trade"

            # 2. CONVICTION & STATUTS (Déjà OK)
            conviction_str = "50%"
            for idx in [4, 3]:
                try:
                    val = int(trade_data[idx])
                    if 0 <= val <= 100:
                        conviction_str = f"{val}%"
                        break
                except: continue
            
            statut_final = next((str(i) for i in trade_data if str(i) in ["En attente", "Sauvegarde", "Validé", "Brouillon", "Terminé"]), "N/A")
            pos_final = next((str(i) for i in trade_data if str(i) in ["Achat", "Vente", "Neutre"]), "N/A")

            # 3. EXTRACTION DU CONTENU (LA CORRECTION EST ICI)
            vrai_analyse = "Aucune analyse détaillée disponible."
            feedback_ia = "🤖 Mentor IA : Analyse en attente d'évaluation..."
            
            # On récupère tous les textes longs en ignorant la date brute
            potential_texts = [str(x) for x in trade_data if isinstance(x, str) and len(str(x)) > 10]
            
            # --- LOGIQUE SPÉCIFIQUE SUIVI IA ---
            if mode_sauvegarde == "Suivi IA":
                # En Suivi IA, le texte qui contient "🤖 MENTOR" est NOTRE ANALYSE (le journal de bord)
                for t in potential_texts:
                    if "🤖 MENTOR" in t:
                        vrai_analyse = t
                        break
                # Le feedback est alors l'autre texte long (le plan généré)
                for t in reversed(potential_texts):
                    if "Plan" in t or (len(t) > 20 and t != vrai_analyse and t != date_brute):
                        feedback_ia = t
                        break
            else:
                # Mode Classique : Le texte avec 🤖 est le feedback
                for t in potential_texts:
                    est_date = (t.count("-") >= 2 and t.count(":") >= 1)
                    if not est_date and "🤖" not in t and t not in ["Expert", "Étudiant"]:
                        vrai_analyse = t
                        break
                for t in reversed(potential_texts):
                    if "🤖" in t or (t != vrai_analyse and t != date_brute and t not in ["Expert", "Étudiant"]):
                        feedback_ia = t
                        break

            # 4. MISE À JOUR VISUELLE
            if hasattr(self, 'detail_view'):
                self.detail_view.configure(state="normal")
                self.detail_view.delete("1.0", "end")
                contenu = (
                    f"📅 {date_brute} | 📊 {actif}\n"
                    f"🏷️ MODE : {mode_sauvegarde}\n"
                    f"🎯 POSITION : {pos_final} | 🔄 ÉTAT : {statut_final}\n"
                    f"🧠 CONVICTION : {conviction_str}\n"
                    f"{'-'*45}\n"
                    f"📝 JOURNAL DE BORD (ANALYSE) :\n{vrai_analyse}\n\n"
                    f"{'-'*45}\n"
                    f"✨ PLAN DE TRADING / FEEDBACK :\n{feedback_ia}"
                )
                self.detail_view.insert("1.0", contenu)
                self.detail_view.configure(state="disabled")

        except Exception as e:
            print(f"❌ Erreur show_detail : {e}")


    def supprimer_trade_action(self, id_trade):
        """Supprime un trade et rafraîchit l'UI sans crash."""
        from tkinter import messagebox
        import backend.database as database

        if messagebox.askyesno("Confirmation", f"Supprimer définitivement le trade #{id_trade} ?"):
            try:
                if database.supprimer_trade_db(id_trade):
                    print(f"🗑️ SQL : Trade {id_trade} supprimé.")
                    
                    # Rafraîchissement sécurisé : on appelle directement la reconstruction
                    # qui nettoie déjà la frame au début
                    self.creer_historique()
                    
                    # Reset de la vue détail si elle existe
                    if hasattr(self, 'detail_view'):
                        self.detail_view.configure(state="normal")
                        self.detail_view.delete("1.0", "end")
                        self.detail_view.insert("1.0", "Analyse supprimée. Sélectionnez un autre trade.")
                        self.detail_view.configure(state="disabled")
                        
                    self.update()
                else:
                    messagebox.showerror("Erreur", "Impossible de supprimer le trade en base de données.")
            except Exception as e:
                print(f"❌ Erreur suppression : {e}")

               
    def continuer_trade(self, trade_data):
        """Réinjecte TOUT (Texte, Statut, Position, Mode) dans l'interface"""
        try:
            # 1. IDENTIFICATION DES INDEX (Basé sur ton SQL)
            # trade_data : (id, date, actif, biais/mode, conviction, score, analyse, feedback, statut, position, plan)
            mode_sauvegarde = str(trade_data[3]) if len(trade_data) > 3 else "Étudiant"
            actif_val = str(trade_data[2])
            conviction_val = trade_data[4]
            analyse_val = str(trade_data[6]) # L'analyse est à l'index 6
            statut_val = str(trade_data[8])  # Statut à l'index 8
            position_val = str(trade_data[9]) # Position à l'index 9

            # 2. TRANSITION ET FORCE DU MODE
            self.show_frame("analyse_frame")
            self.switch_mode(mode_sauvegarde) 

            # 3. RÉINJECTION DES TEXTES (Selon le Mode)
            if mode_sauvegarde == "Suivi IA":
                if hasattr(self, 'guide_texte'):
                    self.guide_texte.configure(state="normal")
                    self.guide_texte.delete("1.0", "end")
                    self.guide_texte.insert("1.0", analyse_val)
                    self.guide_texte.see("end")
                    self.analyse_suivi_ia = analyse_val # Synchro variable tampon
            else:
                if hasattr(self, 'texte_analyse'):
                    self.texte_analyse.delete("1.0", "end")
                    self.texte_analyse.insert("1.0", analyse_val)

            # 4. SYNCHRO ACTIF & CONVICTION
            if hasattr(self, 'entry_actif'):
                self.entry_actif.delete(0, "end")
                self.entry_actif.insert(0, actif_val)
            
            if hasattr(self, 'slider_conviction'):
                self.slider_conviction.set(int(conviction_val))

            # 5. SYNCHRO STATUT & POSITION (Variables Tkinter)
            # On force la mise à jour des variables de contrôle
            if hasattr(self, 'statut_var'):
                self.statut_var.set(statut_val)
            if hasattr(self, 'position_var'):
                self.position_var.set(position_val)
                
            # Si tu as des OptionMenu ou SegmentedButtons liés, on les force aussi
            if hasattr(self, 'seg_button_position'): 
                self.seg_button_position.set(position_val)
            if hasattr(self, 'option_menu_statut'):
                self.option_menu_statut.set(statut_val)

            print(f"🔄 Reprise OK : {actif_val} | Mode: {mode_sauvegarde} | Pos: {position_val} | Statut: {statut_val}")

        except Exception as e:
            print(f"❌ Erreur lors de la reprise du trade : {e}")


    def update_mind_engine_live(self, *args):
        """
        Interface nerveuse Trade Mind - Version 1.5 Final.
        Zéro bug, UX fluide, Logique institutionnelle.
        """
        try:
            # 1. Couleurs Standardisées (Flat Design Pro)
            COLOR_NEUTRAL = "#95a5a6" # Gris neutre
            COLOR_VALID = "#2ecc71"   # Vert Émeraude
            COLOR_WARN = "#f39c12"    # Orange
            COLOR_DANGER = "#e74c3c"  # Rouge

            # 2. Gestion des champs vides (Reset visuel)
            if not self.entry_entree.get() or not self.entry_sl.get() or not self.entry_tp.get():
                self.label_status.configure(text="⏳ Remplis les champs...", text_color=COLOR_NEUTRAL)
                self.label_rr.configure(text="RR: --")
                return

            # 3. Capture et Normalisation
            entree = float(self.entry_entree.get())
            sl = float(self.entry_sl.get())
            tp = float(self.entry_tp.get())
            # Sécurité : strip() + upper() pour correspondre aux attentes du moteur
            trade_type = (self.combobox_type.get() or "LONG").strip().upper()

            # 4. Appel du Moteur Elite
            result = self.engine.calculer_metriques(
                entree=entree,
                sl=sl,
                tp=tp,
                capital=1000, 
                risque_max_percent=1.0,
                trade_type=trade_type
            )

            # 5. Extraction Sécurisée (Ajustements Elite)
            statut = result.get("statut_ia", "ERREUR")
            rr = result.get("rr", "--")
            alerte = result.get("alerte_rr", "")
            score = result.get("score_engine", 0)
            
            # Correction 1 : Extraction du message d'erreur sans risque de crash []
            erreurs = result.get("erreurs", [])
            msg_erreur = erreurs[0]["msg"] if erreurs else "Données Invalides"

            # 6. Logique de Coloration Dynamique
            if statut == "VALIDÉ":
                color = COLOR_VALID
            elif statut == "PARTIEL":
                color = COLOR_WARN
            else:
                color = COLOR_DANGER

            # 7. Mise à jour de l'UI
            if result.get("coherence", False):
                self.label_status.configure(
                    text=f"✅ {statut} | SCORE: {score}/10",
                    text_color=color
                )
            else:
                self.label_status.configure(
                    text=f"❌ {statut} : {msg_erreur}",
                    text_color=color
                )

            self.label_rr.configure(text=f"RR: {rr} ({alerte})")

        except ValueError:
            # Correction 2 : Reset visuel neutre en cas de saisie invalide
            self.label_status.configure(text="⏳ Saisie invalide (chiffres uniquement)", text_color="#95a5a6")
            self.label_rr.configure(text="RR: --")
            
        except Exception as e:
            # Correction 4 : Logging professionnel au lieu du simple print
            logging.error(f"[MindEngine UI Critical] {e}")



# ==========================================
# --- 5. LANCEMENT DE L'APPLICATION ---
# ==========================================    
if __name__ == "__main__":
    # 1. On s'assure que les tables existent
    import backend.database as database 
    database.init_db()
    
    # 2. On lance l'app
    app = TradeMindApp()
    app.mainloop()