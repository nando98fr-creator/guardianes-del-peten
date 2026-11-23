# Guardianes del Petén · Entrega 6

|Dato|Valor|
|-|-|
|Estudiante|Erick Fernando España Ruiz|
|Carné|202201376|
|Grupo|Grupo\_2|
|Fecha|22 de noviembre de 2026|

La Entrega 6 incorpora una cola FIFO de alertas y una pila LIFO para la bitácora de patrulla. Conserva las funciones y las pruebas de las Entregas 1 a 5.

## Ejecución en Windows

Extraer el ZIP. Abrir la carpeta `guardianes-del-peten`, donde está `main.py`. En la barra de dirección del Explorador escribir `cmd` y presionar Enter. Ejecutar:

```bat
py main.py
```

También funciona `python main.py` o `python3 main.py` en Linux. Requiere Python 3.10 o superior, sin paquetes externos. No usar `-O`, porque las comprobaciones usan `assert`.

El programa ejecuta primero las pruebas de la Entrega 6, después la recursividad de la Entrega 5 y finalmente las verificaciones de las entregas anteriores. El `TypeError` al intentar crear `Animal` es una prueba controlada de su carácter abstracto y el programa continúa.

Para ejecutar siete pruebas adicionales de comportamiento:

```bat
py -m unittest -v test\_entrega\_6.py
```

## Cola de alertas y bitácora

`ColaAlertas` encapsula una lista: `encolar()` agrega al final, `atender()` extrae el frente y `siguiente()` consulta el frente sin retirarlo. `esta\_vacia()` y `tamanio()` consultan su estado. Atender o consultar una cola vacía devuelve `None`. Con una lista, extraer el frente desplaza los elementos y cuesta O(n).

`BitacoraPatrulla` encapsula otra lista: `registrar()` apila un texto, `deshacer()` devuelve y retira la última entrada, y `ultima()` la consulta sin retirarla. `mostrar()` imprime desde la más reciente hasta la más antigua. Consultar o deshacer una pila vacía devuelve `None`. Deshacer una anotación solo elimina ese texto, no revierte la atención de una alerta.

`SistemaMonitoreo` crea sus propias instancias `cola\_alertas` y `bitacora`. `crear\_alerta()` conserva cada alerta en el historial y también encola el mismo objeto. Esto cubre las alertas por batería baja y acercamiento a comunidad. El código externo usa los métodos de las clases, sin acceder a sus listas internas.

`atender\_siguiente\_alerta(codigo\_guardarrecursos)` valida al responsable antes de retirar la alerta. Aplica R8, la marca como atendida, guarda al responsable y registra el hecho en la bitácora. Devuelve el objeto atendido. Con la cola vacía imprime exactamente `No hay alertas por atender` y devuelve `None`.

La atención por código de las entregas anteriores permanece disponible. Si una alerta ya fue atendida por ese método, la atención FIFO descarta su referencia cuando llega al frente y R8 evita atenderla de nuevo. No vuelve a registrarla como una nueva atención.

Ordenar el historial por prioridad conserva la función de la Entrega 4, pero no reordena la cola: FIFO depende del orden de llegada.

## Pruebas de la Entrega 6

Las anotaciones y los datos de los animales corresponden a una demostración del programa.

|Paso|Evidencia esperada y comprobada|
|-|-|
|Generar cuatro alertas por las funciones del sistema|AL-001, AL-002, AL-003 y AL-004. Dos de batería y dos de comunidad|
|Consultar la cola|Tamaño 4 y siguiente AL-001|
|Atender dos|Salen AL-001 y AL-002, en ese orden. Quedan 2|
|Registrar cuatro entradas y deshacer una|Se elimina «Cerré la patrulla (anotación equivocada)»|
|Mostrar la bitácora|Tres anotaciones manuales y las dos atenciones, desde la más reciente|
|Vaciar la cola|Salen AL-003 y AL-004|
|Llamada extra|Mensaje de cola vacía y resultado None|

Los tests adicionales cubren FIFO frente a prioridad, LIFO, consultas sin extracción, listas independientes, responsable inválido sin cambios, conservación del historial, R8 y estructuras vacías.

## Zonas recursivas

`SistemaMonitoreo.zonas` contiene solamente las zonas de primer nivel. Cada `Zona` tiene listas independientes `subzonas` y `animales`, creadas con `default\_factory=list`. No se usa una lista plana para resolver las operaciones recursivas.

* `agregar\_subzona(zona)` y `ubicar(animal)` agregan a sus respectivas listas.
* `mostrar(nivel=0)` imprime dos espacios por nivel y llama a `subzona.mostrar(nivel + 1)`.
* `contar\_animales()` comienza con los animales locales y suma el resultado de cada subzona.
* `buscar\_sector(nombre)` devuelve `self` si coincide; de lo contrario recorre las subzonas recursivamente y devuelve la primera coincidencia o `None`.
* La clase central muestra las raíces, suma sus conteos y consulta sus búsquedas.

Una hoja termina el recorrido porque no tiene subzonas. La búsqueda también termina cuando encuentra el nombre. Si hay nombres repetidos, se devuelve la primera coincidencia en profundidad, según el orden de inserción.

Los tipos siguen siendo `núcleo`, `amortiguamiento` y `uso múltiple`. Sector y aguada son niveles/nombres, no tipos nuevos. `Zona.\_\_post\_init\_\_` valida el tipo incluso en objetos destinados a ser subzonas. La carga mediante `agregar\_zona(..., codigo\_padre=None)` conserva los rechazos anteriores y comprueba el padre y los códigos repetidos. La guarda de zona registrada y los casos GPS/avistamiento ahora encuentran códigos en cualquier nivel mediante `buscar\_codigo()`.

El modelo se usa como un árbol: no agregar una zona dentro de sí misma, ni repetir el mismo objeto bajo varios padres. `ubicar()` solo agrega: la prueba ubica a cada animal una vez; no implementa traslados automáticos ni deduplicación.

## Pruebas de la Entrega 5

El mapa tiene siete zonas y tres niveles bajo la reserva: zona → sector → aguada. Cinco animales se reparten en los tres niveles, con Ix en Aguada El Ceibal.

|Prueba|Resultado esperado y comprobado|
|-|-|
|Toda la reserva|5 animales|
|Laguna del Tigre y sus subzonas|4 animales|
|Aguada El Ceibal|1 animal|
|Buscar Aguada El Ceibal (nivel profundo)|Objeto Zona con código Z03|
|Buscar Laguna del Tigre (primer nivel)|Objeto Zona con código Z01|
|Buscar Sector Fantasma|None|

También se comprueban árboles vacíos, hojas, listas independientes, tipo inválido, código repetido, padre inexistente y GPS/avistamiento dentro de una subzona. Las pruebas anteriores comprueban selección, búsqueda binaria, polimorfismo y 22 rechazos de los siete casos de uso.

En la Entrega 4, la selección ordena alertas por prioridad (alta antes que media) y hora. La búsqueda binaria ordena primero los animales por código mediante selección; la búsqueda sobre esa lista es logarítmica y su preparación es cuadrática.

## Diagrama de clases

```mermaid
classDiagram
    class SistemaMonitoreo {
        +list animales
        +list alertas
        +list zonas
        +ColaAlertas cola\_alertas
        +BitacoraPatrulla bitacora
        +crear\_alerta(tipo, prioridad, collar, hora) Alerta
        +atender\_siguiente\_alerta(codigo\_guardarrecursos) Alerta\_o\_None
        +mostrar()
        +contar\_animales() int
        +buscar\_sector(nombre) Zona\_o\_None
        +buscar\_zona\_codigo(codigo) Zona\_o\_None
        +agregar\_zona(codigo, nombre, tipo, codigo\_padre) bool
        +ordenar\_alertas()
        +buscar\_animal(codigo) Animal\_o\_None
        -\_ordenar\_por\_seleccion(elementos, clave)
    }
    class ColaAlertas {
        -list \_alertas
        +encolar(alerta)
        +atender() Alerta\_o\_None
        +siguiente() Alerta\_o\_None
        +esta\_vacia() bool
        +tamanio() int
    }
    class BitacoraPatrulla {
        -list \_entradas
        +registrar(entrada)
        +deshacer() str\_o\_None
        +ultima() str\_o\_None
        +esta\_vacia() bool
        +mostrar()
    }
    SistemaMonitoreo "1" \*-- "1" ColaAlertas : cola\_alertas
    SistemaMonitoreo "1" \*-- "1" BitacoraPatrulla : bitacora
    ColaAlertas o-- Alerta : pendientes en FIFO
    class Zona {
        +str codigo
        +str nombre
        +str tipo
        +list subzonas
        +list animales
        +agregar\_subzona(zona)
        +ubicar(animal)
        +mostrar(nivel=0)
        +contar\_animales() int
        +buscar\_sector(nombre) Zona\_o\_None
        +buscar\_codigo(codigo) Zona\_o\_None
    }
    Zona "1" o-- "0..\*" Zona : subzonas
    Zona "1" o-- "0..\*" Animal : animales ubicados
    class Animal {
        +str codigo
        +str nombre
        +str especie
        +bool en\_peligro
        +identificacion() str
        +ficha() str
        +describir()\* str
    }
    <<abstract>> Animal
    class Jaguar {
        +describir() str
    }
    class Tapir {
        +describir() str
    }
    class GuacamayaRoja {
        +describir() str
    }
    class CocodriloDePantano {
        +describir() str
    }
    class Ocelote {
        +describir() str
    }
    Animal <|-- Jaguar
    Animal <|-- Tapir
    Animal <|-- GuacamayaRoja
    Animal <|-- CocodriloDePantano
    Animal <|-- Ocelote
    class Alerta {
        +str codigo
        +str prioridad
        +datetime hora
        +str estado
    }
    SistemaMonitoreo o-- Animal
    SistemaMonitoreo o-- Alerta
    SistemaMonitoreo o-- Collar
    SistemaMonitoreo o-- Zona
    SistemaMonitoreo o-- Guardarrecursos
    SistemaMonitoreo o-- Lectura
    SistemaMonitoreo o-- CambioBateria
    SistemaMonitoreo --> ServicioSMS
```

## Evidencia de ejecución

La [salida completa real de main.py](docs/ejecucion.txt) incluye las Entregas 1 a 6. Las capturas de terminal muestran la ejecución de `python3 main.py`, paginada para poder leer las pruebas.

!\[Entrega 6: generación y primeras atenciones](docs/ejecucion\_6\_1.png)

!\[Entrega 6: bitácora y cola vacía](docs/ejecucion\_6\_2.png)

El diagrama completo está arriba en Mermaid y en [docs/diagrama\_clases.mmd](docs/diagrama_clases.mmd).

## Entrega en GitHub

Completar el grupo en este README, revisar el código y ejecutar `main.py`. Actualizar el mismo repositorio público con todos los archivos `.py`, `README.md`, `.gitignore` y la carpeta `docs`. No subir `\_\_pycache\_\_`, archivos `.pyc` ni el ZIP.

Al cargar archivos desde GitHub, usar un commit como `Entrega 6: cola FIFO de alertas y bitácora LIFO`. Si se usa Git local, realizar commit y push. Verificar que el último commit tenga los archivos nuevos y que las capturas y el diagrama se visualicen. Entregar el enlace público del repositorio como texto en la tarea.

