"""
alert_engine.py
Filtre le rapport et génère les exports (CSV, JSON).
"""
import csv
import json
import os
from datetime import datetime
from typing import List, Dict


def get_alerts(rapport: List[Dict], niveau: str = None) -> List[Dict]:
    """
    Retourne uniquement les entrées qui ont une anomalie.
    Si niveau est fourni ("DÉPASSEMENT LIMITE"), filtre sur ce niveau exact.
    """
    problemes = [r for r in rapport if r["statut_global"] != "CONFORME"]
    if niveau:
        problemes = [r for r in problemes if r["statut_global"] == niveau]
    return problemes


def export_csv(rapport: List[Dict], dossier: str = "exports/") -> str:
    """Exporte le rapport complet en CSV et retourne le chemin du fichier."""
    os.makedirs(dossier, exist_ok=True)
    horodatage = datetime.now().strftime("%Y%m%d_%H%M%S")
    chemin = os.path.join(dossier, f"rapport_{horodatage}.csv")

    lignes = []
    for entry in rapport:
        for res in entry.get("resultats", []):
            lignes.append({
                "reference":      entry["cle"],
                "present_A":      entry["present_A"],
                "present_B":      entry["present_B"],
                "champ":          res["label"],
                "valeur_theorique": res["valeur_A"],
                "valeur_reelle":  res["valeur_B"],
                "pourcentage":    res["pourcentage"],
                "statut":         res["statut"],
                "statut_global":  entry["statut_global"],
            })
        # Entrées présentes dans une seule base
        if not entry.get("resultats"):
            lignes.append({
                "reference":      entry["cle"],
                "present_A":      entry["present_A"],
                "present_B":      entry["present_B"],
                "statut_global":  entry["statut_global"],
            })

    if not lignes:
        return chemin

    with open(chemin, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=lignes[0].keys())
        writer.writeheader()
        writer.writerows(lignes)

    return chemin


def export_json(rapport: List[Dict], dossier: str = "exports/") -> str:
    """Exporte le rapport complet en JSON et retourne le chemin du fichier."""
    os.makedirs(dossier, exist_ok=True)
    horodatage = datetime.now().strftime("%Y%m%d_%H%M%S")
    chemin = os.path.join(dossier, f"rapport_{horodatage}.json")
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(rapport, f, ensure_ascii=False, indent=2)
    return chemin
