from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
import os

# ==================== CONFIGURATION ====================

app = FastAPI(title="API Industrielle - PFE", version="1.0")

# CORS (indispensable pour le dashboard)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration InfluxDB - À MODIFIER AVEC VOS VALEURS
INFLUXDB_URL = "https://eu-central-1-1.aws.cloud2.influxdata.com"
INFLUXDB_TOKEN = "rRPDt_dCUB_KxObZaP_1RU7mMO5rX6brZXnwlVN7knFlHV48JDtSlQXnkTfY9AW0fP-ue_YQe792eWsl7p8T1A=="
INFLUXDB_ORG = "Development"
INFLUXDB_BUCKET = "mesures"

# Client InfluxDB
try:
    client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
    write_api = client.write_api(write_options=SYNCHRONOUS)
    query_api = client.query_api()
    print("✅ Connexion à InfluxDB établie")
except Exception as e:
    print(f"⚠️ Erreur de connexion à InfluxDB: {e}")

# ==================== MODÈLES ====================

class Mesure(BaseModel):
    capteur: str
    valeur: float
    unite: Optional[str] = ""

# ==================== ENDPOINTS ====================

@app.get("/")
def accueil():
    return {
        "message": "API Industrielle - PFE",
        "version": "1.0",
        "endpoints": {
            "POST /mesures": "Envoyer une mesure",
            "GET /mesures/{capteur}": "Lire les mesures d'un capteur"
        }
    }

@app.post("/mesures")
async def recevoir_mesure(mesure: Mesure):
    """Reçoit une mesure et la stocke dans InfluxDB"""
    try:
        point = {
            "measurement": "mesure",
            "tags": {
                "capteur": mesure.capteur,
                "unite": mesure.unite
            },
            "fields": {
                "valeur": mesure.valeur
            },
            "time": datetime.utcnow().isoformat()
        }
        
        write_api.write(bucket=INFLUXDB_BUCKET, record=point)
        
        return {
            "status": "ok",
            "message": f"{mesure.capteur} = {mesure.valeur} {mesure.unite}",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur InfluxDB: {str(e)}")

@app.get("/mesures/{capteur}")
async def lire_mesures(capteur: str, limit: int = 50):
    """Récupère les dernières mesures d'un capteur"""
    try:
        query = f'''
        from(bucket: "{INFLUXDB_BUCKET}")
          |> range(start: -24h)
          |> filter(fn: (r) => r._measurement == "mesure")
          |> filter(fn: (r) => r.capteur == "{capteur}")
          |> sort(columns: ["_time"], desc: true)
          |> limit(n: {limit})
        '''
        
        tables = query_api.query(query)
        
        resultats = []
        for table in tables:
            for record in table.records:
                resultats.append({
                    "time": record.get_time().isoformat(),
                    "valeur": record.get_value()
                })
        
        return {"capteur": capteur, "mesures": resultats}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur InfluxDB: {str(e)}")

# ==================== DÉMARRAGE ====================

if __name__ == "__main__":
    import uvicorn
    print("🚀 Démarrage de l'API Industrielle...")
    print("📖 Documentation disponible sur http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="127.0.0.1", port=8000)