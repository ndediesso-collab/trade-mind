"use client";

import React, { useState, useEffect } from "react";
import { AuroraBackground } from "@/components/ui/aurora-background";
import { 
  ArrowLeft, 
  Calculator, 
  Save, 
  RotateCcw, 
  BrainCircuit, 
  Target, 
  ShieldAlert, 
  Activity,
  X,
  Zap,
  GraduationCap,
  Send,
  ShieldCheck,
  Flame,
  LineChart,
  Lock,
  Info,
  PlayCircle,
  MessageSquare
} from "lucide-react";
import Link from "next/link";
import ReactPlayer from 'react-player';

// --- AJOUTE CE BLOC ICI, JUSTE AVANT TON EXPORT ---

export default function SwingAnalysis() {
  
  const [playingVideoUrl, setPlayingVideoUrl] = useState<string | null>(null);
  const closeVideo = () => setPlayingVideoUrl(null);

  // 1. On utilise 'any' pour le dictionnaire afin de désactiver les erreurs de typage strict
  const glossary: any = {
    "OB": { definition: "L'Order Block est une zone d'accumulation institutionnelle.", url: "https://youtu.be/NYBvIcPX7XI?si=jmVr_qc31cduWcR_" },
    "FVG": { definition: "Le Fair Value Gap est un déséquilibre du prix.", url: "https://youtu.be/skk0sm6LN6M?si=momYUhKK-E1xLAuT" },
    "Liquidity": { definition: "Zones de concentration d'ordres stop.", url: "https://youtu.be/QPQWlXQ-El4?si=LgdQ-7m1VMiaiEwR" },
    "Taux": { definition: "Différentiel de taux directeur entre deux(en générale) banques centrales.", url: "https://youtu.be/vAyBiASOne4?si=s4gzsbJPko6rlyZZ" },
    "Inflation": { definition: "Mesure de la hausse des prix à la consommation (CPI).", url: "https://youtu.be/40dtvvLCUCQ?si=wT8GAqsts9QekKsg" },
    "Rendements": { definition: "Le rendement des obligations d'État (Yields) influence la devise.", url: "https://youtu.be/fAIpO2Xu8FI?si=1beP53nshsUraYOd" },
    "Geopolitique": { definition: "Influence des tensions internationales sur le marché.", url: "https://youtu.be/Ulq5vBAf9SI?si=xZ7vacvuOoUEpmfz" },
    "Sentiment": { definition: "L'état d'esprit global du marché (Risk-on(appétit du risque)/Risk-off(peur du risque)).", url: "https://youtu.be/3ID2NFqgaCM?si=TBFAJoOz_L5MCKlQ" },
    "Tendance": { definition: "Direction générale des prix (sommets/creux).", url: "https://youtu.be/7_oLrv-TIAA?si=kjzxL8l2RhlMXf_c" }
  };
  const getEmbedUrl = (url: string) => {
  if (!url) return "";
  // Extrait l'ID de la vidéo
  const videoId = url.split('/').pop()?.split('?')[0] || url.split('v=')[1]?.split('&')[0];
  return `https://www.youtube.com/embed/${videoId}?autoplay=1`;
  };
  const HelpTooltip = ({ conceptKey, onOpenVideo }: { conceptKey: string, onOpenVideo: (url: string) => void }) => {
    const [show, setShow] = useState(false);
    // On accède au glossaire sans typage strict pour éviter le rouge
    const data = glossary[conceptKey];
    
    if (!data) return null;

    return (
      <div className="relative inline-block ml-1" onMouseEnter={() => setShow(true)} onMouseLeave={() => setShow(false)}>
        <Info size={12} className="inline text-blue-500 cursor-help" />
        {show && (
          <div className="absolute z-[100] left-0 bottom-6 w-64 bg-[#161B22] border border-blue-500/30 p-4 rounded-2xl shadow-2xl">
            <p className="text-[10px] text-zinc-300 mb-3">{data.definition}</p>
            <button 
              onClick={() => onOpenVideo(data.url)} 
              className="flex items-center gap-2 text-[9px] font-black uppercase text-blue-400 hover:text-white transition-colors"
            >
              <PlayCircle size={12} /> Voir vidéo
            </button>
          </div>
        )}
      </div>
    );
  };
  

  // --- ÉTATS GÉNÉRAUX & IDENTITY ---
  const [position, setPosition] = useState<"ACHAT" | "VENTE" | "NEUTRE">("NEUTRE");
  const [statut, setStatut] = useState<"BROUILLON" | "WIN" | "LOSS">("BROUILLON");
  const [actif, setActif] = useState("");
  const [analyse, setAnalyse] = useState("");
  const [iaFeedback, setIaFeedback] = useState("> MENTOR_IA: Système prêt. En attente de votre saisie structurée.");
  const [isLoading, setIsLoading] = useState(false);
  
  // --- EXTRACTION BARRE TECHNIQUE (DATA PRO) ---
  const [conviction, setConviction] = useState(50);
  const [entryPrice, setEntryPrice] = useState("");
  const [stopLoss, setStopLoss] = useState("");
  const [takeProfit, setTakeProfit] = useState("");
  const [calculatedRR, setCalculatedRR] = useState<number | null>(null);

  // --- ÉTATS NOUVEAUX : LE CHAT COMPAGNON GUARDIAN ---
  const [consoleTab, setConsoleTab] = useState("ARCHITECTE"); // "ARCHITECTE" | "GUARDIAN"
  const [guardianInput, setGuardianInput] = useState("");
  const [guardianHistory, setGuardianHistory] = useState<string[]>([]);
  const [isGuardianLoading, setIsGuardianLoading] = useState(false);


  // Id du trade actuellement chargé pour permettre la mise à jour (évite les doublons)
  const [currentTradeId, setCurrentTradeId] = useState<number | null>(null);


  // --- CALCUL AUTOMATIQUE DU RR EN TEMPS RÉEL ---
  useEffect(() => {
    const entry = parseFloat(entryPrice);
    const sl = parseFloat(stopLoss);
    const tp = parseFloat(takeProfit);

    if (entry && sl && tp && entry !== sl) {
      const risk = Math.abs(entry - sl);
      const reward = Math.abs(tp - entry);
      const rrRatio = reward / risk;
      setCalculatedRR(parseFloat(rrRatio.toFixed(1)));
    } else {
      setCalculatedRR(null);
    }
  }, [entryPrice, stopLoss, takeProfit]);

  // --- ARBITRAGE ET RÉINJECTION SUPABASE DIRECTE VIA CACHE DE ROUTAGE ---
  useEffect(() => {
    const checkRestaurationSupabase = async () => {
      // Extraction du ticket de l'historique
      const hash = localStorage.getItem("tm_swing_cache") || sessionStorage.getItem("swing_restore");
      if (hash) {
        try {
          const target = JSON.parse(hash);
          if (target.trade_id) {
            setIaFeedback(`> SYSTÈME: Interpellation directe de la base SQL Supabase pour le dossier #TM-${target.trade_id}...`);
            
            const res = await fetch(`https://trade-mind-w6rs.onrender.com/historique/get/${target.trade_id}`);
            if (res.ok) {
              const fullTrade = await res.json();
              
              // Injection synchronisée de tous les attributs de la base de données
              setCurrentTradeId(fullTrade.id);
              setActif(fullTrade.actif || "");
              setAnalyse((fullTrade.analyse || "").replace("[PLAN AVANT-TRADE] : ", ""));
              setConviction(fullTrade.conviction || 50);
              setPosition(fullTrade.position || "Neutre");
              setStatut(fullTrade.statut || "Brouillon");
              setEntryPrice(fullTrade.entry_price || "");
              setStopLoss(fullTrade.stop_loss || "");
              setTakeProfit(fullTrade.take_profit || "");
              if (fullTrade.feedback) setIaFeedback(fullTrade.feedback);
              
              setIaFeedback(prev => `✅ SYNAPSE COMPLÈTE: Données rechargées depuis le Cloud.\n` + prev);
              
              // Nettoyage des déclencheurs pour sceller la session active
              localStorage.removeItem("tm_swing_cache");
              sessionStorage.removeItem("swing_restore");
              return; // Coupe pour éviter d'écraser avec le cache v2 local
            }
          }
        } catch (err) {
          console.error("Échec du pont de réinjection Supabase:", err);
        }
      }

      // Fallback historique local si aucune demande cloud n'est interceptée
      const saved = localStorage.getItem("tm_swing_cache_v2");
      if (saved) {
        try {
          const parsed = JSON.parse(saved);
          setCurrentTradeId(parsed.currentTradeId || null);
          setActif(parsed.actif || "");
          setAnalyse(parsed.analyse || "");
          setConviction(parsed.conviction || 50);
          setPosition(parsed.position || "Neutre");
          setStatut(parsed.statut || "Brouillon");
          setEntryPrice(parsed.entryPrice || "");
          setStopLoss(parsed.stopLoss || "");
          setTakeProfit(parsed.takeProfit || "");
          if (parsed.feedback) setIaFeedback(parsed.feedback);
          if (parsed.currentStep !== undefined) setCurrentStep(parsed.currentStep);
          if (parsed.isSuiviActive !== undefined) setIsSuiviActive(parsed.isSuiviActive);
          if (parsed.guardianHistory) setGuardianHistory(parsed.guardianHistory);
        } catch (e) { console.error("Erreur cache:", e); }
      }
    };

    checkRestaurationSupabase();
  }, []);

  useEffect(() => {
    const handler = setTimeout(() => {
      const cache = { 
        currentTradeId, actif, analyse, conviction, position, statut, 
        currentStep, isSuiviActive, feedback: iaFeedback,
        entryPrice, stopLoss, takeProfit, guardianHistory
      };
      localStorage.setItem("tm_swing_cache_v2", JSON.stringify(cache));
    }, 500);
    return () => clearTimeout(handler);
  }, [currentTradeId, actif, analyse, conviction, position, statut, currentStep, isSuiviActive, iaFeedback, entryPrice, stopLoss, takeProfit, guardianHistory]);

  // --- MODAL CALCULATEUR ---
  const [showCalc, setShowCalc] = useState(false);
  const [calcData, setCalcData] = useState({ balance: "1000", risk: "1", pips: "50" });
  const [lotResult, setLotResult] = useState<number | null>(null);

  const calculatePositionSize = () => {
    const bal = parseFloat(calcData.balance);
    const riskPct = parseFloat(calcData.risk) / 100;
    const pips = parseFloat(calcData.pips);
    if (bal && riskPct && pips) {
      const size = (bal * riskPct) / (pips * 10);
      setLotResult(parseFloat(size.toFixed(2)));
    }
  };

  // --- DISPATCHER DU CHAT DÉDIÉ AU SÉCURISATEUR SENSORIEL (GUARDIAN) ---
  const handleGuardianMessageSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!guardianInput.trim() || isGuardianLoading) return;

    const userMsg = guardianInput.trim();
    setGuardianInput("");
    setGuardianHistory(prev => [...prev, `Trader: ${userMsg}`]);
    setIsGuardianLoading(true);

    try {
      const response = await fetch("https://trade-mind-w6rs.onrender.com/analyse/guardian", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: userMsg,
          analyse_complete: analyse || "Aucune thèse rédigée pour le moment.",
          actif: actif
        })
      });

      if (response.ok) {
        const data = await response.json();
        setGuardianHistory(prev => [...prev, `Guardian: ${data.verdict}`]);
      } else {
        setGuardianHistory(prev => [...prev, "Guardian: ❌ Synapse déconnectée du canal d'émotion."]);
      }
    } catch (err) {
      setGuardianHistory(prev => [...prev, "Guardian: ❌ Erreur réseau. Le moteur de discipline n'est pas joignable."]);
    } finally {
      setIsGuardianLoading(false);
    }
  };

  // --- HANDLERS CONTROLES ---
  const updateStatut = (newStatut: "BROUILLON" | "WIN" | "LOSS") => {
  if (statut !== "BROUILLON") return; // Empêche le changement si déjà classé
  setStatut(newStatut);
  };
  const handleAnalyse = async () => {
    if (!analyse || !actif) {
      setIaFeedback("> ERREUR: L'actif et le texte de l'analyse sont requis.");
      return;
    }
    if (calculatedRR !== null && calculatedRR < 2) {
      setIaFeedback("> BLOCAGE GESTION DU RISQUE: Le ratio RR calculé est inférieur à 1:2. Trade rejeté d'office par le système.");
      return;
    }
    if (conviction < 50) {
      setIaFeedback("> BLOCAGE PSYCHOLOGIQUE: Une conviction inférieure à 50% dénote un manque de clarté. Exécution interdite.");
      return;
    }

    setIsLoading(true);
    setConsoleTab("ARCHITECTE"); // Forcer le focus visuel sur l'audit technique
    try {
      const res = await fetch("https://trade-mind-w6rs.onrender.com/analyse/swing", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          actif, 
          analyse, 
          conviction, 
          position, 
          statut,  
          step: currentStep, 
          type: "SWING",
          entry_price: entryPrice,
          stop_loss: stopLoss,
          take_profit: takeProfit,
          calculated_rr: calculatedRR
        })
      });
      const data = await res.json();
      
  const handleSave = async () => {
  if (statut !== "BROUILLON") {
     setIaFeedback("> SYSTÈME: Analyse verrouillée. Impossible de modifier un trade classé WIN/LOSS.");
     return;
  }
    setIaFeedback("> SYSTÈME: Injection SQL en cours....");
    try {
      const res = await fetch("https://trade-mind-w6rs.onrender.com/database/save", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          id: currentTradeId, // Passage de l'ID s'il s'agit d'un brouillon existant
          actif, 
          analyse, 
          conviction, 
          position, 
          statut,  
          type: "SWING",
          entry_price: entryPrice,
          stop_loss: stopLoss,
          take_profit: takeProfit,
          calculated_rr: calculatedRR
        })
      });
      const resData = await res.json();
      if (res.ok) {
        if (resData.trade_id) setCurrentTradeId(resData.trade_id);
        setIaFeedback("> SYSTÈME: Analyse archivée avec succès dans l'historique Supabase.");
      } else {
        setIaFeedback("> ERREUR: Rejet de l'écriture par Supabase.");
      }
    } catch (e) {
      setIaFeedback("> ERREUR: Connexion au pont d'archivage impossible.");
    }
  };

  const handleReset = () => {
    if(confirm("Écarter le protocole en cours et purger la mémoire de travail ?")) {
        setAnalyse(""); setActif(""); setEntryPrice(""); setStopLoss(""); setTakeProfit(""); setCurrentStep(0);
        setIsSuiviActive(false); setGuardianHistory([]); setIaFeedback("> SYSTÈME: Cache vidé."); setCurrentTradeId(null);
        localStorage.removeItem("tm_swing_cache_v2");
    }
  };

  return (
    <AuroraBackground>
      <div className="relative z-10 w-full h-screen flex flex-col p-4 overflow-hidden bg-zinc-950/50 backdrop-blur-[2px]">
        
        {/* MODAL CALCULATEUR DE RISQUE */}
        {showCalc && (
          <div className="absolute inset-0 z-50 flex items-center justify-center bg-black/95 backdrop-blur-md animate-in fade-in zoom-in-95 duration-200">
            <div className="w-[420px] bg-[#0F1117] border border-blue-500/30 rounded-[32px] p-8 shadow-2xl">
              <div className="flex justify-between items-center mb-8">
                <div className="flex items-center gap-3">
                  <Calculator className="text-blue-400" size={24} />
                  <h3 className="text-sm font-black uppercase tracking-widest text-white font-sans">Risk Calculator</h3>
                </div>
                <button onClick={() => setShowCalc(false)} className="p-2 text-zinc-500 hover:text-white transition-all"><X size={20} /></button>
              </div>
              <div className="space-y-6">
                <div className="space-y-2 font-sans text-left">
                   <label className="text-[10px] font-black text-blue-400 uppercase tracking-widest ml-1">Capital Total ($)</label>
                   <input type="number" value={calcData.balance} onChange={(e) => setCalcData({...calcData, balance: e.target.value})} className="w-full bg-zinc-900 border border-white/10 rounded-2xl p-4 text-white text-lg font-mono outline-none focus:border-blue-500 transition-all shadow-inner" placeholder="10000" />
                </div>
                <div className="grid grid-cols-2 gap-4 font-sans text-left">
                  <div className="space-y-2">
                    <label className="text-[10px] font-black text-blue-400 uppercase tracking-widest ml-1">Risque (%)</label>
                    <input type="number" value={calcData.risk} onChange={(e) => setCalcData({...calcData, risk: e.target.value})} className="w-full bg-zinc-900 border border-white/10 rounded-2xl p-4 text-white text-lg font-mono outline-none focus:border-blue-500 transition-all shadow-inner" placeholder="1" />
                  </div>
                  <div className="space-y-2">
                    <label className="text-[10px] font-black text-blue-400 uppercase tracking-widest ml-1">Invalidation (Pips)</label>
                    <input type="number" value={calcData.pips} onChange={(e) => setCalcData({...calcData, pips: e.target.value})} className="w-full bg-zinc-900 border border-white/10 rounded-2xl p-4 text-white text-lg font-mono outline-none focus:border-blue-500 transition-all shadow-inner" placeholder="20" />
                  </div>
                </div>
                <button onClick={calculatePositionSize} className="w-full py-5 bg-blue-600 rounded-2xl font-black text-[11px] uppercase tracking-[0.3em] text-white hover:bg-blue-500 active:scale-[0.98] transition-all shadow-lg shadow-blue-900/40 font-sans">Calculer le Volume</button>
                <div className={`mt-4 p-6 rounded-3xl border transition-all duration-500 ${lotResult !== null ? 'bg-blue-500/10 border-blue-500/40 opacity-100' : 'bg-zinc-900/50 border-white/5 opacity-40'}`}>
                  <div className="flex justify-between items-end font-sans">
                    <div className="space-y-1">
                      <p className="text-[9px] font-black text-zinc-500 uppercase tracking-widest">Dimensionnement</p>
                      <h4 className="text-xs font-bold text-white uppercase tracking-tighter text-left">Taille de lot optimale</h4>
                    </div>
                    <div className="text-right">
                      <span className="text-4xl font-mono font-black text-white drop-shadow-[0_0_15px_rgba(59,130,246,0.5)]">{lotResult !== null ? lotResult : "0.00"}</span>
                      <span className="ml-2 text-xs font-black text-blue-400 uppercase">Lots</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 1. TOP HEADER NAVIGATION (MODIFIÉ) */}
        <header className="h-14 flex items-center justify-between px-6 mb-3 bg-[#0F1117]/90 backdrop-blur-md border border-white/10 rounded-xl shadow-2xl">
          <Link href="/" className="text-zinc-400 hover:text-white flex items-center gap-2 transition-all group font-sans">
            <ArrowLeft size={16} className="group-hover:-translate-x-1 transition-transform" /> 
            <span className="text-[10px] font-bold uppercase tracking-widest text-zinc-100">Trade Mind Hub</span>
          </Link>
          <div className="flex items-center gap-2 px-4 py-1.5 bg-zinc-900/50 rounded-xl border border-white/5">
            <span className="text-[10px] font-black uppercase tracking-widest text-zinc-300">Audit Stratégique Scalp</span>
          </div>
          <div className="flex items-center gap-2 px-3 py-1 bg-red-500/10 rounded-full border border-red-500/30">
            <div className="w-1.5 h-1.5 bg-red-400 rounded-full animate-pulse" />
            <span className="text-[9px] font-black text-red-400 tracking-[0.2em] uppercase font-sans">MODE_SCALP</span>
          </div>
        </header>

        {/* 2. BARRE TECHNIQUE (DATA PRO HUB) */}
        <section className="p-4 mb-3 bg-[#0F1117]/95 border border-white/10 rounded-2xl flex flex-wrap items-center justify-between gap-6 shadow-2xl relative overflow-hidden">
          <div className="absolute top-0 left-0 h-full w-[2px] bg-blue-500" />
          
          {/* BLOC 1: ACTIF & PRIX */}
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-3">
              <div className="p-2.5 bg-zinc-900 rounded-xl border border-white/5 text-blue-400"><LineChart size={16} /></div>
              <div className="flex flex-col font-sans">
                <span className="text-[8px] font-black uppercase text-zinc-500 tracking-wider">Actif</span>
                <input value={actif} onChange={(e) => setActif(e.target.value.toUpperCase())} placeholder="EURUSD" className="w-20 bg-transparent text-sm font-black text-blue-400 focus:outline-none placeholder:text-zinc-800 tracking-widest uppercase mt-0.5" />
              </div>
            </div>

            <div className="flex items-center gap-4 border-l border-white/5 pl-4">
              <div className="flex flex-col">
                <span className="text-[8px] font-black uppercase text-zinc-500">Entrée</span>
                <input type="number" step="0.0001" value={entryPrice} onChange={(e) => setEntryPrice(e.target.value)} className="w-20 bg-transparent text-sm font-mono font-bold text-white focus:outline-none" placeholder="1.0850" />
              </div>
              <div className="flex flex-col">
                <span className="text-[8px] font-black uppercase text-zinc-500">SL</span>
                <input type="number" step="0.0001" value={stopLoss} onChange={(e) => setStopLoss(e.target.value)} className="w-20 bg-transparent text-sm font-mono font-bold text-red-400 focus:outline-none" placeholder="1.0800" />
              </div>
              <div className="flex flex-col">
                <span className="text-[8px] font-black uppercase text-zinc-500">TP</span>
                <input type="number" step="0.0001" value={takeProfit} onChange={(e) => setTakeProfit(e.target.value)} className="w-20 bg-transparent text-sm font-mono font-bold text-green-400 focus:outline-none" placeholder="1.0950" />
              </div>
            </div>
          </div>

          {/* BLOC 2: CONTRÔLES DYNAMIQUES */}
          <div className="flex items-center gap-6 border-l border-white/5 pl-6">
            <div className="flex flex-col gap-1">
              <span className="text-[8px] font-black uppercase text-zinc-500 tracking-wider">Position</span>
              <div className="flex bg-black/40 p-0.5 rounded-lg border border-white/10">
                <button 
                  onClick={() => setPosition("ACHAT")} 
                  className={`px-4 py-1.5 text-[9px] font-black uppercase rounded-md transition-all ${position === "ACHAT" ? "bg-green-500/20 text-green-400 border border-green-500/50" : "text-zinc-600 hover:text-white"}`}>
                  Achat
                </button>
                <button 
                  onClick={() => setPosition("VENTE")} 
                  className={`px-4 py-1.5 text-[9px] font-black uppercase rounded-md transition-all ${position === "VENTE" ? "bg-red-500/20 text-red-400 border border-red-500/50" : "text-zinc-600 hover:text-white"}`}>
                  Vente
                </button>
              </div>
            </div>

            <div className="flex flex-col gap-1">
              <span className="text-[8px] font-black uppercase text-zinc-500 tracking-wider">État</span>
              <div className="flex gap-2">
                <button 
                  onClick={() => setStatut("BROUILLON")}
                  className={`px-4 py-1.5 text-[9px] font-black uppercase rounded-lg border transition-all ${statut === "BROUILLON" ? "bg-zinc-800 text-white border-zinc-500" : "bg-transparent text-zinc-600 border-transparent hover:bg-zinc-900"}`}>
                  Brouillon
                </button>
                <div className="flex gap-1">
                  <button 
                    onClick={() => setStatut("WIN")}
                    className={`px-4 py-1.5 text-[9px] font-black uppercase rounded-lg border transition-all ${statut === "WIN" ? "bg-green-600 text-white border-green-500 shadow-[0_0_10px_rgba(22,163,74,0.3)]" : "bg-zinc-900 text-zinc-600 border-transparent hover:bg-zinc-800"}`}>
                    Win
                  </button>
                  <button 
                    onClick={() => setStatut("LOSS")}
                    className={`px-4 py-1.5 text-[9px] font-black uppercase rounded-lg border transition-all ${statut === "LOSS" ? "bg-red-600 text-white border-red-500 shadow-[0_0_10px_rgba(220,38,38,0.3)]" : "bg-zinc-900 text-zinc-600 border-transparent hover:bg-zinc-800"}`}>
                    Loss
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* BLOC 3: RISQUE & CALCULATEUR */}
          <div className="flex items-center gap-4 border-l border-white/5 pl-6">
            <div className="flex flex-col">
              <span className="text-[8px] font-black uppercase text-zinc-500">RR</span>
              <span className={`text-base font-mono font-black ${calculatedRR !== null && calculatedRR > 2 ? "text-green-400" : "text-zinc-400"}`}>
                {calculatedRR !== null ? `1:${calculatedRR}` : "N/A"}
              </span>
            </div>
            
            <div className="flex flex-col w-24">
              <div className="flex justify-between text-[8px] font-black uppercase text-zinc-500">
                <span>Conviction</span>
                <span className={conviction  >  70 ? 'text-yellow-400' : 'text-blue-400'}>{conviction}%</span>
              </div>
              <input type="range" min="0" max="100" value={conviction} onChange={(e) => setConviction(parseInt(e.target.value))} className="w-full h-1 bg-zinc-800 rounded-full appearance-none cursor-pointer accent-blue-600 mt-1" />
            </div>
            
            <button onClick={() => setShowCalc(true)} className="p-2 bg-blue-600/10 hover:bg-blue-600/20 text-blue-400 border border-blue-500/20 rounded-xl transition-all"><Calculator size={16} /></button>
          </div>
        </section>

        {/* 3. BLOC CENTRAL DE TRAVAIL */}
        <div className="flex h-[45%] gap-4 mb-3 min-h-0">
          
          {/* GAUCHE : PROTOCOLE GUIDELINE */}
          <div className="flex-[0.9] flex flex-col bg-[#0F1117] border border-white/10 rounded-2xl overflow-hidden shadow-2xl">
            <div className="p-2 px-4 border-b border-white/10 flex items-center justify-between bg-zinc-900/40 font-sans">
              <div className="flex items-center gap-2">
                <Target size={13} className="text-blue-400" />
                <span className="text-[9px] font-black text-zinc-400 uppercase tracking-widest">Protocol_Validation_Rules</span>
              </div>
            </div>
            
            <div className="flex-1 p-6 overflow-y-auto custom-scrollbar text-zinc-300 text-[11px] font-mono leading-relaxed bg-[radial-gradient(circle_at_top_right,rgba(37,99,235,0.03),transparent)]">
            <div className="space-y-8 animate-in fade-in duration-300">
              
              {/* En-tête de bienvenue avec la nouvelle approche */}
              <div className="p-4 bg-zinc-900 border border-zinc-800 rounded-lg">
                <h3 className="text-blue-400 font-bold uppercase text-[10px] tracking-widest mb-2">
                  Pistes de réflexion pour votre analyse
                </h3>
                <p className="text-zinc-400 text-[11px] leading-relaxed">
                  Chaque trader possède sa propre méthode. Pour garantir une analyse robuste et alignée 
                  avec nos standards de Risk Management, nous vous recommandons de vérifier les points 
                  suivants avant de valider votre plan :
                </p>
              </div>

              {/* A - IDENTITÉ & CONVICTION */}
              <section className="relative pl-5 border-l-2 border-blue-500/50 font-sans">
                <h4 className="text-base font-black bg-gradient-to-r from-blue-400 to-white bg-clip-text text-transparent mb-4 italic uppercase">A — Identité & Conviction</h4>
                <div className="space-y-4 text-zinc-400 text-[11px]">
                  <div><span className="text-blue-400 font-bold">Actif analysé :</span><br/>→ Précision recommandée : une seule paire à la fois pour éviter la dispersion.</div>
                  <div><span className="text-blue-400 font-bold">Biais & Conviction :</span> Quel est votre biais (Long/Short) ? Quel est votre niveau de conviction (0-100%) ?<br/>→ Conseil : Une conviction élevée sans justification solide cache souvent un biais psychologique (excès de confiance).</div>
                </div>
              </section>

              {/* B - ANALYSE MACRO & CONTEXTE */}
              <section className="relative pl-5 border-l-2 border-zinc-800 font-sans">
                <h4 className="text-base font-black text-zinc-200 mb-4 italic uppercase">B — Analyse Macro & Contexte</h4>
                <div className="space-y-4 text-zinc-400 text-[11px]">
                  <div><span className="text-zinc-200 font-bold">Sentiment global (Risk-on / Risk-off) :</span> Quel est l'état d'esprit actuel des marchés pour cette paire ?<HelpTooltip title="Sentiment" content="L'appétit pour le risque dicte les flux." subVideos={[educationalContent.fundamental.sentiment]} onOpenVideo={(url) => setPlayingVideoUrl(getEmbedUrl(url))} /><br/>→ Points de vigilance : Tendance, incertitude ou compression ? (Justifier avec indices ou flux).</div>
                  <div><span className="text-zinc-200 font-bold">Rendements (Yields) :</span> Quelle est la dynamique des taux de référence (ex: US02Y/GB10Y) ?<HelpTooltip title="Rendements" content="Le moteur des flux Forex." subVideos={[educationalContent.fundamental.rendements]} onOpenVideo={(url) => setPlayingVideoUrl(getEmbedUrl(url))} /></div>
                  <div><span className="text-zinc-200 font-bold">Différentiel de taux :</span> Quelle devise semble la plus attractive au niveau monétaire (taux d’intérêt et la politique monétaire) ?<HelpTooltip title="Taux" content="Comparez les banques centrales." subVideos={[educationalContent.fundamental.taux]} onOpenVideo={(url) => setPlayingVideoUrl(getEmbedUrl(url))} /></div>
                  <div><span className="text-zinc-200 font-bold">Inflation & Emploi :</span> Quelles sont les dernières données clés et leur impact probable (Selon les dernières news, quelle économie est la plus forte) ?<HelpTooltip title="Inflation" content="Données macro cruciales." subVideos={[educationalContent.fundamental.inflation]} onOpenVideo={(url) => setPlayingVideoUrl(getEmbedUrl(url))} /></div>
                  <div><span className="text-zinc-200 font-bold">Géopolitique & Corrélations :</span> Y a-t-il des facteurs externes (Or, Indices, Pétrole) qui influencent votre actif ?<HelpTooltip title="Geopolitique" content="Tensions et impacts." subVideos={[educationalContent.fundamental.geopolitique]} onOpenVideo={(url) => setPlayingVideoUrl(getEmbedUrl(url))} /></div>
                  <div><span className="text-zinc-200 font-bold">Événements à venir :</span> Le calendrier économique présente-t-il des risques (news High Impact) ?</div>
                  <div className="italic text-zinc-500">→ Piste de synthèse macro : Identifiez une dominance claire entre les deux devises.</div>
                </div>
              </section>

              {/* D - ANALYSE TECHNIQUE */}
              <section className="relative pl-5 border-l-2 border-zinc-800 font-sans">
                <h4 className="text-base font-black text-zinc-200 mb-4 italic uppercase">D — Analyse Technique</h4>
                <div className="space-y-4 text-zinc-400 text-[11px]">
                  <div><span className="text-zinc-200 font-bold">Structure & Momentum :</span> Quel est l'état de la tendance sur l’unité de temps supérieure ?<HelpTooltip title="Tendance" content="Définissez votre cadre." subVideos={[educationalContent.technical.tendance]} onOpenVideo={(url) => setPlayingVideoUrl(getEmbedUrl(url))} /></div>
                  <div><span className="text-zinc-200 font-bold">Zones institutionnelles :</span> Avez-vous identifié vos points d'intérêt (FVG, OB, Support/Résistance) ?<HelpTooltip title="Zones Clés" content="Entrez à la source." subVideos={[educationalContent.technical.ob, educationalContent.technical.fvg]} onOpenVideo={(url) => setPlayingVideoUrl(getEmbedUrl(url))} /></div>
                  <div><span className="text-zinc-200 font-bold">Liquidité :</span> Le marché a-t-il déjà “nettoyé” la liquidité pertinente avant votre entrée ?<HelpTooltip title="Liquidité" content="Évitez les pièges." subVideos={[educationalContent.technical.liquidity]} onOpenVideo={(url) => setPlayingVideoUrl(getEmbedUrl(url))} /></div>
                </div>
              </section>

              {/* E - GESTION DU RISQUE */}
              <section className="relative pl-5 border-l-2 border-zinc-800 font-sans">
                <h4 className="text-base font-black text-zinc-200 mb-4 italic uppercase">E — Gestion du Risque</h4>
                <div className="space-y-4 text-zinc-400 text-[11px]">
                  <div><span className="text-zinc-200 font-bold">Logique d'entrée (Timing) :</span> Pourquoi ce moment précis ?</div>
                  <div><span className="text-zinc-200 font-bold">Invalidation (SL) :</span> Où se situe votre niveau d'invalidation technique ?</div>
                  <div><span className="text-zinc-200 font-bold">Ratio Risque/Récompense (RR) :</span> Quel est votre ratio cible ? (Cible {' > '} 1:2 conseillé).</div>
                  <div><span className="text-zinc-200 font-bold">Validation technique :</span> Votre setup est-il pleinement confirmé ?</div>
                </div>
              </section>

              {/* F - RÉSUMÉ & DÉCISION */}
              <section className="relative pl-5 border-l-2 border-zinc-800 font-sans">
                <h4 className="text-base font-black text-zinc-200 mb-2 italic uppercase">F — Résumé & Décision</h4>
                <div className="p-6 bg-blue-600/10 border-2 border-blue-500/30 rounded-[32px] space-y-4">
                  <div className="text-white font-black text-xs flex items-center gap-2 uppercase tracking-widest">
                    <ShieldAlert size={16} className="text-blue-400" /> 🎯 Décision Finale
                  </div>
                  <div className="space-y-3 text-[10px] font-black uppercase tracking-wider">
                    <div className="text-green-400">TOUTES conditions réunies : Trade autorisé.</div>
                    <div className="text-yellow-400">Incohérence détectée : Trade à ajuster.</div>
                    <div className="text-red-500">Incohérences multiples : Abstention recommandée.</div>
                  </div>
                  <div className="text-zinc-500 text-[9px] font-bold mt-4 border-t border-white/5 pt-4 italic uppercase">
                    Règle d'or : Un trade n'est pas validé parce qu'il “semble bon”, mais parce qu'il s'inscrit dans une logique de gestion du risque cohérente.
                  </div>
                </div>
              </section>

            </div>
            </div>
          </div>
          
          {/* DROITE : TERMINAL NEURAL AUDIT STREAM */}
          <div className="flex-1 flex flex-col bg-[#0F1117] border border-white/10 rounded-2xl p-4 gap-3 shadow-2xl relative overflow-hidden">
            
            <div className="flex items-center justify-between mb-2">
              <div className="flex bg-black/40 p-0.5 rounded-lg border border-white/5 w-full gap-0.5">
                <button 
                  onClick={() => setConsoleTab("ARCHITECTE")} 
                  className={`flex-1 py-1.5 rounded-md text-[8px] font-black uppercase tracking-wider flex items-center justify-center gap-1.5 transition-all ${consoleTab === "ARCHITECTE" ? "bg-blue-600/20 border border-blue-500/30 text-blue-400" : "text-zinc-500"}`}
                >
                  <BrainCircuit size={10} /> Architect_Audit
                </button>
                <button 
                  onClick={() => setConsoleTab("GUARDIAN")} 
                  className={`flex-1 py-1.5 rounded-md text-[8px] font-black uppercase tracking-wider flex items-center justify-center gap-1.5 transition-all ${consoleTab === "GUARDIAN" ? "bg-purple-600/20 border border-purple-500/30 text-purple-400" : "text-zinc-500"}`}
                >
                  <MessageSquare size={10} /> Guardian_Chat
                </button>
              </div>
            </div>

            <div className="flex-1 overflow-hidden min-h-0">
              {consoleTab === "GUARDIAN" ? (
                <div className="h-full flex flex-col justify-between animate-in fade-in duration-200">
                  
                  <div className="flex-1 overflow-y-auto custom-scrollbar space-y-2 pr-1 pb-2">
                    {guardianHistory.length === 0 ? (
                      <div className="text-zinc-500 text-[11px] font-sans font-light italic p-2 bg-purple-500/[0.02] border border-purple-500/5 rounded-xl text-left">
                        &gt; MENTOR_IA: Mode Guardian (Discipline & Gestion Émotionnelle Swing) connecté. Formulez vos doutes ou inconforts à chaud pendant la rétention de votre position.
                      </div>
                    ) : (
                      guardianHistory.map((line, idx) => {
                        const isUser = line.startsWith("Trader:");
                        return (
                          <div 
                            key={idx} 
                            className={`p-2.5 rounded-xl text-[11px] font-sans border leading-normal text-left ${
                              isUser 
                                ? "bg-zinc-900/50 border-white/5 text-zinc-300 ml-4" 
                                : "bg-purple-500/5 border-purple-500/10 text-purple-300 mr-4"
                            }`}
                          >
                            <span className="text-[8px] font-black uppercase block mb-1 tracking-wider opacity-40 font-sans">
                              {isUser ? "⚡ SWING_TRADER" : "🛡️ GUARDIAN_ENGINE"}
                            </span>
                            {line.replace("Trader: ", "").replace("Guardian: ", "")}
                          </div>
                        );
                      })
                    )}
                    {isGuardianLoading && (
                      <div className="text-[10px] text-purple-400 font-sans animate-pulse flex items-center gap-1.5 pl-1 text-left">
                        <Activity size={10} className="animate-spin" /> Ingestion des métriques psychologiques...
                      </div>
                    )}
                  </div>

                  <form onSubmit={handleGuardianMessageSubmit} className="mt-2 flex gap-1 border-t border-white/5 pt-2">
                    <input 
                      type="text"
                      value={guardianInput}
                      onChange={(e) => setGuardianInput(e.target.value)}
                      placeholder="Inconfort, envie de couper tôt, doute..."
                      className="flex-1 bg-zinc-900 border border-white/10 rounded-xl px-3 text-xs text-zinc-200 outline-none focus:border-purple-500/50 font-sans"
                    />
                    <button 
                      type="submit" 
                      disabled={isGuardianLoading || !guardianInput.trim()}
                      className="w-8 h-8 bg-purple-600 hover:bg-purple-500 disabled:opacity-20 text-white rounded-xl flex items-center justify-center transition-all shrink-0"
                    >
                      <Send size={12} />
                    </button>
                  </form>
                </div>
              ) : (
                <div className="h-full bg-black/70 border border-white/10 rounded-xl p-4 font-mono text-[11px] text-green-400 overflow-y-auto leading-relaxed border-l-2 border-l-blue-500 shadow-inner text-left">
                  <div className="flex items-center justify-between mb-2 border-b border-white/5 pb-1.5 uppercase text-[8px] font-black text-blue-400/50 font-sans">
                    <div className="flex items-center gap-1.5"><Activity size={10} className="animate-pulse" /> Neural_Audit_Stream</div>
                    <div className="flex gap-0.5">
                      <div className="w-1 h-1 rounded-full bg-blue-500/50 animate-pulse" />
                      <div className="w-1 h-1 rounded-full bg-blue-500/50 animate-pulse [animation-delay:0.2s]" />
                    </div>
                  </div>
                  <div className="space-y-1">
                    {iaFeedback.split('\n').map((line, i) => (
                      <div key={i} className={line.startsWith('>') ? 'text-blue-400 font-sans font-black tracking-tight' : 'text-zinc-300 font-sans text-[11px]'}>{line}</div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="flex gap-2 font-sans">
              <div className="flex gap-1">
                <button onClick={handleReset} title="Reset Work" className="w-10 h-10 bg-zinc-900 border border-white/5 text-zinc-500 rounded-xl hover:text-red-400 flex items-center justify-center transition-all"><RotateCcw size={15} /></button>
                <button onClick={handleSave} title="Archiver SQL" className="w-10 h-10 bg-zinc-900 border border-white/5 text-zinc-500 rounded-xl hover:text-green-400 flex items-center justify-center transition-all"><Save size={15} /></button>
              </div>
            </div>
          </div>
        </div>

        {/* 4. WORKSPACE DE RÉDACTION SÉMANTIQUE */}
        <section className="flex-1 flex flex-col bg-[#0F1117] border border-white/10 rounded-[32px] overflow-hidden shadow-2xl relative">
          <div className="px-8 py-3 border-b border-white/10 flex justify-between items-center bg-zinc-900/40 font-sans">
            <div className="flex items-center gap-2">
              <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-pulse shadow-[0_0_8px_rgba(59,130,246,1)]" />
              <span className="text-[9px] font-black text-zinc-400 uppercase tracking-[0.4em]">Neural_Workspace_v5.2</span>
            </div>
            <span className="text-[8px] font-black text-blue-400/40 uppercase tracking-widest">[ Saisie Sémantique Obligatoire ]</span>
          </div>
          <textarea 
            value={analyse} 
            onChange={(e) => setAnalyse(e.target.value)} 
            className="flex-1 p-8 bg-transparent text-zinc-200 text-[12px] font-light leading-relaxed resize-none focus:outline-none custom-scrollbar font-sans" 
            placeholder={isSuiviActive ? `Formulez vos arguments pour l'étape : ${questionsSuivi[currentStep].split(' - ')[0]}...` : "Déployez ici votre démonstration macro-économique, l'analyse des rendements et la convergence technique H4/Daily de votre configuration Forex..."} 
          />
        </section>

        {playingVideoUrl && (
        <div className="fixed inset-0 bg-black/95 z-[200] flex items-center justify-center p-4 lg:p-12 backdrop-blur-xl" onClick={closeVideo}>
          <div className="relative bg-[#0a0a0a] border border-white/10 w-full max-w-5xl aspect-video rounded-[32px] shadow-2xl p-2" onClick={(e) => e.stopPropagation()}>
            <button onClick={closeVideo} className="absolute -top-12 right-0 text-zinc-500 hover:text-white transition-all"><X size={24} /></button>
            <iframe className="w-full h-full rounded-[24px]" src={playingVideoUrl} title="Vidéo" allowFullScreen />
          </div>
        </div>
      )}
      </div>
    </AuroraBackground>
  );
  
}