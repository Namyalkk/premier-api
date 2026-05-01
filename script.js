// script.js - Fonctions communes

// Configuration - À MODIFIER APRÈS DÉPLOIEMENT
const API_URL = "https://premier-api-production-b355.up.railway.app";  // Remplacez par votre URL Render plus tard

// Liste des capteurs
const capteurs = [
    { id: "temperature", nom: "🌡️ Température", unite: "°C", couleur: "#ef476f", min: 20, max: 30 },
    { id: "pression", nom: "⏲️ Pression", unite: "hPa", couleur: "#ffd166", min: 980, max: 1020 },
    { id: "vibration", nom: "📳 Vibration", unite: "mm/s", couleur: "#06d6a0", min: 0, max: 5 },
    { id: "debit_gaz", nom: "🔥 Débit Gaz", unite: "m³/h", couleur: "#118ab2", min: 0, max: 100 }
];

// Stockage des alertes (localStorage)
let alertes = JSON.parse(localStorage.getItem('alertes') || '[]');

// Récupérer la dernière valeur d'un capteur
async function getDerniereValeur(capteurId) {
    try {
        const response = await fetch(`${API_URL}/mesures/${capteurId}?limit=1`);
        const data = await response.json();
        if (data.mesures && data.mesures.length > 0) {
            return data.mesures[0].valeur;
        }
        return null;
    } catch (error) {
        console.error(`Erreur pour ${capteurId}:`, error);
        return null;
    }
}

// Récupérer l'historique d'un capteur
async function getHistorique(capteurId, limit = 50) {
    try {
        const response = await fetch(`${API_URL}/mesures/${capteurId}?limit=${limit}`);
        const data = await response.json();
        if (data.mesures) {
            return data.mesures.reverse(); // Du plus ancien au plus récent pour les graphiques
        }
        return [];
    } catch (error) {
        console.error(`Erreur pour ${capteurId}:`, error);
        return [];
    }
}

// Vérifier les seuils d'alerte
function verifierAlertes(capteurId, valeur) {
    const alertesActives = alertes.filter(a => a.capteur === capteurId && a.active);
    const declenchees = [];
    
    for (const alerte of alertesActives) {
        if (alerte.type === 'max' && valeur > alerte.seuil) {
            declenchees.push(alerte);
        } else if (alerte.type === 'min' && valeur < alerte.seuil) {
            declenchees.push(alerte);
        }
    }
    
    return declenchees;
}

// Formater la date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('fr-FR');
}

// Sauvegarder les alertes
function sauvegarderAlertes() {
    localStorage.setItem('alertes', JSON.stringify(alertes));
}