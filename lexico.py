import re
from tokens import (
    Token, PALABRAS_RESERVADAS,
    OPERADORES_ARITMETICOS, OPERADORES_RELACIONALES, SIMBOLOS
)


class AnalizadorLexico:
    def __init__(self, codigo):
        self.codigo  = codigo
        self.pos     = 0
        self.linea   = 1
        self.columna = 1
        self.tokens  = []
        self.errores = []

    def caracter_actual(self):
        if self.pos < len(self.codigo):
            return self.codigo[self.pos]
        return None

    def avanzar(self):
        c = self.codigo[self.pos]
        self.pos += 1
        if c == "\n":
            self.linea  += 1
            self.columna = 1
        else:
            self.columna += 1
        return c

    def analizar(self):
        while self.pos < len(self.codigo):
            c = self.caracter_actual()

            if c in " \t\r\n":
                self.avanzar()
                continue

            li = self.linea
            ci = self.columna

            if c == '"':
                self.avanzar()
                lexema = '"'
                while self.pos < len(self.codigo) and self.caracter_actual() != '"':
                    if self.caracter_actual() == "\n":
                        break
                    lexema += self.avanzar()
                if self.pos < len(self.codigo) and self.caracter_actual() == '"':
                    lexema += self.avanzar()
                    self.tokens.append(Token("IDENTIFICADOR", lexema, li, ci))
                else:
                    self.errores.append({"lexema": lexema, "descripcion": "Cadena sin cierre de comillas", "linea": li, "columna": ci})
                continue

            if c.isdigit():
                lexema = ""
                while self.pos < len(self.codigo) and self.caracter_actual().isdigit():
                    lexema += self.avanzar()
                if self.pos < len(self.codigo) and self.caracter_actual() == "." \
                        and self.pos + 1 < len(self.codigo) and self.codigo[self.pos + 1].isdigit():
                    lexema += self.avanzar()
                    while self.pos < len(self.codigo) and self.caracter_actual().isdigit():
                        lexema += self.avanzar()
                    self.tokens.append(Token("NUM_DECIMAL", lexema, li, ci))
                elif self.pos < len(self.codigo) and self.caracter_actual().isalpha():
                    while self.pos < len(self.codigo) and (self.caracter_actual().isalnum() or self.caracter_actual() == "_"):
                        lexema += self.avanzar()
                    self.errores.append({"lexema": lexema, "descripcion": "Identificador no puede iniciar con digito", "linea": li, "columna": ci})
                else:
                    self.tokens.append(Token("NUM_ENTERO", lexema, li, ci))
                continue

            if c.isalpha() or c == "_":
                lexema = ""
                while self.pos < len(self.codigo) and (self.caracter_actual().isalnum() or self.caracter_actual() == "_"):
                    lexema += self.avanzar()
                if lexema.upper() in PALABRAS_RESERVADAS:
                    self.tokens.append(Token("PALABRA_RESERVADA", lexema.upper(), li, ci))
                elif lexema in ("verdadero", "falso"):
                    self.tokens.append(Token("BOOLEANO", lexema, li, ci))
                else:
                    self.tokens.append(Token("IDENTIFICADOR", lexema, li, ci))
                continue

            fecha_match = re.match(r'\d{2}-\d{2}-\d{4}', self.codigo[self.pos:])
            if fecha_match:
                lexema = fecha_match.group()
                for _ in lexema:
                    self.avanzar()
                self.tokens.append(Token("FECHA", lexema, li, ci))
                continue

            if c in OPERADORES_RELACIONALES:
                self.avanzar()
                self.tokens.append(Token("OPERADOR_RELACIONAL", c, li, ci))
                continue

            if c in OPERADORES_ARITMETICOS:
                self.avanzar()
                self.tokens.append(Token("OPERADOR", c, li, ci))
                continue

            if c in SIMBOLOS:
                self.avanzar()
                self.tokens.append(Token(SIMBOLOS[c], c, li, ci))
                continue

            self.avanzar()
            self.errores.append({"lexema": c, "descripcion": f"Caracter no reconocido: '{c}'", "linea": li, "columna": ci})

        return self.tokens, self.errores