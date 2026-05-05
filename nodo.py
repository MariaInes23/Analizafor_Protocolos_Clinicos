class Nodo:
    def __init__(self, etiqueta):
        self.etiqueta = etiqueta
        self.hijos = []

    def agregar_hijo(self, hijo):
        self.hijos.append(hijo)
        return hijo

    def hoja(self, etiqueta):
        n = Nodo(etiqueta)
        self.hijos.append(n)
        return n

    def a_texto(self, prefijo="", es_ultimo=True):
        conector = "└── " if es_ultimo else "├── "
        lineas = [prefijo + conector + self.etiqueta]
        extension = "    " if es_ultimo else "│   "
        for i, hijo in enumerate(self.hijos):
            ultimo = (i == len(self.hijos) - 1)
            lineas.append(hijo.a_texto(prefijo + extension, ultimo))
        return "\n".join(lineas)

    def __str__(self):
        if not self.hijos:
            return self.etiqueta
        lineas = [self.etiqueta]
        for i, hijo in enumerate(self.hijos):
            ultimo = (i == len(self.hijos) - 1)
            lineas.append(hijo.a_texto("", ultimo))
        return "\n".join(lineas)
