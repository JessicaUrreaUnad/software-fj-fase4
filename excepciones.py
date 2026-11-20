
"""
excepciones.py - Software FJ

Define las excepciones personalizadas utilizadas
para controlar los errores del sistema.
"""


class SoftwareFJError(Exception):
    """Excepción base para los errores del sistema Software FJ."""
    pass


class ErrorValidacion(SoftwareFJError):
    """Se genera cuando un dato o parámetro no es válido."""
    pass


class ServicioNoDisponibleError(SoftwareFJError):
    """Se genera cuando se intenta utilizar un servicio no disponible."""
    pass


class ErrorCalculo(SoftwareFJError):
    """Se genera cuando ocurre un error en un cálculo."""
    pass


class ClienteNoEncontradoError(SoftwareFJError):
    """Se genera cuando no se encuentra un cliente registrado."""
    pass


class ReservaError(SoftwareFJError):
    """Se genera cuando ocurre un problema durante una reserva."""
    pass


class EstadoReservaError(ReservaError):
    """Se genera cuando una operación no corresponde al estado de la reserva."""
    pass


class ArchivoLogError(SoftwareFJError):
    """Se genera cuando ocurre un problema con el archivo de registros."""
    pass
