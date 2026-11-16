from dataclasses import dataclass, field
from typing import ClassVar


@dataclass
class Zona:
    codigo: str
    nombre: str
    tipo: str
    subzonas: list = field(default_factory=list)
    animales: list = field(default_factory=list)

    TIPOS_VALIDOS: ClassVar[tuple] = ("núcleo", "amortiguamiento", "uso múltiple")

    def __post_init__(self):
        # R5: también se valida al construir una zona que será subzona.
        if self.tipo not in self.TIPOS_VALIDOS:
            raise ValueError("Tipo de zona inválido: usa núcleo, amortiguamiento o uso múltiple.")

    def agregar_subzona(self, zona):
        self.subzonas.append(zona)

    def ubicar(self, animal):
        self.animales.append(animal)

    def mostrar(self, nivel=0):
        print(f"{'  ' * nivel}{self.nombre} [{self.tipo}] ({len(self.animales)} animales)")
        for subzona in self.subzonas:
            subzona.mostrar(nivel + 1)

    def contar_animales(self):
        total = len(self.animales)
        for subzona in self.subzonas:
            total += subzona.contar_animales()
        return total

    def buscar_sector(self, nombre):
        if self.nombre == nombre:
            return self
        for subzona in self.subzonas:
            resultado = subzona.buscar_sector(nombre)
            if resultado is not None:
                return resultado
        return None

    def buscar_codigo(self, codigo):
        """Permite que los casos GPS y avistamiento reconozcan subzonas."""
        if self.codigo == codigo:
            return self
        for subzona in self.subzonas:
            resultado = subzona.buscar_codigo(codigo)
            if resultado is not None:
                return resultado
        return None
