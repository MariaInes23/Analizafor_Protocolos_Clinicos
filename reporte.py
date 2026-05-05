"""
Generador de Reporte Clínico — Lenguaje LPC
Recorre el árbol sintáctico y extrae los datos de
INGRESAR, DIAGNOSTICO, TRATAMIENTO para construir
un reporte formateado con dosis calculadas automáticamente
según peso y edad del paciente.
"""

from datetime import datetime


# ── Catálogo de medicamentos ──────────────────────────────────────────────────
# Cada entrada define:
#   dosis_base   → mg por kg de peso corporal
#   dosis_min    → dosis mínima absoluta (mg)
#   dosis_max    → dosis máxima absoluta (mg)
#   unidad       → unidad de medida
#   frecuencia   → descripción de frecuencia
#   dias         → duración estándar del tratamiento
#   presentacion → forma farmacéutica
#   via          → vía de administración
#   nota         → nota clínica adicional
#
# Ajuste por edad:
#   Pediátrico (<12 años)  → factor 1.0  (mg/kg directo)
#   Adulto (12-64 años)    → factor 1.0
#   Adulto mayor (≥65)     → factor 0.75 (metabolismo reducido, -25%)

def _ajuste_edad(edad: int) -> float:
    return 0.75 if edad >= 65 else 1.0

CATALOGO = {
    # ── Antihipertensivos ────────────────────────────────────────────────
    "losartan": {
        "nombre_formal": "Losartán",
        "dosis_base":    0.7,
        "dosis_min":     25.0,
        "dosis_max":     100.0,
        "unidad":        "mg",
        "frecuencia":    "cada 24 horas (1 vez al día)",
        "dias":          30,
        "presentacion":  "Tableta",
        "via":           "Oral",
        "nota":          "Tomar a la misma hora cada día. Monitorear presión arterial semanalmente.",
    },
    "enalapril": {
        "nombre_formal": "Enalapril",
        "dosis_base":    0.1,
        "dosis_min":     5.0,
        "dosis_max":     40.0,
        "unidad":        "mg",
        "frecuencia":    "cada 12 horas (2 veces al día)",
        "dias":          30,
        "presentacion":  "Tableta",
        "via":           "Oral",
        "nota":          "Evitar en embarazo. Vigilar niveles de potasio.",
    },
    # ── Analgésicos / Antiinflamatorios ──────────────────────────────────
    "ibuprofeno": {
        "nombre_formal": "Ibuprofeno",
        "dosis_base":    10.0,
        "dosis_min":     200.0,
        "dosis_max":     800.0,
        "unidad":        "mg",
        "frecuencia":    "cada 8 horas (3 veces al día)",
        "dias":          7,
        "presentacion":  "Tableta / Suspensión",
        "via":           "Oral",
        "nota":          "Tomar con alimentos para evitar irritación gástrica.",
    },
    "paracetamol": {
        "nombre_formal": "Paracetamol (Acetaminofén)",
        "dosis_base":    15.0,
        "dosis_min":     500.0,
        "dosis_max":     1000.0,
        "unidad":        "mg",
        "frecuencia":    "cada 6 horas (4 veces al día)",
        "dias":          5,
        "presentacion":  "Tableta / Jarabe",
        "via":           "Oral",
        "nota":          "No exceder 4 000 mg/día en adultos. Reducir en insuficiencia hepática.",
    },
    # ── Antibióticos ─────────────────────────────────────────────────────
    "amoxicilina": {
        "nombre_formal": "Amoxicilina",
        "dosis_base":    25.0,
        "dosis_min":     250.0,
        "dosis_max":     500.0,
        "unidad":        "mg",
        "frecuencia":    "cada 8 horas (3 veces al día)",
        "dias":          7,
        "presentacion":  "Cápsula / Suspensión",
        "via":           "Oral",
        "nota":          "Completar el ciclo completo aunque mejoren los síntomas.",
    },
    "azitromicina": {
        "nombre_formal": "Azitromicina",
        "dosis_base":    10.0,
        "dosis_min":     250.0,
        "dosis_max":     500.0,
        "unidad":        "mg",
        "frecuencia":    "cada 24 horas (1 vez al día)",
        "dias":          5,
        "presentacion":  "Tableta / Suspensión",
        "via":           "Oral",
        "nota":          "Tomar 1 hora antes o 2 horas después de las comidas.",
    },
    # ── Antidiabéticos ───────────────────────────────────────────────────
    "metformina": {
        "nombre_formal": "Metformina",
        "dosis_base":    8.5,
        "dosis_min":     500.0,
        "dosis_max":     1000.0,
        "unidad":        "mg",
        "frecuencia":    "cada 12 horas (2 veces al día)",
        "dias":          30,
        "presentacion":  "Tableta",
        "via":           "Oral",
        "nota":          "Tomar con las comidas. Monitorear glucosa en ayunas cada semana.",
    },
    # ── Antihistamínicos ─────────────────────────────────────────────────
    "loratadina": {
        "nombre_formal": "Loratadina",
        "dosis_base":    0.2,
        "dosis_min":     5.0,
        "dosis_max":     10.0,
        "unidad":        "mg",
        "frecuencia":    "cada 24 horas (1 vez al día)",
        "dias":          14,
        "presentacion":  "Tableta / Jarabe",
        "via":           "Oral",
        "nota":          "No produce somnolencia a dosis terapéuticas normales.",
    },
}


def _calcular_dosis(medicamento_key: str, peso_kg: float, edad: int) -> dict | None:
    """
    Dosis personalizada con regla de tres:
        dosis_calculada = dosis_base (mg/kg) × peso_kg × factor_edad
    Luego se clampea entre dosis_min y dosis_max
    y se redondea al múltiplo de 5 más cercano.
    """
    info = CATALOGO.get(medicamento_key)
    if info is None:
        return None

    factor    = _ajuste_edad(edad)
    calculada = info["dosis_base"] * peso_kg * factor
    calculada = max(info["dosis_min"], min(info["dosis_max"], calculada))

    # Redondear al múltiplo de 5 más cercano dentro del rango
    redondeada = round(calculada / 5) * 5
    redondeada = max(info["dosis_min"], min(info["dosis_max"], redondeada))

    cant = int(redondeada) if redondeada == int(redondeada) else round(redondeada, 1)

    return {
        "nombre_formal": info["nombre_formal"],
        "cantidad":      cant,
        "unidad":        info["unidad"],
        "frecuencia":    info["frecuencia"],
        "dias":          info["dias"],
        "presentacion":  info["presentacion"],
        "via":           info["via"],
        "nota":          info.get("nota", ""),
        "formula": (
            f"{info['dosis_base']} mg/kg × {peso_kg} kg"
            + (f" × {factor} (adulto mayor)" if factor != 1.0 else "")
            + f" = {round(calculada, 1)} mg  →  ajustado a {cant} mg"
        ),
    }


# ── Utilidades sobre el árbol ─────────────────────────────────────────────────

def _etiqueta(nodo) -> str:
    return nodo.etiqueta if nodo else ""

def _hijos(nodo) -> list:
    return nodo.hijos if nodo else []

def _valor_hoja(nodo) -> str:
    v = _etiqueta(nodo).strip()
    if v.startswith('"') and v.endswith('"'):
        return v[1:-1]
    return v


# ── Extractor principal ───────────────────────────────────────────────────────

class ExtractorReporte:
    def __init__(self, arbol, tabla_simbolos=None):
        self.arbol  = arbol
        self.tabla  = tabla_simbolos
        self.datos_paciente: dict = {}
        self.diagnosticos:   list = []
        self.tratamientos:   list = []
        self.variables:      list = []

    def extraer(self):
        self._recorrer(self.arbol)
        if self.tabla:
            self.variables = self.tabla.registros()

    def _recorrer(self, nodo):
        if nodo is None:
            return
        et = _etiqueta(nodo)
        if et == "INGRESAR":
            self._extraer_ingresar(nodo)
        elif et == "DIAGNOSTICO":
            self._extraer_diagnostico(nodo)
        elif et == "TRATAMIENTO":
            self._extraer_tratamiento(nodo)
        for hijo in _hijos(nodo):
            self._recorrer(hijo)

    def _extraer_ingresar(self, nodo):
        hijos = _hijos(nodo)
        i = 0
        while i + 1 < len(hijos):
            campo = _etiqueta(hijos[i])
            valor = _valor_hoja(hijos[i + 1])
            self.datos_paciente[campo.lower()] = valor
            i += 2

    def _extraer_diagnostico(self, nodo):
        for h in _hijos(nodo):
            val = self._eval_expr(h)
            if val:
                self.diagnosticos.append(val)

    def _extraer_tratamiento(self, nodo):
        for h in _hijos(nodo):
            val = self._eval_expr(h)
            if val:
                self.tratamientos.append(val)

    def _eval_expr(self, nodo) -> str:
        et    = _etiqueta(nodo)
        hijos = _hijos(nodo)
        if not hijos:
            v = et.strip()
            if v.startswith('"') and v.endswith('"'):
                return v[1:-1]
            return v
        for h in hijos:
            v = self._eval_expr(h)
            if v and v not in ("(", ")"):
                return v
        return et

    def _peso_kg(self):
        raw = self.datos_paciente.get("peso", "")
        try:
            return float("".join(c for c in str(raw) if c.isdigit() or c == "."))
        except (ValueError, TypeError):
            return None

    def _edad_anos(self):
        raw = self.datos_paciente.get("edad", "")
        try:
            return int("".join(c for c in str(raw) if c.isdigit()))
        except (ValueError, TypeError):
            return None

    # ── Generación del texto ──────────────────────────────────────────────

    def _wrap(self, texto: str, ancho: int = 46) -> list:
        """Parte un texto largo en líneas de 'ancho' caracteres máximo."""
        palabras = texto.split()
        lineas, actual = [], ""
        for p in palabras:
            if len(actual) + len(p) + 1 > ancho:
                lineas.append(actual.strip())
                actual = p
            else:
                actual += " " + p
        if actual:
            lineas.append(actual.strip())
        return lineas or [""]

    def generar_texto(self) -> str:
        lineas = []
        sep    = "─" * 54

        peso_kg = self._peso_kg()
        edad    = self._edad_anos()

        # ── Encabezado ────────────────────────────────────────────────────
        lineas.append("╔" + "═" * 54 + "╗")
        lineas.append("║" + "  REPORTE CLÍNICO — SISTEMA LPC".center(54) + "║")
        lineas.append("╚" + "═" * 54 + "╝")
        lineas.append(f"  Generado: {datetime.now().strftime('%d/%m/%Y  %H:%M:%S')}")
        lineas.append("")

        # ── Datos del paciente ────────────────────────────────────────────
        lineas.append("  DATOS DEL PACIENTE")
        lineas.append("  " + sep)

        etiquetas = {
            "nombre":  "Nombre",
            "edad":    "Edad",
            "peso":    "Peso",
            "presion": "Presión",
            "altura":  "Altura",
            "fecha":   "Fecha",
        }
        orden = ["nombre", "edad", "peso", "presion", "altura", "fecha"]
        mostrados = set()
        for clave in orden:
            if clave in self.datos_paciente:
                etiq = etiquetas.get(clave, clave.capitalize())
                val  = self.datos_paciente[clave]
                if clave == "edad" and str(val).replace(" ", "").isdigit():
                    val = f"{val} años"
                elif clave == "peso" and str(val).replace(".", "").isdigit():
                    val = f"{val} kg"
                lineas.append(f"  {etiq:<16} {val}")
                mostrados.add(clave)
        for clave, val in self.datos_paciente.items():
            if clave not in mostrados:
                lineas.append(f"  {clave.capitalize():<16} {val}")

        if self.variables:
            vars_extra = [
                e for e in self.variables
                if e.identificador.lower() not in self.datos_paciente
            ]
            for e in vars_extra:
                lineas.append(f"  {e.identificador:<16} {e.valor}")

        lineas.append("")

        # ── Diagnóstico ───────────────────────────────────────────────────
        if self.diagnosticos:
            lineas.append("  " + sep)
            lineas.append("  DIAGNÓSTICO")
            lineas.append("  " + sep)
            for d in self.diagnosticos:
                for parte in self._wrap(d, 50):
                    lineas.append(f"  {parte}")
            lineas.append("")

        # ── Tratamiento con dosis calculadas ──────────────────────────────
        if self.tratamientos:
            lineas.append("  " + sep)
            lineas.append("  TRATAMIENTO Y DOSIFICACIÓN")
            lineas.append("  " + sep)

            for trat in self.tratamientos:
                key        = trat.lower().strip()
                info_dosis = None

                if peso_kg is not None and edad is not None:
                    info_dosis = _calcular_dosis(key, peso_kg, edad)

                lineas.append("")
                if info_dosis:
                    lineas.append(f"  ▸ {info_dosis['nombre_formal']}")
                    lineas.append(f"    {'Presentación':<18} {info_dosis['presentacion']}")
                    lineas.append(f"    {'Vía':<18} {info_dosis['via']}")
                    lineas.append(f"    {'Dosis':<18} {info_dosis['cantidad']} {info_dosis['unidad']}")
                    lineas.append(f"    {'Frecuencia':<18} {info_dosis['frecuencia']}")
                    lineas.append(f"    {'Duración':<18} {info_dosis['dias']} días")
                    if info_dosis["nota"]:
                        partes = self._wrap(info_dosis["nota"], 46)
                        lineas.append(f"    {'Nota':<18} {partes[0]}")
                        for parte in partes[1:]:
                            lineas.append(f"    {'':<18} {parte}")
                    lineas.append(f"    {'Cálculo':<18} {info_dosis['formula']}")
                else:
                    lineas.append(f"  ▸ {trat}")
                    if peso_kg is None or edad is None:
                        lineas.append("    ⚠ Se requiere peso y edad en INGRESAR para calcular la dosis.")
                    else:
                        lineas.append("    ⚠ Medicamento no encontrado en el catálogo LPC.")
                        lineas.append("      Consultar con el médico tratante para la dosificación.")

            lineas.append("")

        # ── Pie ───────────────────────────────────────────────────────────
        lineas.append("  " + sep)
        lineas.append(" ")
        lineas.append("  ")
        lineas.append("  " + sep)

        return "\n".join(lineas)


def generar_reporte(arbol, tabla_simbolos=None) -> str:
    extractor = ExtractorReporte(arbol, tabla_simbolos)
    extractor.extraer()
    return extractor.generar_texto()
