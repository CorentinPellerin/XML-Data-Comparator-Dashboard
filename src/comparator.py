"""
comparator.py
Croise deux bases de données et produit un rapport de comparaison.
"""
from typing import List, Dict, Any


def compare(
    data_A: Dict[str, Dict],
    data_B: Dict[str, Dict],
    comparaisons: List[Dict],
    seuils: Dict = None,
) -> List[Dict]:
    """
    Croise data_A et data_B sur leur clé commune.
    Retourne une liste de résultats avec statut par champ comparé.

    Paramètres
    ----------
    data_A       : dict indexé par la clé de jointure (référentiel théorique)
    data_B       : dict indexé par la clé de jointure (données terrain)
    comparaisons : liste de règles issues de config.yaml
    seuils       : dict des libellés d'alerte

    Retour
    ------
    Liste de dicts, un par clé commune :
        {
            "cle":       "CFM56-7B-FAN-001",
            "present_A": True,
            "present_B": True,
            "resultats": [
                {
                    "label":      "Heures de vie",
                    "valeur_A":   20000,
                    "valeur_B":   19800,
                    "statut":     "CONFORME",   # CONFORME | PROCHE LIMITE | DÉPASSEMENT LIMITE
                    "pourcentage": 99.0,
                },
                ...
            ],
            "statut_global": "CONFORME",
        }
    """
    if seuils is None:
        seuils = {
            "critique":      "DÉPASSEMENT LIMITE",
            "avertissement": "PROCHE LIMITE",
            "ok":            "CONFORME",
        }

    all_keys = set(data_A.keys()) | set(data_B.keys())
    rapport = []

    for key in sorted(all_keys):
        rec_A = data_A.get(key)
        rec_B = data_B.get(key)

        entry = {
            "cle":       key,
            "present_A": rec_A is not None,
            "present_B": rec_B is not None,
            "resultats": [],
            "statut_global": seuils["ok"],
        }

        # Clé absente d'un côté → anomalie structurelle
        if not rec_A or not rec_B:
            entry["statut_global"] = seuils["critique"]
            rapport.append(entry)
            continue

        statut_global = seuils["ok"]

        for regle in comparaisons:
            champ_A = regle["champ_A"]
            champ_B = regle["champ_B"]
            label   = regle.get("label", f"{champ_A} vs {champ_B}")
            alerte  = regle.get("alerte_si", "B > A")
            seuil_avert = float(regle.get("seuil_avertissement", 0.90))

            try:
                val_A = float(rec_A.get(champ_A, 0))
                val_B = float(rec_B.get(champ_B, 0))
            except (ValueError, TypeError):
                entry["resultats"].append({
                    "label":      label,
                    "valeur_A":   rec_A.get(champ_A),
                    "valeur_B":   rec_B.get(champ_B),
                    "statut":     "ERREUR DONNÉES",
                    "pourcentage": None,
                })
                continue

            pourcentage = (val_B / val_A * 100) if val_A else 0

            # Évaluation de la règle (extensible : ajouter d'autres opérateurs ici)
            if alerte == "B > A" and val_B > val_A:
                statut = seuils["critique"]
            elif alerte == "B > A" and val_B > val_A * seuil_avert:
                statut = seuils["avertissement"]
            else:
                statut = seuils["ok"]

            if statut == seuils["critique"]:
                statut_global = seuils["critique"]
            elif statut == seuils["avertissement"] and statut_global != seuils["critique"]:
                statut_global = seuils["avertissement"]

            entry["resultats"].append({
                "label":       label,
                "valeur_A":    val_A,
                "valeur_B":    val_B,
                "statut":      statut,
                "pourcentage": round(pourcentage, 1),
            })

        entry["statut_global"] = statut_global
        rapport.append(entry)

    return rapport
