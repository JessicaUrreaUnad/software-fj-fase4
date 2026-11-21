"""
====================================================================================================
UNIVERSIDAD NACIONAL ABIERTA Y A DISTANCIA (UNAD)
ESCUELA DE CIENCIAS BÁSICAS, TECNOLOGÍA E INGENIERÍA (ECBTI)
PROGRAMA DE INGENIERÍA DE SISTEMAS
CURSO: PROGRAMACIÓN - CÓDIGO: 213023
FASE 4: COMPONENTE PRÁCTICO - PRÁCTICAS SIMULADAS (SOFTWARE FJ)

DATOS DEL ESTUDIANTE:
- Nombre: FABIO LEONARDO LOPEZ
- Documento de Identidad: 79897845
- Grupo: 213023_560
- Tutor: MANUEL MEJIA MUNOZ
- Repositorio Colaborativo GitHub: https://github.com/JessicaUrreaUnad/software-fj-fase4
====================================================================================================
DESCRIPCIÓN DEL PROYECTO:
Sistema integral orientado a objetos para la empresa 'Software FJ', sin uso de bases de datos.
Gestiona clientes, servicios especializados y reservas con un modelo riguroso de:
  1. Abstracción y Encapsulamiento (Entidad, Cliente, Servicio, Reserva)
  2. Herencia y Polimorfismo (ReservaSala, AlquilerEquipo, AsesoriaEspecializada)
  3. Manejo Avanzado de Excepciones (Excepciones personalizadas, try/except/else/finally, encadenamiento)
  4. Auditoría y Trazabilidad mediante Logging en archivo físico (software_fj.log)
  5. Suite de 10 Simulaciones obligatorias con casos válidos e inválidos
  6. Interfaz gráfica interactiva desarrollada en Tkinter (completamente en idioma inglés)
====================================================================================================
"""

import os
import sys
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Any

# Asegurar importación de los módulos del paquete software-fj-fase4
DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))
if DIRECTORIO_ACTUAL not in sys.path:
    sys.path.insert(0, DIRECTORIO_ACTUAL)
sub_repo = os.path.join(DIRECTORIO_ACTUAL, "software-fj-fase4")
if os.path.exists(sub_repo) and sub_repo not in sys.path:
    sys.path.insert(0, sub_repo)

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

# Importación de módulos del sistema colaborativo
from entidades import Entidad
from excepciones import (
    SoftwareFJError,
    ErrorValidacion,
    ServicioNoDisponibleError,
    ErrorCalculo,
    ClienteNoEncontradoError,
    ReservaError,
    EstadoReservaError,
    ArchivoLogError
)
from logs import logger
from cliente import Cliente
from servicios import (
    Servicio,
    ReservaSala,
    AlquilerEquipo,
    AsesoriaEspecializada
)
from reserva import Reserva, EstadoReserva


# ==============================================================================
# CONTROLADOR DEL SISTEMA EN MEMORIA (SIN BASE DE DATOS)
# ==============================================================================

class SistemaSoftwareFJ:
    """
    Controlador central de lógica de negocio para Software FJ.
    Mantiene colecciones internas en memoria (listas) y garantiza
    que la aplicación continúe operando ante cualquier fallo.
    """

    def __init__(self):
        self._clientes: List[Cliente] = []
        self._servicios: List[Servicio] = []
        self._reservas: List[Reserva] = []
        logger.info("Sistema Software FJ inicializado en memoria (sin base de datos).")

    # --------------------------------------------------
    # GESTIÓN DE CLIENTES
    # --------------------------------------------------

    def registrar_cliente(self, id_cliente, nombre: str, correo: str, telefono: str) -> Cliente:
        """
        Registra un nuevo cliente validando unicidad de identificación y formato.
        Aplica try/except/else/finally para capturar errores de validación.
        """
        try:
            # Validar que no exista un cliente con el mismo ID
            if any(str(c.id) == str(id_cliente) for c in self._clientes):
                mensaje = f"Ya existe un cliente registrado con la identificación {id_cliente}."
                logger.error("Fallo al registrar cliente: %s", mensaje)
                raise ErrorValidacion(mensaje)

            nuevo_cliente = Cliente(id_cliente, nombre, correo, telefono)

        except ErrorValidacion as err:
            logger.warning("Validación rechazada al registrar cliente: %s", err)
            raise

        except Exception as ex_inesperada:
            logger.critical("Error inesperado en registrar_cliente: %s", ex_inesperada, exc_info=True)
            raise SoftwareFJError("Error crítico al procesar el registro del cliente.") from ex_inesperada

        else:
            self._clientes.append(nuevo_cliente)
            logger.info("Cliente '%s' agregado exitosamente al sistema. Total clientes: %d",
                        nuevo_cliente.nombre, len(self._clientes))
            return nuevo_cliente

        finally:
            logger.debug("Finalizado bloque de registro de cliente ID: %s", id_cliente)

    def buscar_cliente(self, id_cliente) -> Cliente:
        """Busca un cliente por su ID o lanza ClienteNoEncontradoError."""
        for c in self._clientes:
            if str(c.id) == str(id_cliente):
                return c
        mensaje = f"No se encontró ningún cliente registrado con el identificador '{id_cliente}'."
        logger.error(mensaje)
        raise ClienteNoEncontradoError(mensaje)

    def listar_clientes(self) -> List[Cliente]:
        return list(self._clientes)

    # --------------------------------------------------
    # GESTIÓN DE SERVICIOS
    # --------------------------------------------------

    def registrar_servicio(self, servicio: Servicio) -> Servicio:
        """Registra un servicio especializado en el catálogo en memoria."""
        if not isinstance(servicio, Servicio):
            raise ErrorValidacion("El objeto debe ser una instancia derivada de Servicio.")

        if any(str(s.id) == str(servicio.id) for s in self._servicios):
            raise ErrorValidacion(f"Ya existe un servicio con el ID {servicio.id}.")

        self._servicios.append(servicio)
        logger.info("Servicio registrado en catálogo: %s (ID: %s)", servicio.nombre, servicio.id)
        return servicio

    def buscar_servicio(self, id_servicio) -> Servicio:
        """Busca un servicio por su ID o lanza ErrorValidacion."""
        for s in self._servicios:
            if str(s.id) == str(id_servicio):
                return s
        mensaje = f"Servicio con ID '{id_servicio}' no encontrado en el catálogo."
        logger.error(mensaje)
        raise ErrorValidacion(mensaje)

    def listar_servicios(self) -> List[Servicio]:
        return list(self._servicios)

    # --------------------------------------------------
    # GESTIÓN DE RESERVAS
    # --------------------------------------------------

    def crear_reserva(self, id_reserva, id_cliente, id_servicio, duracion: float, **extras) -> Reserva:
        """
        Crea una nueva reserva asociando cliente y servicio.
        Valida existencia, disponibilidad y parámetros específicos de cada servicio.
        """
        try:
            cliente = self.buscar_cliente(id_cliente)
            servicio = self.buscar_servicio(id_servicio)

            if not servicio.disponible:
                raise ServicioNoDisponibleError(
                    f"El servicio '{servicio.nombre}' (ID: {servicio.id}) no se encuentra disponible actualmente."
                )

            # Validar que no se duplique el código de reserva
            if any(str(r.id) == str(id_reserva) for r in self._reservas):
                raise ErrorValidacion(f"Ya existe una reserva con el código '{id_reserva}'.")

            # Instanciar reserva (aplica validaciones internas de duracion y tipos)
            nueva_reserva = Reserva(id_reserva, cliente, servicio, duracion, **extras)

        except (ClienteNoEncontradoError, ServicioNoDisponibleError, ErrorValidacion) as err_conocido:
            logger.error("No se pudo crear la reserva %s: %s", id_reserva, err_conocido)
            raise

        except Exception as err_critico:
            logger.critical("Error no controlado al crear reserva %s: %s", id_reserva, err_critico, exc_info=True)
            raise ReservaError(f"Fallo general al procesar la reserva '{id_reserva}'.") from err_critico

        else:
            self._reservas.append(nueva_reserva)
            logger.info("Reserva %s creada satisfactoriamente.", nueva_reserva.id)
            return nueva_reserva

        finally:
            logger.debug("Finalizado intento de creación de reserva %s", id_reserva)

    def buscar_reserva(self, id_reserva) -> Reserva:
        for r in self._reservas:
            if str(r.id) == str(id_reserva):
                return r
        mensaje = f"Reserva con identificador '{id_reserva}' no existe."
        logger.error(mensaje)
        raise ReservaError(mensaje)

    def listar_reservas(self) -> List[Reserva]:
        return list(self._reservas)

    def poblar_catalogo_base(self):
        """Carga servicios y clientes iniciales para permitir pruebas inmediatas."""
        self._clientes.clear()
        self._servicios.clear()
        self._reservas.clear()

        # 3 Servicios especializados (Herencia y Polimorfismo)
        s1 = ReservaSala("SRV-101", "Executive Conference Room A", 50000.0, capacidad=15)
        s2 = AlquilerEquipo("SRV-201", "Dell Latitude Laptop Pack", 15000.0, stock=8)
        s3 = AsesoriaEspecializada("SRV-301", "Cybersecurity & Cloud Audit", 80000.0, especialidad="Ciberseguridad")

        self.registrar_servicio(s1)
        self.registrar_servicio(s2)
        self.registrar_servicio(s3)

        # Clientes iniciales
        c1 = Cliente("CLI-001", "Carlos Mendoza", "carlos.mendoza@gmail.com", "3001234567")
        c2 = Cliente("CLI-002", "Diana Martinez", "diana.martinez@unadvirtual.edu.co", "3159876543")

        self._clientes.append(c1)
        self._clientes.append(c2)
        logger.info("Catálogo base inicial cargado exitosamente en memoria.")


# ==============================================================================
# SUITE DE LAS 10 SIMULACIONES OBLIGATORIAS (ANEXO 3 Y RÚBRICA)
# ==============================================================================

def ejecutar_suite_10_simulaciones(sistema: SistemaSoftwareFJ) -> List[Dict[str, Any]]:
    """
    Ejecuta de manera secuencial 10 casos de prueba rigurosos que abarcan
    operaciones exitosas y situaciones con errores graves controlados.
    Demuestra que el sistema nunca se detiene y registra todo en el log.
    """
    resultados = []
    logger.info("=================================================================")
    logger.info("INICIANDO SUITE OBLIGATORIA DE 10 SIMULACIONES EN SOFTWARE FJ")
    logger.info("=================================================================")

    # --------------------------------------------------------------------------
    # SIMULACIÓN 1: Registro válido de cliente
    # --------------------------------------------------------------------------
    try:
        c = sistema.registrar_cliente("CLI-101", "Andres Felipe Gomez", "andres.gomez@gmail.com", "3112233445")
        resultados.append({
            "num": 1,
            "tipo": "VALID",
            "escenario": "Client Registration (Valid Data)",
            "resultado": f"SUCCESS: Client created [{c.nombre}] (ID: {c.id})",
            "excepcion": "None",
            "estado": "PASS"
        })
    except Exception as e:
        resultados.append({"num": 1, "tipo": "VALID", "escenario": "Client Registration (Valid)", "resultado": f"FAIL: {e}", "excepcion": type(e).__name__, "estado": "FAIL"})

    # --------------------------------------------------------------------------
    # SIMULACIÓN 2: Registro inválido de cliente (Correo con formato incorrecto)
    # --------------------------------------------------------------------------
    try:
        sistema.registrar_cliente("CLI-102", "Mariana Rios", "correo_invalido_sin_arroba", "3009988776")
        resultados.append({"num": 2, "tipo": "INVALID", "escenario": "Client Registration (Bad Email)", "resultado": "FAIL: Should have rejected invalid email", "excepcion": "None", "estado": "FAIL"})
    except ErrorValidacion as err:
        logger.info("Simulación 2 exitosa: ErrorValidacion capturado correctamente: %s", err)
        resultados.append({
            "num": 2,
            "tipo": "INVALID",
            "escenario": "Client Registration (Bad Email)",
            "resultado": f"CAUGHT: Handled gracefully -> '{err}'",
            "excepcion": type(err).__name__,
            "estado": "PASS"
        })
    except Exception as e:
        resultados.append({"num": 2, "tipo": "INVALID", "escenario": "Client Registration (Bad Email)", "resultado": f"UNEXPECTED: {e}", "excepcion": type(e).__name__, "estado": "FAIL"})

    # --------------------------------------------------------------------------
    # SIMULACIÓN 3: Creación válida de servicio especializado (ReservaSala)
    # --------------------------------------------------------------------------
    try:
        sala = ReservaSala("SRV-401", "Auditorio Central UNAD", 95000.0, capacidad=50)
        sistema.registrar_servicio(sala)
        resultados.append({
            "num": 3,
            "tipo": "VALID",
            "escenario": "Service Creation: ReservaSala (Valid)",
            "resultado": f"SUCCESS: Service created [{sala.describir()}]",
            "excepcion": "None",
            "estado": "PASS"
        })
    except Exception as e:
        resultados.append({"num": 3, "tipo": "VALID", "escenario": "Service Creation: ReservaSala", "resultado": f"FAIL: {e}", "excepcion": type(e).__name__, "estado": "FAIL"})

    # --------------------------------------------------------------------------
    # SIMULACIÓN 4: Creación inválida de servicio (Tarifa por hora negativa)
    # --------------------------------------------------------------------------
    try:
        AlquilerEquipo("SRV-402", "Proyector Laser 4K", -25000.0, stock=3)
        resultados.append({"num": 4, "tipo": "INVALID", "escenario": "Service Creation (Negative Hourly Rate)", "resultado": "FAIL: Should have rejected negative rate", "excepcion": "None", "estado": "FAIL"})
    except ErrorValidacion as err:
        logger.info("Simulación 4 exitosa: ErrorValidacion capturado: %s", err)
        resultados.append({
            "num": 4,
            "tipo": "INVALID",
            "escenario": "Service Creation (Negative Hourly Rate)",
            "resultado": f"CAUGHT: Handled gracefully -> '{err}'",
            "excepcion": type(err).__name__,
            "estado": "PASS"
        })
    except Exception as e:
        resultados.append({"num": 4, "tipo": "INVALID", "escenario": "Service Creation (Negative Rate)", "resultado": f"UNEXPECTED: {e}", "excepcion": type(e).__name__, "estado": "FAIL"})

    # --------------------------------------------------------------------------
    # SIMULACIÓN 5: Creación y liquidación polimórfica de reserva válida
    # --------------------------------------------------------------------------
    try:
        r5 = sistema.crear_reserva("RES-501", "CLI-001", "SRV-101", duracion=3.0, personas=10, proyector=True)
        costo5 = r5.liquidar_costo(impuesto=0.19, descuento=0.10)
        r5.confirmar()
        resultados.append({
            "num": 5,
            "tipo": "VALID",
            "escenario": "Reservation Creation & Polymorphic Cost (Valid)",
            "resultado": f"SUCCESS: Total Cost ${costo5:,.2f} | Status: {r5.estado.value}",
            "excepcion": "None",
            "estado": "PASS"
        })
    except Exception as e:
        resultados.append({"num": 5, "tipo": "VALID", "escenario": "Reservation Creation & Polymorphic Cost", "resultado": f"FAIL: {e}", "excepcion": type(e).__name__, "estado": "FAIL"})

    # --------------------------------------------------------------------------
    # SIMULACIÓN 6: Intento de reserva con duración inválida (<= 0 horas)
    # --------------------------------------------------------------------------
    try:
        sistema.crear_reserva("RES-502", "CLI-001", "SRV-201", duracion=-2.0, cantidad=2)
        resultados.append({"num": 6, "tipo": "INVALID", "escenario": "Reservation (Negative Duration)", "resultado": "FAIL: Should have rejected negative hours", "excepcion": "None", "estado": "FAIL"})
    except ErrorValidacion as err:
        logger.info("Simulación 6 exitosa: ErrorValidacion por duración negativa: %s", err)
        resultados.append({
            "num": 6,
            "tipo": "INVALID",
            "escenario": "Reservation (Negative Duration)",
            "resultado": f"CAUGHT: Handled gracefully -> '{err}'",
            "excepcion": type(err).__name__,
            "estado": "PASS"
        })
    except Exception as e:
        resultados.append({"num": 6, "tipo": "INVALID", "escenario": "Reservation (Negative Duration)", "resultado": f"UNEXPECTED: {e}", "excepcion": type(e).__name__, "estado": "FAIL"})

    # --------------------------------------------------------------------------
    # SIMULACIÓN 7: Intento de reserva con servicio inactivo / no disponible
    # --------------------------------------------------------------------------
    try:
        srv_inactivo = sistema.buscar_servicio("SRV-201")
        srv_inactivo.disponible = False  # Se marca el servicio como fuera de servicio
        sistema.crear_reserva("RES-503", "CLI-002", "SRV-201", duracion=4.0, cantidad=1)
        resultados.append({"num": 7, "tipo": "INVALID", "escenario": "Reservation on Unavailable Service", "resultado": "FAIL: Should have raised ServicioNoDisponibleError", "excepcion": "None", "estado": "FAIL"})
    except ServicioNoDisponibleError as err:
        logger.info("Simulación 7 exitosa: ServicioNoDisponibleError capturado: %s", err)
        srv_inactivo.disponible = True  # Restaurar disponibilidad
        resultados.append({
            "num": 7,
            "tipo": "INVALID",
            "escenario": "Reservation on Unavailable Service",
            "resultado": f"CAUGHT: Handled gracefully -> '{err}'",
            "excepcion": type(err).__name__,
            "estado": "PASS"
        })
    except Exception as e:
        resultados.append({"num": 7, "tipo": "INVALID", "escenario": "Reservation on Unavailable Service", "resultado": f"UNEXPECTED: {e}", "excepcion": type(e).__name__, "estado": "FAIL"})

    # --------------------------------------------------------------------------
    # SIMULACIÓN 8: Intento de reserva con cliente inexistente en el sistema
    # --------------------------------------------------------------------------
    try:
        sistema.crear_reserva("RES-504", "CLI-INEXISTENTE-999", "SRV-301", duracion=2.0, nivel="senior")
        resultados.append({"num": 8, "tipo": "INVALID", "escenario": "Reservation with Non-existent Client", "resultado": "FAIL: Should have raised ClienteNoEncontradoError", "excepcion": "None", "estado": "FAIL"})
    except ClienteNoEncontradoError as err:
        logger.info("Simulación 8 exitosa: ClienteNoEncontradoError capturado: %s", err)
        resultados.append({
            "num": 8,
            "tipo": "INVALID",
            "escenario": "Reservation with Non-existent Client",
            "resultado": f"CAUGHT: Handled gracefully -> '{err}'",
            "excepcion": type(err).__name__,
            "estado": "PASS"
        })
    except Exception as e:
        resultados.append({"num": 8, "tipo": "INVALID", "escenario": "Reservation with Non-existent Client", "resultado": f"UNEXPECTED: {e}", "excepcion": type(e).__name__, "estado": "FAIL"})

    # --------------------------------------------------------------------------
    # SIMULACIÓN 9: Transición inválida de estado (Cancelar reserva ya completada)
    # --------------------------------------------------------------------------
    try:
        r9 = sistema.crear_reserva("RES-505", "CLI-002", "SRV-301", duracion=2.0, nivel="junior")
        r9.liquidar_costo()
        r9.confirmar()
        r9.completar()  # Ya está completada
        r9.cancelar("Intento indebido de anulación")  # Debe fallar
        resultados.append({"num": 9, "tipo": "INVALID", "escenario": "Invalid State Transition (Cancel Completed)", "resultado": "FAIL: Should have raised EstadoReservaError", "excepcion": "None", "estado": "FAIL"})
    except EstadoReservaError as err:
        logger.info("Simulación 9 exitosa: EstadoReservaError capturado: %s", err)
        resultados.append({
            "num": 9,
            "tipo": "INVALID",
            "escenario": "Invalid State Transition (Cancel Completed)",
            "resultado": f"CAUGHT: Handled gracefully -> '{err}'",
            "excepcion": type(err).__name__,
            "estado": "PASS"
        })
    except Exception as e:
        resultados.append({"num": 9, "tipo": "INVALID", "escenario": "Invalid State Transition", "resultado": f"UNEXPECTED: {e}", "excepcion": type(e).__name__, "estado": "FAIL"})

    # --------------------------------------------------------------------------
    # SIMULACIÓN 10: Encadenamiento de excepción y fallo de cálculo de servicio
    # (Parámetro extra inválido: sobrecupo que excede la capacidad de la sala)
    # --------------------------------------------------------------------------
    try:
        # Se solicita sala para 120 personas cuando la capacidad es de 15
        r10 = sistema.crear_reserva("RES-506", "CLI-001", "SRV-101", duracion=2.0, personas=120)
        r10.liquidar_costo()
        resultados.append({"num": 10, "tipo": "INVALID", "escenario": "Chained Exception (Room Overcapacity)", "resultado": "FAIL: Should have raised chained ReservaError", "excepcion": "None", "estado": "FAIL"})
    except ReservaError as err:
        causa = err.__cause__
        logger.info("Simulación 10 exitosa: ReservaError encadenado desde %s: %s", type(causa).__name__, err)
        resultados.append({
            "num": 10,
            "tipo": "INVALID",
            "escenario": "Chained Exception (Room Overcapacity)",
            "resultado": f"CAUGHT: Chained from {type(causa).__name__} -> '{err}'",
            "excepcion": f"{type(err).__name__} <- {type(causa).__name__}",
            "estado": "PASS"
        })
    except Exception as e:
        resultados.append({"num": 10, "tipo": "INVALID", "escenario": "Chained Exception", "resultado": f"UNEXPECTED: {e}", "excepcion": type(e).__name__, "estado": "FAIL"})

    logger.info("=================================================================")
    logger.info("SUITE DE 10 SIMULACIONES FINALIZADA CON ÉXITO Y TOTAL ESTABILIDAD")
    logger.info("=================================================================")
    return resultados


# ==============================================================================
# INTERFAZ GRÁFICA TKINTER (DISEÑADA ÍNTEGRAMENTE EN INGLÉS)
# Cumple con el criterio de componente práctico UNAD y trazabilidad temporal
# ==============================================================================

class SoftwareFJGUI:
    """
    Entorno gráfico interactivo de Software FJ desarrollado en Tkinter.
    Permite ejecutar la suite de simulaciones, visualizar los logs en vivo
    y realizar operaciones interactivas con manejo visual de excepciones.
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Software FJ - Phase 4: Simulated Practice [UNAD Group 560]")
        self.root.geometry("1080x720")
        self.root.minsize(980, 640)
        self.root.configure(bg="#F1F5F9")

        # Inicialización de la lógica del sistema
        self.sistema = SistemaSoftwareFJ()
        self.sistema.poblar_catalogo_base()

        # Construcción visual
        self._construir_banner_institucional()
        self._construir_cuerpo_principal()
        self._construir_barra_inferior()

        # Iniciar reloj en tiempo real
        self._actualizar_reloj()

    def _construir_banner_institucional(self):
        """Banner superior que documenta la autoría de Fabio Leonardo Lopez."""
        banner = tk.Frame(self.root, bg="#1E3A8A", padx=16, pady=10)
        banner.pack(fill="x")

        tk.Label(
            banner,
            text="🏢 SOFTWARE FJ - CLIENT, SERVICE & RESERVATION MANAGEMENT SYSTEM",
            font=("Arial", 12, "bold"),
            fg="#FFFFFF",
            bg="#1E3A8A"
        ).pack(anchor="w")

        subtexto = (
            "Student: FABIO LEONARDO LOPEZ | ID: 79897845 | Group: 213023_560 | Tutor: MANUEL MEJIA MUNOZ | "
            "Phase 4: Simulated Practice | In-Memory (No DB)"
        )
        tk.Label(
            banner,
            text=subtexto,
            font=("Arial", 8),
            fg="#BFDBFE",
            bg="#1E3A8A"
        ).pack(anchor="w", pady=(2, 0))

        tk.Label(
            banner,
            text="GitHub Repository: https://github.com/JessicaUrreaUnad/software-fj-fase4",
            font=("Arial", 8, "italic"),
            fg="#93C5FD",
            bg="#1E3A8A"
        ).pack(anchor="w")

    def _construir_cuerpo_principal(self):
        """Panel central organizado en pestañas mediante ttk.Notebook."""
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=12, pady=(8, 4))

        # Pestaña 1: Suite de 10 Simulaciones
        self.tab_simulaciones = tk.Frame(notebook, bg="#F1F5F9", padx=10, pady=8)
        notebook.add(self.tab_simulaciones, text="  🧪 10 Automated Simulations (Criteria 1 & 2)  ")

        # Pestaña 2: Auditoría y Visualizador de Logs
        self.tab_logs = tk.Frame(notebook, bg="#F1F5F9", padx=10, pady=8)
        notebook.add(self.tab_logs, text="  📜 Audit Log Viewer (software_fj.log)  ")

        # Pestaña 3: Operaciones Interactivas
        self.tab_interactivo = tk.Frame(notebook, bg="#F1F5F9", padx=10, pady=8)
        notebook.add(self.tab_interactivo, text="  🛠️ Interactive Operations (Clients & Services)  ")

        self._construir_pestana_simulaciones()
        self._construir_pestana_logs()
        self._construir_pestana_interactivo()

    # --------------------------------------------------------------------------
    # PESTAÑA 1: SUITE DE 10 SIMULACIONES
    # --------------------------------------------------------------------------
    def _construir_pestana_simulaciones(self):
        f_top = tk.Frame(self.tab_simulaciones, bg="#F1F5F9")
        f_top.pack(fill="x", pady=(0, 6))

        tk.Label(
            f_top,
            text="Mandatory Automated Simulation Suite: 10 Valid & Invalid Operations with Exception Handling",
            font=("Arial", 9, "bold"),
            fg="#1E293B",
            bg="#F1F5F9"
        ).pack(side="left")

        btn_run = tk.Button(
            f_top,
            text="▶ Run 10 Automated Simulations",
            font=("Arial", 9, "bold"),
            bg="#16A34A",
            fg="#FFFFFF",
            relief="groove",
            padx=12,
            pady=4,
            cursor="hand2",
            command=self._ejecutar_simulaciones_gui
        )
        btn_run.pack(side="right")

        # Tabla Treeview para visualizar resultados
        cols = ("num", "type", "scenario", "result", "exception", "status")
        self.tree_sims = ttk.Treeview(self.tab_simulaciones, columns=cols, show="headings", height=13)

        self.tree_sims.heading("num", text="#")
        self.tree_sims.heading("type", text="Type")
        self.tree_sims.heading("scenario", text="Simulation Scenario")
        self.tree_sims.heading("result", text="Execution Outcome / Handled Response")
        self.tree_sims.heading("exception", text="Exception Handled")
        self.tree_sims.heading("status", text="Stability")

        self.tree_sims.column("num", width=35, anchor="center")
        self.tree_sims.column("type", width=75, anchor="center")
        self.tree_sims.column("scenario", width=260, anchor="w")
        self.tree_sims.column("result", width=420, anchor="w")
        self.tree_sims.column("exception", width=160, anchor="center")
        self.tree_sims.column("status", width=70, anchor="center")

        scroll_s = ttk.Scrollbar(self.tab_simulaciones, orient="vertical", command=self.tree_sims.yview)
        self.tree_sims.configure(yscrollcommand=scroll_s.set)

        self.tree_sims.pack(side="left", fill="both", expand=True)
        scroll_s.pack(side="right", fill="y")

    def _ejecutar_simulaciones_gui(self):
        # Limpiar tabla
        for item in self.tree_sims.get_children():
            self.tree_sims.delete(item)

        resultados = ejecutar_suite_10_simulaciones(self.sistema)

        for r in resultados:
            tag = "valid" if r["tipo"] == "VALID" else "invalid"
            self.tree_sims.insert("", "end", values=(
                r["num"],
                r["tipo"],
                r["scenario"],
                r["resultado"],
                r["excepcion"],
                r["estado"]
            ), tags=(tag,))

        self.tree_sims.tag_configure("valid", foreground="#15803D")
        self.tree_sims.tag_configure("invalid", foreground="#B91C1C")

        # Refrescar logs automáticamente
        self._cargar_archivo_logs()

        messagebox.showinfo(
            "Simulations Completed",
            "All 10 simulations were successfully executed without application termination.\n\n"
            "• All exceptions were caught and handled gracefully.\n"
            "• Full operational audit was recorded in 'software_fj.log'."
        )

    # --------------------------------------------------------------------------
    # PESTAÑA 2: VISUALIZADOR DE LOGS
    # --------------------------------------------------------------------------
    def _construir_pestana_logs(self):
        f_ctl = tk.Frame(self.tab_logs, bg="#F1F5F9")
        f_ctl.pack(fill="x", pady=(0, 6))

        tk.Label(
            f_ctl,
            text="Physical Log File Content: software_fj.log (Auditing INFO, WARNING, ERROR, EXCEPTION)",
            font=("Arial", 9, "bold"),
            fg="#1E293B",
            bg="#F1F5F9"
        ).pack(side="left")

        btn_refresh = tk.Button(
            f_ctl,
            text="🔄 Refresh Log",
            font=("Arial", 8, "bold"),
            bg="#0284C7",
            fg="#FFFFFF",
            relief="groove",
            command=self._cargar_archivo_logs
        )
        btn_refresh.pack(side="right")

        self.txt_logs = scrolledtext.ScrolledText(
            self.tab_logs,
            wrap="word",
            font=("Consolas", 8),
            bg="#0F172A",
            fg="#F8FAFC",
            height=15
        )
        self.txt_logs.pack(fill="both", expand=True)

        self._cargar_archivo_logs()

    def _cargar_archivo_logs(self):
        ruta_log = os.path.join(DIRECTORIO_ACTUAL, "software_fj.log")
        if os.path.exists(ruta_log):
            try:
                with open(ruta_log, "r", encoding="utf-8", errors="ignore") as fp:
                    contenido = fp.read()
                self.txt_logs.delete("1.0", tk.END)
                self.txt_logs.insert(tk.END, contenido)
                self.txt_logs.see(tk.END)
            except Exception as e:
                self.txt_logs.delete("1.0", tk.END)
                self.txt_logs.insert(tk.END, f"Could not read log file: {e}")
        else:
            self.txt_logs.delete("1.0", tk.END)
            self.txt_logs.insert(tk.END, "(Log file 'software_fj.log' has not been created yet.)")

    # --------------------------------------------------------------------------
    # PESTAÑA 3: OPERACIONES INTERACTIVAS
    # --------------------------------------------------------------------------
    def _construir_pestana_interactivo(self):
        panel = tk.Frame(self.tab_interactivo, bg="#F1F5F9")
        panel.pack(fill="both", expand=True)

        # Columna Izquierda: Registro interactivo de Cliente
        f_cli = tk.LabelFrame(panel, text=" Interactive Client Registration ", font=("Arial", 9, "bold"), bg="#F1F5F9", padx=8, pady=8)
        f_cli.pack(side="left", fill="both", expand=True, padx=(0, 6))

        tk.Label(f_cli, text="Client ID:", font=("Arial", 9), bg="#F1F5F9").grid(row=0, column=0, sticky="w", pady=3)
        self.entry_cli_id = ttk.Entry(f_cli, width=22)
        self.entry_cli_id.grid(row=0, column=1, sticky="w", pady=3, padx=4)

        tk.Label(f_cli, text="Full Name:", font=("Arial", 9), bg="#F1F5F9").grid(row=1, column=0, sticky="w", pady=3)
        self.entry_cli_nom = ttk.Entry(f_cli, width=22)
        self.entry_cli_nom.grid(row=1, column=1, sticky="w", pady=3, padx=4)

        tk.Label(f_cli, text="Email:", font=("Arial", 9), bg="#F1F5F9").grid(row=2, column=0, sticky="w", pady=3)
        self.entry_cli_mail = ttk.Entry(f_cli, width=22)
        self.entry_cli_mail.grid(row=2, column=1, sticky="w", pady=3, padx=4)

        tk.Label(f_cli, text="Phone (7-15 digits):", font=("Arial", 9), bg="#F1F5F9").grid(row=3, column=0, sticky="w", pady=3)
        self.entry_cli_tel = ttk.Entry(f_cli, width=22)
        self.entry_cli_tel.grid(row=3, column=1, sticky="w", pady=3, padx=4)

        btn_guardar_cli = tk.Button(
            f_cli,
            text="Register Client",
            font=("Arial", 9, "bold"),
            bg="#16A34A",
            fg="#FFFFFF",
            relief="groove",
            command=self._registrar_cliente_gui
        )
        btn_guardar_cli.grid(row=4, column=0, columnspan=2, pady=(8, 4))

        # Lista de clientes
        tk.Label(f_cli, text="Registered Clients (In-Memory):", font=("Arial", 8, "bold"), bg="#F1F5F9").grid(row=5, column=0, columnspan=2, sticky="w", pady=(6, 2))
        self.list_cli = tk.Listbox(f_cli, font=("Arial", 8), height=7)
        self.list_cli.grid(row=6, column=0, columnspan=2, sticky="nsew")

        # Columna Derecha: Catálogo de Servicios y Reservas
        f_srv = tk.LabelFrame(panel, text=" Services & Active Reservations ", font=("Arial", 9, "bold"), bg="#F1F5F9", padx=8, pady=8)
        f_srv.pack(side="right", fill="both", expand=True, padx=(6, 0))

        tk.Label(f_srv, text="Specialized Services Catalog (Inheritance & Polymorphism):", font=("Arial", 8, "bold"), bg="#F1F5F9").pack(anchor="w")
        self.list_srv = tk.Listbox(f_srv, font=("Arial", 8), height=5)
        self.list_srv.pack(fill="x", pady=(2, 8))

        tk.Label(f_srv, text="Current Reservations State Machine:", font=("Arial", 8, "bold"), bg="#F1F5F9").pack(anchor="w")
        self.list_res = tk.Listbox(f_srv, font=("Arial", 8), height=6)
        self.list_res.pack(fill="both", expand=True, pady=(2, 6))

        self._actualizar_vistas_interactivas()

    def _registrar_cliente_gui(self):
        c_id = self.entry_cli_id.get().strip()
        c_nom = self.entry_cli_nom.get().strip()
        c_mail = self.entry_cli_mail.get().strip()
        c_tel = self.entry_cli_tel.get().strip()

        try:
            nuevo = self.sistema.registrar_cliente(c_id, c_nom, c_mail, c_tel)
            messagebox.showinfo("Success", f"Client '{nuevo.nombre}' registered successfully!")
            self.entry_cli_id.delete(0, tk.END)
            self.entry_cli_nom.delete(0, tk.END)
            self.entry_cli_mail.delete(0, tk.END)
            self.entry_cli_tel.delete(0, tk.END)
            self._actualizar_vistas_interactivas()
            self._cargar_archivo_logs()
        except ErrorValidacion as err:
            messagebox.showerror("Validation Error (Handled)", str(err))
            self._cargar_archivo_logs()
        except Exception as e:
            messagebox.showerror("Unexpected Error", str(e))
            self._cargar_archivo_logs()

    def _actualizar_vistas_interactivas(self):
        self.list_cli.delete(0, tk.END)
        for c in self.sistema.listar_clientes():
            self.list_cli.insert(tk.END, f"ID: {c.id} | {c.nombre} | {c.correo}")

        self.list_srv.delete(0, tk.END)
        for s in self.sistema.listar_servicios():
            disp = "Available" if s.disponible else "Unavailable"
            self.list_srv.insert(tk.END, f"[{s.id}] {s.describir()} | Status: {disp}")

        self.list_res.delete(0, tk.END)
        for r in self.sistema.listar_reservas():
            self.list_res.insert(tk.END, r.describir())

    # --------------------------------------------------------------------------
    # BARRA INFERIOR DE ESTADO Y RELOJ
    # --------------------------------------------------------------------------
    def _construir_barra_inferior(self):
        barra = tk.Frame(self.root, bg="#334155", padx=10, pady=4)
        barra.pack(fill="x", side="bottom")

        tk.Label(
            barra,
            text="UNAD Programming Course (213023) | System Status: Active | Logging: software_fj.log",
            font=("Arial", 8),
            fg="#CBD5E1",
            bg="#334155"
        ).pack(side="left")

        self.lbl_reloj = tk.Label(
            barra,
            text="Date & Time: Loading...",
            font=("Arial", 8, "bold"),
            fg="#FFFFFF",
            bg="#334155"
        )
        self.lbl_reloj.pack(side="right")

    def _actualizar_reloj(self):
        ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.lbl_reloj.config(text=f"System Date & Time: {ahora}")
        self.root.after(1000, self._actualizar_reloj)


# ==============================================================================
# EJECUCIÓN PRINCIPAL DEL APLICATIVO
# ==============================================================================

def main():
    root = tk.Tk()
    app = SoftwareFJGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
