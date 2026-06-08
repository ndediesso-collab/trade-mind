"use client";

import { ArrowLeft, Zap, BarChart3, Radio, ExternalLink, BrainCircuit } from "lucide-react";
import Link from "next/link";

export default function ResourcesPage() {
  return (
    <div className="min-h-screen bg-[#06080A] text-zinc-100 p-8 font-sans">
      
      {/* HEADER NAVIGATION */}
      <header className="flex justify-between items-center mb-16 max-w-5xl mx-auto">
        <Link href="/" className="flex items-center gap-2 text-zinc-500 hover:text-zinc-200 transition-all group">
          <ArrowLeft size={16} className="group-hover:-translate-x-1 transition-transform" /> 
          <span className="text-[9px] font-bold uppercase tracking-[0.2em]">Retour au Terminal</span>
        </Link>
        <div className="flex items-center gap-2 bg-blue-900/10 border border-blue-500/20 px-3 py-1.5 rounded-lg">
          <Zap size={12} className="text-blue-400" />
          <span className="text-[9px] font-bold text-blue-400 uppercase tracking-[0.2em]">Niveau Institutionnel A</span>
        </div>
      </header>

      <main className="max-w-5xl mx-auto">
        {/* TITRE DE SECTION */}
        <div className="mb-16">
          <h1 className="text-3xl font-semibold tracking-tight text-white mb-2 italic">Ressources Pro</h1>
          <p className="text-zinc-500 text-xs tracking-wide">Données en flux tendu et analyses macro-économiques.</p>
        </div>

        <div className="space-y-16">
          
          {/* CATEGORIE 1 : LIVE & NEWS */}
          <section className="space-y-6">
            <div className="flex items-center gap-3 border-b border-white/5 pb-4">
              <Radio className="text-red-500" size={16} />
              <h2 className="text-[10px] font-bold uppercase tracking-[0.3em] text-zinc-400">Flux Direct & Actualités</h2>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <ResourceCard 
                title="InvestingLive" 
                desc="Flux Vidéo & Audio en temps réel" 
                url="https://investinglive.com/" 
                isLive={true}
              />
              <ResourceCard 
                title="Investing.com" 
                desc="Portail Global de Marchés" 
                url="https://fr.investing.com/" 
              />
              <ResourceCard 
                title="Bloomberg" 
                desc="Terminal d'information référence" 
                url="https://www.bloomberg.com/markets" 
              />
            </div>
          </section>

          {/* CATEGORIE 2 : MACRO & ANALYSE */}
          <section className="space-y-6">
            <div className="flex items-center gap-3 border-b border-white/5 pb-4">
              <BrainCircuit className="text-blue-500" size={16} />
              <h2 className="text-[10px] font-bold uppercase tracking-[0.3em] text-zinc-400">Analyse Fondamentale</h2>
            </div>
            
            <div className="space-y-2">
              <MacroRow 
                title="Forex Factory" 
                desc="Calendrier Économique Haute Précision" 
                url="https://www.forexfactory.com/calendar"
                icon="📅"
              />
              <MacroRow 
                title="CME FedWatch" 
                desc="Anticipations des Taux de la FED" 
                url="https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html"
                icon="🏦"
              />
              <MacroRow 
                title="Trading Economics" 
                desc="Base de données statistiques mondiales" 
                url="https://tradingeconomics.com"
                icon="🌍"
              />
            </div>
          </section>

          {/* CATEGORIE 3 : SENTIMENT */}
          <section className="space-y-6">
            <div className="flex items-center gap-3 border-b border-white/5 pb-4">
              <BarChart3 className="text-orange-500" size={16} />
              <h2 className="text-[10px] font-bold uppercase tracking-[0.3em] text-zinc-400">Sentiment & Charting</h2>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <ResourceCard 
                title="TradingView" 
                desc="Analyse technique et graphiques" 
                url="https://www.tradingview.com" 
              />
              <ResourceCard 
                title="Fear & Greed" 
                desc="Indice de sentiment CNN Business" 
                url="https://edition.cnn.com/markets/fear-and-greed" 
              />
            </div>
          </section>
        </div>

        <footer className="mt-24 flex justify-center pb-12">
            <Link href="/" className="px-8 py-3 bg-zinc-900 border border-white/5 rounded-full text-zinc-400 hover:text-white transition-all text-[9px] font-bold uppercase tracking-[0.2em]">
                Retour au hub
            </Link>
        </footer>
      </main>
    </div>
  );
}

// COMPOSANTS INTERNES
function ResourceCard({ title, desc, url, isLive = false }: { title: string, desc: string, url: string, isLive?: boolean }) {
  return (
    <a 
      href={url} 
      target="_blank" 
      rel="noopener noreferrer"
      className={`group p-6 rounded-2xl border transition-all duration-300 ${
        isLive ? 'bg-red-950/10 border-red-900/30 hover:bg-red-900/20' : 'bg-zinc-900/20 border-white/5 hover:bg-zinc-900/40 hover:border-blue-500/20'
      }`}
    >
      <div className="flex justify-between items-start mb-6">
        {isLive && <span className="flex items-center gap-1.5 text-[8px] font-bold text-red-500 uppercase tracking-widest animate-pulse">🔴 Live</span>}
        <ExternalLink size={12} className="text-zinc-600 group-hover:text-zinc-300 transition-colors ml-auto" />
      </div>
      <h3 className="text-base font-semibold text-zinc-200 mb-1 group-hover:text-white transition-colors">{title}</h3>
      <p className="text-[11px] text-zinc-500 font-light">{desc}</p>
    </a>
  );
}

function MacroRow({ title, desc, url, icon }: { title: string, desc: string, url: string, icon: string }) {
  return (
    <a 
      href={url} 
      target="_blank" 
      rel="noopener noreferrer"
      className="flex items-center justify-between p-4 bg-zinc-900/10 border border-white/5 rounded-xl hover:bg-zinc-900/30 hover:border-zinc-700 group transition-all"
    >
      <div className="flex items-center gap-4">
        <span className="text-lg opacity-80">{icon}</span>
        <div>
            <h4 className="text-[13px] font-medium text-zinc-200 group-hover:text-blue-400 transition-colors">{title}</h4>
            <p className="text-[10px] text-zinc-500 font-medium tracking-wide uppercase mt-0.5">{desc}</p>
        </div>
      </div>
      <div className="text-[9px] font-bold text-zinc-600 group-hover:text-blue-400 uppercase tracking-wider transition-all">
        Accéder →
      </div>
    </a>
  );
}