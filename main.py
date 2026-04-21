from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

app = FastAPI(title="API Industrielle - PFE")

# CORS
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
client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)
query_api = client.query_api()

class Mesure(BaseModel):
    capteur: str
    valeur: float
    unite: Optional[str] = ""

@app.get("/")
def accueil():
    return {"message": "API Industrielle - PFE"}

@app.post("/mesures")
async def recevoir_mesure(mesure: Mesure):
    """Reçoit les données et les stocke dans InfluxDB"""
    try:
        point = {
            "measurement": "mesure",
            "tags": {"capteur": mesure.capteur, "unite": mesure.unite},
            "fields": {"valeur": mesure.valeur},
            "time": datetime.utcnow().isoformat()
        }
        
        write_api.write(bucket=INFLUXDB_BUCKET, record=point)
        return {"status": "ok", "message": f"{mesure.capteur} = {mesure.valeur} {mesure.unite}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@app.get("/mesures/{capteur}")
async def lire_mesures(capteur: str, limit: int = 50):
    """Récupère les dernières mesures d'un capteur"""
    try:
        query = f'''
        from(bucket: "{INFLUXDB_BUCKET}")
          |> range(start: -1h)
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)