from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
    QScrollArea, QTabWidget
)
from estilos import STYLE_AYUDA
from config import cargar_lexemas_extra


def tab_scroll(contenido_widget):
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setWidget(contenido_widget)
    return scroll


class VentanaAyuda(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ayuda - Lenguaje de Protocolos Clinicos")
        self.setMinimumSize(660, 540)
        self.setMaximumSize(760, 680)
        self.setStyleSheet(STYLE_AYUDA)
        self._construir()

    def _construir(self):
        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(16, 14, 16, 14)
        raiz.setSpacing(10)

        titulo = QLabel("Referencia del Lenguaje — LPC")
        titulo.setObjectName("seccion_ayuda")
        titulo.setStyleSheet("font-size:15px; font-weight:bold; color:#E3B6B1;")
        raiz.addWidget(titulo)

        tabs = QTabWidget()
        tabs.addTab(tab_scroll(self._tab_estructura()),    "Estructura")
        tabs.addTab(tab_scroll(self._tab_instrucciones()), "Instrucciones")
        tabs.addTab(tab_scroll(self._tab_reservadas()),    "Palabras Reservadas")
        tabs.addTab(tab_scroll(self._tab_tokens()),        "Tipos de Token")
        tabs.addTab(tab_scroll(self._tab_semantica()),     "Semántica")
        tabs.addTab(tab_scroll(self._tab_reporte()),       "Reporte")
        tabs.addTab(tab_scroll(self._tab_errores()),       "Errores")
        tabs.addTab(tab_scroll(self._tab_lexemas_extra()), "Lexemas Agregados")
        raiz.addWidget(tabs)

        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setObjectName("btn_cerrar")
        btn_cerrar.clicked.connect(self.close)
        fila = QHBoxLayout()
        fila.addStretch()
        fila.addWidget(btn_cerrar)
        raiz.addLayout(fila)

    # ── Helpers ───────────────────────────────────────────────────────────

    def _seccion(self, texto):
        lbl = QLabel(texto)
        lbl.setObjectName("seccion_ayuda")
        return lbl

    def _desc(self, texto):
        lbl = QLabel(texto)
        lbl.setObjectName("desc")
        lbl.setWordWrap(True)
        return lbl

    def _mono(self, texto):
        lbl = QLabel(texto)
        lbl.setObjectName("mono")
        lbl.setWordWrap(True)
        return lbl

    def _tabla(self, headers, filas, anchos=None):
        t = QTableWidget(len(filas), len(headers))
        t.setHorizontalHeaderLabels(headers)
        t.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        t.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        t.setAlternatingRowColors(True)
        t.verticalHeader().setVisible(False)
        if anchos:
            for i, m in enumerate(anchos):
                if m == -1:
                    t.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
                else:
                    t.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        else:
            t.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        for r, fila in enumerate(filas):
            for c, val in enumerate(fila):
                t.setItem(r, c, QTableWidgetItem(val))
        t.setFixedHeight(min(32 + len(filas) * 28, 340))
        return t

    # ── Pestaña: Estructura ───────────────────────────────────────────────

    def _tab_estructura(self):
        w = QWidget()
        w.setStyleSheet("background-color: #1e2030;")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(12, 8, 12, 12)
        lay.setSpacing(8)

        lay.addWidget(self._seccion("Estructura general del programa"))
        lay.addWidget(self._desc(
            "Todo programa LPC debe comenzar obligatoriamente con PROTOCOLO { "
            "y terminar con } FIN. Dentro del bloque se definen las instrucciones."
        ))
        lay.addWidget(self._mono(
            "PROTOCOLO {\n"
            "    INGRESAR campo = valor;\n"
            "    ASIGNAR variable = valor;\n"
            "    DIAGNOSTICO \"texto\";\n"
            "    REGLA NombreRegla {\n"
            "        SI ( condicion ) ENTONCES {\n"
            "            instrucciones;\n"
            "        }\n"
            "    }\n"
            "} FIN"
        ))

        lay.addWidget(self._seccion("Reglas de bloques"))
        lay.addWidget(self._desc(
            "Los bloques se delimitan con llaves { }. "
            "Cada REGLA tiene su propio bloque { }. "
            "Los bloques SI...ENTONCES y SINO también usan llaves."
        ))
        lay.addWidget(self._mono(
            "REGLA validarPaciente {\n"
            "    SI ( presion > 140 ) ENTONCES {\n"
            "        REGISTRAR presion;\n"
            "    } SINO {\n"
            "        VERIFICAR PACIENTE;\n"
            "    }\n"
            "}"
        ))

        lay.addWidget(self._seccion("Ejemplo completo válido"))
        lay.addWidget(self._mono(
            "PROTOCOLO {\n"
            "    INGRESAR nombre = \"Ana\"; edad = 30;\n"
            "    ASIGNAR temperatura = 38.5;\n"
            "    ASIGNAR fiebre = verdadero;\n"
            "    DIAGNOSTICO \"Fiebre moderada\";\n"
            "    REGLA evaluar {\n"
            "        SI ( fiebre ) ENTONCES {\n"
            "            TRATAMIENTO \"Reposo y liquidos\";\n"
            "            DOSIS medicamento = \"Paracetamol\"; cantidad = 500; unidad = \"mg\"; dias = 5;\n"
            "            REGISTRAR temperatura;\n"
            "        }\n"
            "        VERIFICAR PACIENTE;\n"
            "    }\n"
            "} FIN"
        ))
        lay.addStretch()
        return w

    # ── Pestaña: Instrucciones ────────────────────────────────────────────

    def _tab_instrucciones(self):
        w = QWidget()
        w.setStyleSheet("background-color: #1e2030;")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(12, 8, 12, 12)
        lay.setSpacing(10)

        lay.addWidget(self._seccion("PROTOCOLO / FIN"))
        lay.addWidget(self._desc("Delimitan el programa completo. PROTOCOLO abre el bloque principal con { y FIN lo cierra con }."))
        lay.addWidget(self._mono("PROTOCOLO { ... } FIN"))

        lay.addWidget(self._seccion("INGRESAR"))
        lay.addWidget(self._desc(
            "Declara los datos de entrada del paciente. Cada campo se asigna con = "
            "y se termina con ;. Se registran en la tabla de símbolos igual que ASIGNAR."
        ))
        lay.addWidget(self._mono("INGRESAR nombre = \"Juan\"; edad = 48;"))

        lay.addWidget(self._seccion("ASIGNAR"))
        lay.addWidget(self._desc(
            "Declara y asigna una variable. El tipo se infiere del valor. "
            "No se puede declarar la misma variable dos veces."
        ))
        lay.addWidget(self._mono(
            "ASIGNAR presion = 160;\n"
            "ASIGNAR temperatura = 37.2;\n"
            "ASIGNAR activo = verdadero;\n"
            "ASIGNAR fechaCita = 23-04-2024;\n"
            "ASIGNAR nombre = \"Carlos\";"
        ))

        lay.addWidget(self._seccion("DIAGNOSTICO"))
        lay.addWidget(self._desc("Registra el diagnóstico clínico como texto. No genera variable en la tabla de símbolos."))
        lay.addWidget(self._mono("DIAGNOSTICO \"Hipertension arterial grado II\";"))

        lay.addWidget(self._seccion("TRATAMIENTO"))
        lay.addWidget(self._desc("Registra la indicación de tratamiento. No genera variable en la tabla de símbolos."))
        lay.addWidget(self._mono("TRATAMIENTO \"Dieta baja en sodio\";"))

        lay.addWidget(self._seccion("DOSIS"))
        lay.addWidget(self._desc(
            "Registra los campos de una dosis médica con = y ;. "
            "Todos los campos se agregan a la tabla de símbolos."
        ))
        lay.addWidget(self._mono(
            "DOSIS medicamento = \"Losartan\"; cantidad = 50; unidad = \"mg\"; dias = 30;"
        ))

        lay.addWidget(self._seccion("REGISTRAR"))
        lay.addWidget(self._desc("Registra una variable ya declarada o un valor literal directamente."))
        lay.addWidget(self._mono(
            "REGISTRAR presion;\n"
            "REGISTRAR temperatura;\n"
            "REGISTRAR 36.5;"
        ))

        lay.addWidget(self._seccion("VALIDAR / VERIFICAR / COMPROBAR"))
        lay.addWidget(self._desc(
            "Verifican una entidad clínica reconocida o un identificador declarado previamente."
        ))
        lay.addWidget(self._mono(
            "VALIDAR PACIENTE;\n"
            "VERIFICAR MEDICO;\n"
            "COMPROBAR activo;"
        ))

        lay.addWidget(self._seccion("REGLA"))
        lay.addWidget(self._desc(
            "Define un bloque lógico con nombre único. "
            "No pueden existir dos REGLA con el mismo nombre."
        ))
        lay.addWidget(self._mono(
            "REGLA validarPaciente {\n"
            "    ASIGNAR peso = 70;\n"
            "    VERIFICAR PACIENTE;\n"
            "}"
        ))

        lay.addWidget(self._seccion("SI / ENTONCES / SINO"))
        lay.addWidget(self._desc(
            "Estructura condicional. La condición va entre paréntesis. "
            "SINO es opcional. Ambas ramas usan bloques { }."
        ))
        lay.addWidget(self._mono(
            "SI ( presion > 140 ) ENTONCES {\n"
            "    REGISTRAR presion;\n"
            "} SINO {\n"
            "    VERIFICAR PACIENTE;\n"
            "}"
        ))

        lay.addStretch()
        return w

    # ── Pestaña: Palabras Reservadas ──────────────────────────────────────

    def _tab_reservadas(self):
        w = QWidget()
        w.setStyleSheet("background-color: #1e2030;")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(12, 8, 12, 12)
        lay.setSpacing(8)

        lay.addWidget(self._seccion("Palabras Reservadas del Lenguaje"))
        lay.addWidget(self._desc("Estas palabras tienen significado especial y no pueden usarse como identificadores."))
        lay.addWidget(self._tabla(
            ["Lexema", "Descripción"],
            [
                ("PROTOCOLO",   "Abre el bloque principal del programa"),
                ("FIN",         "Cierra el bloque principal del programa"),
                ("REGLA",       "Define una regla con nombre único dentro del protocolo"),
                ("INGRESAR",    "Declara datos de entrada del paciente"),
                ("ASIGNAR",     "Declara y asigna un valor a una variable"),
                ("DIAGNOSTICO", "Registra el diagnóstico clínico (texto libre)"),
                ("TRATAMIENTO", "Registra la indicación de tratamiento (texto libre)"),
                ("DOSIS",       "Registra los campos de una dosis médica"),
                ("REGISTRAR",   "Registra una variable o valor en el sistema"),
                ("VALIDAR",     "Valida una entidad clínica o variable declarada"),
                ("VERIFICAR",   "Verifica una entidad clínica o variable declarada"),
                ("COMPROBAR",   "Comprueba una entidad clínica o variable declarada"),
                ("SI",          "Inicio de estructura condicional"),
                ("ENTONCES",    "Rama verdadera del condicional"),
                ("SINO",        "Rama alternativa del condicional (opcional)"),
                ("PACIENTE",    "Entidad clínica: paciente"),
                ("MEDICO",      "Entidad clínica: médico"),
                ("CITA",        "Entidad clínica: cita"),
                ("CONSULTA",    "Entidad clínica: consulta"),
                ("RECETA",      "Entidad clínica: receta"),
                ("MEDICAMENTO", "Entidad clínica: medicamento"),
                ("CLINICA",     "Entidad clínica: clínica"),
            ],
            [0, -1]
        ))
        lay.addWidget(self._seccion("Literales especiales"))
        lay.addWidget(self._tabla(
            ["Lexema", "Token", "Descripción"],
            [
                ("verdadero", "BOOLEANO", "Valor lógico verdadero"),
                ("falso",     "BOOLEANO", "Valor lógico falso"),
            ],
            [0, 0, -1]
        ))
        lay.addStretch()
        return w

    # ── Pestaña: Tipos de Token ───────────────────────────────────────────

    def _tab_tokens(self):
        w = QWidget()
        w.setStyleSheet("background-color: #1e2030;")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(12, 8, 12, 12)
        lay.setSpacing(8)

        lay.addWidget(self._seccion("Identificadores y Literales"))
        lay.addWidget(self._tabla(
            ["Token", "Patrón", "Ejemplo"],
            [
                ("IDENTIFICADOR", "letra (letra | dígito | _)*",  "edad, nombrePaciente"),
                ("IDENTIFICADOR", '"texto entre comillas"',        '"urgente", "Juan"'),
                ("NUM_ENTERO",    "dígito+",                       "0, 42, 160"),
                ("NUM_DECIMAL",   "dígito+ . dígito+",             "3.14, 37.2"),
                ("BOOLEANO",      "verdadero | falso",             "verdadero"),
                ("FECHA",         "DD-MM-AAAA",                    "23-04-2024"),
            ],
            [-1, -1, -1]
        ))

        lay.addWidget(self._seccion("Operadores"))
        lay.addWidget(self._tabla(
            ["Lexema", "Token", "Descripción"],
            [
                ("+", "OPERADOR",            "Suma"),
                ("-", "OPERADOR",            "Resta"),
                ("*", "OPERADOR",            "Multiplicación"),
                ("/", "OPERADOR",            "División"),
                ("%", "OPERADOR",            "Módulo"),
                ("=", "OPERADOR",            "Asignación"),
                ("!", "OPERADOR",            "Negación"),
                (">", "OPERADOR_RELACIONAL", "Mayor que"),
                ("<", "OPERADOR_RELACIONAL", "Menor que"),
            ],
            [0, 0, -1]
        ))

        lay.addWidget(self._seccion("Símbolos Especiales"))
        lay.addWidget(self._tabla(
            ["Lexema", "Token", "Descripción"],
            [
                ("{", "DELIMITADOR",      "Apertura de bloque (PROTOCOLO, REGLA, SI...)"),
                ("}", "DELIMITADOR",      "Cierre de bloque"),
                ("(", "DELIMITADOR",      "Apertura de condición o agrupación"),
                (")", "DELIMITADOR",      "Cierre de condición o agrupación"),
                (";", "FIN_SENTENCIA",    "Termina una instrucción"),
                (",", "SIMBOLO_ESPECIAL", "Separador"),
                (".", "SIMBOLO_ESPECIAL", "Acceso a atributo de entidad"),
            ],
            [0, 0, -1]
        ))
        lay.addStretch()
        return w

    # ── Pestaña: Semántica ────────────────────────────────────────────────

    def _tab_semantica(self):
        w = QWidget()
        w.setStyleSheet("background-color: #1e2030;")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(12, 8, 12, 12)
        lay.setSpacing(8)

        lay.addWidget(self._seccion("Análisis Semántico"))
        lay.addWidget(self._desc(
            "El análisis semántico valida que el programa tenga coherencia lógica. "
            "Se detiene al encontrar el primer error."
        ))

        lay.addWidget(self._seccion("Tabla de Símbolos"))
        lay.addWidget(self._desc(
            "Se construye automáticamente al procesar INGRESAR, ASIGNAR y DOSIS. "
            "Cada variable queda registrada con su identificador, tipo inferido, valor, "
            "línea, columna y ámbito (nombre de REGLA o 'global')."
        ))

        lay.addWidget(self._seccion("Tipos inferidos automáticamente"))
        lay.addWidget(self._tabla(
            ["Valor en el código", "Tipo inferido"],
            [
                ('25, 160',             "NUM_ENTERO"),
                ('37.2, 3.14',          "NUM_DECIMAL"),
                ('"Juan", "Losartan"',  "TEXTO"),
                ('verdadero, falso',    "BOOLEANO"),
                ('23-04-2024',          "FECHA"),
                ('PACIENTE, MEDICO...', "ENTIDAD_CLINICA"),
            ],
            [-1, -1]
        ))

        lay.addWidget(self._seccion("Errores Semánticos"))
        lay.addWidget(self._tabla(
            ["Código", "Error", "Cuándo ocurre"],
            [
                ("S-01", "Variable no declarada",     "Se usa un identificador que no está en la tabla"),
                ("S-02", "Redeclaración de variable", "Se intenta declarar un identificador ya existente"),
                ("S-03", "Incompatibilidad de tipos", "Se asigna un tipo diferente al original"),
                ("S-04", "Inválido en VERIFICAR",     "VALIDAR/VERIFICAR/COMPROBAR recibe id no declarado"),
                ("S-05", "Inválido en REGISTRAR",     "REGISTRAR recibe identificador no declarado"),
                ("S-06", "Tipos incompatibles",       "Operación entre tipos distintos (texto + número)"),
                ("S-07", "REGLA duplicada",           "Dos bloques REGLA tienen el mismo nombre"),
            ],
            [0, 0, -1]
        ))
        lay.addStretch()
        return w

    # ── Pestaña: Reporte ──────────────────────────────────────────────────

    def _tab_reporte(self):
        w = QWidget()
        w.setStyleSheet("background-color: #1e2030;")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(12, 8, 12, 12)
        lay.setSpacing(8)

        lay.addWidget(self._seccion("Generación de Reporte Clínico"))
        lay.addWidget(self._desc(
            "Si el programa pasa el análisis semántico sin errores, se genera automáticamente "
            "un reporte clínico en la pestaña 📄 Reporte. También puede guardarse como archivo .txt "
            "con el botón 💾 Guardar .txt."
        ))

        lay.addWidget(self._seccion("Secciones del reporte"))
        lay.addWidget(self._tabla(
            ["Sección", "Fuente", "Descripción"],
            [
                ("DATOS DEL PACIENTE", "INGRESAR + ASIGNAR", "Nombre, edad y variables declaradas"),
                ("DIAGNÓSTICO",        "DIAGNOSTICO",        "Texto del diagnóstico clínico"),
                ("TRATAMIENTO",        "TRATAMIENTO",        "Indicación terapéutica"),
                ("DOSIS",              "DOSIS",              "Medicamento, cantidad, unidad y días"),
            ],
            [0, 0, -1]
        ))

        lay.addWidget(self._seccion("Código de ejemplo para reporte completo"))
        lay.addWidget(self._mono(
            "PROTOCOLO {\n"
            "    INGRESAR nombre = \"Juan\"; edad = 48;\n"
            "    ASIGNAR presion = 160;\n"
            "    DIAGNOSTICO \"Hipertension arterial grado II\";\n"
            "    SI ( presion > 140 ) ENTONCES {\n"
            "        TRATAMIENTO \"Dieta baja en sodio\";\n"
            "        DOSIS medicamento = \"Losartan\"; cantidad = 50; unidad = \"mg\"; dias = 30;\n"
            "        REGISTRAR presion;\n"
            "    }\n"
            "    VERIFICAR PACIENTE;\n"
            "} FIN"
        ))

        lay.addWidget(self._seccion("Reporte generado"))
        lay.addWidget(self._mono(
            "╔══════════════════════════════════════╗\n"
            "║    REPORTE CLÍNICO — SISTEMA LPC     ║\n"
            "╚══════════════════════════════════════╝\n"
            "  DATOS DEL PACIENTE\n"
            "  Nombre           Juan\n"
            "  Edad             48\n"
            "  presion          160\n"
            "  ──────────────────────────────────────\n"
            "  DIAGNÓSTICO\n"
            "  Hipertension arterial grado II\n"
            "  TRATAMIENTO\n"
            "  • Dieta baja en sodio\n"
            "  DOSIS  Losartan  –  50mg  –  30 días"
        ))
        lay.addStretch()
        return w

    # ── Pestaña: Errores ──────────────────────────────────────────────────

    def _tab_errores(self):
        w = QWidget()
        w.setStyleSheet("background-color: #1e2030;")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(12, 8, 12, 12)
        lay.setSpacing(8)

        lay.addWidget(self._seccion("Errores Léxicos"))
        lay.addWidget(self._desc(
            "El analizador léxico detecta todos los errores y los reporta al finalizar. "
            "No se puede avanzar si hay errores léxicos."
        ))
        lay.addWidget(self._tabla(
            ["Tipo de Error", "Ejemplo", "Descripción"],
            [
                ("Identificador inválido", "3edad",        "Inicia con dígito en lugar de letra"),
                ("Carácter no reconocido", "@, $, ^",      "Símbolo fuera del alfabeto del lenguaje"),
                ("Cadena sin cierre",      '"sin cerrar',  "Comilla de apertura sin su cierre"),
            ],
            [-1, 0, -1]
        ))

        lay.addWidget(self._seccion("Errores Sintácticos"))
        lay.addWidget(self._desc(
            "Se detectan si el código léxicamente correcto no sigue la gramática. "
            "El análisis semántico no se ejecuta si hay errores sintácticos."
        ))
        lay.addWidget(self._mono(
            "PROTOCOLO sin {          ->  error sintáctico\n"
            "SI sin ENTONCES          ->  error sintáctico\n"
            "ASIGNAR sin =            ->  error sintáctico\n"
            "Falta } FIN al final     ->  error sintáctico"
        ))

        lay.addWidget(self._seccion("Errores Semánticos"))
        lay.addWidget(self._desc(
            "Se detectan durante el análisis semántico. "
            "El análisis se detiene en el primer error encontrado."
        ))
        lay.addWidget(self._mono(
            "REGISTRAR noExiste;           ->  S-05: no declarado\n"
            "ASIGNAR x=1; ASIGNAR x=2;    ->  S-02: redeclaración\n"
            "ASIGNAR a = \"texto\" + 5;     ->  S-06: tipos incompatibles\n"
            "REGLA r {} REGLA r {}         ->  S-07: REGLA duplicada"
        ))

        lay.addWidget(self._seccion("Alfabeto del lenguaje"))
        lay.addWidget(self._mono(
            "Letras       :  a-z  A-Z  (sin eñe)\n"
            "Dígitos      :  0 - 9\n"
            "Operadores   :  + - * / % > < = !\n"
            "Delimitadores:  ( )  { }  ;\n"
            "Cadenas      :  texto entre comillas dobles  \"...\"\n"
            "Espacios     :  ignorados (no generan token)"
        ))
        lay.addStretch()
        return w

    # ── Pestaña: Lexemas Agregados ────────────────────────────────────────

    def _tab_lexemas_extra(self):
        w = QWidget()
        w.setStyleSheet("background-color: #1e2030;")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(12, 8, 12, 12)
        lay.setSpacing(8)
        lay.addWidget(self._seccion("Lexemas Agregados por el Usuario"))
        lay.addWidget(self._desc(
            "Lexemas personalizados agregados con el botón '+ Agregar Lexema'. "
            "Los de categoría PALABRA_RESERVADA quedan disponibles en el lenguaje automáticamente."
        ))
        lexemas = cargar_lexemas_extra()
        if not lexemas:
            lay.addWidget(self._desc("No hay lexemas agregados aún. Usa el botón '+ Agregar Lexema' para añadir nuevos."))
        else:
            filas = [(l["lexema"], l["categoria"], l["descripcion"]) for l in lexemas]
            lay.addWidget(self._tabla(["Lexema", "Categoría", "Descripción"], filas, [0, 0, -1]))
        lay.addStretch()
        return w
