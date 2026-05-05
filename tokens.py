PALABRAS_RESERVADAS = {
    "PROTOCOLO", "FIN", "REGLA", "SI", "ENTONCES", "SINO",
    "VALIDAR", "VERIFICAR", "COMPROBAR", "REGISTRAR", "ASIGNAR",
    "PACIENTE", "MEDICO", "CITA", "CONSULTA", "RECETA", "MEDICAMENTO", "CLINICA",
    # Nuevas instrucciones de reporte
    "INGRESAR", "DIAGNOSTICO", "TRATAMIENTO", "DOSIS",
}

OPERADORES_ARITMETICOS = {"+", "-", "*", "/", "%", "=", "!"}
OPERADORES_RELACIONALES = {">", "<"}

SIMBOLOS = {
    "(": "DELIMITADOR",
    ")": "DELIMITADOR",
    "{": "DELIMITADOR",
    "}": "DELIMITADOR",
    ";": "FIN_SENTENCIA",
    ",": "SIMBOLO_ESPECIAL",
    ".": "SIMBOLO_ESPECIAL",
}


class Token:
    def __init__(self, tipo, lexema, linea, columna):
        self.tipo    = tipo
        self.lexema  = lexema
        self.linea   = linea
        self.columna = columna