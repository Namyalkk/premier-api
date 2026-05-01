import requests
import random
import time
from datetime import datetime

# ==================== CONFIGURATION ====================

# À MODIFIER selon votre environnement
API_URL = "http://127.0.0.1:8000/mesures"  # Local
# API_URL = "https://votre-api.onrender.com/mesures"  # Cloud (après déploiement)

# Configuration des capteurs simulés
CAPTEURS = [
    {"nom": "temperature", "min": 18, "max": 35, "unite": "°C", "variation": 0.5},
    {"nom": "pression", "min": 980, "max": 1030, "unite": "hPa", "variation": 2},
    {"nom": "vibration", "min": 0, "max": 5, "unite": "mm/s", "variation": 0.2},
    {"nom": "debit_gaz", "min": 10, "max": 80, "unite": "m³/h", "variation": 3}
]

# Valeurs courantes (pour une évolution réaliste)
valeurs_courantes = {}

def init_valeurs():
    """Initialise les valeurs courantes"""
    for capteur in CAPTEURS:
        valeurs_courantes[capteur["nom"]] = (capteur["min"] + capteur["max"]) / 2

def generer_valeur(capteur):
    """Génère une nouvelle valeur avec variation progressive"""
    ancienne = valeurs_courantes[capteur["nom"]]
    variation = random.uniform(-capteur["variation"], capteur["variation"])
    nouvelle = ancienne + variation
    
    # Rester dans les limites
    nouvelle = max(capteur["min"], min(capteur["max"], nouvelle))
    valeurs_courantes[capteur["nom"]] = nouvelle
    
    return round(nouvelle, 1)

def envoyer_mesure(capteur, valeur):
    """Envoie une mesure à l'API"""
    try:
        response = requests.post(
            API_URL,
            json={
                "capteur": capteur["nom"],
                "valeur": valeur,
                "unite": capteur["unite"]
            },
            timeout=5
        )
        
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"Erreur HTTP {response.status_code}"
    
    except requests.exceptions.ConnectionError:
        return False, "Connexion impossible - L'API est-elle lancée ?"
    except Exception as e:
        return False, str(e)

def afficher_banniere():
    """Affiche la bannière de démarrage"""
    print("=" * 60)
    print("🏭 SIMULATEUR INDUSTRIEL - PFE")
    print("=" * 60)
    print(f"📡 API cible : {API_URL}")
    print(f"🎛️ Capteurs actifs : {len(CAPTEURS)}")
    print(f"⏱️  Fréquence : toutes les 3 secondes")
    print("=" * 60)
    print("Appuyez sur Ctrl+C pour arrêter\n")

def afficher_recap(dernieres_mesures):
    """Affiche un récapitulatif des dernières mesures"""
    print("\n" + "=" * 60)
    print(f"📊 RÉCAPITULATIF - {datetime.now().strftime('%H:%M:%S')}")
    print("-" * 40)
    for capteur in CAPTEURS:
        valeur = dernieres_mesures.get(capteur["nom"], "---")
        barre = "█" * min(int(float(valeur) / capteur["max"] * 30), 30) if valeur != "---" else ""
        print(f"{capteur['nom'][:12]:12} : {valeur:>6} {capteur['unite']}  {barre}")
    print("=" * 60)

# ==================== MAIN ====================

if __name__ == "__main__":
    init_valeurs()
    afficher_banniere()
    
    dernieres_mesures = {}
    compteur = 0
    
    try:
        while True:
            compteur += 1
            
            for capteur in CAPTEURS:
                valeur = generer_valeur(capteur)
                succes, resultat = envoyer_mesure(capteur, valeur)
                
                if succes:
                    dernieres_mesures[capteur["nom"]] = valeur
                    print(f"✅ [{compteur}] {capteur['nom']}: {valeur} {capteur['unite']}")
                else:
                    print(f"❌ [{compteur}] {capteur['nom']}: ERREUR - {resultat}")
                
                time.sleep(0.5)  # Petit délai entre capteurs
            
            # Afficher récapitulatif toutes les 3 itérations (environ 6 secondes)
            if compteur % 3 == 0:
                afficher_recap(dernieres_mesures)
            
            print()  # Ligne vide
            time.sleep(1.5)  # Attendre avant le prochain cycle
    
    except KeyboardInterrupt:
        print("\n\n🛑 Simulation arrêtée par l'utilisateur")
        print(f"📊 Total cycles effectués : {compteur}")
        print("👋 Au revoir !")