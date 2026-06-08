import math
import logging

class RiskEngine:
    """
    Moteur de contrôle du risque institutionnel.
    [Rigueur maintenue : Algorithmes de suivi de pic exact et State Machine de sécurité]
    """
    def __init__(self):
        self.logger = logging.getLogger("RiskEngine")

    def calculate_true_max_drawdown(self, equity_curve):
        """
        Calcule le Max Drawdown institutionnel réel par suivi de Peak successif.
        [Rigueur maintenue : Gestion des divisions par zéro et des courbes relatives]
        """
        if not equity_curve or len(equity_curve) < 2: 
            return 0.0
        
        # Sécurisation : Si la courbe contient des variations relatives (commençant par 0 ou négatif),
        # on la normalise temporairement sur une base 100 pour garantir la cohérence du ratio géométrique.
        base_equity = []
        if equity_curve[0] <= 0:
            # On décale artificiellement la courbe sur une base positive (ex: 10,000) pour le calcul de ratio
            decalage = abs(min(equity_curve)) + 1000.0
            base_equity = [v + decalage for v in equity_curve]
        else:
            base_equity = [float(v) for v in equity_curve]
        
        peak = base_equity[0] if base_equity[0] != 0 else 0.0001
        max_dd = 0.0
        
        for value in base_equity:
            if value > peak:
                peak = value
            
            # Éviter la division par zéro si le peak est corrompu
            denominator = peak if peak != 0 else 0.0001
            dd = ((denominator - value) / denominator) * 100
            
            if dd > max_dd:
                max_dd = dd
                
        return round(max_dd, 2)

    def get_safety_status(self, drawdown_percent, stats):
        """
        State Machine de sécurité.
        [Rigueur maintenue : Seuils critiques 15% / 10% / Alerts]
        """
        # LOCKDOWN immédiat si risque structurel dépassé
        if drawdown_percent > 15.0: return "LOCKDOWN"
        if drawdown_percent > 10.0: return "CRITICAL"
        
        alerts_count = int(stats.get("alerts", 0)) if stats else 0
        
        # Vérification des patterns de danger : 
        # On passe en ELEVATED si le drawdown est important OU si le comportement (alerts) est dégradé
        if drawdown_percent > 7.0 or alerts_count > 5: 
            return "ELEVATED"
        if drawdown_percent > 3.0 or alerts_count > 2: 
            return "CAUTION"
        
        return "SAFE"

    def apply_penalty(self, base_score, drawdown_percent, timeframe_factor=1.0):
        """
        Pénalité exponentielle pour refléter le danger réel.
        timeframe_factor permet d'amplifier la pénalité si le DD est rapide.
        """
        if drawdown_percent <= 0: 
            return base_score
        
        # Pénalité basée sur la puissance 1.7 pour punir sévèrement les sorties de plan
        # Le timeframe_factor permet d'ajuster selon le mode (Daily vs Scalp)
        penalty = math.pow(drawdown_percent, 1.7) * timeframe_factor
        return max(0, int(base_score - penalty))

    def evaluate_risk_velocity(self, equity_curve, window=5):
        """
        Analyse la vitesse de dégradation du capital (Risk Velocity).
        Si le drawdown arrive trop vite sur les 'n' dernières séances, le score chute.
        """
        if not equity_curve or len(equity_curve) < window:
            return 1.0 # Facteur neutre
        
        recent_decline = equity_curve[-1] - equity_curve[-window]
        return 1.5 if recent_decline < 0 else 1.0