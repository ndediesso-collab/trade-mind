import os
import sqlite3

# On définit le chemin complet
chemin = os.path.join(os.getcwd(), "trademind_pro.db")
print(f"📍 Le fichier devrait se trouver ici : {chemin}")

# On crée le fichier physiquement
conn = sqlite3.connect(chemin)
conn.close()

if os.path.exists(chemin):
    print("✅ Le fichier a bien été créé à l'instant !")
else:
    print("❌ Toujours rien... Python utilise un chemin virtuel.")