import customtkinter as ctk

class SavoirView(ctk.CTkFrame):
    def __init__(self, master, back_command, **kwargs):
        super().__init__(master, **kwargs)
        
        # Titre
        ctk.CTkLabel(self, text="📚 BIBLIOTHÈQUE DU TRADER", 
                    font=("Inter", 20, "bold"), text_color="#3498db").pack(pady=20)

        # Zone de texte avec le contenu
        self.txt_savoir = ctk.CTkTextbox(self, font=("Inter", 12), border_width=1)
        self.txt_savoir.pack(fill="both", expand=True, padx=20, pady=10)

        
        self.savoir_contenu = """📚 FONDAMENTAL

            📊 BASES IMPORTANTES

            🔹Actif vs Devise

            ✔️ Actif : 
            C'est ce que tu trades.
            Ex: EUR/USD, Or(Gold), Bitcoin, Actions.

            ✔️ Devise :
            C'est une monnaie (EUR(euro), USD(dollar), JPY(yen),...)

            💡Exemple concret: 
            AUD/NZD : actif
            AUD : devise
            NZD : devise

            ━━━━━━━━━━━━━━━━━━━━━━━

            🏦 Banque centrale
            Une banque centrale contrôle la monnaie d’un pays (ex : BCE, FED).

            Pourquoi elle monte les taux ?
            → Pour ralentir l’inflation car plus les taux seront hauts et  moins les locaux consommeront. 
            Les entreprises s'adapteront, ce qui fera progressivement chuter l'inflation.

            Pourquoi elle baisse les taux ?
            → Pour stimuler l’économie. Les Banques Centrales vont injecter de la liquidité sur le marché pour faciliter la relance de l'activité économique.

            Hawkish 🦅 :
            → Politique stricte (hausse des taux) → devise forte

            Dovish 🕊️ :
            → Politique souple (baisse des taux) → devise faible


            📅 Calendrier économique
            Liste des annonces économiques importantes.

            🔹 PIB :
            Mesure la richesse produite → économie forte = devise forte

            🔹 Inflation (CPI) :
            Hausse des prix → influence les taux

            🔹 PMI :
            Santé des entreprises (>50 = croissance)

            🔹 Taux de chômage :
            Faible chômage = économie solide


            💰 Différentiel de taux
            Différence entre les taux de deux devises.

            → Plus le différentiel est élevé, plus une devise est attractive

            Ex :
            USD 5% vs EUR 3% → avantage USD


            🏛️ Politique monétaire
            Ensemble des actions de la banque centrale.

            → Influence directement le marché Forex

            🔹 Rendement (Return)

            C'est ce que tu gagnes par rapport à ton investissement.


            💡 Exemple : 
            Tu investis 100 euros
            Tu gagnes 10 euros

            → rendement = 10% 

            ✔️  Formule : 
            Gain / Capital * 100

            💡 Important : 
            → rendement élevé = plus de risque


            🔗 Corrélations
            Relation entre actifs.

            Exemples :
            - EUR/USD ↔ USD/CHF (souvent opposés)
            - Or ↔ USD (souvent inverse)
            - USD ↔ taux d’intérêt

            💡 Utile pour confirmer une analyse



            ━━━━━━━━━━━━━━━━━━━━━━━

            📊 À SAVOIR - TECHNIQUE

            📈 TYPES DE MARCHE

            🔹 Tendance (Trend)

            Le marché qui monte ou descend clairement

            ✔️ Haussière 📈 : 
            → Sommets plus hauts
            → Creux plus hauts

            ✔️ Baissière 📉 :
            → Sommets plus bas
            → Creux plus bas

            💡 Conseil :
            Trade dans le sens de la tendance


            🔹 Range
            Marché qui oscille entre support et résistance 
            ✔️ Support en bas
            ✔️ Résistance en haut

            💡 Conseils :
            - Acheter en bas
            - Vendre en haut
            - Ne jamais trader le milieu ❌


            🟢 Support
            Zone où le prix rebondit

            🔴 Résistance
            Zone où le prix bloque

            💡 Plus une zone est testée → plus elle est importante

            ━━━━━━━━━━━━━━━━━━━━━━━

            🚀 SMART MONEY (CONCEPTS PRO)

            🔹Order Block(OB)

            Zones où les institutions(banques,fonds) ont placé de gros ordres.

            💡 Concrètement : 
            → Avant un gros muvement, il y'a souvent une zone de "calme".
            → C'est là que les institutions accumulent.

            Le prix revient souvent dans cette zone

            ✔️ Utilité : 
            → Repérer les zones d'entrée

            🔹 Fair Value Gap (FVG)

            Zone où le pprix est allé trop vite → déqéquilibre.

            💡Concrètement : 
            → Le marché "saute" une zone sans vraiment la trader

            Le prix revient souvent combler ce vide

            ✔️ Utilité : 
            → Zones de retour probables

            🔹 Prise de liquidité(Liquidity Grab)

            Les institutions vont chercher les stops des traders.

            💡Exemple : 
            → le prix casse un support
            → tout le monde vend
            → puis le marché remonte

            Piège classique

            ✔️ Pourquoi ?
            → récupérer la liquidité pour entrer en position

            💡 Traduction simple : 
            → Le marché piège les traders avant de partir

            ━━━━━━━━━━━━━━━━━━━━━━━

            📊 STRUCTURE DU MARCHE (AVANCE)

            🔹 Break Of Structure (BOS)

            C'estquand le marché casse une structure importante.

            💡Exemple : 
            → le prix faisait des somets de plus en plus hauts
            → puis casse un sommet précédent

            → Cela confirme la tendance

            ✔️ Utilité :
            → confirmer une continuation

            🔹 Change Of Character (CHOCH)

            C'est un changement de comportement du marché.

            💡Exemple : 
            → marché haussier
            → puis casse un dernier plus bas

            → Possible retouenement

            ✔️ Utilité : 
            → détecter un début de retournement

            💡 Résumé : 
            BOS = Continuation
            CHOCH = Possible retournement

            ━━━━━━━━━━━━━━━━━━━━━━

            🧠 CONSEILS TRADING 

            📊 CONFIRMATIONS IMPORTNTES 

            🔹 Confluuence 

            Plusieurs signaux dans le meme sens 

            💡Exemple : 
            → Tendance hausiière
            → + support
            → + news positives

            Trade plus solide.

            🔹Confirmation

            Attendre une validation avant d'entrer

            💡Exemple : 
            → cassure + retour + réaction

            ✔️ évite les pièges

            📅 Avant une news importante :
            - Évite d’entrer en position ❌
            - Attends la réaction du marché

            📊 Après une news :
            - Attends une confirmation
            - Ne trade pas l’émotion

            ❌ Sans confirmation :
            → Ne trade pas
            → Le marché piège souvent

            ━━━━━━━━━━━━━━━━━━━━━━

            ⚖️ GESTION DU RISQUE (AVANCE)

            🔹 Stop Loss

            Niveau où tu acceptes de perdre

            ✔️ Obligatoire

            🔹 Take Profit

            Niveau où tu prends ton gain

            🔹 Risque Managment

            Ne jamais risquer trop sur un trade 

            💡 Règle :
            → 1 à 2% du capital max

            🔹 Ratio Risk/Reward 

            Comparer perte possible vs gain possible

            💡 Toujours viser :
            → gagner plus que tu ne perds

            Ex :
            - Risque : 10€
            - Gain : 20€ minimum

            ✔️ Ratio conseillé : 1:2 minimum

            Toujours viser minimum 1:2

            🧘 Discipline

            - Sois patient
            - Respecte ton setup
            - Accepte de ne pas trader

            🔥 Le meilleur trade = celui que tu ne prends pas

            ━━━━━━━━━━━━━━━━━━━━━━━ 

            🧠 PSYCHOLOGIE DU TRADER

            🔹Overtrading

            Trader trop souvent

            💡Problème : 
            → Pertes inutiles,
            → fatigue mentale.

            ✔️ Solution
            → attendre un setup propre

            🔹 FOMO ( Fear Of Missing Out ) 

            Peur de rater une opportunité

            💡Résultat : 
            → entrer trop tard
            → mauvais trade

            ✔️ Solution :
            → accepter de rater des trades

            🔹 Discipline

            Respecter ses règles 

            💡Exemple : 
            → respecter son Stop Loss
            → respecter son plan

            ✔️ Clé du succès

            🔹Patience

            Attendre les bonnes conditions

            💡Le marché donnes des opportunités tous les jours

            ✔️ Le bon trader attend
            ━━━━━━━━━━━━━━━━━━━━━━━


            COMPTE DEMO & COMPTE REELLE

            🎮 Pourquoi la Démo avant le Réel ?

            1. Le "Simulateur de Vol" ✈️

            On ne pilote pas un avion sans passer par un simulateur.

            Apprendre les boutons : Éviter de cliquer sur "Achat" au lieu de "Vente" par erreur.

            Zéro Stress : Tes erreurs de débutant sont gratuites. En réel, elles se paient cash.

            2. Valider ta Stratégie 📈

            Si tu ne gagnes pas d'argent virtuel, tu n'en gagneras jamais du vrai.

            Preuve par les chiffres : Teste ta méthode sur 20 trades. Si le bilan est positif, tu as un avantage.

            Habitude : Apprendre à placer tes protections (Stop Loss) sans réfléchir.

            3. Maîtriser le Risque 🛡️

            C'est ici que tu apprends à ne pas "tout cramer".

            Discipline : S'habituer à ne risquer que 1% ou 2% par trade.

            Taille de position : Comprendre comment calculer ton volume avant de cliquer.

            ⚠️ Le Piège à éviter

            Le manque d'émotion : Perdre 1000 € fictifs ne fait pas mal. Perdre 10 € réels peut te faire transpirer.

            Conseil d'or : Traite ton compte démo comme si c'était ton propre argent. Si tu fais n'importe quoi en démo, tu couleras en réel.

            🚀 Quand passer au Réel ?

            Tu es prêt si :

            Tu maîtrises ta plateforme à 100%.

            Ta stratégie est rentable sur au moins 1 mois en démo.

            Tu respectes ton plan sans jamais tricher.

            ━━━━━━━━━━━━━━━━━━━━━━━

            🚀 BONUS

            ✔️ Le marché ne doit rien
            ✔️ Tu dois t’adapter, pas l’inverse
            ✔️ La régularité > gros gains
            ✔️ Moins tu trades, mieux c’est
        """
        self.txt_savoir.insert("1.0", self.savoir_contenu)
        self.txt_savoir.configure(state="disabled")

        # Bouton Retour (on utilise la commande passée en paramètre)
        ctk.CTkButton(self, text="⬅ Retour Menu", command=back_command).pack(pady=20)