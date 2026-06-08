import requests
import time
import threading
import hashlib
import platform 
import uuid

class LicenceManager:
    def __init__(self, app_instance):
        self.app = app_instance
        self.api_url = "https://trademind-server-our3.onrender.com/verify"
        
        self.master_secret = "ULTRA_PRIVATE_TRADEMIND_KEY_2026"
        
        # DONNÉES VOLATILES (Disparaissent si on ferme l'app)
        self.session_valid = False
        self.session_expires = 0
        self.current_proof = ""

    def _get_ultra_fingerprint(self):
        # ... (Garder ton excellente fonction de fingerprinting)
        return hashlib.sha256(f"{platform.processor()}-{uuid.getnode()}".encode()).hexdigest()

    def verifier_statut_abonnement(self):
        """La seule source de vérité est l'expiration du ticket en RAM."""
        now = int(time.time())
        
        # 1. On vérifie si le ticket en mémoire est encore bon
        if self.session_valid and now < self.session_expires:
            return "PREMIUM"
            
        # 2. Si le ticket est expiré, on tente une revalidation silencieuse
        if self.app.user_settings.get("licence_key"):
            # On lance un thread pour ne pas bloquer l'interface
            self.revalider_silencieusement()
            
        return "TRIAL_ACTIVE" # Fallback pendant la revalidation

    def valider_code(self, code):
        """Demande initiale de ticket au serveur."""
        hw_id = self._get_ultra_fingerprint()
        
        try:
            response = requests.post(self.api_url, json={
                "key": code, "device_id": hw_id
            }, timeout=10)

            if response.status_code == 200:
                data = response.json()
                # MISE EN RAM (SÉCURISÉ)
                self.session_valid = True
                self.session_expires = data['expires']
                self.current_proof = data['proof']
                # Stockage minimal pour la session suivante
                self.app.maj_profil("licence_key", code)
                return True
        except:
            return False

    def revalider_silencieusement(self):
        """Vérification en tâche de fond pour renouveler le ticket."""
        key = self.app.user_settings.get("licence_key")
        if key:
            threading.Thread(target=lambda: self.valider_code(key), daemon=True).start()

    def afficher_paywall(self, container):
        """Interface Pro avec moyens de paiement intégrés."""
        import customtkinter as ctk
        import webbrowser

        for widget in container.winfo_children():
            widget.destroy()

        # Container Principal
        s = ctk.CTkFrame(container, fg_color="#080808", corner_radius=20, border_width=1, border_color="#151515")
        s.pack(pady=30, padx=60, fill="both", expand=True)

        ctk.CTkLabel(s, text="⭐ TRADE MIND PRO", font=("Inter", 28, "bold"), text_color="#FFFFFF").pack(pady=(25, 5))
        
        # --- SECTION STATUT ---
        status = self.verifier_statut_abonnement()
        msg = "DÉBLOQUEZ L'IA POUR COMMENCER À TRADER" if status == "EXPIRED" else "VOTRE ACCÈS PRO EST ACTIF"
        color = "#1B365D" if status == "EXPIRED" else "#10b981"
        self.label_status = ctk.CTkLabel(s, text=msg, font=("Inter", 12, "bold"), text_color=color)
        self.label_status.pack()

        # --- SECTION MOYENS DE PAIEMENT (Nouveau) ---
        pay_frame = ctk.CTkFrame(s, fg_color="transparent")
        pay_frame.pack(pady=20, fill="x", padx=100)

        ctk.CTkLabel(pay_frame, text="OBTENIR UNE CLÉ D'ACTIVATION :", font=("Inter", 10, "bold"), text_color="#555").pack(pady=10)

        # Bouton Stripe / Carte Bancaire
        btn_stripe = ctk.CTkButton(pay_frame, text="💳 CARTE BANCAIRE (STRIPE)", fg_color="#635BFF", hover_color="#4339CA",
                                    height=40, font=("Inter", 11, "bold"), 
                                    command=lambda: webbrowser.open("https://buy.stripe.com/votre_lien"))
        btn_stripe.pack(pady=5, fill="x")

        # Bouton PayPal
        btn_paypal = ctk.CTkButton(pay_frame, text="🅿️ PAYPAL", fg_color="#0070BA", hover_color="#005EA6",
                                    height=40, font=("Inter", 11, "bold"), 
                                    command=lambda: webbrowser.open("https://paypal.me/votre_compte"))
        btn_paypal.pack(pady=5, fill="x")

        # Bouton Crypto
        btn_crypto = ctk.CTkButton(pay_frame, text="₿ CRYPTO (USDT / BTC)", fg_color="#F7931A", hover_color="#E88400",
                                    height=40, font=("Inter", 11, "bold"), 
                                    command=lambda: webbrowser.open("https://votre_page_crypto.com"))
        btn_crypto.pack(pady=5, fill="x")

        # --- SECTION ACTIVATION ---
        ctk.CTkLabel(s, text="— DÉJÀ UNE CLÉ ? —", font=("Inter", 10), text_color="#333").pack(pady=(15, 0))
        
        self.entry_code = ctk.CTkEntry(s, placeholder_text="ENTREZ VOTRE CLÉ TM-PRO-XXXXX", width=350, height=45, 
                                       justify="center", border_color="#151515", font=("Consolas", 14), fg_color="#0D0D0D")
        self.entry_code.pack(pady=15)

        # Affichage auto de la clé si déjà présente
        stored_key = self.app.user_settings.get("licence_key")
        if stored_key: self.entry_code.insert(0, stored_key)

        btn_activer = ctk.CTkButton(s, text="ACTIVER MON TERMINAL", width=250, height=45, corner_radius=10,
                                    fg_color="#1B365D", hover_color="#254a7d", font=("Inter", 12, "bold"),
                                    command=lambda: self.valider_code(self.entry_code.get()))
        btn_activer.pack(pady=10)

        # Footer
        hw_id_short = self._get_ultra_fingerprint()[:12]
        ctk.CTkLabel(s, text=f"ID TERMINAL : {hw_id_short} (À fournir en cas de support)", font=("Inter", 9), text_color="#333").pack(side="bottom", pady=20)