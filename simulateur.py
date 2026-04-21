import requests
import random
import time

API_URL = "http://127.0.0.1:8000/mesures"

print("🚀 Envoi de données vers l'API...")
print("Appuyez sur Ctrl+C pour arrêter\n")

while True:
    # Générer des valeurs aléatoires
    temperature = round(random.uniform(20, 30), 1)
    pression = round(random.uniform(980, 1020), 1)
    
    # Envoyer la température
    response = requests.post(API_URL, json={
        "capteur": "temperature",
        "valeur": temperature,
        "unite": "°C"
    })
    print(f"✓ Température : {temperature} °C → {response.json()}")
    
    # Envoyer la pression
    response = requests.post(API_URL, json={
        "capteur": "pression",
        "valeur": pression,
        "unite": "hPa"
    })
    print(f"✓ Pression : {pression} hPa → {response.json()}")
    
    time.sleep(3)  # Attendre 3 secondes