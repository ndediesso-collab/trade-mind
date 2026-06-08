import customtkinter as ctk
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import re
from openai import OpenAI
import requests
from tkinter import filedialog
import PIL.Image
import webbrowser 
import pytz 
from fpdf import FPDF
from tkinter import filedialog 
from tkinter import messagebox, filedialog 
import sqlite3
import hashlib
import cv2 
import PIL.Image
import os
from PIL import Image
import turtle 

ACCENT = "#007AFF"

def charger_logo_pro(taille=(300, 300)):
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    chemin_logo = os.path.join(base_dir, "logo.jpg")

    # 3. Test de présence
    if not os.path.exists(chemin_logo):
        # On essaie en minuscules au cas où
        chemin_logo = os.path.join(base_dir, "logo.jpg")

    if os.path.exists(chemin_logo):
        try:
            img_pil = PIL.Image.open(chemin_logo)
            # On retourne l'image CTK
            return ctk.CTkImage(light_image=img_pil, dark_image=img_pil, size=taille)
        except Exception as e:
            print(f"Erreur lecture fichier : {e}")
            return None
    
    print(f"⚠️ Logo réellement introuvable à : {chemin_logo}")
    return None


# Variable qui va stocker la référence du bouton créé dans le main
btn_profil_fixe = None

def initialiser_media(bouton_cible):
    """Cette fonction reçoit le bouton du main pour pouvoir le modifier après"""
    global btn_profil_fixe
    btn_profil_fixe = bouton_cible

def btn_moderne(parent, text, cmd, color=ACCENT):
    return ctk.CTkButton(
        parent, 
        text=text, 
        command=cmd,
        fg_color=color,
        hover_color="#0056b3", # Un bleu plus sombre au survol
        height=45,
        corner_radius=12,
        font=("Inter", 14, "bold"), # "Inter" est la police standard du web moderne
        border_width=0
    )

def mettre_a_jour_avatar_interface(chemin_image):
    """
    Redimensionne, centre (crop) et affiche l'avatar sur le bouton permanent.
    Gère la persistance mémoire pour éviter les bugs d'affichage Tkinter.
    """
    try:
        # 1. Vérifications de sécurité
        if btn_profil_fixe is None:
            print("⚠️ Erreur : Le bouton de profil n'est pas encore initialisé.")
            return

        if not os.path.exists(chemin_image):
            raise FileNotFoundError(f"Le fichier est introuvable : {chemin_image}")

        # 2. Traitement de l'image avec PIL
        with PIL.Image.open(chemin_image) as img_pil:
            # On convertit en RGB (pour gérer les PNG transparents ou les formats bizarres)
            img_pil = img_pil.convert("RGB")
            
            # Calcul du crop central pour éviter de déformer le visage
            width, height = img_pil.size
            min_dim = min(width, height)
            
            left = (width - min_dim) / 2
            top = (height - min_dim) / 2
            right = (width + min_dim) / 2
            bottom = (height + min_dim) / 2
            
            # Crop + Resize de haute qualité (LANCZOS)
            img_pil = img_pil.crop((left, top, right, bottom))
            img_pil = img_pil.resize((100, 100), PIL.Image.Resampling.LANCZOS)
            
            # 3. Création de l'objet CTkImage
            # On passe l'image PIL directement. 
            # Note : On définit size=(40, 40) pour l'affichage dans la top_bar
            img_ctk = ctk.CTkImage(
                light_image=img_pil, 
                dark_image=img_pil, 
                size=(40, 40)
            )

        # 4. Mise à jour de l'interface (Thread-safe)
        # On enlève le texte (emoji) et on met l'image
        btn_profil_fixe.configure(image=img_ctk, text="")
        
        # --- PROTECTION CRITIQUE ANTI-BUG ---
        # On force Tkinter à garder une référence de l'image dans l'objet bouton.
        # Sans ça, l'image est supprimée par le Garbage Collector après la fonction.
        btn_profil_fixe.image = img_ctk 
        btn_profil_fixe._image_ref = img_ctk 

        # 5. Sauvegarde SQL (Préparation V4)
        # database.sauvegarder_chemin_avatar(self.user_id, chemin_image)

        messagebox.showinfo("Succès", "Votre photo de profil a été mise à jour.")

    except Exception as e:
        error_msg = f"Erreur lors du traitement de l'image : {str(e)}"
        print(f"❌ {error_msg}")
        messagebox.showerror("Erreur Avatar", error_msg)

def changer_photo_profil():
   
    """Ouvre la galerie Windows pour choisir une image"""
    chemin = filedialog.askopenfilename(
        title="Sélectionner votre photo de profil",
        filetypes=[("Images", "*.png;*.jpg;*.jpeg")]
    )
    if chemin:
        mettre_a_jour_avatar_interface(chemin)

def prendre_photo_camera():
    """Ouvre la webcam, capture une image au clavier (S) et ferme"""
    # 1. Allumer la caméra par défaut (0)
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        messagebox.showerror("Erreur", "Caméra non détectée. Vérifiez vos autorisations.")
        return

    messagebox.showinfo("Caméra TradeMind", "Une fenêtre va s'ouvrir.\n\n- Appuyez sur 'S' pour prendre la photo.\n- Appuyez sur 'Q' pour annuler.")

    while True:
        # 2. Lire le flux vidéo
        ret, frame = cap.read()
        if not ret:
            break

        # 3. Afficher le flux dans une fenêtre OpenCV
        cv2.imshow("Capture Profil - [S] Sauver | [Q] Quitter", frame)
        
        # 4. Gérer les touches du clavier
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('s'): # Touche 'S' pour SAUVER
            # Enregistrer l'image capturée temporairement
            nom_fichier = "avatar_capture.jpg"
            cv2.imwrite(nom_fichier, frame)
            
            # Utiliser notre utilitaire pour l'afficher dans l'app
            mettre_a_jour_avatar_interface(nom_fichier)
            break # Quitter la boucle
            
        elif key == ord('q'): # Touche 'Q' pour QUITTER (Annuler)
            break # Quitter la boucle sans sauver

    # 5. Libérer la caméra et fermer la fenêtre OpenCV
    cap.release()
    cv2.destroyAllWindows() 
