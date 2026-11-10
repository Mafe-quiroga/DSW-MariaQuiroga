from abc import ABC, abstractmethod
import datetime
import logging
import os

# Configuración del sistema de logs para registrar errores y eventos
LOG_FILE = "sistema.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8",
)


# ==========================================
# EXCEPCIONES PERSONALIZADAS Y ENCADENAMIENTO
# ==========================================
class ErrorSistemaFJ(Exception):
  """Clase base para excepciones personalizadas del sistema."""

  pass


class ClienteInvalidoError(ErrorSistemaFJ):
  """Excepción para datos de clientes incorrectos o incompletos."""

  pass


class ServicioNoDisponibleError(ErrorSistemaFJ):
  """Excepción cuando un servicio no está disponible o es inválido."""

  pass


class ReservaFallidaError(ErrorSistemaFJ):
  """Excepción para errores al procesar reservas."""

  pass


# ==========================================
# CLASES ABSTRACTAS Y ENTIDADES PRINCIPALES
# ==========================================
class EntidadBase(ABC):
  """Clase abstracta que representa entidades generales del sistema."""

  def __init__(self, identificador: str):
    self._identificador = identificador

  @property
  def identificador(self):
    return self._identificador

  @abstractmethod
  def obtener_detalles(self) -> str:
    pass


class Cliente(EntidadBase):

  def __init__(self, identificador: str, nombre: str, correo: str, telefono: str):
    super().__init__(identificador)
    self.nombre = nombre
    self.correo = correo
    self.telefono = telefono

  @property
  def nombre(self):
    return self._nombre

  @nombre.setter
  def nombre(self, valor):
    if not valor or not isinstance(valor, str) or len(valor.strip()) < 3:
      raise ClienteInvalidoError(
          f"Nombre de cliente inválido: '{valor}'. Debe tener al menos 3"
          " caracteres."
      )
    self._nombre = valor.strip()

  @property
  def correo(self):
    return self._correo

  @correo.setter
  def correo(self, valor):
    if not valor or "@" not in valor or "." not in valor:
      raise ClienteInvalidoError(
          f"Correo electrónico inválido: '{valor}'. Formato incorrecto."
      )
    self._correo = valor.strip()

  @property
  def telefono(self):
    return self._telefono

  @telefono.setter
  def telefono(self, valor):
    if not valor or not str(valor).isdigit() or len(str(valor)) < 7:
      raise ClienteInvalidoError(
          f"Teléfono inválido: '{valor}'. Debe contener solo números y al"
          " menos 7 dígitos."
      )
    self._telefono = str(valor)

  def obtener_detalles(self) -> str:
    return (
        f"Cliente [ID: {self.identificador}, Nombre: {self.nombre},"
        f" Correo: {self.correo}, Teléfono: {self.telefono}]"
    )


class Servicio(EntidadBase, ABC):

  def __init__(self, identificador: str, nombre_servicio: str, costo_base: float):
    super().__init__(identificador)
    self.nombre_servicio = nombre_servicio
    self.costo_base = costo_base

  @property
  def costo_base(self):
    return self._costo_base

  @costo_base.setter
  def costo_base(self, valor):
    if valor < 0:
      raise ServicioNoDisponibleError(
          "El costo base no puede ser negativo: " + str(valor)
      )
    self._costo_base = float(valor)

  @abstractmethod
  def calcular_costo(self, *args, **kwargs) -> float:
    """Método abstracto para el cálculo polimórfico de costos."""
    pass

  def obtener_detalles(self) -> str:
    return (
        f"Servicio: {self.nombre_servicio} (ID: {self.identificador}) - Costo"
        f" Base: ${self.costo_base:.2f}"
    )


# ==========================================
# SERVICIOS ESPECIALIZADOS (POLIMORFISMO)
# ==========================================
class ReservaSalas(Servicio):

  def __init__(self, identificador: str, costo_base: float, capacidad: int):
    super().__init__(identificador, "Reserva de Salas", costo_base)
    self.capacidad = capacidad

  def calcular_costo(self, horas: int, aplicar_impuesto: bool = True) -> float:
    try:
      if horas <= 0:
        raise ValueError("Las horas de reserva deben ser mayores a cero.")
      costo_total = self.costo_base * horas
      if aplicar_impuesto:
        costo_total *= 1.19  # IVA del 19%
      return round(costo_total, 2)
    except Exception as e:
      # Encadenamiento de excepciones
      raise ServicioNoDisponibleError(
          f"Error al calcular costo de sala ID {self.identificador}"
      ) from e


class AlquilerEquipos(Servicio):

  def __init__(self, identificador: str, costo_base: float, tipo_equipo: str):
    super().__init__(identificador, "Alquiler de Equipos", costo_base)
    self.tipo_equipo = tipo_equipo

  # Método sobrecargado mediante argumentos opcionales / kwargs
  def calcular_costo(self, dias: int, descuento: float = 0.0) -> float:
    try:
      if dias <= 0:
        raise ValueError("Los días de alquiler deben ser mayores a cero.")
      if not (0.0 <= descuento <= 1.0):
        raise ValueError("El descuento debe estar entre 0.0 y 1.0.")
      costo_total = (self.costo_base * dias) * (1.0 - descuento)
      return round(costo_total, 2)
    except Exception as e:
      raise ServicioNoDisponibleError(
          f"Error al calcular costo de equipo ID {self.identificador}"
      ) from e


class AsesoriasEspecializadas(Servicio):

  def __init__(self, identificador: str, costo_base: float, especialista: str):
    super().__init__(identificador, "Asesorías Especializadas", costo_base)
    self.especialista = especialista

  def calcular_costo(
      self, sesiones: int, tarifa_plena: bool = True
  ) -> float:
    try:
      if sesiones <= 0:
        raise ValueError("El número de sesiones debe ser mayor a cero.")
      multiplicador = 1.25 if tarifa_plena else 1.0
      costo_total = self.costo_base * sesiones * multiplicador
      return round(costo_total, 2)
    except Exception as e:
      raise ServicioNoDisponibleError(
          f"Error al calcular asesoría ID {self.identificador}"
      ) from e


# ==========================================
# CLASE RESERVA CON MANIOBRA AVANZADA
# ==========================================
class Reserva:

  def __init__(self, id_reserva: str, cliente: Cliente, servicio: Servicio, parametro_uso: int):
    self.id_reserva = id_reserva
    self.cliente = cliente
    self.servicio = servicio
    self.parametro_uso = parametro_uso
    self.estado = "Creada"
    self.costo_calculado = 0.0

  def procesar_reserva(self):
    # Uso de bloques try/except/else/finally exigidos por la guía
    try:
      logging.info(f"Iniciando procesamiento de reserva {self.id_reserva}")
      if not isinstance(self.cliente, Cliente):
        raise ReservaFallidaError("La reserva no tiene un cliente válido asociado.")
      if not isinstance(self.servicio, Servicio):
        raise ReservaFallidaError("La reserva no tiene un servicio válido asociado.")

      # Cálculo polimórfico dependiendo del tipo de servicio
      if isinstance(self.servicio, ReservaSalas):
        self.costo_calculado = self.servicio.calcular_costo(self.parametro_uso, aplicar_impuesto=True)
      elif isinstance(self.servicio, AlquilerEquipos):
        self.costo_calculado = self.servicio.calcular_costo(self.parametro_uso, descuento=0.1)
      elif isinstance(self.servicio, AsesoriasEspecializadas):
        self.costo_calculado = self.servicio.calcular_costo(self.parametro_uso, tarifa_plena=True)
      else:
        raise ReservaFallidaError("Tipo de servicio desconocido en la reserva.")

      self.estado = "Confirmada"

    except (ClienteInvalidoError, ServicioNoDisponibleError, ReservaFallidaError) as e:
      self.estado = "Fallida"
      logging.error(f"Error controlado en reserva {self.id_reserva}: {str(e)}")
      print(f"[ERROR CONTROLADO] Reserva {self.id_reserva}: {e}")
    except Exception as e:
      self.estado = "Error Crítico"
      logging.critical(f"Excepción no prevista en reserva {self.id_reserva}: {str(e)}")
      print(f"[ERROR CRÍTICO] Reserva {self.id_reserva}: {e}")
    else:
      # Se ejecuta si no hubo excepciones
      print(f"[ÉXITO] Reserva {self.id_reserva} procesada correctamente. Costo total: ${self.costo_calculado:.2f}")
      logging.info(f"Reserva {self.id_reserva} confirmada con éxito por un valor de ${self.costo_calculado:.2f}")
    finally:
      # Se ejecuta siempre, ideal para cierres o registros de cierre de operación
      print(f"-> Finalizó intento de procesamiento para la reserva {self.id_reserva}.\n")


# ==========================================
# SIMULACIÓN DE 10 OPERACIONES (EXIGENCIA GUÍA)
# ==========================================
def ejecutar_simulacion():
  print("=== INICIANDO SIMULACIÓN DE 10 OPERACIONES DE SOFTWARE FJ ===\n")

  # Operación 1: Registro de cliente válido
  print("--- Operación 1: Registro de Cliente Válido ---")
  try:
    c1 = Cliente("C001", "Ana María Gómez", "ana.gomez@unad.edu.co", "3104567890")
    print(c1.obtener_detalles())
    logging.info("Operación 1 exitosa: Cliente registrado.")
  except Exception as e:
    print(f"Error: {e}")
  print("-" * 50)

  # Operación 2: Registro de cliente con datos inválidos (Dispara excepción)
  print("--- Operación 2: Registro de Cliente con Error (Nombre corto) ---")
  try:
    c_error = Cliente("C002", "Jo", "correo_malo.com", "123")
  except Exception as e:
    print(f"Excepción capturada exitosamente: {e}")
    logging.warning(f"Operación 2 manejada correctamente: {e}")
  print("-" * 50)

  # Operación 3: Creación correcta de servicio de sala
  print("--- Operación 3: Creación de Servicio (Reserva de Salas) ---")
  try:
    sala1 = ReservaSalas("S001", 50000.0, 20)
    print(sala1.obtener_detalles())
    logging.info("Operación 3 exitosa: Servicio de sala creado.")
  except Exception as e:
    print(f"Error: {e}")
  print("-" * 50)

  # Operación 4: Creación de servicio con costo negativo (Dispara excepción)
  print("--- Operación 4: Creación de Servicio con Costo Negativo ---")
  try:
    sala_err = ReservaSalas("S002", -100.0, 10)
  except Exception as e:
    print(f"Excepción capturada exitosamente: {e}")
    logging.warning(f"Operación 4 manejada correctamente: {e}")
  print("-" * 50)

  # Operación 5: Creación de Alquiler de Equipos
  print("--- Operación 5: Creación de Alquiler de Equipos ---")
  try:
    equipo1 = AlquilerEquipos("E001", 35000.0, "Portátil Core i7")
    print(equipo1.obtener_detalles())
    logging.info("Operación 5 exitosa: Alquiler de equipo creado.")
  except Exception as e:
    print(f"Error: {e}")
  print("-" * 50)

  # Operación 6: Creación de Asesoría Especializada
  print("--- Operación 6: Creación de Asesoría Especializada ---")
  try:
    asesoria1 = AsesoriasEspecializadas("A001", 120000.0, "Dr. Carlos Pérez")
    print(asesoria1.obtener_detalles())
    logging.info("Operación 6 exitosa: Asesoría creada.")
  except Exception as e:
    print(f"Error: {e}")
  print("-" * 50)

  # Operación 7: Reserva exitosa de Sala (Uso de Try/Except/Else/Finally)
  print("--- Operación 7: Reserva Exitosa de Sala ---")
  try:
    cli_val = Cliente("C003", "Pedro Picapiedra", "pedro@stone.com", "3201234567")
    sala_val = ReservaSalas("S100", 40000.0, 15)
    reserva1 = Reserva("R001", cli_val, sala_val, 4) # 4 horas
    reserva1.procesar_reserva()
  except Exception as e:
    print(f"Error en simulación 7: {e}")
  print("-" * 50)

  # Operación 8: Reserva fallida por horas inválidas
  print("--- Operación 8: Reserva con Horas Negativas (Fallida Controlada) ---")
  try:
    reserva2 = Reserva("R002", cli_val, sala_val, -2)
    reserva2.procesar_reserva()
  except Exception as e:
    print(f"Error: {e}")
  print("-" * 50)

  # Operación 9: Reserva exitosa de Alquiler de Equipos con Descuento
  print("--- Operación 9: Reserva de Equipos Exitosa ---")
  try:
    reserva3 = Reserva("R003", cli_val, equipo1, 5) # 5 días
    reserva3.procesar_reserva()
  except Exception as e:
    print(f"Error: {e}")
  print("-" * 50)

  # Operación 10: Reserva de Asesoría con parámetros correctos
  print("--- Operación 10: Reserva de Asesoría Exitosa ---")
  try:
    reserva4 = Reserva("R004", cli_val, asesoria1, 2) # 2 sesiones
    reserva4.procesar_reserva()
  except Exception as e:
    print(f"Error: {e}")
  print("=== FIN DE LA SIMULACIÓN ===")


if __name__ == "__main__":
  ejecutar_simulacion()