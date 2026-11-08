from dataclasses import dataclass
from datetime import datetime

@dataclass
class Lectura:
    animal_codigo: str
    collar_codigo: str | None
    zona_codigo: str
    hora: datetime
    origen: str
    guardarrecursos_codigo: str | None = None
