from animal import Animal


class Ocelote(Animal):
    def __init__(self, codigo: str, nombre: str):
        super().__init__(codigo, nombre, 'ocelote', False)
        self.actividad = 'nocturna'

    def ficha(self) -> str:
        return f"{super().ficha()} | Actividad: {self.actividad}"

    def acechar(self) -> str:
        return 'Acecha animales pequeños en la oscuridad.'

    def describir(self) -> str:
        return (
            f"{self.identificacion()}: "
            f"De actividad {self.actividad}, caza roedores y se refugia entre la vegetación."
        )
