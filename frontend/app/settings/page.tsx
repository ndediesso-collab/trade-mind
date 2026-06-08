"use client";

import { useState } from "react";
import { 
  ArrowLeft, ShieldCheck, BrainCircuit, 
  AlertTriangle, Gem, Save, CheckCircle2, Lock, Key, Database,
  Globe, Activity, Smartphone, CreditCard
} from "lucide-react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState("Accès Terminal");
  const [isPro, setIsPro] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [paymentRegion, setPaymentRegion] = useState("AFRIQUE"); // "AFRIQUE" ou "INTERNATIONAL"

  const menuItems = [
    { id: "Accès Terminal", label: "Accès Terminal", icon: <Key size={14} />, free: true },
    { id: "Protocole Risque", label: "Protocole Risque", icon: <ShieldCheck size={14} />, free: false },
    { id: "AI Persona", label: "AI Persona", icon: <BrainCircuit size={14} />, free: false },
    { id: "Responsabilité", label: "Responsabilité", icon: <AlertTriangle size={14} />, free: true },
  ];

  const handleSave = async () => {
    setIsSaving(true);
    setTimeout(() => {
      setIsSaving(false);
      alert(`Système : Configuration "${activeTab}" synchronisée.`);
    }, 1000);
  };

  // FONCTIONS DE PAIEMENT INJECTÉES POUR VENDREDI
  const handleAfricanPayment = (provider: string) => {
    console.log(`Initialisation paiement Afrique via: ${provider}`);
    alert(`[Passerelle Flutterwave] : Redirection vers l'interface sécurisée ${provider} pour un montant de 8 000 FCFA...`);
  };

  const handleInternationalPayment = (gateway: string) => {
    console.log(`Initialisation paiement International via: ${gateway}`);
    alert(`[Passerelle ${gateway}] : Connexion au point de terminaison sécurisé (Montant: 20 €)...`);
  };

  return (
    <div className="min-h-screen bg-black text-white flex font-sans selection:bg-blue-500/30">
      
      {/* SIDEBAR */}
      <aside className="w-72 bg-[#0A0A0A] border-r border-white/5 flex flex-col text-zinc-500">
        <div className="p-8">
          <h2 className="text-[#14254C] text-[10px] font-black uppercase tracking-[0.4em] mb-10 italic">Core_Configuration</h2>
          <nav className="space-y-1">
            {menuItems.map((item) => (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center justify-between px-4 py-3 rounded-xl text-[10px] font-bold uppercase tracking-widest transition-all group ${
                  activeTab === item.id 
                  ? "bg-zinc-900 text-white border border-white/10 shadow-[0_0_20px_rgba(0,0,0,0.5)]" 
                  : "hover:text-white hover:bg-zinc-900/40"
                }`}
              >
                <div className="flex items-center gap-3">
                  {item.icon} {item.label}
                </div>
                {!item.free && !isPro && <Lock size={10} className="text-zinc-700" />}
              </button>
            ))}
          </nav>
          <div className="h-px bg-white/5 my-6 mx-2" />
          
          {/* BOUTON D'ABONNEMENT PRO CONNECTÉ À L'ONGLET */}
          <button 
            onClick={() => setActiveTab("Abonnement Pro")}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-[10px] font-black uppercase tracking-wider transition-all ${
              activeTab === "Abonnement Pro" 
              ? "bg-[#F1C40F]/10 text-[#F1C40F] border border-[#F1C40F]/20" 
              : "text-[#F1C40F] hover:bg-[#F1C40F]/5"
            }`}
          >
            <Gem size={14} /> Abonnement Pro
          </button>
        </div>
        <div className="mt-auto p-6">
          <Link href="/" className="flex items-center justify-center gap-2 w-full py-4 bg-zinc-900 border border-white/10 rounded-2xl text-[10px] font-black uppercase tracking-widest hover:bg-white hover:text-black transition-all">
            <ArrowLeft size={14} /> Retour Menu
          </Link>
        </div>
      </aside>

      {/* CONTENU */}
      <main className="flex-1 bg-black flex flex-col overflow-hidden">
        <header className="p-12 pb-6 flex justify-between items-center">
          <div>
            <h1 className="text-4xl font-black tracking-tighter uppercase text-[#081E58] italic">{activeTab}</h1>
            <p className="text-[9px] font-mono text-zinc-500 uppercase tracking-widest mt-1 italic">Intelligence_Layer_v2.0_Settings</p>
          </div>
          
          {activeTab !== "Abonnement Pro" && (
            <button 
              onClick={handleSave}
              disabled={isSaving}
              className="flex items-center gap-3 bg-[#081E58] px-8 py-3 rounded-2xl text-[10px] font-black uppercase hover:bg-blue-600 transition-all shadow-xl shadow-blue-900/20"
            >
              {isSaving ? <Loader2 size={14} className="animate-spin" /> : <Save size={14} />} 
              Appliquer_Config
            </button>
          )}
        </header>

        <div className="flex-1 p-12 pt-6 overflow-y-auto custom-scrollbar">
          <div className="max-w-4xl">
            <AnimatePresence mode="wait">
              <motion.div
                key={activeTab}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.2 }}
              >
                
                {/* ACCÈS TERMINAL */}
                {activeTab === "Accès Terminal" && (
                  <div className="space-y-6">
                    <SettingCard title="Authentification_Utilisateur">
                       <div className="grid grid-cols-2 gap-4">
                          <input type="email" placeholder="Terminal_ID (Email)" className="w-full bg-[#1A1A1A] border border-white/5 rounded-2xl p-4 text-sm font-bold outline-none focus:border-blue-500/50 text-blue-400" />
                          <input type="password" placeholder="Access_Code (Password)" className="w-full bg-[#1A1A1A] border border-white/5 rounded-2xl p-4 text-sm font-bold outline-none focus:border-blue-500/50 text-blue-400" />
                       </div>
                    </SettingCard>
                    <SettingCard title="Liaison_Market_Guard (API_Keys)">
                      <div className="space-y-4">
                        <div className="relative">
                          <Database size={14} className="absolute left-4 top-1/2 -translate-y-1/2 text-zinc-600" />
                          <input type="password" placeholder="Polygon.io_Key" className="w-full bg-[#1A1A1A] border border-white/5 rounded-2xl pl-12 pr-4 py-4 text-sm font-mono outline-none focus:border-blue-500/50 text-zinc-400" />
                        </div>
                        <div className="relative">
                          <Globe size={14} className="absolute left-4 top-1/2 -translate-y-1/2 text-zinc-600" />
                          <input type="password" placeholder="NewsAPI_Token" className="w-full bg-[#1A1A1A] border border-white/5 rounded-2xl pl-12 pr-4 py-4 text-sm font-mono outline-none focus:border-blue-500/50 text-zinc-400" />
                        </div>
                      </div>
                    </SettingCard>
                  </div>
                )}

                {/* PROTOCOLE RISQUE */}
                {activeTab === "Protocole Risque" && (
                  <div className="space-y-6">
                    <SettingCard title="Paramètres_Garde_Fou">
                      <div className="grid grid-cols-2 gap-6">
                        <div className="space-y-2">
                           <label className="text-[9px] font-black text-zinc-600 uppercase">Risque_Max_par_Trade (%)</label>
                           <input type="number" step="0.1" placeholder="1.0" className="w-full bg-[#1A1A1A] border border-white/5 rounded-2xl p-4 text-sm font-mono text-red-500 outline-none" />
                        </div>
                        <div className="space-y-2">
                           <label className="text-[9px] font-black text-zinc-600 uppercase">RR_Minimum_Admis</label>
                           <input type="number" step="0.5" placeholder="2.0" className="w-full bg-[#1A1A1A] border border-white/5 rounded-2xl p-4 text-sm font-mono text-green-500 outline-none" />
                        </div>
                      </div>
                    </SettingCard>
                    <SettingCard title="Allocation_Initiale">
                       <input type="number" placeholder="Solde_de_Départ ($)" className="w-full bg-[#1A1A1A] border border-white/5 rounded-2xl p-4 text-xl font-black text-white outline-none focus:border-blue-500/50" />
                    </SettingCard>
                  </div>
                )}

                {/* AI PERSONA */}
                {activeTab === "AI Persona" && (
                  <div className="space-y-6">
                    <SettingCard title="Tempérament_du_Mentor">
                      <div className="flex gap-2 p-2 bg-[#1A1A1A] rounded-[2rem] border border-white/5">
                        {["Doux", "Neutre", "Sévère", "Institutionnel"].map((t) => (
                          <button key={t} className={`flex-1 py-4 rounded-[1.5rem] text-[9px] font-black uppercase tracking-widest transition-all ${t === "Neutre" ? "bg-[#081E58] text-white" : "text-zinc-500 hover:text-white hover:bg-white/5"}`}>
                            {t}
                          </button>
                        ))}
                      </div>
                    </SettingCard>
                    <SettingCard title="Profil_Trader_Cible">
                        <div className="grid grid-cols-3 gap-3">
                           {["Scalping", "Day_Trading", "Swing"].map((val) => (
                             <button key={val} className="py-4 bg-[#1A1A1A] border border-white/5 rounded-2xl text-[9px] font-black uppercase tracking-widest hover:border-blue-500/30 transition-all">
                               {val}
                             </button>
                           ))}
                        </div>
                    </SettingCard>
                  </div>
                )}

                {/* RESPONSABILITÉ */}
                {activeTab === "Responsabilité" && (
                  <div className="bg-[#0A0A0A] border border-white/10 rounded-[2.5rem] p-10 shadow-2xl">
                    <div className="h-[500px] overflow-y-auto custom-scrollbar pr-6 text-[13px] font-sans leading-relaxed text-zinc-400 space-y-8">
                      
                      <div className="border-b border-white/10 pb-6">
                        <h2 className="text-white font-black uppercase text-base tracking-widest italic flex items-center gap-3">
                          <ShieldCheck className="text-blue-500" size={20} />
                          ⚖️ CLAUSES DE RESPONSABILITÉ & CONFIDENTIALITÉ
                        </h2>
                      </div>

                      <section className="space-y-4">
                        <h3 className="text-white font-bold text-[14px] uppercase tracking-wider">1. Nature du Service (Définition et Limites)</h3>
                        <p>
                          L’utilisateur reconnaît expressément que &quot;Trade MIND&quot; est un outil pédagogique d’aide à la réflexion et à la structuration d’un raisonnement en trading, basé sur l’utilisation d’algorithmes d’intelligence artificielle.
                        </p>
                        <p className="italic text-zinc-500">À ce titre :</p>
                        <ul className="space-y-4 pl-4 border-l border-blue-500/30">
                          <li>
                            <strong className="text-zinc-200 block text-[11px] uppercase tracking-tighter">PAS UN CONSEILLER FINANCIER :</strong>
                            &quot;Trade MIND&quot; ne fournit aucun conseil en investissement au sens des autorités de régulation financière. Aucune recommandation personnalisée d’achat ou de vente n’est délivrée.
                          </li>
                          <li>
                            <strong className="text-zinc-200 block text-[11px] uppercase tracking-tighter">PAS UN FOURNISSEUR DE SIGNAUX :</strong>
                            L’application ne génère aucun signal de trading. Elle se limite à analyser et auditer la cohérence d’un plan soumis par l’utilisateur.
                          </li>
                          <li>
                            <strong className="text-zinc-200 block text-[11px] uppercase tracking-tighter">PAS UN SYSTÈME D’EXÉCUTION :</strong>
                            &quot;Trade MIND&quot; n’exécute aucune transaction, n’interagit pas avec des marchés financiers, et ne garantit en aucun cas une performance ou une rentabilité.
                          </li>
                        </ul>
                      </section>

                      <section className="space-y-4">
                        <h3 className="text-white font-bold text-[14px] uppercase tracking-wider">2. Limitation de Responsabilité</h3>
                        <p>L’utilisateur reconnaît être l’unique décisionnaire de ses actions de trading et assume pleinement les risques associés.</p>
                        
                        <div className="space-y-4 bg-white/5 p-6 rounded-2xl border border-white/5">
                          <div>
                            <span className="text-zinc-200 font-bold block mb-1 underline decoration-blue-500/50 underline-offset-4">Absence de garantie :</span>
                            Les données utilisées (via APIs tierces telles que Polygon, NewsAPI, etc.) peuvent contenir des erreurs, retards ou approximations. De même, les analyses générées par l’IA sont basées sur des modèles probabilistes et ne constituent en aucun cas une vérité absolue.
                          </div>
                          <div>
                            <span className="text-zinc-200 font-bold block mb-1 underline decoration-red-500/50 underline-offset-4">Risque de perte en capital :</span>
                            Le trading comporte un risque élevé de perte financière. En aucun cas le développeur ou le projet &quot;Trade MIND&quot; ne pourront être tenus responsables de pertes, directes ou indirectes, résultant de l’utilisation de l’outil.
                          </div>
                          <div>
                            <span className="text-zinc-200 font-bold block mb-1 underline decoration-zinc-500/50 underline-offset-4">Utilisation inappropriée :</span>
                            Toute utilisation détournée de l’application (automatisation non prévue, reverse-engineering, ou interprétation des analyses comme des certitudes) annule immédiatement toute responsabilité du concepteur.
                          </div>
                        </div>
                      </section>

                      <section className="space-y-4">
                        <h3 className="text-white font-bold text-[14px] uppercase tracking-wider">3. Confidentialité & Traitement des Données</h3>
                        <div className="grid gap-4">
                           <p><span className="text-white font-medium mr-2">Traitement des analyses :</span>Les données saisies par l’utilisateur (analyses, réponses, etc.) peuvent être transmises à des services tiers (ex : API d’intelligence artificielle) uniquement dans le cadre du traitement fonctionnel de l’application. Elles ne sont pas exploitées à des fins commerciales par &quot;Trade MIND&quot;.</p>
                           <p><span className="text-white font-medium mr-2">Clés API :</span>L’utilisateur est responsable de la gestion et de la sécurité de ses propres clés API s’il en configure dans l’application.</p>
                           <p><span className="text-white font-medium mr-2">Respect de la vie privée :</span>Aucune donnée personnelle identifiable n’est vendue, cédée ou partagée avec des tiers.</p>
                        </div>
                      </section>

                      <section className="space-y-4 border-t border-white/10 pt-6">
                        <h3 className="text-white font-bold text-[14px] uppercase tracking-wider">4. Acceptation des Conditions</h3>
                        <p>En utilisant <span className="text-white font-bold">&quot;Trade MIND&quot;</span>, l’utilisateur reconnaît avoir lu, compris et accepté l’ensemble des présentes clauses.</p>
                        <p>Il accepte notamment que l’outil soit utilisé uniquement comme support pédagogique et non comme système de prise de décision autonome.</p>
                      </section>

                      <div className="pt-6">
                        <div className="p-6 bg-green-500/5 border border-green-500/10 rounded-2xl flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <CheckCircle2 size={18} className="text-green-500" />
                            <span className="text-[10px] font-black text-green-500 uppercase tracking-widest italic">Protocol_Accepted</span>
                          </div>
                          <span className="text-[9px] font-mono text-zinc-600 italic">14/05/2026_03:31_UTC</span>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* COUCHE D'ABONNEMENT AVEC INTÉGRATION FLUTTERWAVE ET NOUVEAUX CANAUX INTERNATIONAUX */}
                {activeTab === "Abonnement Pro" && (
                  <div className="space-y-6">
                    <SettingCard title="Sélecteur_de_Zone_Économique">
                      <div className="flex gap-2 p-2 bg-[#1A1A1A] rounded-[2rem] border border-white/5">
                        <button 
                          onClick={() => setPaymentRegion("AFRIQUE")}
                          className={`flex-1 py-4 rounded-[1.5rem] text-[9px] font-black uppercase tracking-widest transition-all ${paymentRegion === "AFRIQUE" ? "bg-blue-600 text-white" : "text-zinc-500 hover:text-white"}`}
                        >
                          🌍 Zone Afrique (Tarif Solidaire via Flutterwave)
                        </button>
                        <button 
                          onClick={() => setPaymentRegion("INTERNATIONAL")}
                          className={`flex-1 py-4 rounded-[1.5rem] text-[9px] font-black uppercase tracking-widest transition-all ${paymentRegion === "INTERNATIONAL" ? "bg-zinc-800 text-white" : "text-zinc-500 hover:text-white"}`}
                        >
                          🌐 Reste du Monde (Global Gateways)
                        </button>
                      </div>
                    </SettingCard>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      {/* CARTE DU PRIX */}
                      <div className="bg-[#0A0A0A] border border-[#F1C40F]/20 rounded-[2rem] p-8 flex flex-col justify-between relative overflow-hidden">
                        <div className="absolute top-0 right-0 w-24 h-24 bg-[#F1C40F]/5 rounded-full blur-2xl" />
                        <div>
                          <div className="flex items-center gap-2 text-[#F1C40F] mb-4">
                            <Gem size={16} />
                            <span className="text-[10px] font-black uppercase tracking-widest">Plan_Trade_Mind_Pro</span>
                          </div>
                          
                          {paymentRegion === "AFRIQUE" ? (
                            <div>
                              <h4 className="text-4xl font-black tracking-tight text-white">8 000 FCFA <span className="text-xs font-medium text-zinc-500">/ mois</span></h4>
                              <p className="text-[10px] font-mono text-zinc-500 mt-2">Équivalent local réduit (~12 €) — Centralisé par Flutterwave</p>
                            </div>
                          ) : (
                            <div>
                              <h4 className="text-4xl font-black tracking-tight text-white">20 € <span className="text-xs font-medium text-zinc-500">/ mois</span></h4>
                              <p className="text-[10px] font-mono text-zinc-500 mt-2">Tarif standard international Multi-passerelles</p>
                            </div>
                          )}

                          <ul className="mt-6 space-y-2 text-[11px] text-zinc-400">
                            <li className="flex items-center gap-2">🟢 Audits de l'Architecte IA illimités</li>
                            <li className="flex items-center gap-2">🟢 Activation du Guardian en temps réel</li>
                            <li className="flex items-center gap-2">🟢 Dashboard de performance Neuro-Statistique</li>
                          </ul>
                        </div>
                      </div>

                      {/* VOIES DE PAIEMENT INJECTÉES AVEC LIENS FONCTIONNELS DÉCOUPLÉS */}
                      <div className="bg-[#0A0A0A] border border-white/5 rounded-[2rem] p-8 flex flex-col justify-between">
                        <div>
                          <h4 className="text-[10px] font-black uppercase tracking-wider text-zinc-400 mb-4">Canaux_de_Facturation_Disponibles</h4>
                          
                          {paymentRegion === "AFRIQUE" ? (
                            <div className="space-y-3">
                              <div className="text-[9px] text-zinc-500 font-mono mb-2 uppercase tracking-wide">🔗 Passerelle unifiée Flutterwave active :</div>
                              
                              {/* AIRTEL MONEY */}
                              <button onClick={() => handleAfricanPayment("Airtel Money")} className="w-full bg-[#1A1A1A] hover:bg-zinc-900 border border-white/5 hover:border-red-500/30 p-4 rounded-xl flex items-center justify-between transition-all group">
                                <div className="flex items-center gap-3">
                                  <Smartphone size={16} className="text-red-500" />
                                  <span className="text-[11px] font-bold tracking-wide">Airtel Money</span>
                                </div>
                                <span className="text-[9px] font-mono text-zinc-600 group-hover:text-red-400">Payer via XAF</span>
                              </button>

                              {/* MOOV MONEY */}
                              <button onClick={() => handleAfricanPayment("Moov Money")} className="w-full bg-[#1A1A1A] hover:bg-zinc-900 border border-white/5 hover:border-blue-500/30 p-4 rounded-xl flex items-center justify-between transition-all group">
                                <div className="flex items-center gap-3">
                                  <Smartphone size={16} className="text-blue-500" />
                                  <span className="text-[11px] font-bold tracking-wide">Moov Money</span>
                                </div>
                                <span className="text-[9px] font-mono text-zinc-600 group-hover:text-blue-400">Payer via XAF</span>
                              </button>

                              {/* WAVE */}
                              <button onClick={() => handleAfricanPayment("Wave")} className="w-full bg-[#1A1A1A] hover:bg-zinc-900 border border-white/5 hover:border-cyan-500/30 p-4 rounded-xl flex items-center justify-between transition-all group">
                                <div className="flex items-center gap-3">
                                  <Smartphone size={16} className="text-cyan-400" />
                                  <span className="text-[11px] font-bold tracking-wide">Wave</span>
                                </div>
                                <span className="text-[9px] font-mono text-zinc-600 group-hover:text-cyan-400">Payer via XOF/XAF</span>
                              </button>
                            </div>
                          ) : (
                            <div className="space-y-3">
                              {/* CARTE STRIPE / CB */}
                              <button onClick={() => handleInternationalPayment("Stripe")} className="w-full bg-[#1A1A1A] hover:bg-zinc-900 border border-white/5 hover:border-blue-500/30 p-4 rounded-xl flex items-center justify-between transition-all group">
                                <div className="flex items-center gap-3">
                                  <CreditCard size={16} className="text-blue-400" />
                                  <span className="text-[11px] font-bold tracking-wide">Carte Bancaire (Stripe)</span>
                                </div>
                                <span className="text-[9px] font-mono text-zinc-600 group-hover:text-white">Visa / Mastercard</span>
                              </button>

                              {/* PAYPAL */}
                              <button onClick={() => handleInternationalPayment("PayPal")} className="w-full bg-[#1A1A1A] hover:bg-zinc-900 border border-white/5 hover:border-yellow-500/30 p-4 rounded-xl flex items-center justify-between transition-all group">
                                <div className="flex items-center gap-3">
                                  <CreditCard size={16} className="text-yellow-500" />
                                  <span className="text-[11px] font-bold tracking-wide">PayPal Checkout</span>
                                </div>
                                <span className="text-[9px] font-mono text-zinc-600 group-hover:text-yellow-400">Compte & CB Global</span>
                              </button>

                              {/* APPLE PAY */}
                              <button onClick={() => handleInternationalPayment("Apple Pay")} className="w-full bg-[#1A1A1A] hover:bg-zinc-900 border border-white/5 hover:border-white/30 p-4 rounded-xl flex items-center justify-between transition-all group">
                                <div className="flex items-center gap-3">
                                  <Smartphone size={16} className="text-white" />
                                  <span className="text-[11px] font-bold tracking-wide">Apple Pay</span>
                                </div>
                                <span className="text-[9px] font-mono text-zinc-600 group-hover:text-white">One-Click Wallet</span>
                              </button>
                            </div>
                          )}
                        </div>

                        <div className="mt-4 text-[9px] text-zinc-600 italic font-mono text-center border-t border-white/5 pt-4">
                          Sécurisé par protocole de cryptage AES-256 via Flutterwave & Passerelles Partenaires.
                        </div>
                      </div>
                    </div>
                  </div>
                )}

              </motion.div>
            </AnimatePresence>
          </div>
        </div>
      </main>
    </div>
  );
}

function SettingCard({ title, children }: { title: string, children: React.ReactNode }) {
  return (
    <div className="bg-[#0A0A0A] border border-white/5 rounded-[2rem] p-8 shadow-2xl hover:border-white/10 transition-all">
      <h3 className="text-zinc-600 text-[9px] font-black uppercase tracking-[0.3em] mb-6 flex items-center gap-2 italic">
        <div className="w-1 h-1 rounded-full bg-blue-600" /> {title}
      </h3>
      {children}
    </div>
  );
}

function Loader2({ size, className }: { size: number, className: string }) {
  return (
    <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1, ease: "linear" }}>
      <Activity size={size} className={className} />
    </motion.div>
  );
}