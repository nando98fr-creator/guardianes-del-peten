from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Animal(ABC):
    codigo: str
    nombre: str
    especie: str
    en_peligro: bool

    def identificacion(self) -> str:
        return f"{self.codigo} | {self.nombre}"

    def ficha(self) -> str:
        return f"{self.identificacion()} | {self.especie}"

    @abstractmethod
    def describir(self) -> str:
        """Devuelve una descripción propia de la especie."""
        raise NotImplementedError
