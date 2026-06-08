"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Lock, Mail, Eye, EyeOff, Activity, ShieldAlert } from "lucide-react";
import { AuroraBackground } from "@/components/ui/aurora-background";

// Importation de ton client officiel Supabase
import { createClient } from "@/utils/supabase/client";

export default function LoginPage() {
  const router = useRouter();
  const [isSignUp, setIsSignUp] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [rememberMe, setRememberMe] = useState(false);

  // 🌍 PRÊT POUR TON PLAN D'ACTION TRADUCTION MULTI-LANGUES
  const lang = "fr"; 
  
  const translations = {
    fr: {
      terminalTitle: "Terminal Sécurisé / Connexion",
      loginTab: "Connexion",
      signupTab: "Inscription",
      emailPlaceholder: "Identifiant Terminal (Email)",
      passwordPlaceholder: "Code d'accès (Mot de passe)",
      rememberMe: "Se souvenir de moi",
      forgotPassword: "Mot de passe oublié ?",
      btnInitializing: "INITIALISATION...",
      btnLogin: "Connexion au Terminal",
      btnSignup: "Initialiser le Compte",
      alertSignupSuccess: "Système : Compte créé. Vérifie tes e-mails pour confirmer l'accès.",
      alertContactAdmin: "Système : Contacte l'administrateur pour réinitialiser l'accès."
    }
  };

  const dict = translations[lang] || translations.fr;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMessage("");

    const supabase = createClient();

    if (isSignUp) {
      const { data, error } = await supabase.auth.signUp({ email, password });
      if (error) {
        setErrorMessage(error.message);
      } else {
        alert(dict.alertSignupSuccess);
        setIsSignUp(false);
      }
    } else {
      const { data, error } = await supabase.auth.signInWithPassword({ email, password });
      if (error) {
        setErrorMessage(error.message);
      } else {
        console.log("Terminal : Accès accordé.", data?.user);
        router.push("/"); 
      }
    }
    setLoading(false);
  };

  return (
    <AuroraBackground>
      {/* CONTAINER CENTRAL ALIGNÉ SUR LE GRAPHISME DE L'IMAGE_3 */}
      <motion.div 
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className="relative w-full max-w-[400px] mx-4 bg-[#0B0E11]/90 backdrop-blur-md border border-white/10 rounded-[2.5rem] overflow-hidden shadow-2xl z-10"
      >
        
        {/* BANDEAU SUPÉRIEUR CONTRASTÉ STYLE IMAGE_3 */}
        <div className="bg-[#F5F6F8] pt-8 pb-10 px-8 rounded-b-[2.5rem] flex flex-col items-center relative shadow-lg">
          {/* Logo asymétrique du projet */}
          <div className="mb-4 bg-[#0B0E11] text-white px-5 py-2.5 rounded-2xl font-sans font-black italic tracking-tighter text-xl border border-white/5">
            TM
          </div>
          <div className="flex items-center gap-2 text-[#0B0E11]/60 font-mono text-[9px] uppercase tracking-[0.2em] font-bold">
            <Activity size={12} className="text-[#2A3441]" />
            <span>{dict.terminalTitle}</span>
          </div>
        </div>

        {/* CONTENU DU FORMULAIRE (NOIR MAT / BLEU TERNE ACER) */}
        <div className="p-8 pt-10">
          
          {/* INTERRUPTEUR DE MODE (STYLE IMAGE_3 & PINTEREST) */}
          <div className="grid grid-cols-2 bg-[#161A1E] p-1 rounded-xl mb-8 border border-white/5">
            <button
              type="button"
              onClick={() => { setIsSignUp(false); setErrorMessage(""); }}
              className={`py-2.5 rounded-lg text-xs font-sans font-semibold tracking-wide transition-all ${!isSignUp ? "bg-[#2A3441] text-white shadow-lg border border-white/10" : "text-zinc-500 hover:text-zinc-300"}`}
            >
              {dict.loginTab}
            </button>
            <button
              type="button"
              onClick={() => { setIsSignUp(true); setErrorMessage(""); }}
              className={`py-2.5 rounded-lg text-xs font-sans font-semibold tracking-wide transition-all ${isSignUp ? "bg-[#2A3441] text-white shadow-lg border border-white/10" : "text-zinc-500 hover:text-zinc-300"}`}
            >
              {dict.signupTab}
            </button>
          </div>

          {/* AFFICHAGE DES ERREURS FLUX SÉCURISÉ */}
          {errorMessage && (
            <motion.div 
              initial={{ opacity: 0, x: -5 }}
              animate={{ opacity: 1, x: 0 }}
              className="mb-5 p-3.5 bg-red-950/30 border border-red-500/20 rounded-xl flex items-center gap-3 text-red-400 text-xs font-medium font-sans"
            >
              <ShieldAlert size={14} className="shrink-0 text-red-500" />
              <span>{errorMessage}</span>
            </motion.div>
          )}

          {/* FORMULAIRE MINIMALISTE SANS COULEUR FLASHY */}
          <form onSubmit={handleSubmit} className="space-y-4">
            
            {/* ENTRÉE EMAIL */}
            <div className="relative group">
              <Mail size={14} className="absolute left-4 top-1/2 -translate-y-1/2 text-zinc-500 group-focus-within:text-blue-400 transition-colors" />
              <input 
                type="email" 
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder={dict.emailPlaceholder}
                className="w-full bg-[#1E2329]/40 border border-white/5 rounded-xl pl-11 pr-4 py-4 text-xs font-sans text-white placeholder-zinc-600 outline-none focus:border-white/20 focus:bg-[#1E2329] transition-all tracking-wide"
              />
            </div>

            {/* ENTRÉE MOT DE PASSE */}
            <div className="relative group">
              <Lock size={14} className="absolute left-4 top-1/2 -translate-y-1/2 text-zinc-500 group-focus-within:text-blue-400 transition-colors" />
              <input 
                type={showPassword ? "text" : "password"} 
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder={dict.passwordPlaceholder}
                className="w-full bg-[#1E2329]/40 border border-white/5 rounded-xl pl-11 pr-11 py-4 text-xs font-sans text-white placeholder-zinc-600 outline-none focus:border-white/20 focus:bg-[#1E2329] transition-all tracking-wide"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-4 top-1/2 -translate-y-1/2 text-zinc-500 hover:text-white transition-colors"
              >
                {showPassword ? <EyeOff size={14} /> : <Eye size={14} />}
              </button>
            </div>

            {/* OPTIONS DE SESSION ACCÈS */}
            {!isSignUp && (
              <div className="flex items-center justify-between pt-1 pb-3">
                <label className="flex items-center gap-2.5 cursor-pointer select-none group">
                  <input 
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                    className="hidden"
                  />
                  {/* Commutateur asymétrique bascule noir/bleu acier terne */}
                  <div className={`w-8 h-4 rounded-full transition-all relative p-0.5 flex items-center ${rememberMe ? "bg-[#384A62]" : "bg-zinc-800"}`}>
                    <div className={`w-3 h-3 rounded-full bg-white transition-all shadow-sm ${rememberMe ? "translate-x-3.5" : "translate-x-0"}`} />
                  </div>
                  <span className="text-[11px] font-sans font-medium text-zinc-400 group-hover:text-zinc-200 transition-colors">{dict.rememberMe}</span>
                </label>
                
                <button 
                  type="button"
                  onClick={() => alert(dict.alertContactAdmin)}
                  className="text-[11px] font-medium text-zinc-500 hover:text-zinc-300 transition-colors font-mono"
                >
                  {dict.forgotPassword}
                </button>
              </div>
            )}

            {/* BOUTON D'ACTION PRINCIPAL HAUTE LISIBILITÉ */}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-[#E4E6EB] hover:bg-white text-[#0B0E11] disabled:bg-zinc-800 disabled:text-zinc-600 font-sans font-bold text-xs uppercase tracking-wider py-4 rounded-xl transition-all shadow-md flex items-center justify-center gap-2 mt-2"
            >
              {loading ? dict.btnInitializing : (isSignUp ? dict.btnSignup : dict.btnLogin)}
            </button>
            
          </form>
        </div>
      </motion.div>
    </AuroraBackground>
  );
}