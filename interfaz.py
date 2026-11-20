#Interfaz
import tkinter as tk
from tkinter import ttk, messagebox
import logging
#Clases

from main import (Cliente, ReservaSalas, AlquilerEquipos,
                  AsesoriasEspecializadas, Reserva, ClienteInvalidoError)

clientes = {}
reservas = []

# Servicis 
servicios = {
    "Reserva de Salas (hora)": ReservaSalas("S100", 40000.0, 15),
    "Alquiler de Equipos (días)": AlquilerEquipos("E001", 35000.0, "Portátil Core i7"),
    "Asesorías especializadas (sesion)": Asesoriasespecializadas("A001", 120000.0, "Dr. Carlos Pérez"),
}

#registro
def registrar_cliente():
    try:
        id_cliente = f"C{len(clientes) + 1:03d}"
        cliente = Cliente(id_cliente, entry_nombre.get(), entry_correo.get(), entry_telefono.get())
        clientes[id_cliente] = cliente
        combo_cliente["values"] = [f"{k} - {v.nombre}" for k, v in clientes.items()]
        logging.info(f"Cliente registrado desde la interfaz: {id_cliente}")
        messagebox.showinfo("Éxitoso", "Cliente registrado correctamente")
        for e in (entry_nombre, entry_correo, entry_telefono):
            e.delete(0, tk.END)
    except ClienteInvalidoError as e:
        logging.warning(f"Registro de cliente incorrecto: {e}")
        messagebox.showerror("Error", str(e))



#Reserva
def crear_reserva():
    try:
        if not combo_cliente.get() or not combo_servicio.get():
            raise ValueError("Debe elegir un cliente y un srvicio.")
        cliente = clientes[combo_cliente.get().split(" - ")[0]]
        servicio = servicios[combo_servicio.get()]
        cantidad = int(entry_cantidad.get())

        reserva = Reserva(f"R{len(reservas) + 1:03d}", cliente, servicio, cantidad)
        reserva.procesar_reserva() 
        reservas.append(reserva)

        resultado = f"{reserva.id_reserva} | {cliente.nombre} | {reserva.estado} | ${reserva.costo_calculado:,.2f}"
        lista.insert(tk.END, resultado)
        if reserva.estado == "Confirmado":
            messagebox.showinfo("Reserva", f"Reserva confirmada. Costo: ${reserva.costo_calculado:,.2f}")
        else:
            messagebox.showwarning("Reserva", "La reserva falló. Revise nuevamente el sistema.log")
    except ValueError as e:
        logging.error(f"Dato incorrecto al crear reserva: {e}")
        messagebox.showerror("Error", f"Dato incorrecto: {e}")

#ventana creada
ventana = tk.Tk()
ventana.title("Software FJ")
ventana.geometry("420x560")
tk.Label(ventana, text="Registrar cliente", font=("Arial", 12, "bold")).pack(pady=5)
tk.Label(ventana, text="Nombre:").pack()
entry_nombre = tk.Entry(ventana, width=35); entry_nombre.pack()
tk.Label(ventana, text="Correo:").pack()
entry_correo = tk.Entry(ventana, width=35); entry_correo.pack()
tk.Label(ventana, text="Teléfono:").pack()
entry_telefono = tk.Entry(ventana, width=35); entry_telefono.pack()
tk.Button(ventana, text="Registrar cliente", command=registrar_cliente).pack(pady=5)
tk.Label(ventana, text="Crear reserva", font=("Arial", 12, "bold")).pack(pady=5)
tk.Label(ventana, text="Cliente:").pack()
combo_cliente = ttk.Combobox(ventana, state="readonly", width=32); combo_cliente.pack()
tk.Label(ventana, text="Servicio:").pack()
combo_servicio = ttk.Combobox(ventana, values=list(servicios), state="readonly", width=32); combo_servicio.pack()
tk.Label(ventana, text="Cantidad (horas / días / sesiones):").pack()
entry_cantidad = tk.Entry(ventana, width=35); entry_cantidad.pack()
tk.Button(ventana, text="Reservar", command=crear_reserva).pack(pady=5)
tk.Label(ventana, text="Reservas realizadas:").pack()
lista = tk.Listbox(ventana, width=55); lista.pack(pady=5)
ventana.mainloop()
