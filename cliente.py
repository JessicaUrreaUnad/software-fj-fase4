
"""
cliente.py - Software FJ

Contiene la clase Cliente, encargada de gestionar
los datos personales de los clientes de la empresa.

Aplica:
- Herencia.
- Encapsulación.
- Validaciones.
- Manejo de excepciones.
- Registro de eventos y errores.
"""

import re

from entidades import Entidad
from excepciones import ErrorValidacion
from logs import logger


class Cliente(Entidad):
    """
    Representa un cliente registrado en Software FJ.

    Hereda de Entidad y almacena sus datos personales
    mediante atributos privados.
    """

    def __init__(self, id_cliente, nombre, correo, telefono):

        # Inicializa la clase padre y valida el identificador.
        super().__init__(id_cliente)

        # Valida los datos antes de almacenarlos.
        self._validar_nombre(nombre)
        self._validar_correo(correo)
        self._validar_telefono(telefono)

        # Guarda los datos de forma encapsulada.
        self._nombre = nombre.strip()
        self._correo = correo.strip().lower()
        self._telefono = telefono.strip()

        # Registra la creación del cliente.
        logger.info(
            "Cliente registrado correctamente. ID: %s, Nombre: %s",
            self.id,
            self._nombre
        )

    # --------------------------------------------------
    # VALIDACIONES
    # --------------------------------------------------

    @staticmethod
    def _validar_nombre(nombre):
        """Comprueba que el nombre sea válido."""

        if not isinstance(nombre, str) or not nombre.strip():
            raise ErrorValidacion(
                "El nombre del cliente no puede estar vacío."
            )

        # Permite letras, espacios, puntos, guiones y apóstrofes.
        if not all(
            caracter.isalpha() or caracter in " .'-"
            for caracter in nombre.strip()
        ):
            raise ErrorValidacion(
                "El nombre contiene caracteres no permitidos."
            )

    @staticmethod
    def _validar_correo(correo):
        """Comprueba que el correo tenga un formato válido."""

        if not isinstance(correo, str) or not correo.strip():
            raise ErrorValidacion(
                "El correo electrónico no puede estar vacío."
            )

        patron = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

        if not re.fullmatch(patron, correo.strip()):
            raise ErrorValidacion(
                "El correo electrónico no tiene un formato válido."
            )

    @staticmethod
    def _validar_telefono(telefono):
        """Comprueba que el teléfono tenga un formato válido."""

        if not isinstance(telefono, str) or not telefono.strip():
            raise ErrorValidacion(
                "El teléfono no puede estar vacío."
            )

        # Permite números, espacios, paréntesis, guiones y el signo +.
        patron = r"^\+?[0-9\s()-]+$"

        if not re.fullmatch(patron, telefono.strip()):
            raise ErrorValidacion(
                "El teléfono contiene caracteres no permitidos."
            )

        # Comprueba que tenga entre 7 y 15 dígitos.
        cantidad_digitos = sum(
            caracter.isdigit() for caracter in telefono
        )

        if not 7 <= cantidad_digitos <= 15:
            raise ErrorValidacion(
                "El teléfono debe contener entre 7 y 15 dígitos."
            )

    # --------------------------------------------------
    # PROPIEDADES: ENCAPSULACIÓN
    # --------------------------------------------------

    @property
    def nombre(self):
        """Permite consultar el nombre del cliente."""
        return self._nombre

    @nombre.setter
    def nombre(self, nuevo_nombre):
        """Permite modificar el nombre después de validarlo."""

        self._validar_nombre(nuevo_nombre)
        self._nombre = nuevo_nombre.strip()

        logger.info(
            "Nombre del cliente actualizado. ID: %s",
            self.id
        )

    @property
    def correo(self):
        """Permite consultar el correo electrónico."""
        return self._correo

    @correo.setter
    def correo(self, nuevo_correo):
        """Actualiza el correo después de validarlo."""

        self._validar_correo(nuevo_correo)
        self._correo = nuevo_correo.strip().lower()

        logger.info(
            "Correo del cliente actualizado. ID: %s",
            self.id
        )

    @property
    def telefono(self):
        """Permite consultar el teléfono."""
        return self._telefono

    @telefono.setter
    def telefono(self, nuevo_telefono):
        """Actualiza el teléfono después de validarlo."""

        self._validar_telefono(nuevo_telefono)
        self._telefono = nuevo_telefono.strip()

        logger.info(
            "Teléfono del cliente actualizado. ID: %s",
            self.id
        )

    # --------------------------------------------------
    # MÉTODOS DE GESTIÓN
    # --------------------------------------------------

    def actualizar_datos(
        self,
        nombre=None,
        correo=None,
        telefono=None
    ):
        """
        Permite actualizar uno o varios datos del cliente.

        Los valores que no se proporcionen permanecen iguales.
        """

        try:
            # Comprueba los datos antes de modificarlos.
            if nombre is not None:
                self._validar_nombre(nombre)

            if correo is not None:
                self._validar_correo(correo)

            if telefono is not None:
                self._validar_telefono(telefono)

            # Actualiza únicamente los datos proporcionados.
            if nombre is not None:
                self._nombre = nombre.strip()

            if correo is not None:
                self._correo = correo.strip().lower()

            if telefono is not None:
                self._telefono = telefono.strip()

        except ErrorValidacion as error:
            logger.exception(
                "No fue posible actualizar los datos del cliente %s",
                self.id
            )
            raise

        else:
            logger.info(
                "Datos del cliente actualizados correctamente. ID: %s",
                self.id
            )
            return True

    def obtener_datos(self):
        """
        Devuelve los datos del cliente en un diccionario.
        """

        return {
            "id": self.id,
            "nombre": self.nombre,
            "correo": self.correo,
            "telefono": self.telefono
        }

    def describir(self):
        """
        Implementa el método abstracto heredado de Entidad.
        """

        return (
            f"Cliente: {self._nombre} | "
            f"Identificación: {self.id} | "
            f"Correo: {self._correo} | "
            f"Teléfono: {self._telefono}"
        )

    def __str__(self):
        """Representación del cliente como texto."""
        return self.describir()


# ------------------------------------------------------
# PRUEBAS INDIVIDUALES DE LA CLASE CLIENTE
# ------------------------------------------------------

if __name__ == "__main__":

    print("\n===== PRUEBAS DEL SISTEMA DE CLIENTES =====\n")

    # Lista para almacenar los clientes de prueba.
    clientes = []

    # Prueba 1: Registro correcto.
    try:
        cliente1 = Cliente(
            1,
            "Gabriel Morales",
            "gabriel@gmail.com",
            "3001234567"
        )

        clientes.append(cliente1)
        print("OK: Cliente registrado correctamente.")
        print(cliente1.describir())

    except ErrorValidacion as error:
        print("ERROR:", error)

    # Prueba 2: Nombre vacío.
    try:
        cliente2 = Cliente(
            2,
            "",
            "cliente@gmail.com",
            "3001234567"
        )

        clientes.append(cliente2)

    except ErrorValidacion as error:
        print("ERROR controlado (nombre):", error)

    # Prueba 3: Correo inválido.
    try:
        cliente3 = Cliente(
            3,
            "Carlos Pérez",
            "correo_incorrecto",
            "3001234567"
        )

        clientes.append(cliente3)

    except ErrorValidacion as error:
        print("ERROR controlado (correo):", error)

    # Prueba 4: Teléfono inválido.
    try:
        cliente4 = Cliente(
            4,
            "Laura Gómez",
            "laura@gmail.com",
            "123"
        )

        clientes.append(cliente4)

    except ErrorValidacion as error:
        print("ERROR controlado (teléfono):", error)

    # Prueba 5: Actualización correcta.
    try:
        cliente1.actualizar_datos(
            correo="gabriel.morales@gmail.com",
            telefono="3101234567"
        )

        print("\nOK: Datos actualizados.")
        print(cliente1.describir())

    except ErrorValidacion as error:
        print("ERROR:", error)

    # Prueba 6: Actualización con datos incorrectos.
    try:
        cliente1.actualizar_datos(
            correo="correo_malo"
        )

    except ErrorValidacion as error:
        print("ERROR controlado (actualización):", error)

    # Prueba 7: Consultar todos los clientes registrados.
    print("\n===== CLIENTES REGISTRADOS =====")

    for cliente in clientes:
        print(cliente.obtener_datos())

    print("\nEl programa continúa funcionando correctamente.")
