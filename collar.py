from dataclasses import dataclass
from datetime import datetime

@dataclass
class Collar:
    codigo: str
    bateria: float
    animal_codigo: str | None = None
