
"""
entidades.py - Software FJ

Contiene la clase abstracta Entidad,
que representa los elementos generales del sistema.
"""

from abc import ABC, abstractmethod
from excepciones import ErrorValidacion
from logs import logger


class Entidad(ABC):
    """
    Clase abstracta que representa una entidad general.

    Las clases que hereden de Entidad deberán implementar
    el método describir().
    """

    def __init__(self, id_entidad):
        """
        Inicializa la entidad con un identificador único.
        """

        # Valida que el identificador no esté vacío.
        if isinstance(id_entidad, bool) or not isinstance(
            id_entidad, (int, str)
        ):
            raise ErrorValidacion(
                "El identificador debe ser un número entero o texto."
            )

        if isinstance(id_entidad, str) and not id_entidad.strip():
            raise ErrorValidacion(
                "El identificador no puede estar vacío."
            )

        if isinstance(id_entidad, int) and id_entidad <= 0:
            raise ErrorValidacion(
                "El identificador debe ser mayor a cero."
            )

        # Guarda el identificador como atributo protegido.
        self._id = id_entidad

        logger.info(
            "Entidad creada correctamente. ID: %s",
            self._id
        )

    @property
    def id(self):
        """
        Permite consultar el identificador de la entidad.
        No permite modificarlo directamente.
        """
        return self._id

    @abstractmethod
    def describir(self):
        """
        Método abstracto que deben implementar
        las clases que hereden de Entidad.
        """
        pass
