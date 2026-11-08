from animal import Animal


class GuacamayaRoja(Animal):
    def __init__(self, codigo: str, nombre: str):
        super().__init__(codigo, nombre, 'guacamaya roja', True)
        self.refugio = 'copas de los árboles'

    def ficha(self) -> str:
        return f"{super().ficha()} | Refugio: {self.refugio}"

    def volar(self) -> str:
        return 'Vuela entre las copas en busca de alimento.'

    def describir(self) -> str:
        return (
            f"{self.identificacion()}: "
            f"Vuela sobre el bosque y come frutos y semillas en las {self.refugio}."
        )
