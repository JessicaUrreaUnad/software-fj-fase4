
"""
logs.py - Software FJ

Configura el sistema de registros (logs) para guardar
los eventos y errores importantes de la aplicación.
"""

import logging
import os


def configurar_logging():
    """
    Configura el registro de eventos y errores.

    Los registros se almacenan en el archivo software_fj.log.
    """

    # Obtiene el logger compartido por todos los módulos.
    logger = logging.getLogger("software_fj")

    # Establece el nivel mínimo de registro.
    logger.setLevel(logging.INFO)

    # Evita agregar manejadores repetidos.
    if not logger.handlers:

        try:
            # Crea un manejador para guardar información en un archivo.
            ruta_log = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "software_fj.log"
            )

            manejador = logging.FileHandler(
                ruta_log,
                encoding="utf-8"
            )

            # Define el formato de cada registro.
            formato = logging.Formatter(
                "%(asctime)s | %(levelname)s | %(message)s"
            )

            manejador.setFormatter(formato)

            # Agrega el manejador al logger.
            logger.addHandler(manejador)

        except OSError as error:
            raise OSError(
                "No fue posible configurar el archivo de registros."
            ) from error

    return logger


# Configura automáticamente el logger al importar el módulo.
logger = configurar_logging()
