"use client";

import React, { useState, useEffect } from "react";
import { AuroraBackground } from "@/components/ui/aurora-background";
import { 
  Play, 
  Square, 
  Save, 
  RotateCcw, 
  Activity, 
  Terminal, 
  Target, 
  Zap, 
  ShieldAlert, 
  ChevronLeft, 
  Brain, 
  Calculator,
  LineChart,
  Gauge,
  Trophy,
  History,
  X,
  Plus,
  Info,
  Minus

} from "lucide-react";
import Link from "next/link";
import ReactPlayer from 'react-player';

export default function ScalpMode() {


  const [playingVideoUrl, setPlayingVideoUrl] = useState<string | null>(null);
    const closeVideo = () => setPlayingVideoUrl(null);
  // 1. LES DONNÉES ÉDUCATIVES (Séparées de la logique pour plus de clarté)
  const educationalContent = {
    fundamental: {
      inflation: { title: "L'inflation (CPI/core CPI)", url: "https://youtu.be/40dtvvLCQCQ" },
      rendements: { title: "Comprendre les rendements", url: "https://youtu.be/fAIpO2Xu8FI" },
      calendrier: { title: "Analyser le calendrier", url: "https://youtu.be/4EnnFiu1598" },
      geopolitique: { title: "La géopolitique", url: "https://youtu.be/Ulq5vBAf9SI" },
    },
    technical: {
      scalpSetups: [
        { title: "Order Block (OB)", url: "https://youtu.be/NYBvIcPX7XI" },
        { title: "Liquidity Sweep", url: "https://youtu.be/QPQWlXQ-El4" },
      ]
    }
  };

  // 2. FONCTION UTILITAIRE UNIQUE
  // Fonction pour formater l'URL YouTube en embed (nécessaire pour iframe)
  const getEmbedUrl = (url: string) => {
    if (!url) return "";
    let videoId = "";
    if (url.includes("youtu.be/")) {
      videoId = url.split("youtu.be/")[1]?.split("?")[0] || "";
    } else if (url.includes("v=")) {
      videoId = url.split("v=")[1]?.split("&")[0] || "";
    }
    return `https://www.youtube.com/embed/${videoId}?autoplay=1&rel=0&modestbranding=1`;
  };

  // Le Tooltip unifié qui utilise l'URL formatée
  const HelpTooltip = ({ title, content, subVideos }: any) => {
    const [show, setShow] = useState(false);
    return (
      <div className="relative inline-block ml-1" onMouseEnter={() => setShow(true)} onMouseLeave={() => setShow(false)}>
        <Info size={11} className="inline text-blue-500 cursor-help" />
        {show && (
          <div className="absolute z-[100] left-0 bottom-6 w-72 bg-[#161B22] border border-blue-500/30 p-4 rounded-2xl shadow-2xl animate-in fade-in zoom-in-95">
            <p className="text-[10px] font-bold text-white mb-2 uppercase tracking-wider">{title}</p>
            {content && <p className="text-[10px] text-zinc-400 mb-3 italic">{content}</p>}
            {subVideos?.map((v: any, i: number) => (
              <button 
                key={i} 
                onClick={() => setPlayingVideoUrl(getEmbedUrl(v.url))} 
                className="block w-full text-left text-[9px] text-blue-400 hover:text-white py-1 uppercase font-black transition-colors"
              >
                • {v.title}
              </button>
            ))}
          </div>
        )}
      </div>
    );
  };
  
  const [sessionStatus, setSessionStatus] = useState("DEBUT"); // "DEBUT" | "FIN"
  const [iaVerdict, setIaVerdict] = useState("> Neural Scalp Coach : Prêt pour l'audit. Remplissez vos intentions de session.");
  const [isLoading, setIsLoading] = useState(false);

  // --- CONFIGURATION STRICTE COMMITTÉE SUR SUPABASE ---
  const [actif, setActif] = useState("EURUSD");
  const [biais, setBiais] = useState("NEUTRE");
  const [conviction, setConviction] = useState(50);

  // --- TABLEAU DE BORD DU SOUCHIER DE MICRO-TRADES (SCALPING COMPTEUR) ---
  const [scalcWin, setScalcWin] = useState(0);
  const [scalcLoss, setScalcLoss] = useState(0);
  const [scalcBe, setScalcBe] = useState(0);

  // --- ÉTATS CALCULATEUR DE LOTS UNIFIÉ (SWING / DAILY TEMPLATE) ---
  const [showCalc, setShowCalc] = useState(false);
  const [calcData, setCalcData] = useState({ balance: "10000", risk: "0.5", pips: "5" });
  const [lotResult, setLotResult] = useState<number | null>(null);

  // --- TEXTES DU WORKSPACE SÉPARÉS ---
  const [preSessionText, setPreSessionText] = useState("");
  const [postSessionText, setPostSessionText] = useState("");

  // ID unique pour le dossier de scalping cloud (Évite les conflits et l'erreur 13)
  const [currentTradeId, setCurrentTradeId] = useState<number | null>(null);

  // 🔄 PROTECTION ET RÉINJECTION SUPABASE DIRECTE VIA INTERCEPTION DU ROUTAGE
  useEffect(() => {
    const checkRestaurationSupabase = async () => {
      if (typeof window === "undefined") return;

      // 1. Interception d'un ordre de routage depuis l'historique d'audit
      const ticket = sessionStorage.getItem("scalp_restore");
      if (ticket) {
        try {
          const target = JSON.parse(ticket);
          if (target.trade_id) {
            setIaVerdict(`> SYSTÈME : Extraction du rapport de scalping #TM-${target.trade_id} depuis Supabase...`);
            
            const res = await fetch(`http://127.0.0.1:8000/historique/get/${target.trade_id}`);
            if (res.ok) {
              const fullTrade = await res.json();
              
              setCurrentTradeId(fullTrade.id);
              setActif(fullTrade.actif || "EURUSD");
              setBiais(fullTrade.position || "NEUTRE");
              setConviction(fullTrade.conviction || 50);

              // Extraction des compteurs et du texte si la séance était clôturée
              if (fullTrade.analyse.includes("--- EXTRACTION SCORES SÉANCE ---")) {
                setSessionStatus("FIN");
                
                // Extraction des compteurs via regex pour éviter les pertes
                const winMatch = fullTrade.analyse.match(/WIN:\s*(\d+)/);
                const lossMatch = fullTrade.analyse.match(/LOSS:\s*(\d+)/);
                const beMatch = fullTrade.analyse.match(/BE:\s*(\d+)/);
                
                if (winMatch) setScalcWin(Number(winMatch[1]));
                if (lossMatch) setScalcLoss(Number(lossMatch[1]));
                if (beMatch) setScalcBe(Number(beMatch[1]));
                
                const texteSplit = fullTrade.analyse.split("--- RAPPORT DE COMPORTEMENT ---");
                if (texteSplit[1]) setPostSessionText(texteSplit[1].trim());
              } else {
                setSessionStatus("DEBUT");
                setPreSessionText((fullTrade.analyse || "").replace("[INTENTIONS ANTE-MARKET] : ", ""));
              }

              if (fullTrade.feedback) setIaVerdict(fullTrade.feedback);
              sessionStorage.removeItem("scalp_restore");
              return; // Bloque la récupération du cache local v2
            }
          }
        } catch (err) {
          console.error("Échec de la liaison neuronale Scalp Supabase:", err);
        }
      }

      // 2. Fallback classique sur la mémoire tampon locale debouncée
      const savedCache = localStorage.getItem("tm_scalp_cache_v2");
      if (savedCache) {
        try {
          const parsed = JSON.parse(savedCache);
          setCurrentTradeId(parsed.currentTradeId || null);
          setActif(parsed.actif || "EURUSD");
          setBiais(parsed.biais || "NEUTRE");
          setConviction(parsed.conviction || 50);
          setPreSessionText(parsed.preSessionText || "");
          setPostSessionText(parsed.postSessionText || "");
          setScalcWin(parsed.scalcWin || 0);
          setScalcLoss(parsed.scalcLoss || 0);
          setScalcBe(parsed.scalcBe || 0);
          setSessionStatus(parsed.sessionStatus || "DEBUT");
          if (parsed.iaVerdict) setIaVerdict(parsed.iaVerdict);
        } catch (e) {
          console.error("Erreur cache local Scalp:", e);
        }
      }
    };

    checkRestaurationSupabase();
  }, []);

  // 🔄 MEMOIRE TAMPON LOCALE EN TEMPS RÉEL (Debounce intelligent de 500ms)
  useEffect(() => {
    const handler = setTimeout(() => {
      const cache = {
        currentTradeId,
        actif,
        biais,
        conviction,
        preSessionText,
        postSessionText,
        scalcWin,
        scalcLoss,
        scalcBe,
        sessionStatus,
        iaVerdict
      };
      localStorage.setItem("tm_scalp_cache_v2", JSON.stringify(cache));
    }, 500);
    return () => clearTimeout(handler);
  }, [currentTradeId, actif, biais, conviction, preSessionText, postSessionText, scalcWin, scalcLoss, scalcBe, sessionStatus, iaVerdict]);

  // Logique unifiée du calculateur de volume
  const calculatePositionSize = () => {
    const bal = parseFloat(calcData.balance);
    const riskPct = parseFloat(calcData.risk) / 100;
    const pipsFloat = parseFloat(calcData.pips);
    if (bal && riskPct && pipsFloat) {
      const size = (bal * riskPct) / (pipsFloat * 10);
      setLotResult(parseFloat(size.toFixed(2)));
    }
  };

  // 🟦 SYNC AVANT-SÉANCE (BROUILLON)
  const savePreSession = async () => {
    if (!preSessionText.trim()) {
      setIaVerdict("> SÉCURITÉ : Workspace vide. Saisissez vos intentions de carnet d'ordres avant d'enregistrer.");
      return;
    }
    
    setIsLoading(true);
    try {
      const response = await fetch("http://127.0.0.1:8000/database/save", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          id: currentTradeId, // Mutation si l'ID maître existe déjà
          actif: actif.toUpperCase(),
          analyse: `[INTENTIONS ANTE-MARKET] : ${preSessionText}`,
          conviction: conviction,
          position: biais,
          statut: "Brouillon", 
          mode: "SCALPING", 
          type: "SHORT_TERM" 
        })
      });

      const data = await response.json();
      if (response.ok) {
        if (data.trade_id) setCurrentTradeId(data.trade_id);
        setIaVerdict(`> SYSTEM Cloud : Objectifs Scalp mémorisés en Brouillon.\n[ID_DOSSIER] : #TM-${data.trade_id || currentTradeId}`);
      } else {
        setIaVerdict("> SYSTEM Cloud : Rejet de la requête par la passerelle Supabase.");
      }
    } catch (error) {
      setIaVerdict("> SÉCURITÉ : Le service Mind Engine (api.py) ne répond pas.");
    } bits: {
      setIsLoading(false);
    }
  };

  // 🟦 SYNC AVANT-SÉANCE (AUDIT MACRO & TECHNIQUE)
  const launchPreSessionAudit = async () => {
    if (!preSessionText.trim()) {
      setIaVerdict("> SÉCURITÉ : Workspace vide. Saisissez vos intentions de carnet d'ordres.");
      return;
    }

    setIsLoading(true);
    setIaVerdict("> IA COACH : Audit de cohérence macro-technique en cours...");

    try {
      const response = await fetch("http://127.0.0.1:8000/analyse/swing", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          actif: actif.toUpperCase(),
          analyse: `AUDIT PRÉ-SESSION : ${preSessionText}`,
          conviction: conviction,
          position: biais,
          statut: "Audit_Pre_Session",
          mode: "SCALP",
          type: "SHORT_TERM"
        })
      });

      const data = await response.json();
      
      if (response.ok) {
        setIaVerdict(data.feedback);
      } else {
        setIaVerdict("> SÉCURITÉ : L'API n'a pas validé l'audit.");
      }
    } catch (error) {
      setIaVerdict("> SÉCURITÉ : Le service Mind Engine (api.py) ne répond pas.");
      console.error("Erreur Audit:", error);
    } finally {
      setIsLoading(false);
    }
  };

  // 🟥 SYNC POST-SÉANCE & AUDIT COMPORTEMENTAL FUSIONNÉ
  const launchIaAudit = async () => {
    if (!postSessionText.trim()) {
      setIaVerdict("> SÉCURITÉ : Le workspace de débriefing après-séance est requis pour l'analyse.");
      return;
    }

    setIsLoading(true);
    setIaVerdict("> IA COACH : Analyse croisée de l'intention vs exécution et archivage permanent...");

    const totalTrades = scalcWin + scalcLoss + scalcBe;
    const winRate = totalTrades > 0 ? ((scalcWin / totalTrades) * 100).toFixed(1) : "0.0";
    
    const dictionnairePerformances = 
      `--- EXTRACTION SCORES SÉANCE ---\n` +
      `• Total Micro-Trades : ${totalTrades}\n` +
      `• Répartition : [WIN: ${scalcWin} | LOSS: ${scalcLoss} | BE: ${scalcBe}]\n` +
      `• Winrate Évalué : ${winRate}%\n\n` +
      `--- RAPPORT DE COMPORTEMENT ---\n` +
      `${postSessionText}`;

    try {
      const response = await fetch("http://127.0.0.1:8000/database/save", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          id: currentTradeId, // Utilisation de l'ID maître pour écraser le brouillon
          actif: actif.toUpperCase(),
          analyse: dictionnairePerformances,
          conviction: conviction,
          position: biais,
          statut: scalcWin >= scalcLoss ? "WIN" : "LOSS", 
          mode: "SCALPING", 
          type: "SHORT_TERM" 
        })
      });

      const data = await response.json();
      if (response.ok) {
        localStorage.removeItem("tm_scalp_cache_v2");
        setTimeout(() => {
          setIaVerdict(
            `> SCALP COACH ENGINE : AUDIT TERMINÉ ET SYNCHRONISÉ\n\n` +
            `[STATUT DE SÉPULTURE] : SÉANCE COMPILÉE COHÉRENTE\n` +
            `[TRADES EXÉCUTÉS] : ${totalTrades} micro-scalps\n` +
            `[PERFORMANCE SCORE] : ${scalcWin}W / ${scalcLoss}L / ${scalcBe}BE\n\n` +
            `[ANALYSE EXÉCUTION] : Les métriques de fréquence ont été scellées sur Supabase.\n` +
            `> MENTOR FEEDBACK : ${data.feedback || "Cadre respecté."}`
          );
          setScalcWin(0);
          setScalcLoss(0);
          setScalcBe(0);
          setPreSessionText("");
          setPostSessionText("");
          setCurrentTradeId(null);
          setSessionStatus("DEBUT");
          setIsLoading(false);
        }, 1500);
      } else {
        setIaVerdict("> SYSTEM Cloud : Erreur d'écriture sur la table journal_final.");
        setIsLoading(false);
      }
    } catch (error) {
      setIaVerdict("> SÉCURITÉ : Échec de synchronisation cloud (FastAPI offline).");
      setIsLoading(false);
    }
  };

  const reinitialiserWorkspace = () => {
    if (confirm("Voulez-vous réinitialiser l'intégralité du cache de la session courante ?")) {
      setPreSessionText("");
      setPostSessionText("");
      setScalcWin(0);
      setScalcLoss(0);
      setScalcBe(0);
      setLotResult(null);
      setCurrentTradeId(null);
      setSessionStatus("DEBUT");
      localStorage.removeItem("tm_scalp_cache_v2");
      setIaVerdict("> SYSTEM : Cache nettoyé.");
    }
  };

  return (
    <AuroraBackground>
      {/* BOUTON NAV HEADER */}
      <div className="absolute top-4 left-4 z-50">
        <Link href="/">
          <button className="flex items-center gap-2 px-4 py-2 bg-[#0F1117]/90 border border-white/10 rounded-xl text-zinc-400 hover:text-white transition-all backdrop-blur-xl group shadow-2xl">
            <ChevronLeft size={14} className="group-hover:-translate-x-0.5 transition-transform" />
            <span className="text-[9px] font-black uppercase tracking-widest">Trade Mind Hub</span>
          </button>
        </Link>
      </div>

      {/* COMPOSANT MODAL DU CALCULATEUR DE VOLUME UNIFIÉ */}
      {showCalc && (
        <div className="absolute inset-0 z-50 flex items-center justify-center bg-black/95 backdrop-blur-md animate-in fade-in duration-200">
          <div className="w-[420px] bg-[#0F1117] border border-blue-500/20 rounded-[32px] p-8 shadow-2xl">
            <div className="flex justify-between items-center mb-8">
              <div className="flex items-center gap-3">
                <Calculator className="text-blue-400" size={22} />
                <h3 className="text-sm font-black uppercase tracking-widest text-white font-sans">Risk Calculator</h3>
              </div>
              <button onClick={() => setShowCalc(false)} className="p-2 text-zinc-500 hover:text-white"><X size={18} /></button>
            </div>
            <div className="space-y-6">
              <div className="space-y-2 text-left">
                 <label className="text-[10px] font-black text-blue-400 uppercase tracking-widest ml-1">Capital du Compte ($)</label>
                 <input type="number" value={calcData.balance} onChange={(e) => setCalcData({...calcData, balance: e.target.value})} className="w-full bg-zinc-900 border border-white/10 rounded-2xl p-4 text-white font-mono outline-none" />
              </div>
              <div className="grid grid-cols-2 gap-4 text-left">
                <div className="space-y-2">
                  <label className="text-[10px] font-black text-blue-400 uppercase tracking-widest ml-1">Risque (%)</label>
                  <input type="number" value={calcData.risk} onChange={(e) => setCalcData({...calcData, risk: e.target.value})} className="w-full bg-zinc-900 border border-white/10 rounded-2xl p-4 text-white font-mono outline-none" />
                </div>
                <div className="space-y-2">
                  <label className="text-[10px] font-black text-blue-400 uppercase tracking-widest ml-1">Stop Loss (Pips)</label>
                  <input type="number" value={calcData.pips} onChange={(e) => setCalcData({...calcData, pips: e.target.value})} className="w-full bg-zinc-900 border border-white/10 rounded-2xl p-4 text-white font-mono outline-none" />
                </div>
              </div>
              <button onClick={calculatePositionSize} className="w-full py-4 bg-blue-600 rounded-xl font-black text-[10px] uppercase tracking-wider text-white">Calculer Volume</button>
              <div className="p-4 bg-zinc-900/50 rounded-2xl border border-white/5 flex justify-between items-center">
                <span className="text-[10px] uppercase font-bold text-zinc-400">Lots Suggérés :</span>
                <span className="text-2xl font-mono font-black text-white">{lotResult !== null ? lotResult : "0.00"}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* HORIZON INTERFACE PRINCIPALE */}
      <div className="relative z-10 w-full h-screen flex flex-col p-4 pt-16 gap-4 bg-zinc-950/40 font-sans overflow-hidden">
        
        {/* LIGNE FLUIDE SUPÉRIEURE : PARAMÈTRES TACTIQUES & SÉLECTEUR DE PHASE */}
        <div className="flex gap-4 items-center justify-between w-full bg-[#0F1117]/95 border border-white/10 p-3 rounded-2xl shadow-2xl">
          
          {/* Module Switch Session */}
          <div className="bg-black/40 p-1 rounded-xl border border-white/5 flex gap-1 w-[280px]">
            <button 
              onClick={() => { setSessionStatus("DEBUT"); setIaVerdict("> Neural Scalp Coach : Workspace réinitialisé pour l'avant-séance."); }}
              className={`flex-1 py-1.5 rounded-lg text-[9px] font-black uppercase tracking-wider transition-all flex items-center justify-center gap-2 ${sessionStatus === "DEBUT" ? "bg-blue-600 text-white shadow-md" : "text-zinc-500 hover:text-zinc-300"}`}
            >
              <Play size={10} /> Début Session
            </button>
            <button 
              onClick={() => { setSessionStatus("FIN"); setIaVerdict("> Neural Scalp Coach : Workspace paré pour l'extraction comportementale après-séance."); }}
              className={`flex-1 py-1.5 rounded-lg text-[9px] font-black uppercase tracking-wider transition-all flex items-center justify-center gap-2 ${sessionStatus === "FIN" ? "bg-red-600 text-white shadow-md shadow-red-950/40" : "text-zinc-500 hover:text-zinc-300"}`}
            >
              <Square size={10} /> Fin Session
            </button>
          </div>

          {/* Module Inputs Quantitatifs Fixes */}
          {sessionStatus === "DEBUT" && (
            <div className="flex items-center gap-4 border-l border-white/5 pl-4 animate-in fade-in duration-200">
              <div className="flex flex-col">
                <span className="text-[8px] font-black uppercase text-zinc-500 tracking-tight flex items-center gap-1"><LineChart size={10}/> Actif Scalpé</span>
                <input value={actif} onChange={(e) => setActif(e.target.value.toUpperCase())} className="w-20 bg-transparent text-xs font-black text-blue-400 focus:outline-none placeholder:text-zinc-800 uppercase tracking-wider mt-0.5" />
              </div>

              <div className="flex flex-col border-l border-white/5 platform-input pl-4">
                <span className="text-[8px] font-black uppercase text-zinc-500 tracking-tight">Biais Directionnel</span>
                <select value={biais} onChange={(e) => setBiais(e.target.value)} className="bg-transparent text-xs font-bold text-zinc-200 focus:outline-none mt-0.5 outline-none cursor-pointer">
                  <option value="LONG">LONG (Achat)</option>
                  <option value="SHORT">SHORT (Vente)</option>
                  <option value="NEUTRE">NEUTRE (Observation)</option>
                </select>
              </div>

              <div className="flex flex-col border-l border-white/5 pl-4 w-[120px]">
                <div className="flex justify-between text-[8px] font-black uppercase text-zinc-500">
                  <span>Conviction</span>
                  <span className="text-blue-400 font-bold">{conviction}%</span>
                </div>
                <input type="range" min="0" max="100" value={conviction} onChange={(e) => setConviction(parseInt(e.target.value))} className="w-full accent-blue-600 h-0.5 mt-1 bg-zinc-800 rounded-full" />
              </div>
            </div>
          )}

          {/* Module d'affichage du total de trades compilés */}
          {sessionStatus === "FIN" && (
            <div className="flex items-center gap-4 border-l border-white/5 pl-4 font-sans text-xs animate-in fade-in duration-300">
              <div className="flex flex-col">
                <span className="text-[8px] font-black uppercase text-zinc-500 tracking-tight">Compteur de Fréquence</span>
                <span className="text-white font-mono font-black mt-0.5">Total: {scalcWin + scalcLoss + scalcBe} Trades</span>
              </div>
            </div>
          )}

          {/* Badge Mode Actif Unifié */}
          <div className={`flex items-center gap-1.5 px-3 py-1 bg-white/5 rounded-full border border-white/10 text-[9px] font-mono font-black ${sessionStatus === "DEBUT" ? "text-blue-400" : "text-red-400"}`}>
            <Gauge size={12} />
            <span>{sessionStatus === "DEBUT" ? "ANTE_MARKET_PLAN" : "POST_SESSION_AUDIT"}</span>
          </div>
        </div>

        {/* CONTENEUR SPLIT BILATÉRAL */}
        <div className="flex-1 flex gap-4 min-h-0 w-full">
          
          {/* PANNEAU GAUCHE : WORKSPACE SÉMANTIQUE ET QUESTIONNAIRE PROTOCOLE */}
          <div className="flex-[1.2] flex flex-col gap-4 h-full">
            
            {/* Boîte des directives du Protocole */}
            <div className="h-[40%] bg-[#0F1117]/95 border border-white/10 rounded-[32px] p-5 overflow-y-auto custom-scrollbar shadow-2xl relative">
              <div className="absolute top-6 right-6 text-white/5 pointer-events-none"><Terminal size={80} /></div>
              
              <div className="flex items-center gap-2 mb-3 border-b border-white/5 pb-2">
                <Target size={14} className={sessionStatus === "DEBUT" ? "text-blue-400" : "text-red-400"} />
                <span className="text-[9px] font-black uppercase tracking-widest text-zinc-400">
                  {sessionStatus === "DEBUT" ? "Protocol_Pre_Flight_Instructions" : "Protocol_After_Action_Review"}
                </span>
              </div>

              {/* LOGIQUE QUESTIONNAIRE SÉPARÉE ET COMPLÈTE */}
              <div className="animate-in fade-in duration-300 font-sans">
                {sessionStatus === "DEBUT" ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-3 border-r border-white/5 pr-2">
                      <div className="text-blue-400 font-black uppercase text-[9px] tracking-widest">1 — Analyse Macro (Fondamentale)</div>
                      <div className="text-[11px] text-zinc-400">
                        • Analyse-tu le calendrier économique pour les news High Impact (CPI, NFP, taux) ? 
                        <HelpTooltip title="Calendrier Économique" content="Ne scalpe jamais une news majeure sans préparation." subVideos={[educationalContent.fundamental.calendrier]} onOpenVideo={(url: string) => setPlayingVideoUrl(getEmbedUrl(url))} />
                      </div>
                      <div className="text-[11px] text-zinc-400">• As-tu vérifié la corrélation actuelle du DXY (Dollar) pour confirmer ton biais ? 
                        <HelpTooltip title="Corrélation Forex" content="Le DXY est le pivot du marché." subVideos={[educationalContent.fundamental.rendements]} onOpenVideo={(url: string) => setPlayingVideoUrl(getEmbedUrl(url))} />
                      </div>
                      <div className="text-[11px] text-zinc-400">• Le sentiment actuel du marché (Risk-on/Risk-off) est-il favorable ? 
                        <HelpTooltip title="Géopolitique" content="Les tensions mondiales créent de la volatilité." subVideos={[educationalContent.fundamental.geopolitique]} onOpenVideo={(url: string) => setPlayingVideoUrl(getEmbedUrl(url))} />
                      </div>
                    </div>
                    <div className="space-y-3 pl-2">
                      <div className="text-blue-400 font-black uppercase text-[9px] tracking-widest">2 — Intentions Techniques</div>
                      <div className="text-[11px] text-zinc-400">• Quel setup institutionnel vas-tu cibler aujourd'hui ? (Ex: Breaker, FVG, Liquidity Sweep) 
                        <HelpTooltip title="Setup Scalp" content="Sois sélectif, attends ton setup." subVideos={educationalContent.technical.scalpSetups} onOpenVideo={(url: string) => setPlayingVideoUrl(getEmbedUrl(url))} />
                      </div>
                      <div className="text-[11px] text-zinc-400">• As-tu déterminé ton risque maximal autorisé pour cette session ?</div>
                      <div className="text-[11px] text-zinc-400">• Ton niveau de clarté mentale est-il à 100% pour scalper ?</div>
                    </div>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-1 border-r border-white/5 pr-2">
                      <div className="text-red-400 font-black uppercase text-[9px] tracking-widest">1 — Résultat & Métriques de Clôture</div>
                      <div className="text-[11px] text-zinc-400">Veuillez formuler une rédaction de fin de session qui prendra en compte les points ci-dessous :</div>
                      <div className="text-[11px] text-zinc-400">• Nombre exact de micro-scalps exécutés : <span className="text-white font-bold">{scalcWin + scalcLoss + scalcBe}</span></div>
                      <div className="text-[11px] text-zinc-400">• Ratio exact de trades gagnants / perdants : <span className="text-white font-bold">{scalcWin}W - {scalcLoss}L</span></div>
                    </div>
                    <div className="space-y-1 pl-2 text-[11px] text-zinc-400">
                      <div className="flex items-center gap-1.5 text-red-500 font-black uppercase text-[9px] tracking-widest"><ShieldAlert size={12}/> Action_Requise</div>
                      <div>• Respect du plan, des tailles et du Drawdown maximal ?</div>
                      <div>• Détection de sur-trading ou d&apos;impulsivité mécanique ?</div>
                      <div className="text-zinc-100 italic">• Note finale de propreté d&apos;exécution sur 10.</div>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Boîte de Rédaction Sémantique */}
            <div className="flex-1 bg-[#0F1117] border border-white/10 rounded-[32px] p-5 flex flex-col relative group shadow-inner">
              <span className="absolute top-3 right-6 text-[8px] font-black text-zinc-600 tracking-widest">WORKSPACE_ACTIVE_SCALP</span>
              <textarea 
                value={sessionStatus === "DEBUT" ? preSessionText : postSessionText}
                onChange={(e) => sessionStatus === "DEBUT" ? setPreSessionText(e.target.value) : setPostSessionText(e.target.value)}
                placeholder={sessionStatus === "DEBUT" ? "Rédigez ici vos configurations d'entrée, votre gestion de carnet et les objectifs de gains en suivant le cadre algorithmique..." : "Rédigez l'audit comportemental complet (Comportement face au slippage, gestion des pertes rapides, erreurs de clic, sur-trading...)"}
                className="flex-1 bg-transparent border-none outline-none text-zinc-200 text-xs font-light leading-relaxed resize-none placeholder:text-zinc-800 custom-scrollbar font-sans"
              />
              <div className="mt-3 pt-2 border-t border-white/5 flex justify-between items-center font-sans">
                <span className="text-[9px] font-mono text-zinc-600">Characters : {sessionStatus === "DEBUT" ? preSessionText.length : postSessionText.length}</span>
                <div className="flex gap-2">
                  {sessionStatus === "DEBUT" ? (
                    <>
                      <button onClick={savePreSession} disabled={isLoading} className="flex items-center gap-1.5 px-4 py-2 bg-zinc-900 border border-white/5 rounded-xl text-zinc-400 font-black text-[9px] uppercase tracking-wider hover:text-white disabled:opacity-40 transition-all">
                        <Save size={12} /> Enregistrer Brouillon
                      </button>
                      <button onClick={launchPreSessionAudit} disabled={isLoading} className="flex items-center gap-1.5 px-4 py-2 bg-blue-600 rounded-xl text-white font-black text-[9px] uppercase tracking-wider hover:bg-blue-500 disabled:opacity-40 transition-all">
                        <Zap size={12} /> Activer la Session
                      </button>
                    </>
                  ) : (
                    <button onClick={launchIaAudit} disabled={isLoading} className="flex items-center gap-1.5 px-5 py-2 bg-red-600 rounded-xl text-white font-black text-[9px] uppercase tracking-wider hover:bg-red-500 disabled:opacity-40 transition-all shadow-lg shadow-red-950/20">
                      <Activity size={12} /> Clôturer & Lancer l&apos;Audit IA
                    </button>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* PANNEAU DROIT : CONSOLE DU TERMINAL IA & LIVE SCALPER TACTICAL SCORECARD */}
          <div className="w-[360px] flex flex-col gap-4 h-full">
            
            {/* LIVE SCALPER TACTICAL SCORECARD */}
            <div className="p-4 bg-[#0F1117]/95 border border-white/10 rounded-2xl space-y-4 shadow-2xl font-sans text-left animate-in slide-in-from-right-4 duration-300">
              <div className="flex items-center justify-between border-b border-white/5 pb-2">
                <div className="flex items-center gap-2">
                  <History size={14} className="text-blue-400" />
                  <span className="text-[9px] font-black uppercase tracking-wider text-zinc-400">Live Execution Log (Par Trade)</span>
                </div>
                <span className="text-[8px] font-mono text-zinc-500 tracking-tighter">SMC HIGH-SPEED</span>
              </div>

              <div className="space-y-2.5">
                <div className="flex items-center justify-between bg-black/20 p-2 border border-white/5 rounded-xl">
                  <span className="text-[11px] font-bold text-zinc-400">🟢 MICRO-TRADES WIN :</span>
                  <div className="flex items-center gap-2">
                    <button onClick={() => setScalcWin(prev => Math.max(0, prev - 1))} className="p-1 bg-zinc-900 border border-white/5 text-zinc-400 hover:text-white rounded transition-colors"><Minus size={10}/></button>
                    <span className="w-6 text-center font-mono font-black text-xs text-green-400">{scalcWin}</span>
                    <button onClick={() => setScalcWin(prev => prev + 1)} className="p-1 bg-zinc-900 border border-white/5 text-zinc-400 hover:text-white rounded transition-colors"><Plus size={10}/></button>
                  </div>
                </div>

                <div className="flex items-center justify-between bg-black/20 p-2 border border-white/5 rounded-xl">
                  <span className="text-[11px] font-bold text-zinc-400">🔴 MICRO-TRADES LOSS :</span>
                  <div className="flex items-center gap-2">
                    <button onClick={() => setScalcLoss(prev => Math.max(0, prev - 1))} className="p-1 bg-zinc-900 border border-white/5 text-zinc-400 hover:text-white rounded transition-colors"><Minus size={10}/></button>
                    <span className="w-6 text-center font-mono font-black text-xs text-red-400">{scalcLoss}</span>
                    <button onClick={() => setScalcLoss(prev => prev + 1)} className="p-1 bg-zinc-900 border border-white/5 text-zinc-400 hover:text-white rounded transition-colors"><Plus size={10}/></button>
                  </div>
                </div>

                <div className="flex items-center justify-between bg-black/20 p-2 border border-white/5 rounded-xl">
                  <span className="text-[11px] font-bold text-zinc-400">⚪ MICRO-TRADES BE :</span>
                  <div className="flex items-center gap-2">
                    <button onClick={() => setScalcBe(prev => Math.max(0, prev - 1))} className="p-1 bg-zinc-900 border border-white/5 text-zinc-400 hover:text-white rounded transition-colors"><Minus size={10}/></button>
                    <span className="w-6 text-center font-mono font-black text-xs text-zinc-300">{scalcBe}</span>
                    <button onClick={() => setScalcBe(prev => prev + 1)} className="p-1 bg-zinc-900 border border-white/5 text-zinc-400 hover:text-white rounded transition-colors"><Plus size={10}/></button>
                  </div>
                </div>
              </div>
            </div>

            {sessionStatus === "FIN" && (
              <div className="p-4 bg-red-500/[0.02] border border-red-500/20 rounded-2xl flex gap-3 items-start animate-in slide-in-from-right-4 duration-300 text-left font-sans">
                <Trophy size={16} className="text-red-400 shrink-0 mt-0.5" />
                <div className="space-y-1">
                  <span className="text-[9px] font-black uppercase text-red-400 tracking-wider block">Head of Desk Rule</span>
                  <p className="text-[10px] text-zinc-400 leading-normal italic">&quot;Un trade gagnant hors-plan est une perte de discipline. Un trade perdant dans le plan est une victoire systémique.&quot;</p>
                </div>
              </div>
            )}

            {/* Terminal principal */}
            <div className={`flex-1 bg-black/70 border rounded-[28px] p-5 font-mono text-[11px] leading-relaxed relative overflow-hidden shadow-2xl ${sessionStatus === "DEBUT" ? "border-blue-500/20" : "border-red-500/20"}`}>
              <div className={`flex items-center gap-1.5 mb-3 border-b border-white/5 pb-2 ${sessionStatus === "DEBUT" ? "text-blue-400" : "text-red-400"}`}>
                <Activity size={12} className={isLoading ? "animate-spin" : "animate-pulse"} />
                <span className="font-black uppercase tracking-wider text-[8px] font-sans">
                  {sessionStatus === "DEBUT" ? "Neural_Scalp_Coach_v2" : "Performance_Behavior_Audit"}
                </span>
              </div>
              
              <div className="text-zinc-300 text-left custom-scrollbar overflow-y-auto h-[calc(100%-35px)] font-sans font-light">
                {iaVerdict.split('\n').map((line, i) => (
                  <div key={i} className={line.startsWith('>') ? `${sessionStatus === "DEBUT" ? "text-blue-400" : "text-red-400"} font-black tracking-tight mb-2` : 'text-zinc-300 text-[11px] leading-relaxed'}>
                    {line}
                  </div>
                ))}
              </div>
              <div className={`absolute bottom-0 left-0 w-full h-0.5 ${sessionStatus === "DEBUT" ? "bg-blue-600/30" : "bg-red-600/30"}`} />
            </div>

            {/* Action bar */}
            <div className="grid grid-cols-3 gap-2 font-sans">
              <button onClick={reinitialiserWorkspace} title="Purge Cache Session" className="py-2.5 bg-zinc-900 border border-white/5 rounded-xl text-zinc-500 flex items-center justify-center hover:text-red-400 transition-all shadow-md">
                <RotateCcw size={14} />
              </button>
              <button onClick={() => setShowCalc(true)} className="col-span-2 py-2.5 bg-zinc-900 border border-white/5 rounded-xl text-zinc-400 font-black text-[9px] uppercase tracking-wider flex items-center justify-center gap-2 hover:bg-zinc-800 transition-all shadow-md">
                <Calculator size={12} className="text-blue-400" /> Calculateur Lots
              </button>
            </div>

          </div>
        </div>
        {playingVideoUrl && (
          <div className="fixed inset-0 bg-black/95 z-[200] flex items-center justify-center p-4 lg:p-12 backdrop-blur-xl" onClick={closeVideo}>
            <div className="relative bg-[#0a0a0a] border border-white/10 w-full max-w-5xl aspect-video rounded-[32px] shadow-2xl p-2" onClick={(e) => e.stopPropagation()}>
              <button onClick={closeVideo} className="absolute -top-12 right-0 text-zinc-500 hover:text-white transition-all">
                <X size={24} />
              </button>
              
              <iframe
                className="w-full h-full rounded-[24px]"
                src={playingVideoUrl}
                title="Vidéo éducative"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
              />
            </div>
          </div>
        )}

      </div>
    </AuroraBackground>
  );
}