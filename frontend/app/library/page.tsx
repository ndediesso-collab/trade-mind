"use client";

import { useState } from "react";
import { ArrowLeft, BookOpen, ScrollText, PlayCircle, X, ChevronRight } from "lucide-react";
import Link from "next/link";
import ReactPlayer from 'react-player';

const educationalContent = {
  fundamental: [
    { title: "Comprendre l'analyse fondamentale (cas 1)", url: "https://youtu.be/gYMmJXAZy9M?si=HfI7mvunaRucJ5pE" },
    { title: "Comprendre l'analyse fondamentale (cas 2)", url: "https://youtu.be/nzVp2XB3auU?si=Y5bIlw_N_Dob6_Wu" },
    { title: "Taux d'intérêt et différentiels de taux", url: "https://youtu.be/vAyBiASOne4?si=s4gzsbJPko6rlyZZ" },
    { title: "L'inflation (CPI/core CPI)", url: "https://youtu.be/40dtvvLCUCQ?si=wT8GAqsts9QekKsg" },
    { title: "Le marché du travail (Vidéo à venir)", url: "" },
    { title: "Analyser le calendrier économique", url: "https://youtu.be/4EnnFiu1598?si=COEeoQ6oJiOCM93y" },
    { title: "Le sentiment du marché", url: "https://youtu.be/3ID2NFqgaCM?si=TBFAJoOz_L5MCKlQ" },
    { title: "Comprendre les rendements", url: "https://youtu.be/fAIpO2Xu8FI?si=1beP53nshsUraYOd" },
    { title: "La géopolitique et la finance", url: "https://youtu.be/Ulq5vBAf9SI?si=xZ7vacvuOoUEpmfz" },
  ],
  technical: [
    { title: "Qu'est-ce qu'on entend par tendance du marché?", isDefinition: true, content: "La tendance est la direction générale des prix. Elle se compose de sommets et creux ascendants (haussier) ou descendants (baissier). Trader avec la tendance est la base de la survie." },
    { 
      title: "Comprendre les zones institutionnelles (OB, FVG, etc.)", 
      isCategory: true,
      subVideos: [
        { title: "Order Block (OB)", url: "https://youtu.be/NYBvIcPX7XI?si=jmVr_qc31cduWcR_" },
        { title: "Fair Value Gap (FVG)", url: "https://youtu.be/skk0sm6LN6M?si=momYUhKK-E1xLAuT" },
        { title: "Support & Résistance", url: "https://youtu.be/7_oLrv-TIAA?si=kjzxL8l2RhlMXf_c" },
        { title: "Liquidity Sweep", url: "https://youtu.be/QPQWlXQ-El4?si=LgdQ-7m1VMiaiEwR" },
      ]
    },
    { title: "La prise de liquidité ou zone de liquidité en trading", isDefinition: true, content: "La liquidité représente les zones où les ordres stop sont concentrés. Les institutions manipulent le prix pour activer ces stops avant de prendre la direction réelle." },
  ]
};

export default function LibraryPage() {
  const [playingVideoUrl, setPlayingVideoUrl] = useState<string | null>(null);
  const [activeSubMenu, setActiveSubMenu] = useState<any | null>(null);
  const [definition, setDefinition] = useState<string | null>(null);

  const openVideo = (url: string) => {
    if (!url) return;
    
    // Nettoyage agressif pour ne garder que l'ID de la vidéo
    let videoId = "";
    if (url.includes("youtu.be/")) {
      videoId = url.split("youtu.be/")[1]?.split("?")[0] || "";
    } else if (url.includes("v=")) {
      videoId = url.split("v=")[1]?.split("&")[0] || "";
    }
    
    // On construit l'URL embed officielle
    setPlayingVideoUrl(`https://www.youtube.com/embed/${videoId}?autoplay=1&rel=0&modestbranding=1`);
    setActiveSubMenu(null);
  };

  const closeVideo = () => {
    setPlayingVideoUrl(null);
  };

  return (
    <div className="min-h-screen bg-[#0B0E14] text-zinc-200 p-6 md:p-12 font-sans antialiased selection:bg-blue-500/20">
      
      <header className="flex justify-between items-center mb-12 max-w-7xl mx-auto">
        <Link href="/" className="flex items-center gap-2 text-zinc-500 hover:text-zinc-100 transition-colors duration-300">
          <ArrowLeft size={16} /> 
          <span className="text-[11px] font-bold uppercase tracking-[0.2em]">Back to Terminal</span>
        </Link>
        <div className="flex items-center gap-3 bg-[#161B22] px-6 py-3 rounded-full border border-white/5 shadow-2xl">
          <BookOpen className="text-blue-500" size={14} />
          <h1 className="text-[10px] font-bold uppercase tracking-[0.2em] text-zinc-400">Trader Library v2.0</h1>
        </div>
      </header>

      <main className="max-w-7xl mx-auto grid grid-cols-12 gap-8">
        
        <section className="col-span-12 lg:col-span-8 bg-[#161B22]/30 border border-white/[0.05] rounded-[32px] shadow-2xl overflow-hidden backdrop-blur-xl">
          <div className="flex items-center justify-between px-10 py-6 bg-[#161B22]/50 border-b border-white/[0.05]">
            <div className="flex items-center gap-2 text-zinc-500">
                <ScrollText size={14} />
                <span className="text-[10px] font-bold uppercase tracking-widest text-zinc-500">mind_engine_knowledge.txt</span>
            </div>
            <div className="flex gap-2">
                <div className="w-2.5 h-2.5 rounded-full bg-red-500/10" />
                <div className="w-2.5 h-2.5 rounded-full bg-yellow-500/10" />
                <div className="w-2.5 h-2.5 rounded-full bg-green-500/10" />
            </div>
          </div>
          <div className="p-10">
            <pre className="whitespace-pre-wrap font-sans text-[15px] leading-8 text-zinc-300 max-h-[70vh] overflow-y-auto pr-6 custom-scrollbar">
{`📚 FONDAMENTAL

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
            Santé des entreprises (*supérieur à 50 = croissance)

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

            Peu de rater une opportunité

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

            C'est ici que tu apprens à ne pas "tout cramer".

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
            ✔️ La régularité est supérieur aux gros gains
            ✔️ Moins tu trades, mieux c’est`}
            </pre>
          </div>
        </section>

        <aside className="col-span-12 lg:col-span-4 flex flex-col gap-6">
            <div className="bg-[#161B22]/50 p-8 rounded-[32px] border border-white/[0.05] shadow-lg backdrop-blur-md">
                <h3 className="text-emerald-500 font-black uppercase text-[10px] tracking-[0.2em] mb-6 flex items-center gap-2">
                    <PlayCircle size={14}/> Learning Fundamental
                </h3>
                <div className="space-y-3">
                  {educationalContent.fundamental.map((video, index) => (
                    <button 
                      key={index} 
                      onClick={() => openVideo(video.url)}
                      className="w-full flex items-center gap-4 text-[13px] font-medium text-zinc-400 hover:text-emerald-500 text-left transition-all duration-300 p-4 rounded-2xl hover:bg-white/[0.03]"
                    >
                      <PlayCircle size={16} className="text-emerald-500/50 shrink-0" />
                      {video.title}
                    </button>
                  ))}
                </div>
            </div>

            <div className="bg-[#161B22]/50 p-8 rounded-[32px] border border-white/[0.05] shadow-lg backdrop-blur-md">
                <h3 className="text-blue-500 font-black uppercase text-[10px] tracking-[0.2em] mb-6 flex items-center gap-2">
                    <PlayCircle size={14}/> Learning Technical
                </h3>
                <div className="space-y-3">
                  {educationalContent.technical.map((video: any, index) => (
                    <button 
                      key={index} 
                      onClick={() => video.isCategory ? setActiveSubMenu(video) : video.isDefinition ? setDefinition(video.content) : openVideo(video.url)}
                      className="w-full flex items-center gap-4 text-[13px] font-medium text-zinc-400 hover:text-blue-500 text-left transition-all duration-300 p-4 rounded-2xl hover:bg-white/[0.03]"
                    >
                      {video.isCategory ? <ChevronRight size={16} className="text-blue-500" /> : <PlayCircle size={16} className="text-blue-500/50" />}
                      {video.title}
                    </button>
                  ))}
                </div>
            </div>
        </aside>
      </main>

      <footer className="mt-12 flex flex-col items-center justify-center pb-12 gap-4">
        <p className="text-zinc-600 text-[10px] uppercase tracking-widest max-w-xl text-center px-4">
          Le trading est une discipline de recherche permanente. Ne prends rien ici comme une vérité absolue. Analyse, teste, et forge ta propre intelligence. Tu es capable de comprendre le marché, fais-toi confiance.
        </p>
        <Link href="/" className="px-10 py-4 bg-[#161B22] border border-white/5 rounded-2xl text-zinc-500 hover:text-white hover:border-blue-500 transition-all text-[10px] font-black uppercase tracking-[0.2em]">
            EXIT_KNOWLEDGE_BASE
        </Link>
      </footer>

      {activeSubMenu && (
        <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4 backdrop-blur-xl" onClick={() => setActiveSubMenu(null)}>
          <div className="bg-[#0a0a0a] border border-white/10 w-full max-w-sm rounded-[32px] p-8 shadow-2xl" onClick={(e) => e.stopPropagation()}>
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-[10px] font-black uppercase tracking-widest text-blue-500">Concepts Techniques</h3>
              <button onClick={() => setActiveSubMenu(null)} className="text-zinc-600 hover:text-white"><X size={18}/></button>
            </div>
            <div className="space-y-2">
              {activeSubMenu.subVideos.map((sub: any, i: number) => (
                <button key={i} onClick={() => openVideo(sub.url)} className="w-full flex items-center justify-between p-4 bg-white/[0.02] rounded-2xl border border-white/[0.05] hover:border-blue-500/50 transition-all">
                  <span className="text-[12px] font-bold text-zinc-300">{sub.title}</span>
                  <PlayCircle size={14} className="text-blue-500/50" />
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {definition && (
        <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4 backdrop-blur-xl" onClick={() => setDefinition(null)}>
          <div className="bg-[#0a0a0a] border border-white/10 w-full max-w-sm rounded-[32px] p-8 shadow-2xl" onClick={(e) => setDefinition(null)}>
            <h3 className="text-[10px] font-black uppercase tracking-widest text-blue-500 mb-4">Définition</h3>
            <p className="text-sm text-zinc-300 leading-relaxed">{definition}</p>
          </div>
        </div>
      )}

      {playingVideoUrl && (
        <div className="fixed inset-0 bg-black/95 z-[60] flex items-center justify-center p-4 lg:p-12 backdrop-blur-xl" onClick={closeVideo}>
          <div className="relative bg-[#0a0a0a] border border-white/10 w-full max-w-5xl aspect-video rounded-[32px] shadow-2xl p-2" onClick={(e) => e.stopPropagation()}>
            <button onClick={closeVideo} className="absolute -top-12 right-0 text-zinc-500 hover:text-white transition-all"><X size={24} /></button>
            
            <iframe
              className="w-full h-full rounded-[24px]"
              src={playingVideoUrl}
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
            />
          </div>
        </div>
      )}
    </div>
  );
}