from contextlib import redirect_stdout
from io import StringIO
from datetime import datetime, timedelta
from copy import deepcopy
from sistema_monitoreo import SistemaMonitoreo
from jaguar import Jaguar
from tapir import Tapir
from guacamaya_roja import GuacamayaRoja
from cocodrilo_de_pantano import CocodriloDePantano
from ocelote import Ocelote
from animal import Animal
from alerta import Alerta
from zona import Zona


def probar_casos_previos():
    s = SistemaMonitoreo()
    hora = datetime(2026, 9, 15, 18, 30)
    for codigo, nombre, tipo in [
        ("Z01", "Laguna del Tigre", "núcleo"),
        ("Z02", "Mirador Río Azul", "núcleo"),
        ("Z03", "Zona de amortiguamiento de ejemplo", "amortiguamiento"),
        ("Z04", "Uaxactún", "uso múltiple")]:
        assert s.agregar_zona(codigo, nombre, tipo)
    for datos in [("JAG-001", "Balam", "jaguar", True),
                  ("TAP-001", "Tziquin", "tapir", True),
                  ("GUA-001", "Ix", "guacamaya roja", True),
                  ("COC-001", "Ak", "cocodrilo de pantano", False),
                  ("OCE-001", "Mancha", "ocelote", False)]:
        assert s.registrar_animal(*datos)
    for codigo, bateria in [("COL-01", 80), ("COL-02", 5), ("COL-03", 10)]:
        assert s.agregar_collar(codigo, bateria)
    assert s.agregar_guardarrecursos("GR-07", "Mateo Chayax", "TELEFONO_DE_PRUEBA")
    assert s.establecer_turno("GR-07")
    for collar, animal in [("COL-01", "JAG-001"), ("COL-02", "TAP-001"), ("COL-03", "COC-001")]:
        assert s.asignar_collar(collar, animal)

    # Caminos felices y variantes sin alerta / con alerta alta.
    assert s.reportar_posicion("COL-01", "Z01", hora)
    assert s.reportar_posicion("COL-01", "Z04", hora + timedelta(minutes=1))
    assert len(s.servicio_sms.envios) == 1
    assert s.reportar_posicion("COL-03", "Z04", hora)
    assert len(s.servicio_sms.envios) == 1  # Cocodrilo: no está en peligro.
    assert s.registrar_avistamiento("GR-07", "OCE-001", "Z03", hora)
    assert len(s.consultar_movimientos("JAG-001")) == 2
    assert s.consultar_movimientos("GUA-001") == []

    # Toda guarda rechazada debe conservar el estado, excepto la alerta
    # de batería baja que el artículo 3 exige generar.
    rechazos = 0
    def rechazo(funcion, *args):
        nonlocal rechazos
        antes = deepcopy(s.__dict__)
        assert funcion(*args) is False
        despues = deepcopy(s.__dict__)
        # ServicioSMS es un objeto: comparar sus datos, no su identidad.
        antes["servicio_sms"] = antes["servicio_sms"].envios
        despues["servicio_sms"] = despues["servicio_sms"].envios
        assert antes == despues, "Un rechazo modificó el estado."
        rechazos += 1

    rechazo(s.registrar_animal, "jag001", "Otro", "jaguar", True)
    rechazo(s.registrar_animal, "JAG-001", "Duplicado", "jaguar", True)
    rechazo(s.registrar_animal, "TAP-002", "Otro", "tapir", False)
    rechazo(s.registrar_animal, "JAG-002", "Otro", "tapir", True)
    rechazo(s.asignar_collar, "NO-EXISTE", "JAG-001")
    rechazo(s.asignar_collar, "COL-01", "OCE-001")
    assert s.agregar_collar("COL-04", 100)  # Cuarto collar para probar animal ya equipado.
    rechazo(s.asignar_collar, "COL-04", "JAG-001")
    rechazo(s.reportar_posicion, "COL-01", "Z99", hora)
    rechazo(s.reportar_posicion, "COL-01", "Z01", hora)
    rechazo(s.reportar_posicion, "COL-04", "Z01", hora)
    rechazo(s.reportar_posicion, "NO-EXISTE", "Z01", hora)
    rechazo(s.registrar_avistamiento, "GR7", "OCE-001", "Z03", hora)
    rechazo(s.registrar_avistamiento, "GR-07", "OCE-999", "Z03", hora)
    rechazo(s.registrar_avistamiento, "GR-07", "OCE-001", "Z99", hora)
    assert s.consultar_movimientos("JAG-999") == []

    antes_lecturas = len(s.lecturas)
    antes_alertas = len(s.alertas)
    assert s.reportar_posicion("COL-02", "Z01", hora) is False
    assert len(s.lecturas) == antes_lecturas
    assert len(s.alertas) == antes_alertas + 1
    assert s.alertas[-1].prioridad == "media"
    rechazos += 1
    assert s.registrar_cambio_bateria("GR-07", "COL-02", 100, hora)
    assert s.reportar_posicion("COL-02", "Z01", hora + timedelta(minutes=2))
    rechazo(s.registrar_cambio_bateria, "GR7", "COL-02", 100, hora)
    rechazo(s.registrar_cambio_bateria, "GR-07", "COL-02", 9, hora)
    rechazo(s.registrar_cambio_bateria, "GR-07", "COL-02", 101, hora)
    rechazo(s.registrar_cambio_bateria, "GR-07", "NO-EXISTE", 100, hora)
    assert s.atender_alerta("AL-001", "GR-07")
    rechazo(s.atender_alerta, "AL-001", "GR-07")
    rechazo(s.atender_alerta, "AL-999", "GR-07")
    rechazo(s.atender_alerta, "AL-002", "GR7")
    assert s.atender_alerta("AL-002", "GR-07")
    assert s.listar_alertas_pendientes() == []
    print(f"VERIFICACIÓN COMPLETA: {rechazos} rechazos comprobados; siete casos de uso ejecutados.")


def probar_entrega_3():
    animales = [
        Jaguar('JAG-001', 'Balam'),
        Tapir('TAP-001', 'Tziquin'),
        GuacamayaRoja('GUA-001', 'Ix'),
        CocodriloDePantano('COC-001', 'Ak'),
        Ocelote('OCE-001', 'Mancha'),
    ]
    print("ENTREGA 3 | Ciclo polimórfico")
    for animal in animales:
        print(animal.describir())

    print("\nIntento de crear Animal directamente")
    try:
        Animal("ANI-001", "Prueba", "genérica", False)
    except TypeError as error:
        print(f"{type(error).__name__}: {error}")
    else:
        raise AssertionError("Animal debe ser abstracta.")



def probar_entrega_4():
    sistema = SistemaMonitoreo()
    hora_base = datetime(2026, 11, 7, 8)
    for codigo, prioridad, minutos in [
        ("AL-001", "media", 30),
        ("AL-002", "alta", 45),
        ("AL-003", "media", 10),
        ("AL-004", "alta", 15),
        ("AL-005", "media", 20),
    ]:
        tipo = "batería baja" if prioridad == "media" else "acercamiento a comunidad"
        sistema.alertas.append(
            Alerta(codigo, tipo, prioridad, "COL-01", hora_base + timedelta(minutes=minutos))
        )

    def imprimir_alertas(titulo):
        print(titulo)
        for alerta in sistema.alertas:
            print(f"  {alerta.codigo} | {alerta.prioridad:<5} | {alerta.hora:%H:%M}")

    print("\nENTREGA 4 · ORDENAMIENTO POR SELECCIÓN")
    imprimir_alertas("Antes de ordenar:")
    sistema.ordenar_alertas()
    imprimir_alertas("Después de ordenar:")
    assert [alerta.codigo for alerta in sistema.alertas] == [
        "AL-004", "AL-002", "AL-003", "AL-005", "AL-001",
    ]

    print("\nENTREGA 4 · BÚSQUEDA BINARIA")
    for datos in [
        ("TAP-002", "Tziquin", "tapir", True),
        ("JAG-001", "Balam", "jaguar", True),
        ("COC-001", "Ak", "cocodrilo de pantano", False),
    ]:
        assert sistema.registrar_animal(*datos)

    for codigo, esperado in [("COC-001", "Ak"), ("TAP-002", "Tziquin"), ("JAG-999", None)]:
        resultado = sistema.buscar_animal(codigo)
        print(f"  {codigo} -> {resultado}")
        if esperado is None:
            assert resultado is None
        else:
            assert resultado is not None
            assert (resultado.codigo, resultado.nombre) == (codigo, esperado)

    assert [animal.codigo for animal in sistema.animales] == [
        "COC-001", "JAG-001", "TAP-002",
    ]
    print("Pruebas de la Entrega 4 completadas.")


def probar_entrega_5():
    sistema = SistemaMonitoreo()
    print("ENTREGA 5 | RECURSIVIDAD: ZONAS DENTRO DE ZONAS")
    # Tres niveles bajo la reserva: zona -> sector -> aguada.
    mapa = [
        ("Z01", "Laguna del Tigre", "núcleo", None),
        ("Z02", "Sector El Ceibal", "núcleo", "Z01"),
        ("Z03", "Aguada El Ceibal", "núcleo", "Z02"),
        ("Z04", "Sector Los Cedros", "núcleo", "Z01"),
        ("Z05", "Mirador Río Azul", "núcleo", None),
        ("Z06", "Sector La Caoba", "núcleo", "Z05"),
        ("Z07", "Uaxactún", "uso múltiple", None),
    ]
    for datos in mapa:
        assert sistema.agregar_zona(*datos)

    # Una sola ubicación por animal en esta demostración.
    with redirect_stdout(StringIO()):
        for datos in [
            ("JAG-001", "Balam", "jaguar", True),
            ("TAP-001", "Tziquin", "tapir", True),
            ("GUA-001", "Ix", "guacamaya roja", True),
            ("COC-001", "Ak", "cocodrilo de pantano", False),
            ("OCE-001", "Mancha", "ocelote", False),
        ]:
            assert sistema.registrar_animal(*datos)
    ubicaciones = [
        ("JAG-001", "Laguna del Tigre"),
        ("TAP-001", "Sector El Ceibal"),
        ("GUA-001", "Aguada El Ceibal"),
        ("COC-001", "Sector Los Cedros"),
        ("OCE-001", "Sector La Caoba"),
    ]
    for codigo, nombre_zona in ubicaciones:
        animal = sistema.buscar_animal(codigo)
        zona = sistema.buscar_sector(nombre_zona)
        assert animal is not None and zona is not None
        zona.ubicar(animal)

    print("\nMAPA COMPLETO (7 zonas)")
    sistema.mostrar()
    print("\nUBICACIONES")
    for codigo, nombre_zona in ubicaciones:
        print(f"  {sistema.buscar_animal(codigo).nombre} -> {nombre_zona}")

    laguna = sistema.buscar_sector("Laguna del Tigre")
    print(f"\nAnimales en toda la reserva: {sistema.contar_animales()}")
    print(f"Animales en Laguna del Tigre y sus sectores: {laguna.contar_animales()}")
    assert sistema.contar_animales() == 5
    assert laguna.contar_animales() == 4
    assert sistema.buscar_sector("Aguada El Ceibal").contar_animales() == 1

    print("\nBUSQUEDAS (profundo, primer nivel, inexistente)")
    for nombre in ["Aguada El Ceibal", "Laguna del Tigre", "Sector Fantasma"]:
        resultado = sistema.buscar_sector(nombre)
        if resultado is None:
            print(f"  {nombre} -> None")
        else:
            print(f"  {nombre} -> Zona(codigo={resultado.codigo}, nombre={resultado.nombre}, tipo={resultado.tipo})")
    assert sistema.buscar_sector("Aguada El Ceibal") is sistema.buscar_zona_codigo("Z03")
    assert sistema.buscar_sector("Laguna del Tigre") is sistema.zonas[0]
    assert sistema.buscar_sector("Sector Fantasma") is None
    print("Pruebas de la Entrega 5 completadas.\n")


def probar_integracion_zonas():
    # Listas independientes y casos base de un árbol vacío/una hoja.
    a = Zona("A", "Hoja A", "núcleo")
    b = Zona("B", "Hoja B", "núcleo")
    assert a.subzonas is not b.subzonas and a.animales is not b.animales
    assert a.contar_animales() == 0
    assert a.buscar_sector("Hoja A") is a
    assert a.buscar_sector("Ausente") is None
    vacio = SistemaMonitoreo()
    assert vacio.contar_animales() == 0 and vacio.buscar_sector("Ausente") is None
    try:
        Zona("X", "Inválida", "sector")
    except ValueError:
        pass
    else:
        raise AssertionError("R5 debe rechazar un tipo inválido.")
    s = SistemaMonitoreo()
    assert s.agregar_zona("Z01", "Raíz", "núcleo")
    assert s.agregar_zona("Z02", "Sector", "uso múltiple", "Z01")
    assert not s.agregar_zona("Z03", "Inválida", "sector", "Z01")
    assert not s.agregar_zona("Z02", "Repetida", "núcleo")
    assert not s.agregar_zona("Z04", "Sin padre", "núcleo", "Z99")
    assert len(s.zonas) == 1 and len(s.zonas[0].subzonas) == 1
    assert s.registrar_animal("JAG-001", "Balam", "jaguar", True)
    assert s.agregar_collar("COL-01", 80)
    assert s.asignar_collar("COL-01", "JAG-001")
    assert s.agregar_guardarrecursos("GR-07", "Mateo", "TELEFONO_DE_PRUEBA")
    assert s.establecer_turno("GR-07")
    assert s.reportar_posicion("COL-01", "Z02", datetime(2026, 11, 15, 8))
    assert len(s.servicio_sms.envios) == 1
    assert s.registrar_avistamiento("GR-07", "JAG-001", "Z02", datetime(2026, 11, 15, 9))
    assert len(s.lecturas) == 2


def probar_entrega_6():
    sistema = SistemaMonitoreo()
    hora = datetime(2026, 11, 22, 8)
    with redirect_stdout(StringIO()):
        assert sistema.agregar_zona("Z01", "Uaxactún", "uso múltiple")
        assert sistema.agregar_guardarrecursos("GR-07", "Mateo", "TELEFONO_DE_PRUEBA")
        assert sistema.establecer_turno("GR-07")
        assert sistema.registrar_animal("JAG-001", "Balam", "jaguar", True)
        assert sistema.registrar_animal("TAP-001", "Tziquin", "tapir", True)
        assert sistema.agregar_collar("COL-01", 5)
        assert sistema.agregar_collar("COL-02", 80)
        assert sistema.asignar_collar("COL-01", "JAG-001")
        assert sistema.asignar_collar("COL-02", "TAP-001")

    print("ENTREGA 6 | COLA FIFO Y BITACORA LIFO")
    print("\n1. GENERAR CUATRO ALERTAS (orden de llegada)")
    with redirect_stdout(StringIO()):
        assert sistema.reportar_posicion("COL-01", "Z01", hora) is False
        assert sistema.reportar_posicion("COL-02", "Z01", hora + timedelta(minutes=1))
        assert sistema.reportar_posicion("COL-01", "Z01", hora + timedelta(minutes=2)) is False
        assert sistema.reportar_posicion("COL-02", "Z01", hora + timedelta(minutes=3))
    for alerta in sistema.alertas:
        print(f"  {alerta.codigo}: {alerta.tipo}, {alerta.prioridad}, {alerta.hora:%H:%M}")
    print(f"En la cola: {sistema.cola_alertas.tamanio()}")
    print(f"Siguiente: {sistema.cola_alertas.siguiente().codigo}")
    assert sistema.cola_alertas.tamanio() == 4
    assert sistema.cola_alertas.siguiente() is sistema.alertas[0]

    print("\n2. ATENDER DOS ALERTAS")
    primera = sistema.atender_siguiente_alerta("GR-07")
    segunda = sistema.atender_siguiente_alerta("GR-07")
    print(f"Salieron en orden: {primera.codigo}, {segunda.codigo}")
    print(f"Quedan: {sistema.cola_alertas.tamanio()}")
    assert [primera.codigo, segunda.codigo] == ["AL-001", "AL-002"]
    assert primera.estado == segunda.estado == "atendida"
    assert primera.atendida_por == segunda.atendida_por == "GR-07"
    assert sistema.cola_alertas.siguiente().codigo == "AL-003"

    print("\n3. REGISTRAR CUATRO ENTRADAS Y DESHACER LA ULTIMA")
    for entrada in ["Inicié la patrulla en Uaxactún",
                    "Revisé la aguada Los Patos",
                    "Verifiqué los collares del sector",
                    "Cerré la patrulla (anotación equivocada)"]:
        sistema.bitacora.registrar(entrada)
    print(f"Deshecha: {sistema.bitacora.deshacer()}")
    assert sistema.bitacora.ultima() == "Verifiqué los collares del sector"
    print("Bitácora, de la más reciente a la más antigua:")
    sistema.bitacora.mostrar()

    print("\n4. VACIAR LA COLA Y ATENDER UNA VEZ MAS")
    restantes = []
    while not sistema.cola_alertas.esta_vacia():
        restantes.append(sistema.atender_siguiente_alerta("GR-07").codigo)
    assert restantes == ["AL-003", "AL-004"]
    print(f"En la cola: {sistema.cola_alertas.tamanio()}")
    resultado = sistema.atender_siguiente_alerta("GR-07")
    print(f"Resultado de la llamada extra: {resultado}")
    assert resultado is None
    assert all(a.estado == "atendida" for a in sistema.alertas)
    assert len(sistema.alertas) == 4  # El historial se conserva.
    print("Pruebas de la Entrega 6 completadas.\n")


def main():
    probar_entrega_6()
    probar_entrega_5()
    with redirect_stdout(StringIO()):
        probar_integracion_zonas()
    print("Integración: R5, listas independientes, GPS y avistamientos en subzonas: OK.\n")
    probar_entrega_4()
    probar_entrega_3()
    with redirect_stdout(StringIO()) as salida:
        probar_casos_previos()
    print()
    print(salida.getvalue().splitlines()[-1])


if __name__ == "__main__":
    main()
