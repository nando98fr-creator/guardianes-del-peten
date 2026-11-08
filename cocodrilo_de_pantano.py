from animal import Animal


class CocodriloDePantano(Animal):
    def __init__(self, codigo: str, nombre: str):
        super().__init__(codigo, nombre, 'cocodrilo de pantano', False)
        self.habitat = 'lagunas y pantanos'

    def ficha(self) -> str:
        return f"{super().ficha()} | Habitat: {self.habitat}"

    def sumergirse(self) -> str:
        return 'Se desplaza nadando bajo la superficie.'

    def describir(self) -> str:
        return (
            f"{self.identificacion()}: "
            f"Habita en {self.habitat} y captura peces y otras presas."
        )
