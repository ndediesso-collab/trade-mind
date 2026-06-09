"use client";

import React, { useState, useEffect } from "react";
import { AuroraBackground } from "@/components/ui/aurora-background";
import { motion, AnimatePresence } from "framer-motion";
import { 
  LayoutDashboard, History, Library, Settings, Plus, 
  ChartBarIcon, Activity, Globe, Zap, AlertTriangle, ExternalLink, RefreshCcw, ShieldAlert
} from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation"; 

// 👑 LOGISTIQUE SUPABASE INTERNE
import { createClient } from "@/utils/supabase/client"; 

export default function Home() {
  const [isSidebarOpen, setSidebarOpen] = useState(false);
  const [prices, setPrices] = useState({ 
    btcusdt: { price: "0.00", change: "0.00" }, 
    ethusdt: { price: "0.00", change: "0.00" }, 
    solusdt: { price: "0.00", change: "0.00" } 
  });

  const [intel, setIntel] = useState({
    fearGreed: { score: 50, rating: 'NEUTRAL', label: 'Initialisation...' },
    news: "Chargement du flux MentorIA..."
  });
  const [loading, setLoading] = useState(false);

  const router = useRouter();

  // 🛡️ SECURITY HANDSHAKE
  useEffect(() => {
    const checkUserSession = async () => {
      const supabase = createClient();
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) {
        router.push("/login"); 
      }
    };
    checkUserSession();
  }, [router]);

  // 1. LIVE MARKET STREAM (WebSocket Binance)
  useEffect(() => {
    const ws = new WebSocket("wss://stream.binance.com:9443/ws/btcusdt@ticker/ethusdt@ticker/solusdt@ticker");
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setPrices(prev => ({
        ...prev,
        [data.s.toLowerCase()]: { 
          price: parseFloat(data.c).toFixed(2), 
          change: parseFloat(data.P).toFixed(2) 
        }
      }));
    };
    return () => ws.close();
  }, []);

  // 2. SYNCHRONISATION MENTOR IA (MarketGuard Bridge)
  // 2. SYNCHRONISATION MENTOR IA (MarketGuard Bridge)
  const syncIntelligence = async () => {
    setLoading(true);
    try {
      const res = await fetch('https://trade-mind-w6rs.onrender.com/market/intelligence');
      const data = await res.json();
      
      // On met à jour avec les données reçues, même si elles sont partielles
      setIntel({
        fearGreed: data.fear_greed || { score: 50, rating: 'NEUTRAL', label: 'Indisponible' },
        news: data.news_feed || "Flux d'intelligence momentanément suspendu."
      });
    } catch (e) {
      console.error("Erreur de synchronisation, mode dégradé activé", e);
      // ICI : On affiche ce qu'on peut, sans bloquer l'interface
      setIntel(prev => ({
        ...prev,
        news: "Système Market Intelligence actif (Mode Lecture Seule)"
      }));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    syncIntelligence();
    const interval = setInterval(syncIntelligence, 60000);
    return () => clearInterval(interval);
  }, []);

  const navItems = [
    { id: 'dashboard', name: 'Mind Engine', path: '/dashboard', icon: <LayoutDashboard size={19} /> },
    { id: 'historique', name: 'Historique', path: '/historique', icon: <History size={19} /> },
    { id: 'library', name: 'Bibliothèque', path: '/library', icon: <Library size={19} /> },
    { id: 'resources', name: 'Analyse & Stats', path: '/resources', icon: <ChartBarIcon size={19} /> },
    { id: 'settings', name: 'Paramètres', path: '/settings', icon: <Settings size={19} /> },
  ];

  const tradingModes = [
    { name: 'Swing Trading', path: '/swing', desc: 'Suivi des tendances macroéconomiques' },
    { name: 'Daily Trading', path: '/daily', desc: 'Exploitation des sessions intraday' },
    { name: 'Scalping', path: '/scalp', desc: 'Exécution ultra-rapide à haute vélocité' },
    { name: 'Investor Mode', path: '/investor', desc: 'Gestion de portefeuille moyen & long terme' },
  ];

  const currentScore = intel?.fearGreed?.score ?? 50;
  const currentRating = intel?.fearGreed?.rating ?? 'NEUTRAL';

  return (
    <AuroraBackground className="bg-[#090B0D]">
      <div className="min-h-screen w-full text-zinc-100 antialiased relative flex selection:bg-blue-500/20">
        
        {/* 1. SIDEBAR MINIMALISTE SANS BRUIT VISUEL */}
        <motion.aside 
          onMouseEnter={() => setSidebarOpen(true)}
          onMouseLeave={() => setSidebarOpen(false)}
          className="fixed left-5 top-1/2 -translate-y-1/2 z-50 flex flex-col gap-1.5 p-2 bg-zinc-950/40 backdrop-blur-2xl border border-white/5 rounded-2xl shadow-[0_30px_60px_-15px_rgba(0,0,0,0.7)]"
          animate={{ width: isSidebarOpen ? "210px" : "56px" }}
          transition={{ type: "spring", stiffness: 220, damping: 28 }}
        >
          <div className="flex items-center gap-3.5 p-3 mb-1 border-b border-white/5 overflow-hidden">
            <Activity size={15} className="text-blue-400 animate-pulse min-w-[15px]" />
            {isSidebarOpen && (
              <span className="text-[10px] font-semibold uppercase tracking-widest text-zinc-500">Navigation</span>
            )}
          </div>

          {navItems.map((item) => (
            <Link href={item.path} key={item.id} className="flex items-center gap-4 p-3 rounded-xl hover:bg-white/5 text-zinc-400 hover:text-zinc-100 transition-all group relative">
              <div className="min-w-[19px] text-zinc-400 group-hover:text-blue-400 transition-colors">{item.icon}</div>
              <AnimatePresence>
                {isSidebarOpen && (
                  <motion.span initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -8 }} className="text-xs font-medium tracking-wide whitespace-nowrap">
                    {item.name}
                  </motion.span>
                )}
              </AnimatePresence>
            </Link>
          ))}
        </motion.aside>

        {/* CONTENEUR PRINCIPAL ÉPURÉ */}
        <div className="flex-1 flex flex-col h-screen p-8 pl-28 pr-8 max-w-[1450px] mx-auto z-10 relative">
          
          {/* 2. TOP EXECUTIVE BAR */}
          <header className="flex justify-between items-center mb-8 border-b border-white/5 pb-5">
            <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} className="flex items-baseline gap-4">
              <span className="text-2xl font-semibold tracking-tight text-white">Trade Mind</span>
              <span className="text-[10px] font-medium text-zinc-500 tracking-wider">v2.0 // Node Active</span>
            </motion.div>
            
            <div className="flex items-center gap-6 text-[10px] text-zinc-400 font-medium tracking-wider">
              <div className="text-right hidden sm:block leading-tight text-zinc-500">
                Network: <span className="text-blue-400">MarketGuard Stream</span>
                <span className="mx-2 text-zinc-700">|</span>
                Security: <span className="text-zinc-300">Ghost Secure</span>
              </div>
              <button onClick={syncIntelligence} className="p-2 bg-zinc-900/40 hover:bg-zinc-900/80 border border-white/5 rounded-xl text-zinc-400 hover:text-white transition-all shadow-md">
                <RefreshCcw size={13} className={loading ? 'animate-spin text-blue-400' : ''} />
              </button>
            </div>
          </header>

          {/* 3. CORE ASYMMETRIC GRID */}
          <div className="grid grid-cols-12 gap-6 flex-1 min-h-0 mb-6">
            
            {/* VECTEUR DE TRADING (GAUCHE) */}
            <div className="col-span-12 xl:col-span-4 flex flex-col gap-3 min-h-0">
              <span className="text-[10px] font-semibold text-zinc-500 uppercase tracking-widest mb-1">Configuration Opérationnelle</span>
              <div className="grid grid-cols-1 gap-3 flex-1 overflow-y-auto pr-1 custom-scrollbar">
                {tradingModes.map((mode) => (
                  <Link href={mode.path} key={mode.name} className="group relative bg-zinc-900/20 hover:bg-zinc-900/40 backdrop-blur-md border border-white/5 hover:border-zinc-700 p-5 rounded-2xl flex flex-col justify-between transition-all duration-300 shadow-lg">
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="text-base font-semibold tracking-tight text-zinc-200 group-hover:text-white transition-colors">{mode.name}</h3>
                        <p className="text-xs text-zinc-500 mt-1.5 leading-relaxed font-light">{mode.desc}</p>
                      </div>
                      <div className="p-2 bg-white/5 rounded-xl border border-white/5 group-hover:bg-blue-500/10 group-hover:border-blue-500/20 transition-all">
                        <Plus size={13} className="text-zinc-500 group-hover:text-blue-400 transition-transform duration-300 group-hover:rotate-90" />
                      </div>
                    </div>
                    <div className="mt-4 pt-3 border-t border-white/5 flex justify-between items-center text-[9px] tracking-wider text-zinc-600 group-hover:text-blue-400 transition-colors font-medium uppercase">
                      <span>Prêt au logging</span>
                      <span>Initialiser l'analyse &rarr;</span>
                    </div>
                  </Link>
                ))}
              </div>
            </div>

            {/* MONITORING DE MARCHÉ FLUIDE (MILIEU) */}
            <div className="col-span-12 md:col-span-6 xl:col-span-5 bg-zinc-900/20 backdrop-blur-md border border-white/5 rounded-2xl flex flex-col overflow-hidden shadow-xl">
              <div className="p-4 border-b border-white/5 flex items-center justify-between bg-zinc-900/30">
                <div className="flex gap-2.5 items-center">
                  <Zap size={13} className="text-amber-400" />
                  <span className="text-[10px] font-semibold text-zinc-400 uppercase tracking-widest">Flux d'Actifs Temps Réel</span>
                </div>
                <span className="text-[9px] text-zinc-600 tracking-wider font-mono">WS_BINANCE_CONNECTED</span>
              </div>

              <div className="flex-1 p-5 space-y-3 overflow-y-auto custom-scrollbar bg-zinc-950/10">
                {Object.entries(prices).map(([symbol, data]) => {
                  const isPositive = parseFloat(data.change) >= 0;
                  return (
                    <div key={symbol} className="p-4 rounded-xl flex items-center justify-between border border-white/[0.02] bg-zinc-900/10 hover:bg-zinc-900/30 hover:border-white/10 transition-all duration-200 group">
                      <div className="flex flex-col">
                        <span className="text-[10px] font-bold text-zinc-500 tracking-wider uppercase font-mono">{symbol.replace('usdt', '')} / USDT</span>
                        <span className="text-xl font-medium text-white tracking-tight mt-1 tabular-nums">${data.price}</span>
                      </div>
                      <div className="text-right flex flex-col items-end justify-between h-full">
                        <span className={`text-xs font-medium px-2 py-0.5 rounded-md font-mono ${isPositive ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'}`}>
                          {isPositive ? '+' : ''}{data.change}%
                        </span>
                        <div className="h-5 w-20 mt-3 opacity-10 group-hover:opacity-40 transition-opacity">
                           <svg viewBox="0 0 100 20" className="w-full h-full">
                             <path d={isPositive ? "M0 16 Q 25 4, 50 11 T 100 2" : "M0 2 Q 25 16, 50 7 T 100 18"} fill="none" stroke={isPositive ? '#22c55e' : '#ef4444'} strokeWidth="1.5" />
                           </svg>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* BLOC FUSIONNÉ : GLOBAL MARKET INTELLIGENCE */}
            <div className="col-span-12 md:col-span-6 xl:col-span-3 flex flex-col gap-4 overflow-hidden">
              <div className="bg-zinc-900/20 backdrop-blur-md border border-white/5 rounded-2xl p-5 shadow-xl flex flex-col h-full min-h-[500px]">
                <div className="flex items-center justify-between mb-6 border-b border-white/5 pb-4">
                  <span className="text-[10px] font-semibold text-zinc-400 uppercase tracking-widest">Global Market Intelligence</span>
                  <Globe size={13} className="text-zinc-500" />
                </div>
                
                <div className="text-center mb-6">
                  <div className="text-5xl font-bold text-white mb-1">{currentScore}</div>
                  <div className={`text-[10px] font-bold uppercase tracking-widest ${currentScore > 50 ? 'text-green-500' : 'text-red-500'}`}>
                    {currentRating}
                  </div>
                </div>

                <div className="flex-1 overflow-y-auto custom-scrollbar pr-2 space-y-4 font-sans text-[11px] text-zinc-400">
                  <div className="whitespace-pre-line leading-relaxed italic font-light">
                    {intel.news}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* 4. DISCRET DISPATCH ACTION BUTTON */}
          <footer className="flex justify-end p-2">
            <Link href="/swing">
              <motion.button 
                whileHover={{ scale: 1.01, backgroundColor: "#2563eb" }} 
                whileTap={{ scale: 0.99 }} 
                className="px-8 py-3 bg-blue-600 text-white rounded-xl text-xs font-medium tracking-wide shadow-xl border border-blue-500/20 transition-all duration-200"
              >
                Ouvrir le terminal principal &rarr;
              </motion.button>
            </Link>
          </footer>
          
        </div>
      </div>
    </AuroraBackground>
  );
}