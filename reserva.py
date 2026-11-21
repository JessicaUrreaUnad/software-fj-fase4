"""
reserva.py - Software FJ

Contiene la clase Reserva y la enumeración EstadoReserva,
encargadas de integrar un cliente, un servicio especializado,
la duración y el ciclo de vida de los estados de la reserva.

Aplica:
- Herencia de Entidad.
- Encapsulación de atributos.
- Polimorfismo al invocar calcular_costo() del servicio.
- Manejo avanzado de excepciones con try/except/else/finally y encadenamiento.
- Registro en logs de auditoría (software_fj.log).
"""

from enum import Enum
from typing import Dict, Any, Optional

from entidades import Entidad
from excepciones import (
    ErrorValidacion,
    ReservaError,
    EstadoReservaError,
    ServicioNoDisponibleError,
    ErrorCalculo
)
from logs import logger
from cliente import Cliente
from servicios import Servicio


class EstadoReserva(str, Enum):
    """
    Representa los estados posibles por los que transita una reserva
    dentro del flujo operativo de Software FJ.
    """
    PENDIENTE = "PENDIENTE"
    CONFIRMADA = "CONFIRMADA"
    COMPLETADA = "COMPLETADA"
    CANCELADA = "CANCELADA"


class Reserva(Entidad):
    """
    Modela una reserva en Software FJ vinculando un cliente, un servicio
    y una duración en horas. Administra las transiciones de estado
    y la liquidación del costo total del servicio contratado.
    """

    def __init__(self, id_reserva, cliente: Cliente, servicio: Servicio, duracion: float, **extras):
        # Inicializa la entidad base con validación de identificador
        super().__init__(id_reserva)

        # Validación estricta del objeto cliente
        if not isinstance(cliente, Cliente):
            mensaje = "El cliente proporcionado debe ser una instancia válida de la clase Cliente."
            logger.error("Error al instanciar Reserva %s: %s", id_reserva, mensaje)
            raise ErrorValidacion(mensaje)

        # Validación estricta del objeto servicio
        if not isinstance(servicio, Servicio):
            mensaje = "El servicio proporcionado debe heredar de la clase base Servicio."
            logger.error("Error al instanciar Reserva %s: %s", id_reserva, mensaje)
            raise ErrorValidacion(mensaje)

        # Validación de la duración en horas
        if isinstance(duracion, bool) or not isinstance(duracion, (int, float)) or duracion <= 0:
            mensaje = "La duración de la reserva debe ser un número positivo mayor a 0 horas."
            logger.error("Error al instanciar Reserva %s: %s", id_reserva, mensaje)
            raise ErrorValidacion(mensaje)

        # Atributos encapsulados
        self._cliente: Cliente = cliente
        self._servicio: Servicio = servicio
        self._duracion: float = float(duracion)
        self._extras: Dict[str, Any] = dict(extras)
        self._estado: EstadoReserva = EstadoReserva.PENDIENTE
        self._costo_total: Optional[float] = None

        logger.info(
            "Reserva creada en estado PENDIENTE. ID: %s | Cliente: %s | Servicio: %s | Duración: %s h",
            self.id, self._cliente.nombre, self._servicio.nombre, self._duracion
        )

    # --------------------------------------------------
    # PROPIEDADES (ENCAPSULACIÓN)
    # --------------------------------------------------

    @property
    def cliente(self) -> Cliente:
        return self._cliente

    @property
    def servicio(self) -> Servicio:
        return self._servicio

    @property
    def duracion(self) -> float:
        return self._duracion

    @property
    def estado(self) -> EstadoReserva:
        return self._estado

    @property
    def costo_total(self) -> Optional[float]:
        return self._costo_total

    @property
    def extras(self) -> Dict[str, Any]:
        return dict(self._extras)

    # --------------------------------------------------
    # GESTIÓN POLIMÓRFICA DEL COSTO CON TRY/EXCEPT/ELSE/FINALLY
    # --------------------------------------------------

    def liquidar_costo(self, impuesto: float = 0.19, descuento: float = 0.0) -> float:
        """
        Calcula el valor monetario final delegando polimórficamente en el método
        calcular_costo() del servicio. Aplica manejo de excepciones y encadenamiento.
        """
        resultado = None
        try:
            logger.info("Iniciando liquidación económica para la Reserva %s...", self.id)

            # Invocación polimórfica al método del servicio correspondiente
            resultado = self._servicio.calcular_costo(
                duracion=self._duracion,
                impuesto=impuesto,
                descuento=descuento,
                **self._extras
            )

        except (ErrorValidacion, ServicioNoDisponibleError, ErrorCalculo) as error_servicio:
            logger.exception(
                "Fallo en cálculo de costo para Reserva %s. Causa: %s",
                self.id, error_servicio
            )
            # Encadenamiento semántico de excepción
            raise ReservaError(
                f"No fue posible liquidar el costo de la reserva '{self.id}': {error_servicio}"
            ) from error_servicio

        except Exception as error_inesperado:
            logger.critical(
                "Error no previsto al liquidar Reserva %s: %s",
                self.id, error_inesperado, exc_info=True
            )
            raise ReservaError(
                f"Error crítico en el cálculo de la reserva '{self.id}'."
            ) from error_inesperado

        else:
            self._costo_total = resultado
            logger.info(
                "Costo liquidado exitosamente para Reserva %s. Monto final: $ %s",
                self.id, f"{resultado:,.2f}"
            )
            return self._costo_total

        finally:
            logger.info("Finalizado bloque de liquidación para Reserva ID: %s", self.id)

    # --------------------------------------------------
    # MÁQUINA DE ESTADOS Y CONTROL DE TRANSICIONES
    # --------------------------------------------------

    def confirmar(self) -> None:
        """Transiciona la reserva de PENDIENTE a CONFIRMADA."""
        if self._estado != EstadoReserva.PENDIENTE:
            mensaje = (
                f"No se puede confirmar la Reserva {self.id} porque su estado actual es {self._estado.value} "
                f"(solo se permite confirmar desde PENDIENTE)."
            )
            logger.error(mensaje)
            raise EstadoReservaError(mensaje)

        self._estado = EstadoReserva.CONFIRMADA
        logger.info("Reserva %s CONFIRMADA exitosamente.", self.id)

    def completar(self) -> None:
        """Transiciona la reserva de CONFIRMADA a COMPLETADA."""
        if self._estado != EstadoReserva.CONFIRMADA:
            mensaje = (
                f"No se puede completar la Reserva {self.id} porque su estado actual es {self._estado.value} "
                f"(requiere estado previo CONFIRMADA)."
            )
            logger.error(mensaje)
            raise EstadoReservaError(mensaje)

        self._estado = EstadoReserva.COMPLETADA
        logger.info("Reserva %s COMPLETADA exitosamente.", self.id)

    def cancelar(self, motivo: str = "Cancelación solicitada por el usuario") -> None:
        """Transiciona la reserva a CANCELADA, salvo que ya esté completada o cancelada."""
        if self._estado == EstadoReserva.COMPLETADA:
            mensaje = f"No es posible cancelar la Reserva {self.id} ya que el servicio se encuentra COMPLETADO."
            logger.error(mensaje)
            raise EstadoReservaError(mensaje)

        if self._estado == EstadoReserva.CANCELADA:
            mensaje = f"La Reserva {self.id} ya se encuentra previamente CANCELADA."
            logger.warning(mensaje)
            raise EstadoReservaError(mensaje)

        self._estado = EstadoReserva.CANCELADA
        logger.info("Reserva %s CANCELADA. Motivo: %s", self.id, motivo)

    # --------------------------------------------------
    # REPRESENTACIÓN Y CONSULTA
    # --------------------------------------------------

    def describir(self) -> str:
        """Implementación del método abstracto de Entidad."""
        costo_str = f"${self._costo_total:,.2f}" if self._costo_total is not None else "Sin liquidar"
        return (
            f"[Reserva {self.id}] Estado: {self._estado.value} | "
            f"Cliente: {self._cliente.nombre} (ID: {self._cliente.id}) | "
            f"Servicio: {self._servicio.nombre} ({self._duracion} h) | Costo: {costo_str}"
        )

    def obtener_datos(self) -> Dict[str, Any]:
        """Devuelve un diccionario estructurado con el estado de la reserva."""
        return {
            "id_reserva": self.id,
            "cliente_id": self._cliente.id,
            "cliente_nombre": self._cliente.nombre,
            "servicio_id": self._servicio.id,
            "servicio_nombre": self._servicio.nombre,
            "duracion": self._duracion,
            "estado": self._estado.value,
            "costo_total": self._costo_total,
            "extras": self._extras
        }

    def __str__(self) -> str:
        return self.describir()
