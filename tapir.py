from animal import Animal


class Tapir(Animal):
    def __init__(self, codigo: str, nombre: str):
        super().__init__(codigo, nombre, 'tapir', True)
        self.alimento = 'hojas y frutos'

    def ficha(self) -> str:
        return f"{super().ficha()} | Alimento: {self.alimento}"

    def ramonear(self) -> str:
        return 'Se alimenta de la vegetación del bosque.'

    def describir(self) -> str:
        return (
            f"{self.identificacion()}: "
            f"Come {self.alimento} y puede nadar para cruzar ríos."
        )
