from nodo import Nodo


class ErrorSintactico(Exception):
    def __init__(self, mensaje, linea=None, columna=None):
        self.mensaje = mensaje
        self.linea = linea
        self.columna = columna
        super().__init__(mensaje)


class AnalizadorSintactico:
    def __init__(self, tokens):
        self.tokens = [t for t in tokens if t.tipo not in ("ESPACIO", "COMENTARIO")]
        self.pos = 0
        self.errores = []

    def token_actual(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def ver(self, offset=0):
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return None

    def consumir(self, tipo=None, lexema=None):
        tok = self.token_actual()
        if tok is None:
            raise ErrorSintactico(
                "Se esperaba mas tokens pero se llego al final del codigo"
            )
        if tipo and tok.tipo != tipo:
            raise ErrorSintactico(
                f"Se esperaba {tipo} pero se encontro {tok.tipo} '{tok.lexema}'",
                tok.linea, tok.columna
            )
        if lexema and tok.lexema != lexema:
            raise ErrorSintactico(
                f"Se esperaba '{lexema}' pero se encontro '{tok.lexema}'",
                tok.linea, tok.columna
            )
        self.pos += 1
        return tok

    def consumir_pr(self, lexema):
        tok = self.token_actual()
        if tok is None:
            raise ErrorSintactico(
                f"Se esperaba '{lexema}' pero se llego al final del codigo"
            )
        if tok.tipo != "PALABRA_RESERVADA" or tok.lexema != lexema:
            raise ErrorSintactico(
                f"Se esperaba palabra reservada '{lexema}' pero se encontro '{tok.lexema}'",
                tok.linea, tok.columna
            )
        self.pos += 1
        return tok

    def es_pr(self, lexema):
        tok = self.token_actual()
        return tok is not None and tok.tipo == "PALABRA_RESERVADA" and tok.lexema == lexema

    def es_delimitador(self, lexema):
        tok = self.token_actual()
        return tok is not None and tok.tipo == "DELIMITADOR" and tok.lexema == lexema

    def analizar(self):
        try:
            arbol = self.programa()
            tok = self.token_actual()
            if tok is not None:
                raise ErrorSintactico(
                    f"Token inesperado '{tok.lexema}' despues de FIN",
                    tok.linea, tok.columna
                )
            return arbol, []
        except ErrorSintactico as e:
            return None, [{"mensaje": e.mensaje, "linea": e.linea, "columna": e.columna}]

    def programa(self):
        nodo = Nodo("PROGRAMA")

        tok_proto = self.consumir_pr("PROTOCOLO")
        nodo.hoja(tok_proto.lexema)

        nodo_bloque = self.bloque()
        nodo.agregar_hijo(nodo_bloque)

        tok_fin = self.consumir_pr("FIN")
        nodo.hoja(tok_fin.lexema)

        return nodo

    def bloque(self):
        nodo = Nodo("BLOQUE")

        tok_ab = self.consumir("DELIMITADOR", "{")
        nodo.hoja(tok_ab.lexema)

        if not self.es_delimitador("}"):
            nodo_lista = self.lista_sentencias()
            nodo.agregar_hijo(nodo_lista)

        tok_ci = self.consumir("DELIMITADOR", "}")
        nodo.hoja(tok_ci.lexema)

        return nodo

    def lista_sentencias(self):
        nodo = Nodo("SENTENCIAS")
        while not self.es_delimitador("}") and self.token_actual() is not None and not self.es_pr("FIN"):
            nodo_sent = self.sentencia()
            nodo.agregar_hijo(nodo_sent)
        return nodo

    def sentencia(self):
        tok = self.token_actual()
        if tok is None:
            raise ErrorSintactico("Se esperaba una sentencia pero se llego al final del codigo")

        if tok.tipo == "PALABRA_RESERVADA":
            if tok.lexema == "REGLA":
                return self.regla()
            elif tok.lexema == "SI":
                return self.condicional()
            elif tok.lexema == "ASIGNAR":
                return self.asignacion()
            elif tok.lexema == "REGISTRAR":
                return self.registro()
            elif tok.lexema in ("VALIDAR", "VERIFICAR", "COMPROBAR"):
                return self.verificacion()
            elif tok.lexema == "INGRESAR":
                return self.ingresar()
            elif tok.lexema == "DIAGNOSTICO":
                return self.diagnostico()
            elif tok.lexema == "TRATAMIENTO":
                return self.tratamiento()
            elif tok.lexema == "DOSIS":
                return self.dosis()
            else:
                raise ErrorSintactico(
                    f"Palabra reservada '{tok.lexema}' no inicia ninguna sentencia valida",
                    tok.linea, tok.columna
                )

        raise ErrorSintactico(
            f"Se esperaba una sentencia pero se encontro '{tok.lexema}' ({tok.tipo})",
            tok.linea, tok.columna
        )

    def regla(self):
        nodo = Nodo("REGLA")

        tok_r = self.consumir_pr("REGLA")
        nodo.hoja(tok_r.lexema)

        tok_id = self.consumir("IDENTIFICADOR")
        nodo.hoja(tok_id.lexema)

        nodo_bloque = self.bloque()
        nodo.agregar_hijo(nodo_bloque)

        return nodo

    def condicional(self):
        nodo = Nodo("CONDICIONAL")

        tok_si = self.consumir_pr("SI")
        nodo.hoja(tok_si.lexema)

        tok_ap = self.consumir("DELIMITADOR", "(")
        nodo.hoja(tok_ap.lexema)

        nodo_expr = self.expresion()
        nodo.agregar_hijo(nodo_expr)

        tok_cp = self.consumir("DELIMITADOR", ")")
        nodo.hoja(tok_cp.lexema)

        tok_ent = self.consumir_pr("ENTONCES")
        nodo.hoja(tok_ent.lexema)

        nodo_then = self.bloque()
        nodo_then.etiqueta = "BLOQUE_ENTONCES"
        nodo.agregar_hijo(nodo_then)

        if self.es_pr("SINO"):
            tok_sino = self.consumir_pr("SINO")
            nodo.hoja(tok_sino.lexema)
            nodo_else = self.bloque()
            nodo_else.etiqueta = "BLOQUE_SINO"
            nodo.agregar_hijo(nodo_else)

        return nodo

    def asignacion(self):
        nodo = Nodo("ASIGNACION")

        tok_a = self.consumir_pr("ASIGNAR")
        nodo.hoja(tok_a.lexema)

        tok_id = self.consumir("IDENTIFICADOR")
        nodo.hoja(tok_id.lexema)

        tok_eq = self.consumir("OPERADOR", "=")
        nodo.hoja(tok_eq.lexema)

        nodo_expr = self.expresion()
        nodo.agregar_hijo(nodo_expr)

        tok_sc = self.consumir("FIN_SENTENCIA", ";")
        nodo.hoja(tok_sc.lexema)

        return nodo

    def registro(self):
        nodo = Nodo("REGISTRO")

        tok_r = self.consumir_pr("REGISTRAR")
        nodo.hoja(tok_r.lexema)

        nodo_expr = self.expresion()
        nodo.agregar_hijo(nodo_expr)

        tok_sc = self.consumir("FIN_SENTENCIA", ";")
        nodo.hoja(tok_sc.lexema)

        return nodo

    def verificacion(self):
        nodo = Nodo("VERIFICACION")

        tok_v = self.consumir("PALABRA_RESERVADA")
        nodo.hoja(tok_v.lexema)

        tok_id = self.token_actual()
        if tok_id is None:
            raise ErrorSintactico("Se esperaba IDENTIFICADOR o entidad clinica despues de la verificacion")
        if tok_id.tipo not in ("IDENTIFICADOR", "PALABRA_RESERVADA"):
            raise ErrorSintactico(
                f"Se esperaba IDENTIFICADOR o entidad clinica pero se encontro '{tok_id.lexema}' ({tok_id.tipo})",
                tok_id.linea, tok_id.columna
            )
        self.consumir()
        nodo.hoja(tok_id.lexema)

        tok_sc = self.consumir("FIN_SENTENCIA", ";")
        nodo.hoja(tok_sc.lexema)

        return nodo

    # ── INGRESAR nombre("Juan") edad(48) ──────────────────────────────────
    # ── INGRESAR nombre = "Juan"; edad = 48; ─────────────────────────────
    def ingresar(self):
        nodo = Nodo("INGRESAR")
        self.consumir_pr("INGRESAR")
        STOP_PR = {
            "PROTOCOLO","FIN","REGLA","SI","ENTONCES","SINO",
            "VALIDAR","VERIFICAR","COMPROBAR","REGISTRAR","ASIGNAR",
            "DIAGNOSTICO","TRATAMIENTO","DOSIS","INGRESAR",
        }
        while self.token_actual() is not None:
            tok = self.token_actual()
            # parar en keywords de estructura
            if tok.tipo == "PALABRA_RESERVADA" and tok.lexema in STOP_PR:
                break
            if tok.tipo not in ("IDENTIFICADOR", "PALABRA_RESERVADA"):
                break
            # verificar que el siguiente token sea "="
            siguiente = self.ver(1)
            if siguiente is None or not (siguiente.tipo == "OPERADOR" and siguiente.lexema == "="):
                break
            tok_id = self.consumir()
            nodo.hoja(tok_id.lexema)
            self.consumir("OPERADOR", "=")
            nodo_val = self.expresion()
            nodo.agregar_hijo(nodo_val)
            if self.token_actual() and self.token_actual().tipo == "FIN_SENTENCIA":
                self.consumir()
        return nodo

    # ── DIAGNOSTICO "texto"; ──────────────────────────────────────────────
    def diagnostico(self):
        nodo = Nodo("DIAGNOSTICO")
        self.consumir_pr("DIAGNOSTICO")
        nodo_val = self.expresion()
        nodo.agregar_hijo(nodo_val)
        self.consumir("FIN_SENTENCIA", ";")
        return nodo

    # ── TRATAMIENTO "texto"; ──────────────────────────────────────────────
    def tratamiento(self):
        nodo = Nodo("TRATAMIENTO")
        self.consumir_pr("TRATAMIENTO")
        nodo_val = self.expresion()
        nodo.agregar_hijo(nodo_val)
        self.consumir("FIN_SENTENCIA", ";")
        return nodo

    # ── DOSIS medicamento = "Losartan"; cantidad = 50; unidad = "mg"; dias = 30;
    def dosis(self):
        nodo = Nodo("DOSIS")
        self.consumir_pr("DOSIS")
        STOP_PR = {
            "PROTOCOLO","FIN","REGLA","SI","ENTONCES","SINO",
            "VALIDAR","VERIFICAR","COMPROBAR","REGISTRAR","ASIGNAR",
            "DIAGNOSTICO","TRATAMIENTO","DOSIS","INGRESAR",
        }
        while self.token_actual() is not None:
            tok = self.token_actual()
            if tok.tipo == "PALABRA_RESERVADA" and tok.lexema in STOP_PR:
                break
            if tok.tipo not in ("IDENTIFICADOR", "PALABRA_RESERVADA"):
                break
            siguiente = self.ver(1)
            if siguiente is None or not (siguiente.tipo == "OPERADOR" and siguiente.lexema == "="):
                break
            tok_id = self.consumir()
            nodo.hoja(tok_id.lexema)
            self.consumir("OPERADOR", "=")
            nodo_val = self.expresion()
            nodo.agregar_hijo(nodo_val)
            if self.token_actual() and self.token_actual().tipo == "FIN_SENTENCIA":
                self.consumir()
        return nodo

    def expresion(self):
        nodo = Nodo("EXPRESION")
        nodo_t = self.termino()
        nodo.agregar_hijo(nodo_t)

        while self.token_actual() is not None and self.token_actual().tipo in ("OPERADOR", "OPERADOR_RELACIONAL"):
            tok_op = self.consumir()
            nodo.hoja(tok_op.lexema)
            nodo_t2 = self.termino()
            nodo.agregar_hijo(nodo_t2)

        if len(nodo.hijos) == 1:
            return nodo.hijos[0]

        return nodo

    def termino(self):
        tok = self.token_actual()
        if tok is None:
            raise ErrorSintactico("Se esperaba un termino pero se llego al final del codigo")

        if tok.tipo in ("IDENTIFICADOR", "NUM_ENTERO", "NUM_DECIMAL", "BOOLEANO", "FECHA"):
            self.consumir()
            return Nodo(tok.lexema)

        if tok.tipo == "PALABRA_RESERVADA" and tok.lexema in (
            "PACIENTE", "MEDICO", "CITA", "CONSULTA", "RECETA", "MEDICAMENTO", "CLINICA"
        ):
            self.consumir()
            return Nodo(tok.lexema)

        if tok.tipo == "DELIMITADOR" and tok.lexema == "(":
            nodo = Nodo("GRUPO")
            self.consumir("DELIMITADOR", "(")
            nodo.hoja("(")
            nodo_expr = self.expresion()
            nodo.agregar_hijo(nodo_expr)
            self.consumir("DELIMITADOR", ")")
            nodo.hoja(")")
            return nodo

        raise ErrorSintactico(
            f"Se esperaba un termino (identificador, numero, booleano) pero se encontro '{tok.lexema}' ({tok.tipo})",
            tok.linea, tok.columna
        )
