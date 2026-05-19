"""
parser.py
Lit un fichier XML et retourne une liste de dicts.
Chaque dict représente un enregistrement (une pièce, une ligne, etc.)
"""
import xml.etree.ElementTree as ET
from typing import List, Dict


def parse_xml(filepath: str) -> List[Dict]:
    """
    Parse un fichier XML et retourne une liste de dictionnaires.
    Chaque enfant direct de la racine devient un dict.

    Exemple :
        [{"id": "P001", "reference": "CFM56...", "vie_limite_heures": "20000"}, ...]
    """
    tree = ET.parse(filepath)
    root = tree.getroot()

    records = []
    for child in root:
        record = dict(child.attrib)          # attributs XML (ex: id="P001")
        for element in child:
            record[element.tag] = element.text.strip() if element.text else ""
        records.append(record)

    return records


def records_to_dict(records: List[Dict], key: str) -> Dict[str, Dict]:
    """
    Transforme une liste de dicts en dict indexé par une clé.
    Facilite la jointure entre deux bases.

    Exemple :
        {"CFM56-7B-FAN-001": {"reference": "...", ...}, ...}
    """
    if not records:
        return {}
    result = {}
    for r in records:
        if key not in r:
            raise KeyError(f"Clé '{key}' absente dans l'enregistrement : {r}")
        result[r[key]] = r
    return result
