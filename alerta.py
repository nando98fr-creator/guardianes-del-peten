from dataclasses import dataclass
from datetime import datetime

@dataclass
class Alerta:
    codigo: str
    tipo: str
    prioridad: str
    collar_codigo: str
    hora: datetime
    estado: str = "pendiente"
    atendida_por: str | None = None
