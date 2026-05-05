import json
import os

_DIR = os.path.dirname(os.path.abspath(__file__))
_CONFIG_PATH = os.path.join(_DIR, "config.json")
_LEXEMAS_PATH = os.path.join(_DIR, "lexemas_extra.json")

_DEFAULT_CONFIG = {"font_size": 13}


def cargar_config():
    if os.path.exists(_CONFIG_PATH):
        try:
            with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return dict(_DEFAULT_CONFIG)


def guardar_config(datos):
    with open(_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)


def cargar_lexemas_extra():
    if os.path.exists(_LEXEMAS_PATH):
        try:
            with open(_LEXEMAS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []


def guardar_lexemas_extra(lista):
    with open(_LEXEMAS_PATH, "w", encoding="utf-8") as f:
        json.dump(lista, f, indent=2, ensure_ascii=False)
