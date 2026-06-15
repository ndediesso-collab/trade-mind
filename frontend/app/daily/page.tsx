"use client";

import React, { useState, useEffect } from "react";
import { AuroraBackground } from "@/components/ui/aurora-background";
import { 
  Play, 
  Square, 
  Save, 
  RotateCcw, 
  Activity, 
  Target, 
  ShieldAlert, 
  ChevronLeft, 
  Brain, 
  Calculator, 
  LineChart, 
  Lock, 
  Eye, 
  CheckCircle,
  AlertTriangle,
  X,
  MessageSquare,
  Send
} from "lucide-react";
import Link from "next/link";

// Déclaration de l'interface stricte pour une position Intraday
interface TradePosition {
  actif: string;
  biais: string; // "ACHAT" | "VENTE" | "NEUTRE"
  entryPrice: string;
  stopLoss: string;
  takeProfit: string;
  conviction: number;
  calculatedRR: number | null;
  analyseText: string;
  statutPosition: string; // "Brouillon" | "WIN" | "LOSS" | "BE"
  auditedByIa: boolean;
}

export default function DailyMode() {
  // --- CYCLES DE SESSIONS ---
  const [sessionStatus, setSessionStatus] = useState("DEBUT"); // "DEBUT" (Pendant session) | "FIN" (Après session)
  const [activePositionTab, setActivePositionTab] = useState(0); // 0 = Pos 1, 1 = Pos 2, 2 = Pos 3
  const [iaVerdict, setIaVerdict] = useState("> Neural Daily Manager : Prêt pour l'audit intraday. Configurez la position active.");
  const [isLoading, setIsLoading] = useState(false);
  const [postSessionText, setPostSessionText] = useState("");

  // --- NOUVEAUX ÉTATS POUR L'INTERFACE INTERACTIVE DU GUARDIAN CHAT ---
  const [consoleTab, setConsoleTab] = useState("ARCHITECTE"); // "ARCHITECTE" | "GUARDIAN"
  const [guardianInput, setGuardianInput] = useState("");
  const [guardianHistory, setGuardianHistory] = useState<string[]>([]);
  const [isGuardianLoading, setIsGuardianLoading] = useState(false);

  // ID du dossier maître rechargé depuis Supabase
  const [currentTradeId, setCurrentTradeId] = useState<number | null>(null);

  // --- MATRICE DE STRUCTURE DES 3 POSITIONS SIMULTANÉES ---
  const [positions, setPositions] = useState<TradePosition[]>([
    { actif: "EURUSD", biais: "NEUTRE", entryPrice: "", stopLoss: "", takeProfit: "", conviction: 50, calculatedRR: null, analyseText: "", statutPosition: "Brouillon", auditedByIa: false },
    { actif: "EURUSD", biais: "NEUTRE", entryPrice: "", stopLoss: "", takeProfit: "", conviction: 50, calculatedRR: null, analyseText: "", statutPosition: "Brouillon", auditedByIa: false },
    { actif: "EURUSD", biais: "NEUTRE", entryPrice: "", stopLoss: "", takeProfit: "", conviction: 50, calculatedRR: null, analyseText: "", statutPosition: "Brouillon", auditedByIa: false }
  ]);

  // --- ÉTATS CALCULATEUR DE LOTS (UNIFIÉ SWING) ---
  const [showCalc, setShowCalc] = useState(false);
  const [calcData, setCalcData] = useState({ balance: "10000", risk: "1", pips: "10" });
  const [lotResult, setLotResult] = useState<number | null>(null);

  // --- EXTRACTION ET RACCOURCIS POUR LA POSITION EN COURS D'ÉDITION ---
  const currentPos = positions[activePositionTab];

  const updateCurrentPosition = (fields: Partial<TradePosition>) => {
    setPositions(prev => prev.map((pos, idx) => idx === activePositionTab ? { ...pos, ...fields } : pos));
  };

  // --- CALCUL AUTOMATIQUE DU RR SUR L'ONGLET ACTIF ---
  useEffect(() => {
    const entry = parseFloat(currentPos.entryPrice);
    const sl = parseFloat(currentPos.stopLoss);     
    const tp = parseFloat(currentPos.takeProfit);   

    if (entry && sl && tp && entry !== sl) {
      const risk = Math.abs(entry - sl);
      const reward = Math.abs(tp - entry);
      const rrRatio = reward / risk;
      updateCurrentPosition({ calculatedRR: parseFloat(rrRatio.toFixed(1)) });
    } else {
      updateCurrentPosition({ calculatedRR: null });
    }
  }, [currentPos.entryPrice, currentPos.stopLoss, currentPos.takeProfit, activePositionTab]); 

  // 🔄 DOUBLE ENGIN DE PERSISTANCE SÉCURISÉ (SUPABASE + LOCAL STORAGE DEBOUNCE)
  useEffect(() => {
    const checkRestaurationSupabase = async () => {
      // 1. Interception d'un ticket de routage depuis l'historique
      const ticket = sessionStorage.getItem("daily_restore");
      if (ticket) {
        try {
          const target = JSON.parse(ticket);
          if (target.trade_id) {
            setIaVerdict(`> SYSTÈME : Rappel du dossier #TM-${target.trade_id} depuis les serveurs Supabase...`);
            
            const res = await fetch(`https://trade-mind-w6rs.onrender.com/historique/get/${target.trade_id}`);
            if (res.ok) {
              const fullTrade = await res.json();
              
              setCurrentTradeId(fullTrade.id);
              
              // Si les données proviennent d'une matrice complexe sauvegardée
              if (fullTrade.analyse.includes("--- SÉANCE COMPLÈTE ---")) {
                setSessionStatus("FIN");
                const sections = fullTrade.analyse.split("--- COMPORTEMENT APRÈS-SESSION ---");
                if (sections[1]) setPostSessionText(sections[1].trim());
              } else {
                // Restauration sur l'emplacement Pos 1 par défaut
                setSessionStatus("DEBUT");
                setPositions(prev => prev.map((pos, idx) => idx === 0 ? {
                  ...pos,
                  actif: fullTrade.actif || "EURUSD",
                  biais: fullTrade.position || "NEUTRE",
                  conviction: fullTrade.conviction || 50,
                  analyseText: (fullTrade.analyse || "").replace(/\[POSITION \d+\]\[RR: \d+[\d.]*\] : /, ""),
                  entryPrice: fullTrade.entry_price || "",
                  stopLoss: fullTrade.stop_loss || "",
                  takeProfit: fullTrade.take_profit || "",
                  auditedByIa: true
                } : pos));
              }
              
              if (fullTrade.feedback) setIaVerdict(fullTrade.feedback);
              sessionStorage.removeItem("daily_restore");
              return; // Coupe pour bloquer l'écrasement par l'ancien cache local v2
            }
          }
        } catch (err) {
          console.error("Échec de la liaison neuronale Supabase:", err);
        }
      }

      // 2. Fallback classique sur la mémoire tampon locale (v2 Debounced)
      const savedCache = localStorage.getItem("tm_daily_cache_v2");
      if (savedCache) {
        try {
          const parsed = JSON.parse(savedCache);
          setCurrentTradeId(parsed.currentTradeId || null);
          setPositions(parsed.positions || []);
          setPostSessionText(parsed.postSessionText || "");
          setSessionStatus(parsed.sessionStatus || "DEBUT");
          setGuardianHistory(parsed.guardianHistory || []);
          if (parsed.iaVerdict) setIaVerdict(parsed.iaVerdict);
        } catch (e) {
          console.error("Purger l'index de cache Daily corrompu:", e);
        }
      }
    };

    checkRestaurationSupabase();
  }, []);

  // Écriture debouncée (temporisation de 500ms pour épargner le processeur)
  useEffect(() => {
    const handler = setTimeout(() => {
      const cache = {
        currentTradeId,
        positions,
        postSessionText,
        sessionStatus,
        guardianHistory,
        iaVerdict
      };
      localStorage.setItem("tm_daily_cache_v2", JSON.stringify(cache));
    }, 500);
    return () => clearTimeout(handler);
  }, [currentTradeId, positions, postSessionText, sessionStatus, guardianHistory, iaVerdict]);

  // --- CALCULATEUR LOCAL ---
  const calculatePositionSize = () => {
    const bal = parseFloat(calcData.balance);
    const riskPct = parseFloat(calcData.risk) / 100;
    const pips = parseFloat(calcData.pips);
    if (bal && riskPct && pips) {
      const size = (bal * riskPct) / (pips * 10);
      setLotResult(parseFloat(size.toFixed(2)));
    }
  };

  // --- ENGINE ACTION 1 : VÉRIFICATION ET AUDIT PAR L'IA ARCHITECTE ---
  const handleIaThèseAudit = async () => {
    if (!currentPos.analyseText.trim() || !currentPos.actif) {
      setIaVerdict("> SÉCURITÉ : L'actif et la rédaction sémantique de la thèse sont obligatoires pour l'audit.");
      setConsoleTab("ARCHITECTE");
      return;
    }
    if (currentPos.calculatedRR !== null && currentPos.calculatedRR < 2) {
      setIaVerdict("> BLOCAGE RISK_ENGINE : Ratio RR inférieur à 1:2. Impossible d'auditer un signal hors cadre de survie.");
      setConsoleTab("ARCHITECTE");
      return;
    }

    setIsLoading(true);
    setConsoleTab("ARCHITECTE");
    setIaVerdict(`> ARCHITECTE ENGINE : Analyse de cohérence sémantique sur la Position ${activePositionTab + 1} (${currentPos.actif})...`);

    try {
      const res = await fetch("https://trade-mind-w6rs.onrender.com/analyse/daily", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          actif: currentPos.actif,
          analyse: currentPos.analyseText,
          conviction: currentPos.conviction,
          position: currentPos.biais,
          statut: "Brouillon",
          mode: "DAILY_DEBUT",
          entry_price: currentPos.entryPrice,
          stop_loss: currentPos.stopLoss,
          take_profit: currentPos.takeProfit,
          calculated_rr: currentPos.calculatedRR
        })
      });
      const data = await res.json();
      updateCurrentPosition({ auditedByIa: true });
      setIaVerdict(`> ARCHITECTE ENGINE : AUDIT INTRADAY COMPLET (POSITION ${activePositionTab + 1})\n\n${data.feedback || data.verdict}`);
    } catch (e) {
      setIaVerdict("> ERREUR : Connexion rompue avec l'Architecte Python.");
    } finally {
      setIsLoading(false);
    }
  };

  // --- SOUCHIER LIVE DU COMPAGNON (THE GUARDIAN ACTION CHAT) ---
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
          analyse_complete: currentPos.analyseText || "Aucune thèse rédigée pour le moment.",
          actif: currentPos.actif
        })
      });

      if (response.ok) {
        const data = await response.json();
        setGuardianHistory(prev => [...prev, `Guardian: ${data.verdict}`]);
      } else {
        setGuardianHistory(prev => [...prev, "Guardian: ❌ Échec de réception de la synapse décisionnelle."]);
      }
    } catch (err) {
      setGuardianHistory(prev => [...prev, "Guardian: ❌ Le serveur de discipline (FastAPI) ne répond pas."]);
    } finally {
      setIsGuardianLoading(false);
    }
  };

  // --- ENGINE ACTION 2 : ENREGISTREMENT EN MEMOIRE DES "N" TRADES DE LA SEANCE ---
  const handleSaveTradeInSession = async () => {
    if (!currentPos.auditedByIa) {
      setIaVerdict(`> SÉCURITÉ : La position ${activePositionTab + 1} doit impérativement être auditée et validée par l'IA avant d'être enregistrée pour l'Après-Session.`);
      setConsoleTab("ARCHITECTE");
      return;
    }

    setIsLoading(true);
    setIaVerdict(`> SYSTEM : Archivage de la Position ${activePositionTab + 1} dans la base cloud...`);

    try {
      const response = await fetch("https://trade-mind-w6rs.onrender.com/database/save", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          id: currentTradeId,
          actif: currentPos.actif.toUpperCase(),
          analyse: `[POSITION ${activePositionTab + 1}][RR: 1:${currentPos.calculatedRR}] : ${currentPos.analyseText}`,
          conviction: currentPos.conviction,
          position: currentPos.biais,
          statut: "Brouillon", 
          mode: "DAILY",
          type: "INTRADAY",
          entry_price: currentPos.entryPrice,
          stop_loss: currentPos.stopLoss,
          take_profit: currentPos.takeProfit,
          calculated_rr: currentPos.calculatedRR
        })
      });

      const resData = await response.json();
      if (response.ok) {
        if (resData.trade_id) setCurrentTradeId(resData.trade_id);
        setIaVerdict(`> SYSTEM Cloud : Position ${activePositionTab + 1} stockée avec succès.\nElle est désormais protégée et indexée.`);
      } else {
        setIaVerdict("> SYSTEM Cloud : Erreur d'écriture réseau vers l'API de stockage.");
      }
    } catch (e) {
      setIaVerdict("> SÉCURITÉ : Serveur FastAPI introuvable. Échec d'archivage.");
    } finally {
      setIsLoading(false);
    }
  };

  // --- ENGINE ACTION 3 : CLÔTURE ET DEBRIEFING GLOBAL (APRÈS-SESSION) ---
  const handleFinalSessionCloture = async () => {
    if (!postSessionText.trim()) {
      setIaVerdict("> SÉCURITÉ : Veuillez rédiger vos notes comportementales globales avant de clore définitivement la séance.");
      return;
    }

    setIsLoading(true);
    setIaVerdict("> ARCHITECTE ENGINE : Traitement de fin de session et génération du rapport cognitif...");

    const syntheseSéance = positions.map((p, i) => (
      `[TRADE ${i + 1}][${p.actif}] Biais: ${p.biais} | Statut final: ${p.statutPosition} | Thèse: ${p.analyseText}`
    )).join("\n\n");

    try {
      const response = await fetch("https://trade-mind-w6rs.onrender.com/database/save", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          id: currentTradeId,
          actif: "DAILY_INDEX",
          analyse: `--- SÉANCE COMPLÈTE ---\n${syntheseSéance}\n\n--- COMPORTEMENT APRÈS-SESSION ---\n${postSessionText}`,
          conviction: 100,
          position: "NEUTRE",
          statut: "Clôturé",
          mode: "DAILY",
          type: "INTRADAY",
          entry_price: currentPos.entryPrice,
          stop_loss: currentPos.stopLoss,
          take_profit: currentPos.takeProfit,
          calculated_rr: currentPos.calculatedRR
        })
      });

      const data = await response.json();
      if (response.ok) {
        setGuardianHistory([]);
        setPostSessionText("");
        setCurrentTradeId(null);
        setPositions([
          { actif: "EURUSD", biais: "NEUTRE", entryPrice: "", stopLoss: "", takeProfit: "", conviction: 50, calculatedRR: null, analyseText: "", statutPosition: "Brouillon", auditedByIa: false },
          { actif: "EURUSD", biais: "NEUTRE", entryPrice: "", stopLoss: "", takeProfit: "", conviction: 50, calculatedRR: null, analyseText: "", statutPosition: "Brouillon", auditedByIa: false },
          { actif: "EURUSD", biais: "NEUTRE", entryPrice: "", stopLoss: "", takeProfit: "", conviction: 50, calculatedRR: null, analyseText: "", statutPosition: "Brouillon", auditedByIa: false }
        ]);
        localStorage.removeItem("tm_daily_cache_v2");
        setSessionStatus("DEBUT");
        setIaVerdict(`> ARCHITECTE ENGINE : SÉANCE COMPLÈTEMENT VERROUILLÉE\n\n${data.feedback || "Dossier archivé."}`);
      } else {
        setIaVerdict("> SYSTEM Cloud : Échec lors de la fermeture globale de la séance.");
      }
    } catch (e) {
      setIaVerdict("> SÉCURITÉ : Erreur critique d'infrastructure lors de la clôture.");
    } finally {
      setIsLoading(false);
    }
  };

  // --- GARDE-FOU POUR ADAPTER LE PASSAGE AUX POSITIONS SUIVANTES ---
  const handleTabChange = (targetIndex: number) => {
    const openTradesCount = positions.filter(p => p.statutPosition === "Brouillon" && p.analyseText.trim() !== "").length;
    
    if (targetIndex > activePositionTab && openTradesCount >= 3 && currentPos.statutPosition === "Brouillon") {
      setIaVerdict(`> GUARDIAN IA : PROTECTION DU FOCUS MENTAL.\nPour basculer sur une autre position, veuillez d'abord fixer le statut de l'opération en cours (WIN, LOSS ou BE) afin de ne pas fragmenter votre attention.`);
      setConsoleTab("ARCHITECTE");
      return;
    }
    setActivePositionTab(targetIndex);
    setIaVerdict(`> GUARDIAN IA : Focus déplacé sur la Position ${targetIndex + 1}. Collecte des données.`);
  };

  const reinitialiserWorkspace = () => {
    if (confirm("Voulez-vous purger la mémoire de travail de la séance active ?")) {
      setPositions([
        { actif: "EURUSD", biais: "NEUTRE", entryPrice: "", stopLoss: "", takeProfit: "", conviction: 50, calculatedRR: null, analyseText: "", statutPosition: "Brouillon", auditedByIa: false },
        { actif: "EURUSD", biais: "NEUTRE", entryPrice: "", stopLoss: "", takeProfit: "", conviction: 50, calculatedRR: null, analyseText: "", statutPosition: "Brouillon", auditedByIa: false },
        { actif: "EURUSD", biais: "NEUTRE", entryPrice: "", stopLoss: "", takeProfit: "", conviction: 50, calculatedRR: null, analyseText: "", statutPosition: "Brouillon", auditedByIa: false }
      ]);
      setPostSessionText("");
      setGuardianHistory([]);
      setCurrentTradeId(null);
      localStorage.removeItem("tm_daily_cache_v2");
      setSessionStatus("DEBUT");
      setIaVerdict("> SYSTEM : Cache local et mémoire de travail entièrement purgés.");
    }
  };

  return (
    <AuroraBackground>
      {/* HEADER ET BACK LINK */}
      <div className="absolute top-4 left-6 z-50 flex items-center gap-4">
        <Link href="/">
          <button className="flex items-center gap-2 px-4 py-2 bg-[#0F1117]/90 border border-white/10 rounded-xl text-zinc-400 hover:text-white transition-all backdrop-blur-xl shadow-2xl">
            <ChevronLeft size={16} />
            <span className="text-[9px] font-black uppercase tracking-widest">Trade Mind Hub</span>
          </button>
        </Link>
      </div>

      {/* COMPOSANT MODAL DU CALCULATEUR DE VOLUME */}
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

      {/* LAYOUT PRINCIPAL DE LA SÉANCE */}
      <div className="relative z-10 w-full h-screen flex gap-4 p-4 bg-zinc-950/40 font-sans pt-16 overflow-hidden">
        
        {/* COLONNE DE GAUCHE : WORKSPACE ET PROTOCOLE DE RECHERCHE */}
        <div className="flex-1 flex flex-col gap-3 h-full min-w-0">
          
          {/* BARRE TECHNIQUE DYNAMIQUE DE LA POSITION SÉLECTIONNÉE */}
          {sessionStatus === "DEBUT" && (
            <section className="p-3 bg-[#0F1117]/95 border border-white/10 rounded-2xl flex flex-wrap items-center justify-between gap-3 shadow-2xl relative">
              <div className="absolute top-0 left-0 h-full w-[2px] bg-blue-500" />
              
              <div className="flex items-center gap-2">
                <LineChart size={14} className="text-blue-400" />
                <div className="flex flex-col">
                  <span className="text-[8px] font-black uppercase text-zinc-500 tracking-tight">Actif [Intraday]</span>
                  <input value={currentPos.actif} onChange={(e) => updateCurrentPosition({ actif: e.target.value.toUpperCase() })} className="w-20 bg-transparent text-xs font-black text-blue-400 focus:outline-none placeholder:text-zinc-800 uppercase mt-0.5 tracking-wider" />
                </div>
              </div>

              <div className="flex items-center gap-2 bg-black/30 p-1 rounded-xl border border-white/5">
                {["Achat", "Vente", "Neutre"].map(b => (
                  <button key={b} onClick={() => updateCurrentPosition({ biais: b.toUpperCase() })} className={`px-2 py-1 text-[8px] font-black uppercase rounded-lg transition-all ${currentPos.biais === b.toUpperCase() ? "bg-blue-600 text-white shadow-md" : "text-zinc-600"}`}>{b}</button>
                ))}
              </div>

              <div className="flex items-center gap-4 border-l border-white/5 pl-4">
                <div className="flex flex-col">
                  <span className="text-[8px] font-black text-zinc-500 uppercase">Entrée</span>
                  <input type="number" step="0.0001" value={currentPos.entryPrice} onChange={(e) => updateCurrentPosition({ entryPrice: e.target.value })} placeholder="1.0850" className="w-16 bg-transparent text-xs font-mono font-bold text-white focus:outline-none" />
                </div>
                <div className="flex flex-col">
                  <span className="text-[8px] font-black text-zinc-500 uppercase">Stop Loss</span>
                  <input type="number" step="0.0001" value={currentPos.stopLoss} onChange={(e) => updateCurrentPosition({ stopLoss: e.target.value })} placeholder="1.0840" className="w-16 bg-transparent text-xs font-mono font-bold text-red-400 focus:outline-none" />
                </div>
                <div className="flex flex-col">
                  <span className="text-[8px] font-black text-zinc-500 uppercase">Take Profit</span>
                  <input type="number" step="0.0001" value={currentPos.takeProfit} onChange={(e) => updateCurrentPosition({ takeProfit: e.target.value })} placeholder="1.0880" className="w-16 bg-transparent text-xs font-mono font-bold text-green-400 focus:outline-none" />
                </div>
              </div>

              <div className="flex flex-col border-l border-white/5 pl-4">
                <span className="text-[8px] font-black text-zinc-500 uppercase">Ratio R:R</span>
                <div className="flex items-center gap-1.5 mt-0.5">
                  <span className={`text-xs font-mono font-black ${currentPos.calculatedRR && currentPos.calculatedRR >= 2 ? "text-green-400" : "text-zinc-500"}`}>
                    {currentPos.calculatedRR !== null ? `1:${currentPos.calculatedRR}` : "N/A"}
                  </span>
                  {currentPos.calculatedRR !== null && currentPos.calculatedRR < 2 && <Lock size={10} className="text-red-500" />}
                </div>
              </div>

              <div className="flex flex-col max-w-[120px] border-l border-white/5 pl-4">
                <div className="flex justify-between text-[8px] font-black uppercase text-zinc-500">
                  <span>Conviction</span>
                  <span className="text-blue-400">{currentPos.conviction}%</span>
                </div>
                <input type="range" min="0" max="100" value={currentPos.conviction} onChange={(e) => updateCurrentPosition({ conviction: parseInt(e.target.value) })} className="w-full accent-blue-600 h-0.5 mt-1 bg-zinc-800" />
              </div>
            </section>
          )}

          {/* CRAN 1 : FORMULAIRE DE GUIDELINE ET RÈGLES */}
          <div className="h-[45%] bg-[#0F1117]/90 border border-white/10 rounded-[32px] p-5 overflow-y-auto custom-scrollbar shadow-2xl backdrop-blur-3xl relative">
            <div className="flex items-center justify-between mb-3 border-b border-white/5 pb-2">
              <div className="flex items-center gap-2">
                <Target size={14} className="text-blue-400" />
                <h2 className="text-[9px] font-black uppercase tracking-[0.3em] text-zinc-400">
                  {sessionStatus === "DEBUT" ? `Structure_Intraday — Position ${activePositionTab + 1}` : "After_Session_Cognitive_Review"}
                </h2>
              </div>
              <span className="text-[9px] font-mono text-zinc-500 bg-white/5 px-2 py-0.5 rounded border border-white/5">
                {sessionStatus === "DEBUT" ? "PENDANT SESSION" : "DEBRIEFING"}
              </span>
            </div>

            <div className="text-[11px] leading-relaxed text-zinc-400 whitespace-pre-line">
              {sessionStatus === "DEBUT" ? (
                <div className="space-y-8 animate-in fade-in duration-200 font-sans">
  
                {/* Message d'accueil / Pistes de réflexion */}
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

                {/* SECTION 1 */}
                <section className="relative pl-4 border-l-2 border-blue-500/50">
                  <h4 className="text-[10px] font-black uppercase tracking-widest text-blue-400 mb-4">
                    1 — Contexte & Carburant (Macro & ADR)
                  </h4>
                  <div className="space-y-3 text-[11px] text-zinc-300">
                    <p><span className="font-bold text-zinc-100">Biais HTF vs Dynamique :</span> Quelle est la tendance de fond et comment s'inscrit-elle dans l'impulsion du jour ?</p>
                    <p><span className="font-bold text-zinc-100">Effets de traîne (Post-News) :</span> Y a-t-il des données fondamentales récentes (travail, inflation, géopolitique) qui influencent le sentiment actuel ?</p>
                    <p><span className="font-bold text-zinc-100">État ADR (Average Daily Range) :</span> Quel est l'ATR actuel ? Le prix a-t-il déjà parcouru plus de 80% de son range quotidien ?</p>
                    <p><span className="font-bold text-zinc-100">Calendrier Macro :</span> Une news majeure est-elle prévue dans les 60 prochaines minutes ?</p>
                  </div>
                </section>

                {/* SECTION 2 */}
                <section className="relative pl-4 border-l-2 border-blue-500/50">
                  <h4 className="text-[10px] font-black uppercase tracking-widest text-blue-400 mb-4">
                    2 — Setup Technique & Timing (Audit d'Entrée)
                  </h4>
                  <div className="space-y-3 text-[11px] text-zinc-300">
                    <p><span className="font-bold text-zinc-100">Setup Institutionnel :</span> Quel est le déclencheur précis ? (Ex: Sweep, FVG + OB, Breakout)</p>
                    <p><span className="font-bold text-zinc-100">Validation de la Killzone :</span> Quelle session tradez-vous (Londres/NY/Asiatique) ? Est-on dans une fenêtre de haute volatilité propice à votre setup ?</p>
                    <p><span className="font-bold text-zinc-100">Logique d'Invalidation (SL) :</span> Où est placé le SL par rapport à la structure intraday ? (Est-il cohérent avec l'ATR actuel ?)</p>
                  </div>
                </section>

                {/* SECTION 3 */}
                <section className="relative pl-4 border-l-2 border-blue-500/50">
                  <h4 className="text-[10px] font-black uppercase tracking-widest text-blue-400 mb-4">
                    3 — Gestion du Risque & Disciplines (Psychologie)
                  </h4>
                  <div className="space-y-3 text-[11px] text-zinc-300">
                    <p><span className="font-bold text-zinc-100">Rapport Risque/Récompense (RR) :</span> Quel est votre objectif ? (Nous recommandons une cible {'>'} 1:2).</p>
                    <p><span className="font-bold text-zinc-100">Exposition :</span> Quel est votre risque total en % du capital ?</p>
                    <p><span className="font-bold text-zinc-100">Clarté Mentale :</span> Est-ce une entrée planifiée ou une réaction à l'impulsion actuelle (FOMO) ?</p>
                    <p><span className="font-bold text-zinc-100">Règle de clôture :</span> Avez-vous conscience de la nécessité de clôturer avant la fin de session (00h00) ?</p>
                  </div>
                </section>

                {/* DÉCISION FINALE (Homogène avec le Swing) */}
                <section className="mt-8 p-6 bg-blue-600/10 border-2 border-blue-500/30 rounded-[32px] space-y-4">
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
                </section>
              </div>
              ) : (
                <div className="space-y-4 animate-in fade-in duration-200 font-sans">
                  <div className="flex items-center gap-2 text-green-400 font-black uppercase tracking-widest text-[9px]"><ShieldAlert size={12} /> 1 — AUDIT DE CLÔTURE DE SÉANCE GLOBAL</div>
                  <p className="text-zinc-400">Veuillez formuler un résumé écrit de votre séance. Vos réponses doivent être honnêtes pour permettre un débriefing objectif.</p>
                  <div className="p-4 bg-zinc-900/50 rounded-xl border border-white/5 space-y-3 text-[11px] text-zinc-300">
                    <p>• <span className="font-bold text-white">Analysez vos déviances psychologiques majeures</span> face aux 3 positions.</p>
                    <p>• Vos gains découlent-ils <span className="font-bold text-white">du plan ou d&apos;une impulsion heureuse ?</span></p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* CRAN 2 : CHANTIER DE RÉDACTION (TEXTAREA SÉMANTIQUE) */}
          <div className="flex-1 bg-[#0F1117] border border-white/10 rounded-[32px] p-5 flex flex-col relative group shadow-inner">
            <div className="absolute top-3 right-6 text-[8px] font-black text-blue-500/20 uppercase tracking-widest">
              {sessionStatus === "DEBUT" ? `Workspace_Position_${activePositionTab + 1}` : "Workspace_Post_Session"}
            </div>
            
            <textarea 
              value={sessionStatus === "DEBUT" ? currentPos.analyseText : postSessionText}
              onChange={(e) => sessionStatus === "DEBUT" ? updateCurrentPosition({ analyseText: e.target.value }) : setPostSessionText(e.target.value)}
              placeholder={sessionStatus === "DEBUT" ? "Rédigez la thèse technique complète de la position active en répondant scrupuleusement au protocole..." : "Rédigez votre débriefing comportemental honnête (déviances majeures, origine des gains...) pour clôturer cette séance..."}
              className="flex-1 bg-transparent border-none outline-none text-zinc-200 text-xs font-light leading-relaxed resize-none placeholder:text-zinc-800 custom-scrollbar font-sans"
            />

            <div className="mt-2 pt-2 border-t border-white/5 flex justify-between items-center font-sans">
              <span className="text-[9px] font-mono text-zinc-600">Characters : {sessionStatus === "DEBUT" ? currentPos.analyseText.length : postSessionText.length}</span>
              
              <div className="flex gap-2">
                {sessionStatus === "DEBUT" ? (
                  <>
                    <button onClick={handleSaveTradeInSession} disabled={isLoading} className="flex items-center gap-1.5 px-4 py-2 bg-zinc-900 border border-white/5 rounded-xl text-zinc-400 font-black text-[9px] uppercase tracking-wider hover:text-white disabled:opacity-40">
                      <Save size={12} /> Enregistrer la Position
                    </button>
                    <button onClick={handleIaThèseAudit} disabled={isLoading} className="flex items-center gap-1.5 px-4 py-2 bg-blue-600 rounded-xl text-white font-black text-[9px] uppercase tracking-wider hover:bg-blue-500 disabled:opacity-40">
                      <Brain size={12} /> {isLoading ? "Synapse..." : "Auditer la Thèse (IA)"}
                    </button>
                  </>
                ) : (
                  <button onClick={handleFinalSessionCloture} disabled={isLoading} className="flex items-center gap-1.5 px-5 py-2 bg-green-600 rounded-xl text-white font-black text-[9px] uppercase tracking-wider hover:bg-green-500 disabled:opacity-40">
                    <CheckCircle size={12} /> Clôturer la Séance & Débriefer
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* COLONNE DE DROITE : TERMINAL IA AUDIO / VISUEL ET SWITCHES DE POSITIONS */}
        <div className="w-[380px] flex flex-col gap-3 h-full">
          
          {/* SWITCHS DE STRUCTURE SUPÉRIEURE : SESSIONS ET MANAGEMENT DE MARGE */}
          <div className="bg-[#0F1117] border border-white/10 rounded-xl p-1 flex flex-col gap-1.5 shadow-xl">
            <div className="flex gap-1">
              <button onClick={() => setSessionStatus("DEBUT")} className={`flex-1 py-2 rounded-lg text-[9px] font-black uppercase tracking-wider flex items-center justify-center gap-1.5 transition-all ${sessionStatus === "DEBUT" ? "bg-blue-600 text-white shadow" : "text-zinc-500 hover:text-zinc-300"}`}>
                <Play size={10} /> Pendant Session
              </button>
              <button onClick={() => { setSessionStatus("FIN"); setConsoleTab("ARCHITECTE"); }} className={`flex-1 py-2 rounded-lg text-[9px] font-black uppercase tracking-wider flex items-center justify-center gap-1.5 transition-all ${sessionStatus === "FIN" ? "bg-green-600 text-white shadow" : "text-zinc-500 hover:text-zinc-300"}`}>
                <Square size={10} /> Après Session
              </button>
            </div>

            {/* BARRE DE SWITCH ENTRE LES 3 POSITIONS SÉLECTIONNABLES (PENDANT SESSION ONLY) */}
            {sessionStatus === "DEBUT" && (
              <div className="grid grid-cols-3 gap-1 bg-black/40 p-0.5 rounded-lg border border-white/5 font-sans animate-in fade-in duration-200">
                {positions.map((pos, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleTabChange(idx)}
                    className={`py-1 rounded-md text-[8px] font-black uppercase tracking-tight flex flex-col items-center justify-center transition-all ${
                      activePositionTab === idx ? "bg-zinc-800 text-blue-400 border border-blue-500/20" : "text-zinc-600 hover:bg-white/5"
                    }`}
                  >
                    <span>Pos {idx + 1}</span>
                    <span className={`text-[7px] font-mono ${pos.statutPosition === "WIN" ? "text-green-400" : pos.statutPosition === "LOSS" ? "text-red-400" : "text-zinc-500"}`}>
                      [{pos.statutPosition}]
                    </span>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* CRAN MANAGEMENT STRATÉGIQUE DU STATUT DES POSITIONS EN DIRECT */}
          {sessionStatus === "DEBUT" && (
            <div className="p-3 bg-[#0F1117]/60 border border-white/5 rounded-2xl grid grid-cols-4 gap-1 animate-in slide-in-from-right-4 font-sans font-black">
              {["Brouillon", "WIN", "LOSS", "BE"].map(st => (
                <button
                  key={st}
                  onClick={() => updateCurrentPosition({ statutPosition: st })}
                  className={`py-1 text-[8px] uppercase rounded-lg transition-all border ${
                    currentPos.statutPosition === st 
                      ? "bg-zinc-100 border-white text-black font-black" 
                      : "bg-black/20 border-transparent text-zinc-500 hover:bg-white/5"
                  }`}
                >
                  {st}
                </button>
              ))}
            </div>
          )}

          {/* STREAM TERMINAL EN CONSOLE (AVEC SYSTÈME DE DOUBLE ONGLETS LOCAUX) */}
          <div className={`flex-1 bg-black/70 border rounded-[28px] p-5 flex flex-col relative overflow-hidden shadow-2xl ${sessionStatus === "DEBUT" && consoleTab === "GUARDIAN" ? "border-purple-500/30" : sessionStatus === "DEBUT" ? "border-blue-500/20" : "border-green-500/20"}`}>
            
            {/* EN-TÊTE DU TERMINAL AVEC SWITCH D'IA */}
            <div className="flex items-center justify-between mb-3 border-b border-white/5 pb-2">
              {sessionStatus === "DEBUT" ? (
                <div className="flex bg-black/40 p-0.5 rounded-lg border border-white/5 w-full gap-0.5">
                  <button 
                    onClick={() => setConsoleTab("ARCHITECTE")} 
                    className={`flex-1 py-1.5 rounded-md text-[8px] font-black uppercase tracking-wider flex items-center justify-center gap-1.5 transition-all ${consoleTab === "ARCHITECTE" ? "bg-blue-600/20 border border-blue-500/30 text-blue-400" : "text-zinc-500"}`}
                  >
                    <Brain size={10} /> Architect_Audit
                  </button>
                  <button 
                    onClick={() => setConsoleTab("GUARDIAN")} 
                    className={`flex-1 py-1.5 rounded-md text-[8px] font-black uppercase tracking-wider flex items-center justify-center gap-1.5 transition-all ${consoleTab === "GUARDIAN" ? "bg-purple-600/20 border border-purple-500/30 text-purple-400" : "text-zinc-500"}`}
                  >
                    <MessageSquare size={10} /> Guardian_Chat
                  </button>
                </div>
              ) : (
                <div className="flex items-center gap-2 text-green-400">
                  <Activity size={12} className={isLoading ? "animate-spin" : "animate-pulse"} />
                  <span className="font-black uppercase tracking-wider text-[9px]">Architect_Intraday_Review</span>
                </div>
              )}
            </div>
            
            {/* CONTENU VARIABLE DU TERMINAL DE CONSOLE */}
            <div className="flex-1 overflow-hidden min-h-0">
              {sessionStatus === "DEBUT" && consoleTab === "GUARDIAN" ? (
                <div className="h-full flex flex-col justify-between animate-in fade-in duration-200">
                  
                  {/* Flux des messages */}
                  <div className="flex-1 overflow-y-auto custom-scrollbar space-y-2 pr-1 pb-2">
                    {guardianHistory.length === 0 ? (
                      <div className="text-zinc-500 text-[11px] font-sans font-light italic p-2 bg-purple-500/[0.02] border border-purple-500/5 rounded-xl text-left">
                        &gt; MENTOR_IA: Mode Guardian (Discipline & Gestion Émotionnelle) connecté. Formulez votre doute ou inconfort à chaud par rapport à vos positions actives.
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
                            <span className="text-[8px] font-black uppercase block mb-1 tracking-wider opacity-40">
                              {isUser ? "⚡ SESSION_TRADER" : "🛡️ GUARDIAN_ENGINE"}
                            </span>
                            {line.replace("Trader: ", "").replace("Guardian: ", "")}
                          </div>
                        );
                      })
                    )}
                    {isGuardianLoading && (
                      <div className="text-[10px] text-purple-400 font-mono animate-pulse flex items-center gap-1.5 pl-1">
                        <Activity size={10} className="animate-spin" /> Ingestion des métriques cognitives...
                      </div>
                    )}
                  </div>

                  {/* Formulaire de saisie du chat */}
                  <form onSubmit={handleGuardianMessageSubmit} className="mt-2 flex gap-1 border-t border-white/5 pt-2">
                    <input 
                      type="text"
                      value={guardianInput}
                      onChange={(e) => setGuardianInput(e.target.value)}
                      placeholder="Doute, peur, déviance comportementale..."
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
                <div className="h-full text-zinc-300 whitespace-pre-wrap custom-scrollbar overflow-y-auto font-sans font-light text-left animate-in fade-in duration-200">
                  {iaVerdict.split('\n').map((line, i) => (
                    <div key={i} className={line.startsWith('>') ? 'text-blue-400 font-black tracking-tight mb-2' : 'text-zinc-300 text-[11px] leading-relaxed'}>
                      {line}
                    </div>
                  ))}
                </div>
              )}
            </div>
            
            <div className={`absolute bottom-0 left-0 w-full h-0.5 ${sessionStatus === "DEBUT" && consoleTab === "GUARDIAN" ? "bg-purple-600/30" : sessionStatus === "DEBUT" ? "bg-blue-600/30" : "bg-green-600/30"}`} />
          </div>

          {/* COMMANDE COMMUNE DE BAS DE CONSOLE */}
          <div className="grid grid-cols-3 gap-2 font-sans">
            <button onClick={reinitialiserWorkspace} title="Purge Cache" className="py-2.5 bg-zinc-900 border border-white/5 rounded-xl text-zinc-500 flex items-center justify-center hover:text-red-400 transition-all shadow-md">
              <RotateCcw size={14} />
            </button>
            <button onClick={() => setShowCalc(true)} className="col-span-2 py-2.5 bg-zinc-900 border border-white/5 rounded-xl text-zinc-400 font-black text-[9px] uppercase tracking-wider flex items-center justify-center gap-2 hover:bg-zinc-800 transition-all shadow-md">
              <Calculator size={12} className="text-blue-400" /> Calculateur Lots
            </button>
          </div>

        </div>
      </div>
    </AuroraBackground>
  );
}