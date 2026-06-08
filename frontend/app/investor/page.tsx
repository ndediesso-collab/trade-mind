"use client";

import React, { useState, useEffect } from "react";
import { AuroraBackground } from "@/components/ui/aurora-background";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Save, ShieldCheck, Globe, Loader2, 
  Search, ChevronLeft, Newspaper, Gauge,
  Activity, CheckCircle2, XCircle, X
} from "lucide-react";
import Link from "next/link";

export default function InvestorPage() {
  const [analysis, setAnalysis] = useState("");
  const [asset, setAsset] = useState("BTC-USD");
  const [auditResult, setAuditResult] = useState<any>(null);
  const [marketIntel, setMarketIntel] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [showCloseModal, setShowCloseModal] = useState(false);

  // ID unique persistant du dossier d'investissement cloud
  const [currentTradeId, setCurrentTradeId] = useState<number | null>(null);

  useEffect(() => {
    fetchMarketData();
  }, [asset]);

  const fetchMarketData = async () => {
    try {
      const res = await fetch(`http://127.0.0.1:8000/market/intelligence?actif=${asset}`);
      const data = await res.json();
      setMarketIntel(data);
    } catch (e) { console.error("Intel fetch failed", e); }
  };

  // 🔄 DOUBLE ENGIN DE PERSISTANCE SÉCURISÉ (SUPABASE CLOUD + LOCAL DEBOUNCE)
  useEffect(() => {
    const checkRestaurationSupabase = async () => {
      // 1. Interception d'un ordre de routage depuis l'historique d'audit
      const ticket = sessionStorage.getItem("investor_restore");
      if (ticket) {
        try {
          const target = JSON.parse(ticket);
          if (target.trade_id) {
            const res = await fetch(`http://127.0.0.1:8000/historique/get/${target.trade_id}`);
            if (res.ok) {
              const fullTrade = await res.json();
              
              setCurrentTradeId(fullTrade.id);
              setAsset(fullTrade.actif || "BTC-USD");
              setAnalysis(fullTrade.analyse || "");
              
              if (fullTrade.feedback) {
                setAuditResult({ audit: fullTrade.feedback });
              }
              
              sessionStorage.removeItem("investor_restore");
              return; // Bloque la récupération du cache local temporaire v2
            }
          }
        } catch (err) {
          console.error("Échec de la liaison neuronale Investor Supabase:", err);
        }
      }

      // 2. Récupération de la mémoire tampon locale debouncée
      const savedCache = localStorage.getItem("tm_investor_cache_v2");
      if (savedCache) {
        try {
          const parsed = JSON.parse(savedCache);
          setCurrentTradeId(parsed.currentTradeId || null);
          setAsset(parsed.asset || "BTC-USD");
          setAnalysis(parsed.analysis || "");
          if (parsed.auditResult) setAuditResult(parsed.auditResult);
        } catch (e) {
          console.error("Erreur de lecture de la mémoire tampon de l'investisseur :", e);
        }
      }
    };

    checkRestaurationSupabase();
  }, []);

  // Écriture différée automatique (Évite les lags d'écriture toutes les 500ms)
  useEffect(() => {
    const handler = setTimeout(() => {
      const cache = {
        currentTradeId,
        asset,
        analysis,
        auditResult
      };
      localStorage.setItem("tm_investor_cache_v2", JSON.stringify(cache));
    }, 500);
    return () => clearTimeout(handler);
  }, [currentTradeId, asset, analysis, auditResult]);

  const handleSaveDraft = async () => {
    setIsSaving(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/database/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          id: currentTradeId, // Mutation si l'ID est déjà instancié
          analyse: analysis, 
          actif: asset, 
          statut: "BROUILLON", 
          mode: "INVESTOR", 
          type: "LONG_TERM" 
        })
      });
      const resData = await res.json();
      if (res.ok && resData.trade_id) {
        setCurrentTradeId(resData.trade_id);
      }
    } catch (e) { console.error(e); } finally { setIsSaving(false); }
  };

  const handleRequestAudit = async () => {
    if (!analysis) return;
    setIsLoading(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/investor/audit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: analysis, actif: asset })
      });
      const data = await res.json();
      setAuditResult(data);
    } catch (e) { console.error(e); } finally { setIsLoading(false); }
  };

  const handleFinalClose = async (result: 'WIN' | 'LOSS') => {
    try {
      await fetch('http://127.0.0.1:8000/database/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          id: currentTradeId,
          analyse: analysis, 
          actif: asset, 
          statut: result, 
          mode: "INVESTOR", 
          type: "LONG_TERM" 
        })
      });
      localStorage.removeItem("tm_investor_cache_v2");
      window.location.href = "/";
    } catch (e) { console.error(e); }
  };

  return (
    <AuroraBackground>
      {/* MODALE DE CLÔTURE */}
      <AnimatePresence>
        {showCloseModal && (
          <motion.div 
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed inset-0 z-[100] flex items-center justify-center bg-black/90 backdrop-blur-md p-6"
          >
            <motion.div initial={{ scale: 0.9 }} animate={{ scale: 1 }} className="bg-[#0B0E11] border border-white/10 p-10 rounded-[2.5rem] max-w-sm w-full text-center shadow-2xl">
              <h3 className="text-xl font-black italic text-white mb-8 uppercase">Clôturer Thèse</h3>
              <div className="grid grid-cols-2 gap-4">
                <button onClick={() => handleFinalClose('WIN')} className="flex flex-col items-center gap-3 p-6 bg-green-500/10 border border-green-500/20 rounded-3xl hover:bg-green-500/20 transition-all">
                  <CheckCircle2 size={32} className="text-green-500" />
                  <span className="text-[10px] font-black text-green-500 uppercase tracking-widest">Profit</span>
                </button>
                <button onClick={() => handleFinalClose('LOSS')} className="flex flex-col items-center gap-3 p-6 bg-red-500/10 border border-red-500/20 rounded-3xl hover:bg-red-500/20 transition-all">
                  <XCircle size={32} className="text-red-500" />
                  <span className="text-[10px] font-black text-red-500 uppercase tracking-widest">Loss</span>
                </button>
              </div>
              <button onClick={() => setShowCloseModal(false)} className="mt-8 text-[9px] text-zinc-600 uppercase font-bold hover:text-white">Annuler</button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="relative z-10 w-full max-w-[1700px] mx-auto h-screen flex p-6 gap-6 overflow-hidden">
        
        {/* COLONNE GAUCHE : WORKSPACE */}
        <div className="flex-[1.8] flex flex-col gap-4">
          <div className="bg-[#0B0E11]/60 backdrop-blur-2xl border border-white/5 p-4 rounded-[2rem] flex justify-between items-center shadow-2xl">
             <div className="flex items-center gap-4">
                <Link href="/" className="p-2 text-zinc-500 hover:text-white transition-all"><ChevronLeft size={20} /></Link>
                <div className="flex items-center gap-2 bg-black/40 px-4 py-2 rounded-xl border border-white/5">
                  <Search size={14} className="text-blue-500" />
                  <input 
                    value={asset} onChange={(e) => setAsset(e.target.value.toUpperCase())}
                    className="bg-transparent text-white font-black text-xs uppercase tracking-widest focus:outline-none w-32"
                    placeholder="TICKER"
                  />
                </div>
             </div>
             <div className="flex gap-2">
                <button onClick={handleSaveDraft} className="px-6 py-2 bg-zinc-900 border border-white/5 rounded-xl text-[9px] font-black uppercase text-zinc-400 hover:text-white transition-all">
                  {isSaving ? "Sauvegarde..." : "Brouillon"}
                </button>
                <button onClick={() => setShowCloseModal(true)} className="px-6 py-2 bg-red-600/20 border border-red-600/30 rounded-xl text-[9px] font-black uppercase text-red-400 hover:bg-red-600 hover:text-white transition-all">
                  Clôturer
                </button>
             </div>
          </div>

          <div className="flex-1 bg-[#0B0E11]/60 backdrop-blur-2xl border border-white/5 rounded-[2.5rem] p-10 flex flex-col shadow-2xl">
            <textarea 
              className="flex-1 bg-transparent text-zinc-300 text-sm leading-[2.2] focus:outline-none resize-none custom-scrollbar font-serif placeholder:text-zinc-800"
              placeholder="Déployez ici votre thèse d'investissement (Cycle économique, fondamental, avantage compétitif...)"
              value={analysis} onChange={(e) => setAnalysis(e.target.value)}
            />
            <button 
              onClick={handleRequestAudit}
              disabled={isLoading || !analysis}
              className="w-full mt-4 py-4 bg-white/5 hover:bg-white/10 border border-white/10 text-white rounded-2xl font-black text-[10px] uppercase tracking-[0.2em] transition-all disabled:opacity-30"
            >
              {isLoading ? <Loader2 className="animate-spin mx-auto" size={16} /> : "Lancer l'Audit Stratégique"}
            </button>
          </div>
        </div>

        {/* COLONNE DROITE : INTEL & AUDIT */}
        <div className="w-[500px] flex flex-col gap-4 h-full overflow-y-auto custom-scrollbar">
          
          <div className="bg-[#0B0E11]/80 backdrop-blur-2xl border border-white/5 rounded-[2.5rem] p-8 shadow-2xl">
            <div className="flex items-center gap-3 mb-6">
              <Newspaper className="text-blue-500" size={16} />
              <span className="text-[9px] font-black uppercase tracking-[0.2em] text-blue-500">Fil_Actu_En_Direct</span>
            </div>
            
            {marketIntel ? (
              <div className="space-y-6">
                 <div className="flex items-center justify-between p-4 bg-white/5 rounded-2xl border border-white/5">
                    <div className="flex items-center gap-3">
                      <Gauge className="text-zinc-500" size={18} />
                      <span className="text-[10px] font-bold text-zinc-400 uppercase">Sentiment</span>
                    </div>
                    <span className="text-xs font-black text-white italic">{marketIntel.fear_greed?.label || "---"}</span>
                 </div>

                 <div className="relative h-40 overflow-hidden bg-black/20 rounded-xl border border-white/5 p-4">
                    <div className="absolute inset-0 flex flex-col gap-3 animate-scroll">
                      {marketIntel.news_feed.split('\n').filter((line: string) => line.startsWith('⚠️') || line.startsWith('📰')).map((line: string, i: number) => (
                        <p key={i} className="text-[10px] text-zinc-300 border-b border-white/5 pb-2 hover:text-blue-400 transition-colors">
                          {line}
                        </p>
                      ))}
                    </div>
                    <div className="absolute top-0 left-0 w-full h-8 bg-gradient-to-b from-[#0B0E11] to-transparent" />
                    <div className="absolute bottom-0 left-0 w-full h-8 bg-gradient-to-t from-[#0B0E11] to-transparent" />
                 </div>
              </div>
            ) : (
              <div className="flex items-center gap-2 text-zinc-700 text-[10px]"><Loader2 size={12} className="animate-spin" /> Analyse des flux...</div>
            )}
          </div>

          <div className="flex-1 bg-[#0B0E11]/80 backdrop-blur-2xl border border-white/5 rounded-[2.5rem] p-8 shadow-2xl">
            <div className="flex items-center gap-3 mb-6 text-purple-500">
              <ShieldCheck size={16} />
              <span className="text-[9px] font-black uppercase tracking-[0.2em]">Audit_Investisseur_IA</span>
            </div>
            {auditResult ? (
              <div className="space-y-6 animate-in slide-in-from-bottom-2">
                 <div className="p-6 bg-white/5 rounded-2xl flex items-center justify-between border border-white/5">
                    <div>
                      <div className="text-4xl font-black italic text-white">{auditResult.audit.split("NOTE : ")[1]?.split("/")[0] || "--"}</div>
                      <div className="text-[8px] font-black text-zinc-500 uppercase tracking-widest mt-1">Score_Coherence</div>
                    </div>
                    <Activity className="text-purple-500" size={32} />
                 </div>
                 <div className="text-[11px] text-zinc-300 leading-relaxed font-serif bg-black/20 p-5 rounded-2xl/20 whitespace-pre-wrap">
                   {auditResult.audit.split("ANALYSE :")[1] || auditResult.audit}
                 </div>
              </div>
            ) : (
              <div className="h-64 flex flex-col items-center justify-center text-zinc-600 gap-4">
                <Globe size={32} />
                <p className="text-[9px] uppercase font-bold tracking-widest">En attente de thèse</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </AuroraBackground>
  );
}