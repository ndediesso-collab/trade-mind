"use client";

import { useState, useMemo } from 'react';
import useSWR, { mutate } from 'swr';
import { AreaChart, Area, ResponsiveContainer, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { 
  ArrowLeft, AlertCircle, Activity, Globe, Zap, Shield, 
  Edit3, Check, BrainCircuit, X, BarChart3, TrendingUp, FolderOpen, Play
} from "lucide-react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";

const fetcher = (url: string) => fetch(url).then((res) => res.json());

export default function Dashboard() {
  const [selectedMode, setSelectedMode] = useState<'GLOBAL' | 'SWING' | 'DAILY' | 'SCALP' | 'INVESTOR'>('GLOBAL');
  const [isEditingCap, setIsEditingCap] = useState(false);
  const [newCap, setNewCap] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  
  // Requête SWR sur ton API Python
  const { data, error } = useSWR('https://trade-mind-w6rs.onrender.com/dashboard/metrics', fetcher, {
    refreshInterval: 5000 
  });

  // CORRECTION MAJEURE : data est DEJA l'objet de métriques. Pas de sous-couche .metrics
  const metrics = data || {};
  const health = metrics.health || { global: 0 };
  const behavioralMemory = metrics.behavioral_memory || { consistency_score: 0, avg_rr_trend: "STABLE", tilt_frequency: "LOW" };
  const psy = metrics.psychology || { state: "OPTIMAL", confidence: 100, patterns: [] };
  const risk = metrics.risk_engine || { status: "SAFE", max_drawdown_historical: 0, environment: "STABLE" };
  const sessions = metrics.sessions || { NY: "CLOSED", LON: "CLOSED", TOK: "CLOSED", time_utc: "--:--", time_local: "--:--" };
  const rawTrades = metrics.trades || [];

  // 📈 Tracé de l'Equity Curve
  const chartData = useMemo(() => {
    if (!metrics.equity || !Array.isArray(metrics.equity)) return [];
    return metrics.equity.map((val: any, index: number) => ({
      name: index,
      val: parseFloat(val)
    }));
  }, [metrics.equity]);

  // 📁 Filtrage des Brouillons pour la réinjection
  const brouillonsEnAttente = useMemo(() => {
    return rawTrades.filter((t: any) => {
      const statut = isinstanceOfTradeDict(t) ? t.statut : t[8];
      return String(statut).toUpperCase() === "BROUILLON";
    });
  }, [rawTrades]);

  const handleReprendreSession = (trade: any) => {
    if (isinstanceOfTradeDict(trade)) {
      const mode = String(trade.mode).toUpperCase();
      const payload = JSON.stringify({ trade_id: trade.id });
      
      if (mode === "SCALPING" || mode === "SCALP") {
        sessionStorage.setItem("scalp_restore", payload);
        window.location.href = "/scalp";
      } else if (mode === "DAILY" || mode === "INTRADAY") {
        sessionStorage.setItem("daily_restore", payload);
        window.location.href = "/daily";
      } else if (mode === "INVESTOR") {
        sessionStorage.setItem("investor_restore", payload);
        window.location.href = "/investor";
      } else {
        sessionStorage.setItem("tm_swing_cache", payload);
        window.location.href = "/swing";
      }
    } else {
      const tId = trade[0];
      const tMode = String(trade[10]).toUpperCase();
      const payload = JSON.stringify({ trade_id: tId });
      
      if (tMode === "SCALPING" || tMode === "SCALP") {
        sessionStorage.setItem("scalp_restore", payload);
        window.location.href = "/scalp";
      } else if (tMode === "DAILY" || tMode === "INTRADAY") {
        sessionStorage.setItem("daily_restore", payload);
        window.location.href = "/daily";
      } else if (tMode === "INVESTOR") {
        sessionStorage.setItem("investor_restore", payload);
        window.location.href = "/investor";
      } else {
        sessionStorage.setItem("tm_swing_cache", payload);
        window.location.href = "/swing";
      }
    }
  };

  const handleSaveToDatabase = async () => {
    const val = parseFloat(newCap);
    if (isNaN(val)) {
        setIsEditingCap(false);
        setNewCap("");
        return;
    }
    setIsSaving(true);
    try {
      const res = await fetch(`https://trade-mind-w6rs.onrender.com/dashboard/update-capital?amount=${val}`, { method: 'POST' });
      if (res.ok) {
        await mutate('https://trade-mind-w6rs.onrender.com/dashboard/metrics');
        setIsEditingCap(false);
        setNewCap("");
      }
    } catch (e) { console.error(e); } finally { setIsSaving(false); }
  };

  if (error) return <div className="p-8 text-red-500 bg-[#0B0E11] min-h-screen flex flex-col items-center justify-center font-mono uppercase text-[10px] tracking-[0.3em]"><AlertCircle size={32} className="mb-4 animate-bounce" /> Liaison interrompue</div>;
  if (!data || data.status === "LOCKDOWN") return <div className="p-8 text-blue-500 bg-[#0B0E11] min-h-screen flex flex-col items-center justify-center font-mono uppercase text-[10px] tracking-[0.3em]"><Activity size={32} className="mb-4 animate-spin" /> {data?.error ? "ALERTE VERROU STRUCTUREL" : "Synchronisation..."}</div>;

  return (
    <div className="min-h-screen bg-[#0B0E11] text-white p-6 selection:bg-blue-500/30 overflow-x-hidden">

      {/* HEADER */}
      <header className="flex items-center justify-between mb-10 max-w-7xl mx-auto border-b border-white/5 pb-6">
        <Link href="/" className="flex items-center gap-4 text-zinc-500 hover:text-white transition-all group">
          <div className="p-2 bg-white/5 rounded-lg group-hover:bg-blue-600/20 transition-colors"><ArrowLeft size={16} /></div>
          <div className="flex flex-col">
            <span className="text-[10px] font-black uppercase tracking-[0.3em]">Mind_Engine_v2</span>
            <span className={`text-[8px] font-bold uppercase ${risk.status === 'SAFE' ? 'text-green-500' : 'text-red-500 animate-pulse'}`}>{risk.status} PROTOCOL</span>
          </div>
        </Link>

        <div className="flex gap-4">
           {['TOK', 'LON', 'NY'].map((city) => (
             <div key={city} className="flex items-center gap-3 px-4 py-2 bg-[#161A1E] border border-white/5 rounded-xl shadow-lg">
               <span className="text-[9px] font-black text-zinc-500 tracking-widest uppercase">{city}</span>
               <div className={`w-1.5 h-1.5 rounded-full ${sessions[city] === 'OPEN' ? 'bg-green-500 animate-pulse' : 'bg-red-900'}`} />
               <span className="text-[10px] font-mono">{sessions[city] || "CLOSED"}</span>
             </div>
           ))}

           <div className="flex items-center px-4 py-2 bg-blue-600/10 border border-blue-500/20 rounded-xl font-mono text-[10px] text-blue-400 font-bold gap-2">
              <Globe size={12} className="animate-spin-slow" />
              <span>{sessions.time_local || "--:--"} (GABON)</span>
              <span className="opacity-40">|</span>
              <span>{sessions.time_utc || "--:--"} UTC</span>
           </div>
        </div>
      </header>

      <div className="grid grid-cols-12 gap-8 max-w-7xl mx-auto">

        {/* COLONNE GAUCHE */}
        <div className="col-span-12 lg:col-span-3 flex flex-col gap-6">
          <div className="bg-[#161A1E] border border-white/10 p-8 rounded-[32px] shadow-2xl relative overflow-hidden group">
            <div className="flex justify-between items-center mb-4">
                <h3 className="text-zinc-500 text-[9px] font-black uppercase tracking-[0.4em]">Equity_Manager</h3>
                <div className="flex gap-2">
                    {isEditingCap ? (
                        <button onClick={handleSaveToDatabase} disabled={isSaving} className="text-green-500 hover:scale-110"><Check size={16} /></button>
                    ) : (
                        <button onClick={() => setIsEditingCap(true)} className="text-zinc-600 hover:text-blue-400 transition-colors"><Edit3 size={14} /></button>
                    )}
                </div>
            </div>

            <div className="flex items-baseline gap-2 justify-center h-12 mb-4">
              {isEditingCap ? (
                  <input 
                    autoFocus className="bg-black/40 text-2xl font-black text-white outline-none border border-blue-500/50 rounded-lg w-full text-center font-mono"
                    value={newCap} onChange={(e) => setNewCap(e.target.value)}
                  />
              ) : (
                <p className="text-5xl font-black text-white tracking-tighter tabular-nums italic">
                    {metrics.capital_total?.toLocaleString()}<span className="text-blue-500 text-xl font-mono ml-2">$</span>
                </p>
              )}
            </div>

            <div className="mt-6 pt-6 border-t border-white/5">
                <div className="flex justify-between items-center mb-2 text-[9px] font-black text-zinc-500 uppercase tracking-widest">
                    <span>Global_Health</span>
                    <span className="text-blue-400 font-mono">{health.global}%</span>
                </div>
                <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
                    <motion.div initial={{ width: 0 }} animate={{ width: `${health.global}%` }} className={`h-full ${health.global < 50 ? 'bg-red-500' : 'bg-blue-500'}`} />
                </div>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-3">
              <p className="text-[9px] font-black text-zinc-500 uppercase tracking-[0.3em] mb-1 italic">Mode_Performance</p>
              <ModeCard label="SWING" val={metrics.distribution_par_type?.SWING || 0} active={selectedMode === 'SWING'} onClick={() => setSelectedMode('SWING')} color="blue" />
              <ModeCard label="DAILY" val={metrics.distribution_par_type?.DAILY || 0} active={selectedMode === 'DAILY'} onClick={() => setSelectedMode('DAILY')} color="yellow" />
              <ModeCard label="SCALP" val={metrics.distribution_par_type?.SCALP || 0} active={selectedMode === 'SCALP'} onClick={() => setSelectedMode('SCALP')} color="green" />
              <ModeCard label="INVESTOR" val={metrics.distribution_par_type?.INVESTOR || 0} active={selectedMode === 'INVESTOR'} onClick={() => setSelectedMode('INVESTOR')} color="purple" />
          </div>
        </div>

        {/* COLONNE CENTRALE */}
        <div className="col-span-12 lg:col-span-6 flex flex-col gap-6">
            {/* CORRECTION GRAPHIQUE : Définition d'une hauteur fixe stricte sur le parent de ResponsiveContainer */}
            <div className="bg-[#0B0E11] border border-white/10 rounded-[40px] shadow-2xl p-8 h-[450px] w-full flex flex-col min-h-[450px]">
                <div className="flex justify-between items-start mb-6">
                    <h2 className="text-[10px] font-black uppercase tracking-[0.4em] text-white flex items-center gap-2"><BarChart3 size={14} className="text-blue-500" /> Performance_Engine</h2>
                    <span className="text-[10px] font-mono text-zinc-600 uppercase italic">{selectedMode} / DD Hist: {risk.max_drawdown_historical}%</span>
                </div>
                
                {/* w-full h-full et min-h-0 indispensables pour neutraliser l'erreur width(-1) de Recharts */}
                <div className="w-full h-full min-h-0 flex-1">
                    <ResponsiveContainer width="100%" height="100%" minWidth={0} minHeight={0}>
                        <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                            <defs>
                                <linearGradient id="areaG" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.4} />
                                    <stop offset="100%" stopColor="#3b82f6" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="#ffffff05" vertical={false} />
                            <XAxis hide dataKey="name" />
                            <YAxis hide domain={['dataMin - 10', 'dataMax + 10']} />
                            <Tooltip contentStyle={{ backgroundColor: '#161A1E', border: 'none', borderRadius: '12px', fontSize: '10px' }} />
                            <Area type="monotone" dataKey="val" stroke="#3b82f6" strokeWidth={3} fill="url(#areaG)" />
                        </AreaChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* NEURAL REPORT */}
            <div className="bg-[#161A1E] border border-blue-500/20 rounded-[32px] p-8 relative overflow-hidden group shadow-lg">
                <div className="absolute top-0 left-0 w-1 h-full bg-blue-500 animate-pulse" />
                <h3 className="text-blue-400 text-[10px] font-black uppercase tracking-[0.3em] flex items-center gap-2 mb-6"><BrainCircuit size={16} /> Neural_Report_Analysis</h3>
                <div className="p-5 bg-black/40 rounded-2xl border border-white/5 font-mono text-[11px] leading-relaxed italic text-zinc-300">
                    <span className="text-blue-500 font-bold mr-2">{">"}</span>
                    Mental_State : <span className="text-white font-bold uppercase">{psy.state}</span> (Confiance: {psy.confidence}%). 
                    {risk.status !== 'SAFE' 
                        ? ` ALERTE CRITIQUE : Régime de risque en statut [${risk.status}]. Protection active.` 
                        : " Structure de risque nominale. Alignement psychologique et discipline validés."}
                    {psy.patterns && psy.patterns.length > 0 && (
                      <div className="mt-2 text-red-400 font-sans text-[10px] not-italic font-black">
                        ⚠️ ANOMALIES COMPORTEMENTALES COGNITIVES DÉTECTEES : {psy.patterns.join(", ")}
                      </div>
                    )}
                </div>
            </div>
        </div>

        {/* COLONNE DROITE */}
        <div className="col-span-12 lg:col-span-3 flex flex-col gap-6">
            <div className="bg-[#161A1E] border border-white/10 p-6 rounded-[32px] flex flex-col gap-4 shadow-2xl">
              <h3 className="text-zinc-500 text-[9px] font-black uppercase tracking-[0.4em] mb-2 italic">Detailed_Analytics</h3>
              <KpiRow label="Discipline (Alerts)" val={behavioralMemory.consistency_score} color="text-green-400" />
              <KpiRow label="Risk Velocity" val={risk.status === 'SAFE' ? 100 : 40} color="text-yellow-400" />
              <KpiRow label="Winrate" val={metrics.winrate || 0} color="text-blue-400" />
            </div>

            {/* 📁 DOSSIERS EN ATTENTE */}
            <div className="bg-[#161A1E] border border-white/10 p-6 rounded-[32px] flex flex-col shadow-2xl max-h-[220px] overflow-hidden">
              <div className="flex items-center gap-2 text-zinc-500 font-black text-[9px] uppercase tracking-[0.4em] mb-4">
                <FolderOpen size={12} className="text-yellow-500" />
                <span>Dossiers_Brouillons</span>
              </div>
              
              <div className="flex-1 overflow-y-auto custom-scrollbar space-y-2 pr-1">
                {brouillonsEnAttente.length === 0 ? (
                  <p className="text-[10px] text-zinc-600 font-mono italic text-center py-4">Aucun brouillon en attente.</p>
                ) : (
                  brouillonsEnAttente.map((t: any, idx: number) => {
                    const id = isinstanceOfTradeDict(t) ? t.id : t[0];
                    const actifName = isinstanceOfTradeDict(t) ? t.actif : t[2];
                    const modeName = isinstanceOfTradeDict(t) ? t.mode : t[10];
                    return (
                      <div key={idx} className="flex justify-between items-center bg-black/40 border border-white/5 p-2.5 rounded-xl hover:border-blue-500/30 transition-all">
                        <div className="flex flex-col text-left">
                          <span className="text-[11px] font-black text-white">{actifName}</span>
                          <span className="text-[8px] font-mono uppercase text-zinc-500 tracking-tighter">{modeName} (#TM-{id})</span>
                        </div>
                        <button onClick={() => handleReprendreSession(t)} className="p-2 bg-blue-600/10 hover:bg-blue-600 text-blue-400 hover:text-white rounded-lg transition-all group">
                          <Play size={10} className="group-hover:scale-110 transition-transform" />
                        </button>
                      </div>
                    );
                  })
                )}
              </div>
            </div>

            {/* NEURAL GATE */}
            <div className={`p-6 rounded-[32px] transition-all duration-700 ${risk.status === 'SAFE' ? 'bg-blue-600' : 'bg-red-600'} shadow-2xl`}>
                <div className="flex items-center gap-2 text-white/50 mb-6 font-black text-[9px] uppercase tracking-[0.4em]"><Shield size={14} /> Neural_Gate</div>
                <h3 className="text-white/60 text-[10px] font-black uppercase tracking-[0.2em] mb-1 italic text-center">Active_Focus</h3>
                <p className="text-4xl font-black text-white tracking-tighter mb-4 text-center underline decoration-white/20">{metrics.focus?.actif || "IDLE"}</p>
                <div className="bg-black/20 p-4 rounded-xl backdrop-blur-sm border border-white/5">
                    <div className="flex justify-between text-[10px] font-bold mb-2 uppercase text-white">
                        <span>Conviction</span>
                        <span>{metrics.focus?.conviction || 0}%</span>
                    </div>
                    <div className="h-1.5 w-full bg-white/10 rounded-full overflow-hidden">
                        <motion.div initial={{ width: 0 }} animate={{ width: `${metrics.focus?.conviction || 0}%` }} className="h-full bg-white" />
                    </div>
                </div>
            </div>
        </div>
      </div>
    </div>
  );
}

function isinstanceOfTradeDict(object: any): boolean {
  return object && typeof object === 'object' && !Array.isArray(object) && 'id' in object;
}

function ModeCard({ label, val, active, onClick, color }: { label: string, val: number, active: boolean, onClick: () => void, color: string }) {
    return (
        <button onClick={onClick} className={`flex flex-col p-4 rounded-2xl border transition-all w-full text-left ${active ? 'bg-white/10 border-white/30 ring-1 ring-white/20' : 'bg-[#161A1E] border-white/5 opacity-60 hover:opacity-100'}`}>
            <div className="flex justify-between items-center w-full">
                <span className="text-[9px] font-black text-white/50 uppercase tracking-widest">{label}</span>
                <span className="text-[10px] font-mono font-black text-white">{val} Dossier(s)</span>
            </div>
        </button>
    );
}

function KpiRow({ label, val, color }: { label: string, val: number | string, color: string }) {
    const numericVal = typeof val === 'number' ? val : parseFloat(val) || 0;
    return (
        <div className="flex flex-col gap-2 p-2 text-left">
            <div className="flex justify-between items-center text-[8px] font-black uppercase tracking-widest text-zinc-500">
                <span>{label}</span>
                <span className={color}>{val}{typeof val === 'number' && "%"}</span>
            </div>
            <div className="h-1 w-full bg-white/5 rounded-full overflow-hidden">
                <motion.div animate={{ width: `${Math.min(100, numericVal)}%` }} className={`h-full ${color.replace('text', 'bg')}`} />
            </div>
        </div>
    );
}