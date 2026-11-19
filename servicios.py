"""
servicios.py - Software FJ
Clase abstracta Servicio y tres servicios especializados:
ReservaSala, AlquilerEquipo y AsesoriaEspecializada.

Aplica: abstracción, herencia, polimorfismo, encapsulación,
métodos sobrescritos, parámetros opcionales (sobrecarga en Python)
y manejo de excepciones (try/except/else/finally y encadenamiento).
"""

# ABC y abstractmethod permiten crear clases abstractas
from abc import ABC, abstractmethod
# logging permite registrar eventos y errores en el archivo de logs
import logging

# Logger compartido con el resto del proyecto
logger = logging.getLogger("software_fj")

# --- Dependencias de los compañeros -------------------------------------
# Si los módulos excepciones.py y entidades.py ya existen, se usan.
# Si no, se definen versiones mínimas para que este archivo funcione solo.
try:
    from excepciones import (ErrorValidacion, ServicioNoDisponibleError,
                             ErrorCalculo)
except ImportError:
    class ErrorValidacion(Exception):
        """Dato inválido o parámetro faltante."""

    class ServicioNoDisponibleError(Exception):
        """El servicio no está disponible."""

    class ErrorCalculo(Exception):
        """Resultado inconsistente en un cálculo."""

try:
    from entidades import Entidad
except ImportError:
    class Entidad(ABC):
        """Clase abstracta general del sistema (versión mínima)."""

        def __init__(self, id_entidad):
            # Atributo protegido: solo se accede por la propiedad
            self._id = id_entidad

        @property
        def id(self):
            """Identificador de la entidad (solo lectura)."""
            return self._id

        @abstractmethod
        def describir(self):
            """Cada entidad debe describirse a sí misma."""


class Servicio(Entidad, ABC):
    """Clase abstracta que representa cualquier servicio de Software FJ."""

    def __init__(self, id_servicio, nombre, tarifa_hora):
        super().__init__(id_servicio)
        # Validaciones estrictas antes de guardar los datos
        if not isinstance(nombre, str) or not nombre.strip():
            raise ErrorValidacion("El nombre del servicio no puede estar vacío.")
        if (isinstance(tarifa_hora, bool)
                or not isinstance(tarifa_hora, (int, float))
                or tarifa_hora <= 0):
            raise ErrorValidacion("La tarifa por hora debe ser un número mayor a 0.")
        # Atributos encapsulados (protegidos)
        self._nombre = nombre.strip()
        self._tarifa_hora = float(tarifa_hora)
        self._disponible = True

    # --- Propiedades (encapsulación) ---
    @property
    def nombre(self):
        return self._nombre

    @property
    def tarifa_hora(self):
        return self._tarifa_hora

    @property
    def disponible(self):
        return self._disponible

    @disponible.setter
    def disponible(self, valor):
        if not isinstance(valor, bool):
            raise ErrorValidacion("La disponibilidad debe ser True o False.")
        self._disponible = valor

    # --- Métodos abstractos: cada hija DEBE sobrescribirlos ---
    @abstractmethod
    def validar_parametros(self, duracion, **extras):
        """Valida duración y parámetros propios del servicio."""

    @abstractmethod
    def _costo_base(self, duracion, **extras):
        """Costo sin impuestos ni descuentos."""

    @abstractmethod
    def describir(self):
        """Texto que describe el servicio."""

    # --- Método concreto compartido ---
    def _validar_duracion(self, duracion):
        """Valida que la duración sea un número positivo de horas."""
        if (isinstance(duracion, bool)
                or not isinstance(duracion, (int, float))
                or duracion <= 0):
            raise ErrorValidacion("La duración debe ser un número de horas mayor a 0.")

    def calcular_costo(self, duracion, impuesto=0.0, descuento=0.0, **extras):
        """
        Calcula el costo final. Está 'sobrecargado' con parámetros opcionales:
          calcular_costo(2)                      -> solo costo base
          calcular_costo(2, impuesto=0.19)       -> con impuesto
          calcular_costo(2, 0.19, 0.10)          -> con impuesto y descuento
        impuesto y descuento van como fracción (0.19 = 19 %).
        """
        total = None
        try:
            if not self._disponible:
                raise ServicioNoDisponibleError(
                    f"El servicio '{self._nombre}' no está disponible.")
            self.validar_parametros(duracion, **extras)
            if not 0 <= impuesto <= 1:
                raise ErrorValidacion("El impuesto debe estar entre 0 y 1.")
            if not 0 <= descuento <= 1:
                raise ErrorValidacion("El descuento debe estar entre 0 y 1.")
            base = self._costo_base(duracion, **extras)
            total = base * (1 - descuento) * (1 + impuesto)
        except TypeError as error:
            # Encadenamiento: se conserva el error original con 'from'
            logger.error("Parámetros inválidos en %s: %s", self._nombre, error)
            raise ErrorCalculo("No se pudo calcular el costo por parámetros inválidos.") from error
        except (ErrorValidacion, ServicioNoDisponibleError) as error:
            logger.error("Error al calcular costo de %s: %s", self._nombre, error)
            raise
        else:
            # Solo se ejecuta si no hubo errores
            if total <= 0:
                raise ErrorCalculo("El costo calculado es inconsistente.")
            logger.info("Costo de %s calculado: %.2f", self._nombre, total)
            return round(total, 2)
        finally:
            # Se ejecuta siempre, haya o no error
            logger.info("Fin del cálculo de costo para %s", self._nombre)


class ReservaSala(Servicio):
    """Servicio de reserva de salas."""

    def __init__(self, id_servicio, nombre, tarifa_hora, capacidad):
        super().__init__(id_servicio, nombre, tarifa_hora)
        if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad <= 0:
            raise ErrorValidacion("La capacidad debe ser un entero mayor a 0.")
        self._capacidad = capacidad

    def validar_parametros(self, duracion, **extras):
        self._validar_duracion(duracion)
        personas = extras.get("personas")
        if personas is None:
            raise ErrorValidacion("Falta el parámetro 'personas'.")
        if not isinstance(personas, int) or not 1 <= personas <= self._capacidad:
            raise ErrorValidacion(f"Las personas deben estar entre 1 y {self._capacidad}.")

    def _costo_base(self, duracion, **extras):
        costo = self._tarifa_hora * duracion
        if extras.get("proyector"):
            costo += 15000  # recargo fijo por usar proyector
        return costo

    def describir(self):
        return f"Sala '{self._nombre}' (capacidad {self._capacidad}) - ${self._tarifa_hora:,.0f}/hora"


class AlquilerEquipo(Servicio):
    """Servicio de alquiler de equipos."""

    def __init__(self, id_servicio, nombre, tarifa_hora, stock):
        super().__init__(id_servicio, nombre, tarifa_hora)
        if isinstance(stock, bool) or not isinstance(stock, int) or stock <= 0:
            raise ErrorValidacion("El stock debe ser un entero mayor a 0.")
        self._stock = stock

    def validar_parametros(self, duracion, **extras):
        self._validar_duracion(duracion)
        cantidad = extras.get("cantidad")
        if cantidad is None:
            raise ErrorValidacion("Falta el parámetro 'cantidad'.")
        if not isinstance(cantidad, int) or not 1 <= cantidad <= self._stock:
            raise ErrorValidacion(f"La cantidad debe estar entre 1 y {self._stock}.")

    def _costo_base(self, duracion, **extras):
        return self._tarifa_hora * duracion * extras["cantidad"]

    def describir(self):
        return f"Equipo '{self._nombre}' (stock {self._stock}) - ${self._tarifa_hora:,.0f}/hora c/u"


class AsesoriaEspecializada(Servicio):
    """Servicio de asesoría especializada."""

    # Recargo según el nivel del asesor
    NIVELES = {"junior": 1.0, "senior": 1.5}

    def __init__(self, id_servicio, nombre, tarifa_hora, especialidad):
        super().__init__(id_servicio, nombre, tarifa_hora)
        if not isinstance(especialidad, str) or not especialidad.strip():
            raise ErrorValidacion("La especialidad no puede estar vacía.")
        self._especialidad = especialidad.strip()

    def validar_parametros(self, duracion, **extras):
        self._validar_duracion(duracion)
        nivel = extras.get("nivel")
        if nivel not in self.NIVELES:
            raise ErrorValidacion("El nivel debe ser 'junior' o 'senior'.")

    def _costo_base(self, duracion, **extras):
        return self._tarifa_hora * duracion * self.NIVELES[extras["nivel"]]

    def describir(self):
        return f"Asesoría de {self._especialidad} - ${self._tarifa_hora:,.0f}/hora"


# --- Prueba rápida: ejecutar con  python servicios.py ---
if __name__ == "__main__":
    logging.basicConfig(filename="servicios_demo.log", level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")

    # Lista de servicios: ejemplo de polimorfismo (todos usan describir())
    servicios = [
        ReservaSala(1, "Sala Andes", 40000, 10),
        AlquilerEquipo(2, "Portátil", 8000, 5),
        AsesoriaEspecializada(3, "Asesoría TI", 60000, "Ciberseguridad"),
    ]
    for s in servicios:
        print(s.describir())

    # Pruebas: (servicio, duración, impuesto, descuento, extras)
    pruebas = [
        (servicios[0], 2, 0.19, 0.10, {"personas": 6, "proyector": True}),  # válida
        (servicios[1], 3, 0.19, 0.0, {"cantidad": 2}),                      # válida
        (servicios[2], 1, 0.0, 0.0, {"nivel": "senior"}),                   # válida
        (servicios[0], 2, 0.19, 0.0, {"personas": 50}),                     # inválida
        (servicios[1], -1, 0.0, 0.0, {"cantidad": 1}),                      # inválida
        (servicios[2], 1, 0.0, 0.0, {}),                                    # falta nivel
        (servicios[0], "dos", 0.0, 0.0, {"personas": 3}),                   # tipo inválido
    ]
    for servicio, dur, imp, desc, extra in pruebas:
        try:
            costo = servicio.calcular_costo(dur, imp, desc, **extra)
            print(f"OK    {servicio.nombre}: ${costo:,.2f}")
        except (ErrorValidacion, ServicioNoDisponibleError, ErrorCalculo) as e:
            print(f"ERROR {servicio.nombre}: {e}")

    # Servicio no disponible
    servicios[1].disponible = False
    try:
        servicios[1].calcular_costo(1, cantidad=1)
    except ServicioNoDisponibleError as e:
        print(f"ERROR {servicios[1].nombre}: {e}")
    print("El programa sigue funcionando.")
