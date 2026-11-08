import re
import math
import unicodedata
from datetime import datetime
from jaguar import Jaguar
from tapir import Tapir
from guacamaya_roja import GuacamayaRoja
from cocodrilo_de_pantano import CocodriloDePantano
from ocelote import Ocelote
from collar import Collar
from zona import Zona
from guardarrecursos import Guardarrecursos
from lectura import Lectura
from alerta import Alerta
from cambio_bateria import CambioBateria
from servicio_sms import ServicioSMS


class SistemaMonitoreo:
    # Catálogo cerrado para esta entrega. Ocelote: decisión del ejercicio.
    ESPECIES = {"jaguar": True, "tapir": True,
                "guacamaya roja": True, "cocodrilo de pantano": False,
                "ocelote": False}
    CLASES_ANIMALES = {
        'jaguar': Jaguar,
        'tapir': Tapir,
        'guacamaya roja': GuacamayaRoja,
        'cocodrilo de pantano': CocodriloDePantano,
        'ocelote': Ocelote,
    }
    TIPOS = ("núcleo", "amortiguamiento", "uso múltiple")

    def __init__(self):
        self.animales = []
        self.collares = []
        self.zonas = []
        self.guardarrecursos = []
        self.lecturas = []
        self.alertas = []
        self.cambios_bateria = []
        self.servicio_sms = ServicioSMS()
        self.turno_codigo = None

    @staticmethod
    def _ordenar_por_seleccion(elementos, clave):
        """Ordena en la misma lista, con un intercambio como máximo por pasada."""
        for inicio in range(len(elementos) - 1):
            menor = inicio
            for candidato in range(inicio + 1, len(elementos)):
                if clave(elementos[candidato]) < clave(elementos[menor]):
                    menor = candidato
            if menor != inicio:
                elementos[inicio], elementos[menor] = elementos[menor], elementos[inicio]

    def ordenar_alertas(self):
        def nivel(alerta):
            if alerta.prioridad == "alta":
                return 1
            return 2

        self._ordenar_por_seleccion(
            self.alertas, lambda alerta: (nivel(alerta), alerta.hora)
        )

    def buscar_animal(self, codigo):
        self._ordenar_por_seleccion(self.animales, lambda animal: animal.codigo)
        inicio = 0
        fin = len(self.animales) - 1

        while inicio <= fin:
            medio = (inicio + fin) // 2
            animal = self.animales[medio]
            if animal.codigo == codigo:
                return animal
            if animal.codigo < codigo:
                inicio = medio + 1
            else:
                fin = medio - 1

        return None

    def buscar(self, objetos, codigo):
        for objeto in objetos:
            if objeto.codigo == codigo:
                return objeto
        return None

    def rechazar(self, mensaje):
        print(f"RECHAZADO: {mensaje}")
        return False

    def articulo_1(self, codigo, especie):
        if not isinstance(codigo, str) or not re.fullmatch(r"[A-Z]{3}-[0-9]{3}", codigo):
            return self.rechazar("Código animal inválido; usa JAG-001.")
        prefijo = unicodedata.normalize("NFKD", especie[:3]).encode("ascii", "ignore").decode().upper()
        if codigo[:3] != prefijo:
            return self.rechazar("El prefijo debe coincidir con las primeras tres letras de la especie.")
        if self.buscar(self.animales, codigo):
            return self.rechazar("Código animal repetido.")
        return True

    def articulo_2(self, especie, en_peligro):
        if especie not in self.ESPECIES:
            return self.rechazar("Especie fuera del catálogo de esta entrega.")
        if type(en_peligro) is not bool or en_peligro != self.ESPECIES[especie]:
            return self.rechazar("Estado de conservación incompatible con el catálogo del ejercicio.")
        return True

    def nivel_valido(self, nivel):
        return type(nivel) in (int, float) and math.isfinite(nivel) and 0 <= nivel <= 100

    def articulo_3(self, collar, hora):
        if not self.nivel_valido(collar.bateria):
            return self.rechazar("Nivel de batería fuera de 0 a 100.")
        if collar.bateria < 10:
            self.crear_alerta("batería baja", "media", collar, hora)
            return self.rechazar("Batería menor de 10 %; lectura no guardada.")
        return True

    def articulo_4(self, collar, animal):
        if collar.animal_codigo is not None:
            return self.rechazar(f"Collar ocupado por {collar.animal_codigo}.")
        for otro in self.collares:
            if otro.animal_codigo == animal.codigo:
                return self.rechazar(f"El animal ya lleva el collar {otro.codigo}.")
        return True

    def articulo_5(self, codigo_zona):
        if not self.buscar(self.zonas, codigo_zona):
            return self.rechazar("Zona no registrada.")
        return True

    def requiere_alerta_comunidad(self, animal, zona):
        return animal.en_peligro and zona.tipo == "uso múltiple"

    def articulo_6(self, animal, zona, collar, hora):
        if self.requiere_alerta_comunidad(animal, zona):
            alerta = self.crear_alerta("acercamiento a comunidad", "alta", collar, hora)
            responsable = self.buscar(self.guardarrecursos, self.turno_codigo)
            self.servicio_sms.enviar(responsable.telefono,
                f"{alerta.codigo}: {animal.codigo} en {zona.nombre}")

    def articulo_7(self, codigo):
        if not isinstance(codigo, str) or not re.fullmatch(r"[A-Z]{2}-[0-9]{2}", codigo):
            return self.rechazar("Código de guardarrecursos inválido; usa GR-07.")
        return True

    def responsable_valido(self, codigo):
        if not self.articulo_7(codigo):
            return False
        if not self.buscar(self.guardarrecursos, codigo):
            return self.rechazar("Guardarrecursos no registrado.")
        return True

    def articulo_8(self, alerta):
        if alerta.estado != "pendiente":
            return self.rechazar(f"La alerta ya fue atendida por {alerta.atendida_por}.")
        return True

    def articulo_9(self, codigo_guardarrecursos, nivel):
        if not self.responsable_valido(codigo_guardarrecursos):
            return False
        if not self.nivel_valido(nivel) or nivel < 10:
            return self.rechazar("La batería nueva debe estar entre 10 y 100 %.")
        return True

    def articulo_10(self, collar_codigo, hora):
        for lectura in self.lecturas:
            if lectura.origen == "GPS" and lectura.collar_codigo == collar_codigo and lectura.hora == hora:
                return self.rechazar("Lectura GPS repetida para el mismo collar y hora.")
        return True

    def hora_valida(self, hora):
        if not isinstance(hora, datetime):
            return self.rechazar("La hora debe ser un objeto datetime.")
        return True

    # Métodos auxiliares para la carga inicial, no metas adicionales del diagrama.
    def agregar_zona(self, codigo, nombre, tipo):
        if tipo not in self.TIPOS or self.buscar(self.zonas, codigo):
            return self.rechazar("Tipo de zona inválido o código repetido.")
        self.zonas.append(Zona(codigo, nombre, tipo))
        return True

    def agregar_collar(self, codigo, bateria):
        if not self.nivel_valido(bateria) or self.buscar(self.collares, codigo):
            return self.rechazar("Batería inválida o collar repetido.")
        self.collares.append(Collar(codigo, bateria))
        return True

    def agregar_guardarrecursos(self, codigo, nombre, telefono):
        if not self.articulo_7(codigo):
            return False
        if self.buscar(self.guardarrecursos, codigo):
            return self.rechazar("Guardarrecursos repetido.")
        self.guardarrecursos.append(Guardarrecursos(codigo, nombre, telefono))
        return True

    def establecer_turno(self, codigo):
        if not self.responsable_valido(codigo):
            return False
        self.turno_codigo = codigo
        return True

    def registrar_animal(self, codigo, nombre, especie, en_peligro):
        if not isinstance(especie, str):
            return self.rechazar("Especie inválida.")
        if not self.articulo_1(codigo, especie):
            return False
        if not self.articulo_2(especie, en_peligro):
            return False
        clase_animal = self.CLASES_ANIMALES[especie]
        self.animales.append(clase_animal(codigo, nombre))
        print(f"Animal registrado: {codigo}")
        return True

    def asignar_collar(self, codigo_collar, codigo_animal):
        collar = self.buscar(self.collares, codigo_collar)
        animal = self.buscar(self.animales, codigo_animal)
        if collar is None or animal is None:
            return self.rechazar("No existe el collar o el animal.")
        if not self.articulo_4(collar, animal):
            return False
        collar.animal_codigo = animal.codigo
        print(f"Collar {collar.codigo} asignado a {animal.codigo}.")
        return True

    def crear_alerta(self, tipo, prioridad, collar, hora):
        alerta = Alerta(f"AL-{len(self.alertas)+1:03d}", tipo, prioridad, collar.codigo, hora)
        self.alertas.append(alerta)
        print(f"Alerta pendiente: {alerta.codigo}, {tipo}, prioridad {prioridad}.")
        return alerta

    def reportar_posicion(self, codigo_collar, codigo_zona, hora):
        collar = self.buscar(self.collares, codigo_collar)
        if collar is None:
            return self.rechazar("Collar no registrado.")
        if not self.hora_valida(hora):
            return False
        if not self.articulo_3(collar, hora):
            return False
        if not self.articulo_5(codigo_zona):
            return False
        animal = self.buscar(self.animales, collar.animal_codigo)
        if animal is None:
            return self.rechazar("El collar no tiene animal asignado.")
        zona = self.buscar(self.zonas, codigo_zona)
        if not self.articulo_10(codigo_collar, hora):
            return False
        if self.requiere_alerta_comunidad(animal, zona) and not self.buscar(self.guardarrecursos, self.turno_codigo):
            return self.rechazar("Configura un guardarrecursos de turno antes de procesar esta lectura.")
        self.lecturas.append(Lectura(animal.codigo, collar.codigo, zona.codigo, hora, "GPS"))
        self.articulo_6(animal, zona, collar, hora)
        print("Lectura GPS registrada.")
        return True

    def registrar_avistamiento(self, codigo_guardarrecursos, codigo_animal, codigo_zona, hora):
        if not self.responsable_valido(codigo_guardarrecursos):
            return False
        if not self.buscar(self.animales, codigo_animal):
            return self.rechazar("Animal no registrado.")
        if not self.articulo_5(codigo_zona) or not self.hora_valida(hora):
            return False
        self.lecturas.append(Lectura(codigo_animal, None, codigo_zona, hora, "avistamiento", codigo_guardarrecursos))
        print("Avistamiento registrado.")
        return True

    def listar_alertas_pendientes(self):
        pendientes = []
        for alerta in self.alertas:
            if alerta.estado == "pendiente":
                pendientes.append(alerta)
                print(f"{alerta.codigo}: {alerta.tipo}, {alerta.prioridad}")
        if not pendientes:
            print("No hay alertas pendientes.")
        return pendientes

    def atender_alerta(self, codigo_alerta, codigo_guardarrecursos):
        self.listar_alertas_pendientes()
        if not self.responsable_valido(codigo_guardarrecursos):
            return False
        alerta = self.buscar(self.alertas, codigo_alerta)
        if alerta is None:
            return self.rechazar("Alerta no registrada.")
        if not self.articulo_8(alerta):
            return False
        alerta.estado = "atendida"
        alerta.atendida_por = codigo_guardarrecursos
        print(f"Alerta {alerta.codigo} atendida por {codigo_guardarrecursos}.")
        return True

    def consultar_movimientos(self, codigo_animal):
        if not self.buscar(self.animales, codigo_animal):
            self.rechazar("Animal no registrado.")
            return []
        movimientos = []
        for lectura in self.lecturas:
            if lectura.animal_codigo == codigo_animal:
                movimientos.append(lectura)
        for lectura in movimientos:
            print(f"{lectura.hora.isoformat()} | {lectura.zona_codigo} | {lectura.origen}")
        if not movimientos:
            print("El animal no tiene movimientos registrados.")
        return movimientos

    def registrar_cambio_bateria(self, codigo_guardarrecursos, codigo_collar, nuevo_nivel, hora):
        if not self.articulo_9(codigo_guardarrecursos, nuevo_nivel):
            return False
        collar = self.buscar(self.collares, codigo_collar)
        if collar is None:
            return self.rechazar("Collar no registrado.")
        if not self.hora_valida(hora):
            return False
        cambio = CambioBateria(collar.codigo, codigo_guardarrecursos, collar.bateria, nuevo_nivel, hora)
        collar.bateria = nuevo_nivel
        self.cambios_bateria.append(cambio)
        print(f"Cambio registrado: {collar.codigo}, batería {nuevo_nivel} %.")
        return True
