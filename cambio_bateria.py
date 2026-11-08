from dataclasses import dataclass
from datetime import datetime

@dataclass
class CambioBateria:
    collar_codigo: str
    guardarrecursos_codigo: str
    nivel_anterior: float
    nivel_nuevo: float
    hora: datetime
