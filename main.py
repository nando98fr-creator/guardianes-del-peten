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


def main():
    probar_entrega_4()
    probar_entrega_3()
    with redirect_stdout(StringIO()) as salida:
        probar_casos_previos()
    print()
    print(salida.getvalue().splitlines()[-1])


if __name__ == "__main__":
    main()
