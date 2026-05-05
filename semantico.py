"""
Analizador Semántico — Lenguaje de Protocolos Clínicos (LPC)
Recibe el árbol sintáctico generado por AnalizadorSintactico y
valida la coherencia semántica del programa.

Reglas implementadas:
  S-01  Variable no declarada
  S-02  Redeclaración de variable
  S-03  Incompatibilidad de tipos en asignación
  S-04  Identificador no válido en VALIDAR/VERIFICAR/COMPROBAR
  S-05  Identificador no válido en REGISTRAR
  S-06  Expresión con tipos incompatibles
  S-07  Nombre de REGLA duplicado
"""

ENTIDADES_CLINICAS = {
    "PACIENTE", "MEDICO", "CITA",
    "CONSULTA", "RECETA", "MEDICAMENTO", "CLINICA",
}

# Tipos que el lenguaje reconoce
TIPOS_VALIDOS = {"NUM_ENTERO", "NUM_DECIMAL", "TEXTO", "BOOLEANO", "FECHA", "ENTIDAD_CLINICA"}


class ErrorSemantico(Exception):
    def __init__(self, codigo, mensaje, linea=None, columna=None):
        self.codigo  = codigo
        self.mensaje = mensaje
        self.linea   = linea
        self.columna = columna
        super().__init__(mensaje)


class EntradaTabla:
    """Registro en la Tabla de Símbolos."""
    def __init__(self, identificador, tipo, valor, linea, columna, ambito):
        self.identificador = identificador
        self.tipo          = tipo
        self.valor         = valor
        self.linea         = linea
        self.columna       = columna
        self.ambito        = ambito

    def to_dict(self):
        return {
            "identificador": self.identificador,
            "tipo":          self.tipo,
            "valor":         self.valor,
            "linea":         self.linea,
            "columna":       self.columna,
            "ambito":        self.ambito,
        }


class TablaSimbolos:
    """Tabla de símbolos construida automáticamente durante el análisis."""
    def __init__(self):
        self._tabla: list[EntradaTabla] = []

    def existe(self, nombre: str) -> bool:
        return any(e.identificador == nombre for e in self._tabla)

    def obtener(self, nombre: str) -> EntradaTabla | None:
        for e in self._tabla:
            if e.identificador == nombre:
                return e
        return None

    def insertar(self, entrada: EntradaTabla):
        self._tabla.append(entrada)

    def registros(self) -> list[EntradaTabla]:
        return list(self._tabla)

    def __len__(self):
        return len(self._tabla)


# ---------------------------------------------------------------------------
# Funciones auxiliares sobre nodos del árbol
# ---------------------------------------------------------------------------

def _etiqueta(nodo) -> str:
    return nodo.etiqueta if nodo else ""

def _hijos(nodo) -> list:
    return nodo.hijos if nodo else []

def _hijo(nodo, idx: int):
    hijos = _hijos(nodo)
    return hijos[idx] if idx < len(hijos) else None


# ---------------------------------------------------------------------------
# Inferencia de tipo a partir de un nodo hoja (token)
# ---------------------------------------------------------------------------

def _inferir_tipo_literal(lexema: str) -> str | None:
    """Devuelve el tipo inferido de un valor literal, o None si es identificador."""
    if lexema.startswith('"') and lexema.endswith('"'):
        return "TEXTO"
    if lexema in ("verdadero", "falso"):
        return "BOOLEANO"
    if lexema in ENTIDADES_CLINICAS:
        return "ENTIDAD_CLINICA"
    # Fecha: dd-mm-yyyy
    import re
    if re.match(r'^\d{2}-\d{2}-\d{4}$', lexema):
        return "FECHA"
    try:
        int(lexema)
        return "NUM_ENTERO"
    except ValueError:
        pass
    try:
        float(lexema)
        return "NUM_DECIMAL"
    except ValueError:
        pass
    return None  # Es un identificador


# ---------------------------------------------------------------------------
# Analizador Semántico principal
# ---------------------------------------------------------------------------

class AnalizadorSemantico:
    def __init__(self, arbol, tokens: list):
        self.arbol          = arbol
        self.tokens         = tokens          # lista de Token (para buscar línea/columna)
        self.tabla          = TablaSimbolos()
        self.reglas_vistas  = set()           # nombres de REGLA únicos
        self.error          = None            # primer error encontrado
        self._ambito_actual = "global"

    # ----- Punto de entrada -----

    def analizar(self):
        """Recorre el árbol y construye la tabla. Devuelve (tabla, error_o_None)."""
        try:
            self._procesar_programa(self.arbol)
        except ErrorSemantico as e:
            self.error = e
        return self.tabla, self.error

    # ----- Procesadores por tipo de nodo -----

    def _procesar_programa(self, nodo):
        if _etiqueta(nodo) != "PROGRAMA":
            return
        for hijo in _hijos(nodo):
            if _etiqueta(hijo) == "BLOQUE":
                self._procesar_bloque(hijo)

    def _procesar_bloque(self, nodo):
        for hijo in _hijos(nodo):
            et = _etiqueta(hijo)
            if et == "SENTENCIAS":
                self._procesar_sentencias(hijo)

    def _procesar_sentencias(self, nodo):
        for hijo in _hijos(nodo):
            self._procesar_sentencia(hijo)

    def _procesar_sentencia(self, nodo):
        et = _etiqueta(nodo)
        if et == "REGLA":
            self._procesar_regla(nodo)
        elif et == "ASIGNACION":
            self._procesar_asignacion(nodo)
        elif et == "REGISTRO":
            self._procesar_registro(nodo)
        elif et == "VERIFICACION":
            self._procesar_verificacion(nodo)
        elif et == "CONDICIONAL":
            self._procesar_condicional(nodo)
        elif et == "INGRESAR":
            self._procesar_ingresar(nodo)
        elif et == "DOSIS":
            self._procesar_dosis(nodo)
        # DIAGNOSTICO y TRATAMIENTO son solo texto, no generan variables

    # --- REGLA ---

    def _procesar_regla(self, nodo):
        # Estructura hijos: ["REGLA", <nombre_id>, BLOQUE]
        hijos = _hijos(nodo)
        nombre_nodo = None
        bloque_nodo = None
        for h in hijos:
            if _etiqueta(h) == "BLOQUE":
                bloque_nodo = h
            elif _etiqueta(h) not in ("REGLA",):
                if nombre_nodo is None and _etiqueta(h) != "REGLA":
                    nombre_nodo = h

        # El segundo hijo (índice 1) es el identificador de la REGLA
        if len(hijos) >= 2:
            nombre_regla = _etiqueta(hijos[1])
            linea, col   = self._posicion_token(nombre_regla)

            if nombre_regla in self.reglas_vistas:
                raise ErrorSemantico(
                    "S-07",
                    f"La regla '{nombre_regla}' ya fue definida.",
                    linea, col
                )
            self.reglas_vistas.add(nombre_regla)
            ambito_previo       = self._ambito_actual
            self._ambito_actual = nombre_regla

        for h in hijos:
            if _etiqueta(h) == "BLOQUE":
                self._procesar_bloque(h)

        self._ambito_actual = ambito_previo if len(hijos) >= 2 else self._ambito_actual

    # --- ASIGNAR ---

    def _procesar_asignacion(self, nodo):
        # Hijos: ["ASIGNAR", <id>, "=", EXPRESION/hoja_valor, ";"]
        hijos = _hijos(nodo)
        # El identificador está en hijos[1]
        if len(hijos) < 4:
            return

        nombre   = _etiqueta(hijos[1])
        linea, col = self._posicion_token(nombre)

        # S-02: Redeclaración
        if self.tabla.existe(nombre):
            raise ErrorSemantico(
                "S-02",
                f"La variable '{nombre}' ya fue declarada previamente.",
                linea, col
            )

        # Evaluar expresión del lado derecho (hijos[3] en adelante, antes del ";")
        nodos_expr = [h for h in hijos[3:] if _etiqueta(h) != ";"]
        tipo_valor, valor_repr = self._evaluar_expresion_nodos(nodos_expr)

        self.tabla.insertar(EntradaTabla(
            identificador = nombre,
            tipo          = tipo_valor,
            valor         = valor_repr,
            linea         = linea,
            columna       = col,
            ambito        = self._ambito_actual,
        ))

    # --- INGRESAR (registra variables en tabla igual que ASIGNAR) ---

    def _procesar_ingresar(self, nodo):
        """
        INGRESAR nombre = "Juan"; edad = 48;
        Estructura de hijos: campo_hoja, valor_hoja, campo_hoja, valor_hoja ...
        Cada par se registra en la tabla de símbolos.
        """
        hijos = _hijos(nodo)
        i = 0
        while i + 1 < len(hijos):
            nombre    = _etiqueta(hijos[i])
            val_nodo  = hijos[i + 1]
            linea, col = self._posicion_token(nombre)

            if self.tabla.existe(nombre):
                raise ErrorSemantico(
                    "S-02",
                    f"La variable '{nombre}' ya fue declarada previamente.",
                    linea, col
                )

            tipo_valor, valor_repr = self._evaluar_nodo_expresion(val_nodo)
            self.tabla.insertar(EntradaTabla(
                identificador = nombre,
                tipo          = tipo_valor,
                valor         = valor_repr,
                linea         = linea,
                columna       = col,
                ambito        = self._ambito_actual,
            ))
            i += 2

    # --- DOSIS (cada campo = variable en la tabla) -----------------------

    def _procesar_dosis(self, nodo):
        """
        DOSIS medicamento = "Losartan"; cantidad = 50; unidad = "mg"; dias = 30;
        Misma estructura alterna que INGRESAR.
        """
        hijos = _hijos(nodo)
        i = 0
        while i + 1 < len(hijos):
            nombre    = _etiqueta(hijos[i])
            val_nodo  = hijos[i + 1]
            linea, col = self._posicion_token(nombre)

            if self.tabla.existe(nombre):
                raise ErrorSemantico(
                    "S-02",
                    f"La variable '{nombre}' ya fue declarada previamente.",
                    linea, col
                )

            tipo_valor, valor_repr = self._evaluar_nodo_expresion(val_nodo)
            self.tabla.insertar(EntradaTabla(
                identificador = nombre,
                tipo          = tipo_valor,
                valor         = valor_repr,
                linea         = linea,
                columna       = col,
                ambito        = self._ambito_actual,
            ))
            i += 2

    # --- REGISTRAR ---

    def _procesar_registro(self, nodo):
        hijos = _hijos(nodo)
        # Hijos: ["REGISTRAR", <expresion_o_id>, ";"]
        nodos_arg = [h for h in hijos[1:] if _etiqueta(h) != ";"]
        if not nodos_arg:
            return

        arg = nodos_arg[0]
        lexema = _etiqueta(arg)
        tipo_literal = _inferir_tipo_literal(lexema)

        if tipo_literal is None:
            # Es un identificador → verificar en tabla
            if not self.tabla.existe(lexema):
                linea, col = self._posicion_token(lexema)
                raise ErrorSemantico(
                    "S-05",
                    f"No se puede registrar '{lexema}', no está declarado.",
                    linea, col
                )

    # --- VALIDAR / VERIFICAR / COMPROBAR ---

    def _procesar_verificacion(self, nodo):
        hijos = _hijos(nodo)
        # Hijos: [<instruccion>, <argumento>, ";"]
        if len(hijos) < 2:
            return

        arg    = _etiqueta(hijos[1])
        linea, col = self._posicion_token(arg)

        # Entidad clínica reconocida → aceptar directamente
        if arg in ENTIDADES_CLINICAS:
            return

        # Identificador → verificar en tabla
        if not self.tabla.existe(arg):
            raise ErrorSemantico(
                "S-04",
                f"No se puede verificar '{arg}', no está declarado.",
                linea, col
            )

    # --- SI / ENTONCES / SINO ---

    def _procesar_condicional(self, nodo):
        hijos = _hijos(nodo)
        for h in hijos:
            et = _etiqueta(h)
            if et == "EXPRESION":
                self._evaluar_expresion_nodos([h])
            elif et in ("BLOQUE_ENTONCES", "BLOQUE_SINO", "BLOQUE"):
                self._procesar_bloque_condicional(h)
            elif et not in ("SI", "ENTONCES", "SINO", "(", ")"):
                # Puede ser un nodo hoja de la condición
                tipo_lit = _inferir_tipo_literal(et)
                if tipo_lit is None and et not in ("SI", "ENTONCES", "SINO", "(", ")"):
                    # Verificar que el identificador de condición exista
                    if not self.tabla.existe(et) and et not in ENTIDADES_CLINICAS:
                        linea, col = self._posicion_token(et)
                        raise ErrorSemantico(
                            "S-01",
                            f"La variable '{et}' no ha sido declarada.",
                            linea, col
                        )

    def _procesar_bloque_condicional(self, nodo):
        for hijo in _hijos(nodo):
            et = _etiqueta(hijo)
            if et == "SENTENCIAS":
                self._procesar_sentencias(hijo)

    # ----- Evaluación de expresiones -----

    def _evaluar_expresion_nodos(self, nodos: list) -> tuple[str, str]:
        """
        Evalúa una lista de nodos de expresión.
        Devuelve (tipo_resultado, representación_valor).
        """
        if not nodos:
            return "DESCONOCIDO", ""

        nodo = nodos[0]
        return self._evaluar_nodo_expresion(nodo)

    def _evaluar_nodo_expresion(self, nodo) -> tuple[str, str]:
        et = _etiqueta(nodo)

        # Nodo EXPRESION con hijos (operación binaria)
        if et == "EXPRESION":
            hijos = _hijos(nodo)
            if len(hijos) == 1:
                return self._evaluar_nodo_expresion(hijos[0])
            # Expresión binaria: izq op der
            if len(hijos) >= 3:
                tipo_izq, val_izq = self._evaluar_nodo_expresion(hijos[0])
                operador          = _etiqueta(hijos[1])
                tipo_der, val_der = self._evaluar_nodo_expresion(hijos[2])
                return self._verificar_compatibilidad_op(tipo_izq, tipo_der, operador, nodo)
            return "DESCONOCIDO", et

        # Nodo GRUPO
        if et == "GRUPO":
            hijos = _hijos(nodo)
            for h in hijos:
                if _etiqueta(h) not in ("(", ")"):
                    return self._evaluar_nodo_expresion(h)
            return "DESCONOCIDO", et

        # Nodo hoja: literal o identificador
        tipo_lit = _inferir_tipo_literal(et)
        if tipo_lit is not None:
            return tipo_lit, et

        # Es un identificador
        entrada = self.tabla.obtener(et)
        if entrada is None:
            # S-01: Variable no declarada
            linea, col = self._posicion_token(et)
            raise ErrorSemantico(
                "S-01",
                f"La variable '{et}' no ha sido declarada.",
                linea, col
            )
        return entrada.tipo, et

    def _verificar_compatibilidad_op(self, tipo_izq, tipo_der, operador, nodo) -> tuple[str, str]:
        """S-06: Verifica que ambos operandos sean compatibles."""
        numericos = {"NUM_ENTERO", "NUM_DECIMAL"}

        # Mismos tipos → siempre compatible (resultado = mismo tipo)
        if tipo_izq == tipo_der:
            return tipo_izq, f"{tipo_izq} {operador} {tipo_der}"

        # Mezcla de enteros y decimales → compatible, resultado decimal
        if tipo_izq in numericos and tipo_der in numericos:
            return "NUM_DECIMAL", f"NUM_DECIMAL {operador} NUM_DECIMAL"

        # Cualquier otra combinación → error S-06
        linea = getattr(nodo, "linea", None)
        col   = getattr(nodo, "columna", None)
        raise ErrorSemantico(
            "S-06",
            f"Operación inválida entre tipos {tipo_izq} y {tipo_der}.",
            linea, col
        )

    # ----- Utilidad: buscar línea/columna de un lexema en la lista de tokens -----

    def _posicion_token(self, lexema: str) -> tuple[int | None, int | None]:
        for tok in self.tokens:
            if tok.lexema == lexema:
                return tok.linea, tok.columna
        return None, None
