from animal import Animal


class Jaguar(Animal):
    def __init__(self, codigo: str, nombre: str):
        super().__init__(codigo, nombre, 'jaguar', True)
        self.presas = 'venados y pecaríes'

    def ficha(self) -> str:
        return f"{super().ficha()} | Presas: {self.presas}"

    def rastrear(self) -> str:
        return 'Acecha presas entre la vegetación.'

    def describir(self) -> str:
        return (
            f"{self.identificacion()}: "
            f"Caza {self.presas} y se desplaza por el bosque y cerca de ríos."
        )
