class ServicioSMS:
    """Adaptador simulado: no envía mensajes reales."""
    def __init__(self):
        self.envios = []

    def enviar(self, telefono, mensaje):
        self.envios.append((telefono, mensaje))
        print(f"SMS SIMULADO a {telefono}: {mensaje}")
