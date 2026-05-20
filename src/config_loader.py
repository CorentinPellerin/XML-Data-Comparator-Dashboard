"""
config_loader.py
Charge et valide le fichier de configuration YAML.
"""
import yaml
import os


def load_config(path: str = "config.yaml") -> dict:
    """Charge le fichier YAML et retourne un dict."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Fichier de config introuvable : {path}")
    with open(path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    _validate(config)
    return config


def _validate(config: dict):
    """Vérifie que les clés obligatoires sont présentes."""
    required = ["sources", "cle_jointure", "comparaisons"]
    for key in required:
        if key not in config:
            raise ValueError(f"Clé manquante dans config.yaml : '{key}'")
