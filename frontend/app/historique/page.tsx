"use client";

import useSWR, { mutate } from 'swr';
import { 
  ArrowLeft, Eye, Trash2, Database, ShieldCheck, Target, 
  TrendingUp, TrendingDown, Minus, Activity, AlertTriangle, 
  Play, Layers, Zap, Clock, Briefcase 
} from "lucide-react";
import Link from "next/link";
import { useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';

const fetcher = (url: string) => fetch(url).then((res) => {
    if (!res.ok) throw new Error('Erreur réseau');
    return res.json();
});

export default function HistoriquePage() {
    const router = useRouter();
    const { data, error, isLoading } = useSWR('https://trade-mind-w6rs.onrender.com/historique/all', fetcher, {
        refreshInterval: 3000,
        revalidateOnFocus: true
    });
    
    const [selectedTrade, setSelectedTrade] = useState<any>(null);
    const [filter, setFilter] = useState("ALL");

    const tradeCategories = [
        { id: "ALL", label: "Tous", icon: <Layers size={14} /> },
        { id: "SWING", label: "Swing", icon: <Target size={14} /> },
        { id: "INTRADAY", label: "Daily", icon: <Clock size={14} /> },
        { id: "SCALPING", label: "Scalp", icon: <Zap size={14} /> },
        { id: "INVESTOR", label: "Investor", icon: <Briefcase size={14} /> },
    ];

    const deleteTrade = async (id: number) => {
        if (!confirm("🚨 Supprimer définitivement cette exécution de la base SQL ?")) return;
        try {
            const res = await fetch(`https://trade-mind-w6rs.onrender.com/historique/delete/${id}`, { method: 'DELETE' });
            if (res.ok) {
                mutate('https://trade-mind-w6rs.onrender.com/historique/all'); 
                if (selectedTrade?.id === id) setSelectedTrade(null);
            }
        } catch (e) {
            console.error("Erreur suppression:", e);
        }
    };

    const reprendreAnalyse = async (trade: any) => {
        try {
            // 1. Récupération complète depuis le backend (Supabase)
            const res = await fetch(`https://trade-mind-w6rs.onrender.com/historique/get/${trade.id}`);
            if (!res.ok) throw new Error("Échec de récupération");
            const fullTrade = await res.json();

            // 2. Nettoyage des données pour éviter les pollutions de texte
            const texteNettoye = (fullTrade.analyse || "")
                .replace("[PLAN AVANT-TRADE] : ", "")
                .replace("[PLAN AVANT-SÉANCE SCALP] : ", "");

            // 3. Préparation du payload de restauration
            const restorePayload = {
                trade_id: fullTrade.id,
                actif: fullTrade.actif || "EURUSD",
                biais: fullTrade.position || "NEUTRE",
                conviction: fullTrade.conviction || 50,
                analyse: texteNettoye,
                mode: (fullTrade.type || "SWING").toUpperCase(),
                timestamp: Date.now()
            };

            // 4. Injection dans le stockage persistant et redirection
            const currentType = restorePayload.mode;

            if (currentType === "INTRADAY") {
                sessionStorage.setItem("daily_restore", JSON.stringify(restorePayload));
                router.push("/daily");
            } 
            else if (currentType === "SCALPING") {
                sessionStorage.setItem("scalp_restore", JSON.stringify(restorePayload));
                router.push("/scalp");
            }
            else if (currentType === "INVESTOR") {
                sessionStorage.setItem("investor_restore", JSON.stringify(restorePayload));
                router.push("/investor");
            }
            else {
                localStorage.setItem("tm_swing_cache", JSON.stringify(restorePayload));
                router.push("/swing");
            }
        } catch (e) {
            console.error("Erreur Restauration:", e);
            alert("🚨 Erreur critique : Impossible de charger les données du trade.");
        }
    };

    const filteredTrades = useMemo(() => {
        const trades = data?.trades || [];
        if (filter === "ALL") return trades;
        return trades.filter((t: any) => (t.type || "SWING").toUpperCase() === filter);
    }, [data, filter]);

    if (error) return (
        <div className="min-h-screen bg-[#0B0E14] flex items-center justify-center p-10 font-sans">
            <div className="bg-red-500/10 border border-red-500/20 p-8 rounded-[32px] text-center max-w-md">
                <AlertTriangle className="text-red-500 mx-auto mb-4" size={48} />
                <h2 className="text-red-500 font-black uppercase tracking-widest mb-2 italic">Liaison SQL Interrompue</h2>
                <p className="text-zinc-500 text-[10px] leading-relaxed uppercase tracking-tighter text-center">Le serveur Python sur le port 8000 ne répond pas.</p>
            </div>
        </div>
    );

    if (isLoading && !data) return (
        <div className="min-h-screen bg-[#0B0E14] flex items-center justify-center">
            <div className="text-center space-y-4">
                <Activity className="text-blue-500 animate-spin mx-auto" size={40} />
                <p className="text-zinc-500 font-black uppercase text-[10px] tracking-[0.5em]">Synchronisation_Archives...</p>
            </div>
        </div>
    );

    return (
        <div className="min-h-screen bg-[#0B0E14] text-white p-8 font-sans selection:bg-blue-500/30">
            <header className="flex flex-col md:flex-row justify-between items-start md:items-end mb-12 max-w-7xl mx-auto gap-6 animate-in fade-in slide-in-from-top-4 duration-700">
                <div>
                    <Link href="/" className="flex items-center gap-2 text-zinc-500 hover:text-white mb-4 transition-all group">
                        <ArrowLeft size={16} className="group-hover:-translate-x-1 transition-transform" /> 
                        <span className="text-[10px] font-black uppercase tracking-widest">Back to Hub</span>
                    </Link>
                    <h1 className="text-5xl font-black tracking-tighter italic uppercase">Audits_Archivés</h1>
                </div>
                <div className="flex bg-black/40 p-1 rounded-2xl border border-white/5 gap-1 shadow-2xl backdrop-blur-md">
                    {tradeCategories.map((cat) => (
                        <button
                            key={cat.id}
                            onClick={() => setFilter(cat.id)}
                            className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all ${
                                filter === cat.id ? "bg-blue-600 text-white shadow-lg" : "text-zinc-500 hover:bg-white/5"
                            }`}
                        >
                            {cat.icon} {cat.label}
                        </button>
                    ))}
                </div>
            </header>

            <div className="grid grid-cols-12 gap-8 max-w-7xl mx-auto">
                <div className="col-span-7 space-y-4 max-h-[75vh] overflow-y-auto pr-4 custom-scrollbar">
                    {filteredTrades.length === 0 ? (
                        <div className="py-32 text-center border-2 border-dashed border-white/5 rounded-[40px] opacity-20">
                            <Layers className="mx-auto mb-4" size={40} />
                            <p className="text-zinc-500 font-black uppercase tracking-widest text-[10px]">Aucun flux archivé dans ce secteur</p>
                        </div>
                    ) : (
                        filteredTrades.map((t: any) => {
                            // Normalisation du statut pour la logique d'affichage
                            const status = String(t.statut || "BROUILLON").toUpperCase().trim();
                            const isDraft = ["BROUILLON", "DRAFT"].includes(status);
                            
                            return (
                                <div key={t.id} 
                                    className={`group relative bg-[#161B22] border transition-all duration-300 p-6 rounded-[32px] flex justify-between items-center hover:border-zinc-500 cursor-pointer shadow-xl ${
                                        selectedTrade?.id === t.id ? 'border-blue-500 bg-[#1c212a]' : 'border-[#30363D]'
                                    }`}
                                    onClick={() => setSelectedTrade(t)}>
                                    
                                    <div className="flex items-center gap-6">
                                        <div className={`w-14 h-14 rounded-2xl flex items-center justify-center shadow-inner ${
                                            t.position === 'LONG' || t.position === 'Achat' ? 'bg-green-500/10 text-green-500' : 
                                            t.position === 'SHORT' || t.position === 'Vente' ? 'bg-red-500/10 text-red-500' : 'bg-zinc-800 text-zinc-500'
                                        }`}>
                                            {t.position === 'LONG' || t.position === 'Achat' ? <TrendingUp size={24} /> : 
                                            t.position === 'SHORT' || t.position === 'Vente' ? <TrendingDown size={24} /> : <Minus size={24} />}
                                        </div>
                                        <div>
                                            <div className="flex items-center gap-3 mb-1">
                                                <span className="text-[9px] font-black text-zinc-500 uppercase tracking-widest">{t.date ? String(t.date).slice(0,10) : "Intraday"}</span>
                                                <span className="px-2 py-0.5 bg-blue-900/30 text-blue-400 text-[8px] font-black rounded-md uppercase tracking-tighter border border-blue-500/10">
                                                    {t.type === "INTRADAY" ? "DAILY" : t.type === "SCALPING" ? "SCALP" : t.type || "SWING"}
                                                </span>
                                                {isDraft && <span className="px-2 py-0.5 bg-yellow-500/10 text-yellow-500 text-[8px] font-black rounded-md uppercase animate-pulse">Draft</span>}
                                                {status === 'WIN' && <span className="px-2 py-0.5 bg-green-500/10 text-green-500 text-[8px] font-black rounded-md uppercase">WIN</span>}
                                                {status === 'LOSS' && <span className="px-2 py-0.5 bg-red-500/10 text-red-500 text-[8px] font-black rounded-md uppercase">LOSS</span>}
                                            </div>
                                            <h3 className="text-2xl font-black tracking-tighter text-zinc-100 uppercase font-sans">{t.actif}</h3>
                                        </div>
                                    </div>

                                    <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-all">
                                        {isDraft && (
                                            <button onClick={(e) => { e.stopPropagation(); reprendreAnalyse(t); }} className="w-11 h-11 flex items-center justify-center bg-yellow-600 text-black rounded-2xl hover:bg-yellow-500 transition-all shadow-lg active:scale-90" title="Reprendre">
                                                <Play size={20} fill="currentColor" />
                                            </button>
                                        )}
                                        <button className="w-11 h-11 flex items-center justify-center bg-blue-600 text-white rounded-2xl hover:bg-blue-500 transition-all shadow-lg active:scale-90">
                                            <Eye size={20} />
                                        </button>
                                        <button onClick={(e) => { e.stopPropagation(); deleteTrade(t.id); }} className="w-11 h-11 flex items-center justify-center bg-zinc-800 text-zinc-400 rounded-2xl hover:bg-red-600 hover:text-white transition-all shadow-lg active:scale-90">
                                            <Trash2 size={20} />
                                        </button>
                                    </div>
                                </div>
                            );
                        })
                    )}
                </div>

                <div className="col-span-5">
                    <div className="bg-[#161B22] border border-[#30363D] rounded-[40px] overflow-hidden sticky top-8 shadow-2xl h-[600px] flex flex-col">
                        <div className="bg-[#1F242C] px-8 py-5 border-b border-[#30363D] flex justify-between items-center">
                            <span className="text-[10px] font-black text-zinc-100 uppercase tracking-[0.3em]">Report_Viewer_v5</span>
                            <div className="bg-blue-600/20 px-3 py-1 rounded-full border border-blue-500/20">
                                <span className="text-[8px] font-black text-blue-400 uppercase tracking-widest">{selectedTrade?.type || "Waiting"}</span>
                            </div>
                        </div>
                        <div className="p-8 font-mono text-sm overflow-y-auto flex-1 bg-[radial-gradient(circle_at_bottom_left,rgba(37,99,235,0.02),transparent)]">
                            {selectedTrade ? (
                                <div className="space-y-8">
                                    {/* Logic ID */}
                                    <div className="p-5 bg-black/40 rounded-[24px] border border-white/5">
                                        <p className="text-[8px] text-zinc-600 uppercase font-black mb-2 tracking-widest">Logic_ID</p>
                                        <p className="text-blue-400 font-black text-lg">#TM-{selectedTrade.id.toString().padStart(4, '0')}</p>
                                    </div>
                                    
                                    {/* Workspace Content */}
                                    <div className="space-y-4">
                                        <div className="flex items-center gap-2 text-blue-500/50">
                                            <Target size={14} />
                                            <span className="text-[10px] font-black uppercase tracking-widest">Workspace_Content</span>
                                        </div>
                                        <div className="p-6 bg-black/30 rounded-[32px] border border-white/5 text-zinc-300 text-xs leading-relaxed italic border-l-4 border-l-blue-600 whitespace-pre-wrap">
                                            {selectedTrade.analyse || "> Aucune donnée textuelle."}
                                        </div>
                                    </div>

                                    {/* NEURAL FEEDBACK (Réinjecté ici) */}
                                    <div className="space-y-4">
                                        <div className="flex items-center gap-2 text-green-500/50">
                                            <ShieldCheck size={14} />
                                            <span className="text-[10px] font-black uppercase tracking-widest">Neural_Feedback</span>
                                        </div>
                                        <div className="p-6 bg-green-500/[0.02] rounded-[32px] border border-green-500/10 text-green-400/70 text-[11px] leading-relaxed whitespace-pre-wrap">
                                            {selectedTrade.feedback || "> MENTOR_IA: Aucune rétroaction disponible pour ce cycle."}
                                        </div>
                                    </div>

                                    {/* Bouton Restauration */}
                                    {['BROUILLON', 'DRAFT'].includes(String(selectedTrade.statut || "").toUpperCase().trim()) && (
                                        <button 
                                            onClick={() => reprendreAnalyse(selectedTrade)} 
                                            className="w-full py-5 bg-blue-600 text-white rounded-3xl text-[10px] font-black uppercase tracking-[0.3em] hover:bg-blue-500 transition-all active:scale-95 shadow-xl shadow-blue-900/20"
                                        >
                                            <Play size={14} fill="white" /> Restaurer_Session
                                        </button>
                                    )}
                                </div>
                            ) : (
                                <div className="h-full flex flex-col items-center justify-center opacity-20">
                                    <Database size={64} className="animate-pulse mb-6 text-zinc-600" />
                                    <p className="text-[10px] font-black uppercase tracking-[0.5em] text-center text-zinc-500">Flux_Statique<br/>Saisie requise</p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}