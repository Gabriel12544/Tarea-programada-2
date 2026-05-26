#Elaborado por: Gabriel Gómez Fallas y Saul Dorado Ureña
#Fecha de creación 19/05/2026
#Versión 3.10.12
#ultima versión 5:24 del 19 de mayo del 2026
#Aporte de Gabriel Gómez Fallas 
#Elaborado por: Gabriel Gómez Fallas y Saul Dorado Ureña
#Fecha de creación 19/05/2026
#Versión 3.10.12
#Última versión: Mayo 2026
import re
import os
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk             #añadido
from datetime import datetime       #añadido

# Estructura global en Matriz (RAM)
baseDonantes = []
archivoPersistente = "donantes_incompleto.txt"

# Catálogo de provincias según el primer dígito de la cédula
provinciasCatalogo = {
    "1": "San José", "2": "Alajuela", "3": "Cartago", "4": "Heredia",
    "5": "Guanacaste", "6": "Puntarenas", "7": "Limón", "8": "Naturalizado"
}


#########################################################################
# ===================================================================== #
#               BLOQUE 1: REQUERIMIENTOS LÓGICOS (3 CAPAS)              #
# ===================================================================== #
#########################################################################

# ==========================================
# REQUERIMIENTO: CÉDULA
# ==========================================

def auxValidarCedula(cedula: str) -> bool:
    """Función de Validación: Comprueba el formato #-####-#### sin ceros al inicio."""
    if not isinstance(cedula, str): 
        return False
    patron = r"^[1-9]-\d{4}-\d{4}$"
    return bool(re.match(patron, cedula))

def registrarCedulaLogica(cedula: str) -> str:
    """Función Principal: Determina la provincia según el primer dígito."""
    provinciaId = cedula[0]
    return provinciasCatalogo.get(provinciaId, "Desconocida")

def llamarRegistrarCedulaLogica(entradaCedulaWidget) -> tuple:
    """Función de Llamada: Gestiona la desacoplación con la interfaz."""
    cedulaTexto = entradaCedulaWidget.get() if hasattr(entradaCedulaWidget, 'get') else entradaCedulaWidget
    if auxValidarCedula(cedulaTexto):
        provincia = registrarCedulaLogica(cedulaTexto)
        return True, provincia
    else:
        return False, "Formato de cédula inválido. Debe ser #-####-#### (Sin iniciar en 0)."

def llamarRegistrarCedulaLogica(entradaCedulaWidget) -> tuple:
    """Función de Llamada: Gestiona la desacoplación con la interfaz."""
    cedulaTexto = entradaCedulaWidget.get() if hasattr(entradaCedulaWidget, 'get') else entradaCedulaWidget
    if auxValidarCedula(cedulaTexto):
        provincia = registrarCedulaLogica(cedulaTexto)
        return True, provincia
    else:
        return False, "Formato de cédula inválido. Debe ser #-####-#### (Sin iniciar en 0)."

#modificacion E2 Avance 1 Sem 2
# ==========================================
# REQUERIMIENTO: PESO
# ==========================================

def auxValidarPeso(entrada: str) -> bool:
    """funcionalidad: Valida si la cadena ingresada corresponde a un valor numerico entero o decimal positivo."""
    patron = r"^\d+(\.\d+)?$"
    if re.match(patron, entrada):
        if float(entrada) > 0:
            return True
    return False

def evaluarPesoDonacion(pesoNum: float) -> bool:
    """funcionalidad: Evalua si el peso cumple con el requisito minimo establecido de 50 kg para poder donar."""
    return pesoNum >= 50.0

def llamarEvaluarPesoDonacion(entradaPesoWidget) -> tuple:
    """funcionalidad: Coordina la validacion de la entrada del peso y determina si el valor es apto para la donacion."""
    pesoTexto = entradaPesoWidget.get() if hasattr(entradaPesoWidget, 'get') else entradaPesoWidget
    if not auxValidarPeso(pesoTexto):
        return False, "El peso debe ser un número mayor a cero."
    
    pesoNumerico = float(pesoTexto)
    if evaluarPesoDonacion(pesoNumerico):
        return True, "Cumple con el peso mínimo."
    else:
        return False, "Dado su peso actual usted no cumple con el mínimo de 50 kg para donar."

# ==========================================
# REQUERIMIENTO: CORREO ELECTRÓNICO
# ==========================================

def auxValidarCorreo(correo: str) -> bool:
    """funcionalidad: Valida si el formato del correo electronico cumple con el estandar internacional."""
    patron = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(patron, correo))

#Hasta aquí

#########################################################################
# ===================================================================== #
#                 BLOQUE 2: PERSISTENCIA Y CAMPOS VACÍOS                #
# ===================================================================== #
#########################################################################

def auxVerificarCamposVacios(datos: dict) -> bool:
    """Valida que ninguna de las entradas del formulario esté en blanco."""
    for valor in datos.values():
        if str(valor).strip() == "":
            return False
    return True

def guardarMatrizAArchivo() -> bool:
    """Almacena secuencialmente la matriz RAM en el archivo de texto separado por ';'."""
    try:
        with open(archivoPersistente, "w", encoding="utf-8") as f:
            for donante in baseDonantes:
                linea = ";".join(str(campo) for campo in donante)
                f.write(linea + "\n")
        return True
    except Exception as e:
        print(f"Error crítico al persistir información: {e}")
        return False


#########################################################################
# ===================================================================== #
#             BLOQUE 3: INTERFAZ GRÁFICA INCOMPLETA (HASTA SEXO)        #
# ===================================================================== #
#########################################################################
#Programación orientada a objetos
class AppDonacionesIncompleta:
    def __init__(self, root):
        self.root = root
        self.root.title("TEC - Registro Incompleto de Donadores")
        self.root.geometry("850x450")  # Ventana más compacta al tener menos campos
        self.root.resizable(False, False)
        
        # Paleta de Colores Solicitada (Azul, Blanco, Celeste)
        self.cBg = "#f4f7f6"           # Fondo principal claro (Blanco suave)
        self.cPanel = "#ffffff"        # Tarjetas internas en Blanco Puro
        self.cBrand = "#0f4c81"        # Azul Clásico Institucional
        self.cCeleste = "#aed9e0"      # Celeste suave para destaques y bordes
        self.cCelesteOsc = "#5e9ca7"   # Celeste oscuro para texto secundario legible
        self.cTextDark = "#1c2541"     # Texto principal oscuro
        self.cEntryBg = "#f8f9fa"      # Fondo grisáceo muy claro para inputs
        
        self.root.configure(bg=self.cBg)
        self.crearComponentes()

#modificacion E2 Avance 1 Sem 2        
    def crearComponentes(self):
        # Se estableció el tamaño de la ventana para que quepan todos los campos
        self.root.geometry("850x600") 
        self.root.resizable(False, False)
        
        # PANEL IZQUIERDO: Branding Institucional (Azul Real)
        panelIzq = tk.Frame(self.root, bg=self.cBrand, width=280, height=600)
        panelIzq.pack(side=tk.LEFT, fill=tk.Y)
        panelIzq.pack_propagate(False)
        
        lblTituloInst = tk.Label(panelIzq, text="TEC", font=("Helvetica", 28, "bold"), bg=self.cBrand, fg="#ffffff")
        lblTituloInst.pack(pady=(40, 5))
        
        lblSubInst = tk.Label(panelIzq, text="Tecnológico\nde Costa Rica", font=("Helvetica", 12), bg=self.cBrand, fg=self.cCeleste)
        lblSubInst.pack(pady=5)
        
        canvasLinea = tk.Canvas(panelIzq, width=180, height=2, bg="#ffffff", highlightthickness=0)
        canvasLinea.pack(pady=20)
        
        infoProyecto = (
            "SISTEMA DE REGISTRO\n"
            "DE DONADORES\n\n"
            "Formulario Completo\n"
            "Taller de Programación\n\n"
            "Desarrollado por:\n"
            "• Gabriel Gómez F.\n"
            "• Saul Dorado U."
        )
        lblInfo = tk.Label(panelIzq, text=infoProyecto, font=("Helvetica", 11), bg=self.cBrand, fg="#ffffff", justify=tk.CENTER)
        lblInfo.pack(pady=10)

        # PANEL DERECHO: Formulario Completo
        panelDer = tk.Frame(self.root, bg=self.cBg, width=570, height=600)
        panelDer.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        panelDer.pack_propagate(False)
        
        lblFormTitle = tk.Label(panelDer, text="Formulario de Inscripción Completo", font=("Helvetica", 18, "bold"), bg=self.cBg, fg=self.cTextDark)
        lblFormTitle.pack(anchor=tk.W, padx=40, pady=(20, 10))
        
        # Tarjeta interna contenedora
        self.card = tk.Frame(panelDer, bg=self.cPanel, padx=25, pady=15, bd=1, relief=tk.SOLID, highlightbackground=self.cCeleste, highlightcolor=self.cBrand)
        self.card.pack(fill=tk.BOTH, expand=True, padx=40, pady=(0, 20))
        
        # Grid del Formulario Completo
        # Fila 0: Nombre Completo
        self.crearLabel("Nombre Completo:", 0, 0)
        self.txtNombre = self.crearEntry(0, 1)
        
        # Fila 1: Cédula
        self.crearLabel("Cédula (#-####-####):", 1, 0)
        self.txtCedula = self.crearEntry(1, 1)
        
        # Fila 2: Sexo / Género
        self.crearLabel("Sexo / Género:", 2, 0)
        self.valSexo = tk.StringVar(value="Masculino")
        frameRadio = tk.Frame(self.card, bg=self.cPanel)
        frameRadio.grid(row=2, column=1, sticky=tk.W, pady=6)
        rbM = tk.Radiobutton(frameRadio, text="Masculino", variable=self.valSexo, value="Masculino", bg=self.cPanel, fg=self.cTextDark, selectcolor="#ffffff")
        rbF = tk.Radiobutton(frameRadio, text="Femenino", variable=self.valSexo, value="Femenino", bg=self.cPanel, fg=self.cTextDark, selectcolor="#ffffff")
        rbM.pack(side=tk.LEFT, padx=(0, 20))
        rbF.pack(side=tk.LEFT)

        # Fila 3: Fecha de Nacimiento
        self.crearLabel("Fecha Nacimiento (DD/MM/AAAA):", 3, 0)
        self.txtFecha = self.crearEntry(3, 1)

        # Fila 4: Peso
        self.crearLabel("Peso en Kilogramos (ej: 68.5):", 4, 0)
        self.txtPeso = self.crearEntry(4, 1)

        # Fila 5: Correo Electrónico
        self.crearLabel("Correo Electrónico:", 5, 0)
        self.txtCorreo = self.crearEntry(5, 1)

        # Fila 6: Tipo de Sangre (Menú Desplegable)
        self.crearLabel("Tipo de Sangre:", 6, 0)
        self.comboSangre = ttk.Combobox(self.card, values=["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"], state="readonly", font=("Helvetica", 11))
        self.comboSangre.grid(row=6, column=1, sticky=tk.EW, pady=6, ipady=2)
        self.comboSangre.set("Seleccione...")
        
        # Sección de botones de control (Fila 7)
        frameBotones = tk.Frame(self.card, bg=self.cPanel)
        frameBotones.grid(row=7, column=0, columnspan=2, pady=(25, 0), sticky=tk.EW)
        
        btnGuardar = tk.Button(frameBotones, text="REGISTRAR DONANTE", command=self.procesarFormulario, bg=self.cBrand, fg="#ffffff", font=("Helvetica", 11, "bold"), bd=0, height=2, cursor="hand2")
        btnGuardar.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))
        
        btnLimpiar = tk.Button(frameBotones, text="Limpiar Campos", command=self.limpiarCampos, bg=self.cCeleste, fg=self.cTextDark, font=("Helvetica", 10, "bold"), bd=0, height=2, cursor="hand2")
        btnLimpiar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

#hasta aqui

    def crearLabel(self, texto, fila, columna):
        lbl = tk.Label(self.card, text=texto, font=("Helvetica", 10, "bold"), bg=self.cPanel, fg=self.cTextDark)
        lbl.grid(row=fila, column=columna, sticky=tk.W, pady=12, padx=(0, 15))
        return lbl
        
    def crearEntry(self, fila, columna):
        entry = tk.Entry(self.card, font=("Helvetica", 11), bg=self.cEntryBg, fg=self.cTextDark, bd=0, insertbackground=self.cTextDark, highlightthickness=1, highlightbackground="#d1d7e0", highlightcolor=self.cBrand)
        entry.grid(row=fila, column=columna, sticky=tk.EW, pady=12, ipady=4)
        self.card.grid_columnconfigure(columna, weight=1)
        return entry

#avance
    def limpiarCampos(self):
        """Limpia las entradas actuales de la interfaz gráfica."""
        self.txtNombre.delete(0, tk.END)
        self.txtCedula.delete(0, tk.END)
        self.valSexo.set("Masculino")
        self.txtFecha.delete(0, tk.END)  #añadido
        self.txtPeso.delete(0, tk.END)   #añadido
        self.txtCorreo.delete(0, tk.END)  #añadido 
        self.comboSangre.set("Seleccione...")   #añadido
#modificado
    def procesarFormulario(self):
        """Orquesta las validaciones de todos los campos e inserta el registro completo."""
        datosFormulario = {
            "nombre": self.txtNombre.get().strip(),
            "cedula": self.txtCedula.get().strip(),
            "fecha_nacimiento": self.txtFecha.get().strip(),
            "peso": self.txtPeso.get().strip(),
            "correo": self.txtCorreo.get().strip(),
            "sangre": self.comboSangre.get()
        }

        # 1. Comprobación de campos vacíos o sin seleccionar sangre
        if not auxVerificarCamposVacios(datosFormulario) or datosFormulario["sangre"] == "Seleccione...":
            messagebox.showerror("Campos Incompletos", "Por favor rellene todos los campos obligatorios del formulario.")
            return

        # 2. Validación de Cédula (Capa Llamada)
        valCed, resCed = llamarRegistrarCedulaLogica(self.txtCedula)
        if not valCed:
            messagebox.showerror("Validación Fallida", resCed)
            return

        # 3. Validación de Fecha de Nacimiento (Mayoría de edad)
        valFecha, resFecha = llamadaValidarFecha(self.txtFecha)
        if not valFecha:
            messagebox.showerror("Validación Fallida", resFecha)
            return

        # 4. Validación de Peso (Mínimo 50 kg y evaluación de estados)
        valPeso, resPeso = llamarEvaluarPesoDonacion(self.txtPeso)
        if not valPeso:
            messagebox.showerror("Validación Fallida", resPeso)
            return

        # 5. Validación de Correo Electrónico
        if not auxValidarCorreo(datosFormulario["correo"]):
            messagebox.showerror("Validación Fallida", "El formato del correo electrónico es inválido.")
            return

        # Sincronización de variables físicas (Sexo)
        sexoBool = True if self.valSexo.get() == "Masculino" else False
        
        # 6. Inserción estructurada completa en Matriz RAM
        nuevaFilaDonante = [
            datosFormulario["nombre"],
            datosFormulario["cedula"],
            sexoBool,
            datosFormulario["fecha_nacimiento"],
            float(datosFormulario["peso"]),
            datosFormulario["correo"],
            datosFormulario["sangre"]
        ]
        
        baseDonantes.append(nuevaFilaDonante)
        guardarMatrizAArchivo()

        # Despliegue de confirmación con la bitácora completa en la ventana emergente
        msgExito = (
            f"¡Registro Completado Exitosamente!\n\n"
            f"• Nombre: {datosFormulario['nombre']}\n"
            f"• Cédula: {datosFormulario['cedula']}\n"
            f"• Provincia: {resCed}\n"
            f"• Condición: {resFecha}\n"
            f"• Peso: {datosFormulario['peso']} kg\n"
            f"• Correo: {datosFormulario['correo']}\n"
            f"• Sangre: {datosFormulario['sangre']}\n\n"
            f"Ficha guardada de forma persistente en {archivoPersistente}."
        )
        messagebox.showinfo("Inserción Exitosa", msgExito)
        self.limpiarCampos()
        #hasta aqui

# ===================================================================== #
#                        INICIALIZADOR DEL SISTEMA                      #
# ===================================================================== #
if __name__ == "__main__":
    rootWindow = tk.Tk()
    app = AppDonacionesIncompleta(rootWindow)
    rootWindow.mainloop()