# Elaborado por: Gabriel Gómez Fallas y Saúl Dorado Ureña
# Fecha de creación: 19/05/2026
# Última versión: 27/05/2026 8:12pm
# Versión de Python: 3.10.12

import re
import os
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from datetime import datetime

# Estructura global en Matriz (RAM)
# Estructura de cada fila: [Nombre, Cédula, Sexo(Bool), FechaNac, Peso(float), Correo, Sangre]
baseDonantes = []
archivoPersistente = "donantes_completo.txt"
#avance 6
INDICENombre = 0
INDICECedula = 1
INDICESexo = 2
INDICEFechaNacimiento = 3
INDICEPeso = 4
INDICECorreo = 5
INDICESangre = 6

# Tupla global de tipos de sangre requerida por la especificación
TIPOS_SANGRE_GLOBAL = ("O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-")

# Catálogo de provincias según el primer dígito de la cédula
provinciasCatalogo = {
    "1": "San José", "2": "Alajuela", "3": "Cartago", "4": "Heredia",
    "5": "Guanacaste", "6": "Puntarenas", "7": "Limón", "8": "Naturalizado"
}

#########################################################################
# ===================================================================== #
#                BLOQUE 1: REQUERIMIENTOS LÓGICOS (3 CAPAS)              #
# ===================================================================== #
#########################################################################

def cargarArchivoAMatriz():
    """Lee el archivo plano al arrancar y recupera los datos en la RAM."""
    global baseDonantes
    if os.path.exists(archivoPersistente):
        try:
            with open(archivoPersistente, "r", encoding="utf-8") as f:
                for linea in f:
                    linea = linea.strip()
                    if linea:
                        campos = linea.split(";")
                        campos[2] = campos[2] == "True"
                        campos[4] = float(campos[4])
                        baseDonantes.append(campos)
        except Exception as e:
            print(f"Error al cargar el almacenamiento persistente: {e}")

def auxValidarCedula(cedula: str) -> bool:
    patron = r"^[1-9]-\d{4}-\d{4}$"
    return bool(re.match(patron, cedula))

def registrarCedulaLogica(cedula: str) -> str:
    provinciaId = cedula[0]
    return provinciasCatalogo.get(provinciaId, "Desconocida")

def llamarRegistrarCedulaLogica(entradaCedulaWidget) -> tuple:
    cedulaTexto = entradaCedulaWidget.get().strip() if hasattr(entradaCedulaWidget, 'get') else str(entradaCedulaWidget).strip()
    if auxValidarCedula(cedulaTexto):
        provincia = registrarCedulaLogica(cedulaTexto)
        return True, provincia
    return False, "Formato de cédula inválido. Debe ser #-####-#### (Sin iniciar en 0)."

def auxValidarPeso(entrada: str) -> bool:
    patron = r"^\d+(\.\d+)?$"
    if re.match(patron, entrada) and float(entrada) > 0:
        return True
    return False

def evaluarPesoDonacion(pesoNum: float) -> bool:
    return pesoNum >= 50.0

def llamarEvaluarPesoDonacion(entradaPesoWidget) -> tuple:
    pesoTexto = entradaPesoWidget.get().strip() if hasattr(entradaPesoWidget, 'get') else str(entradaPesoWidget).strip()
    if not auxValidarPeso(pesoTexto):
        return False, "El peso debe ser un número mayor a cero."
    if evaluarPesoDonacion(float(pesoTexto)):
        return True, "Cumple con el peso mínimo."
    return False, "Dado su peso actual usted no cumple con el mínimo de 50 kg para donar."

def auxValidarFecha(fecha_str: str) -> bool:
    return bool(re.match(r"^\d{2}/\d{2}/\d{4}$", fecha_str))

def calcularEdadExacta(fecha_str: str) -> int:
    fecha_nac = datetime.strptime(fecha_str, "%d/%m/%Y").date()
    hoy = datetime.now().date()
    return hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))

def evaluarEdadLogica(fecha_str: str) -> tuple:
    try:
        edad = calcularEdadExacta(fecha_str)
    except ValueError:
        return False, "La fecha ingresada no es válida en el calendario."
    if edad >= 18:
        return True, f"Apto: Mayor de edad ({edad} años)."
    return False, f"Rechazado: Debe ser mayor de edad. Edad actual: {edad} años."

def llamadaValidarFecha(entradaFechaWidget) -> tuple:
    fechaTexto = entradaFechaWidget.get().strip() if hasattr(entradaFechaWidget, 'get') else str(entradaFechaWidget).strip()
    if not auxValidarFecha(fechaTexto):
        return False, "El formato de fecha debe ser DD/MM/AAAA."
    return evaluarEdadLogica(fechaTexto)

def auxValidarCorreo(correo: str) -> bool:
    return bool(re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", correo))

def auxVerificarCamposVacios(datos: dict) -> bool:
    for valor in datos.values():
        if str(valor).strip() == "":
            return False
    return True

def guardarMatrizAArchivo() -> bool:
    try:
        with open(archivoPersistente, "w", encoding="utf-8") as f:
            for donante in baseDonantes:
                linea = ";".join(str(campo) for campo in donante)
                f.write(linea + "\n")
        return True
    except Exception as e:
        print(f"Error crítico al persistir información: {e}")
        return False

#avance 6
def buscarDonantePorCedula(cedula):
    """
    Funcionalidad: Buscar un donante dentro de la matriz principal.
    Entradas:
    - cedula(str): número de identificación del donante.
    Salidas:
    - indice(int | None): posición del donante o None si no existe.
    """
    for indice, donante in enumerate(baseDonantes):
        if donante[INDICECedula] == cedula:
            return indice
    return None

def validarDatosActualizacion(datosDonante):
    """
    Funcionalidad: Validar los datos ingresados para actualizar un donante.
    Entradas:
    - datosDonante(dict): información nueva del donante.
    Salidas:
    - resultado(tuple): estado y mensaje de validación.
    """
    if not auxVerificarCamposVacios(datosDonante):
        return False, "Todos los campos son obligatorios."

    if not auxValidarFecha(datosDonante["fechaNacimiento"]):
        return False, "La fecha debe tener formato DD/MM/AAAA."

    if not auxValidarPeso(datosDonante["peso"]):
        return False, "El peso debe ser numérico y mayor a cero."

    if not auxValidarCorreo(datosDonante["correo"]):
        return False, "El correo electrónico es inválido."

    if datosDonante["sangre"] == "Seleccione...":
        return False, "Debe seleccionar un tipo de sangre."

    return True, "Datos válidos."

def procesarActualizacionDonante(indiceDonante, datosDonante):
    """
    Funcionalidad: Actualizar los datos de un donante existente.
    Entradas:
    - indiceDonante(int): posición del donante en la matriz.
    - datosDonante(dict): datos nuevos del donante.
    Salidas:
    - resultado(tuple): estado y mensaje final.
    """
    sexoBool = True if datosDonante["sexo"] == "Masculino" else False

    baseDonantes[indiceDonante][INDICENombre] = datosDonante["nombreCompleto"]
    baseDonantes[indiceDonante][INDICESexo] = sexoBool
    baseDonantes[indiceDonante][INDICEFechaNacimiento] = datosDonante["fechaNacimiento"]
    baseDonantes[indiceDonante][INDICEPeso] = float(datosDonante["peso"])
    baseDonantes[indiceDonante][INDICECorreo] = datosDonante["correo"]
    baseDonantes[indiceDonante][INDICESangre] = datosDonante["sangre"]

    if guardarMatrizAArchivo():
        return True, "Datos actualizados correctamente."

    return False, "No fue posible guardar los cambios."

# ==========================================
# LÓGICA LOGÍSTICA DE REPORTES (HTML 5)
# ==========================================

def generarReporteProvinciaLogica(provincia_destino: str) -> bool:
    donantes_filtrados = []
    for d in baseDonantes:
        cedula = d[1]
        prov_donante = registrarCedulaLogica(cedula)
        if prov_donante.lower() == provincia_destino.lower():
            donantes_filtrados.append(d)
            
    donantes_filtrados = sorted(donantes_filtrados, key=lambda x: x[0])
    fecha_hora_sistema = datetime.now().strftime("%d/%m/%Y %I:%M:%S %p")
    nombre_archivo = f"reporte_donantes_{provincia_destino.lower().replace(' ', '_')}.html"
    
    try:
        with open(nombre_archivo, "w", encoding="utf-8") as html:
            html.write("<!DOCTYPE html>\n<html lang='es'>\n<head>\n  <meta charset='UTF-8'>\n")
            html.write(f"  <title>Reporte de Donantes - {provincia_destino}</title>\n")
            html.write("  <style>\n")
            html.write("    body { font-family: 'Helvetica Neue', Arial, sans-serif; background-color: #f4f7f6; color: #1c2541; margin: 0; padding: 40px; }\n")
            html.write("    .container { max-width: 1000px; background: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-top: 8px solid #0f4c81; margin: 0 auto; }\n")
            html.write("    h1 { color: #0f4c81; margin-top: 0; font-size: 24px; text-transform: uppercase; border-bottom: 2px solid #aed9e0; padding-bottom: 10px; }\n")
            html.write("    .meta-info { font-size: 14px; color: #5e9ca7; margin-bottom: 30px; font-style: italic; }\n")
            html.write("    table { width: 100%; border-collapse: collapse; margin-top: 10px; }\n")
            html.write("    th { background-color: #0f4c81; color: white; padding: 12px; text-align: left; font-size: 14px; text-transform: uppercase; }\n")
            html.write("    td { padding: 12px; border-bottom: 1px solid #e1e8ed; font-size: 14px; }\n")
            html.write("    tr:nth-child(even) { background-color: #f8f9fa; }\n")
            html.write("    tr:hover { background-color: #eef7f9; }\n")
            html.write("    .no-data { text-align: center; color: #95a5a6; padding: 40px; font-size: 16px; }\n")
            html.write("  </style>\n</head>\n<body>\n  <div class='container'>\n")
            html.write(f"    <h1>Reporte de Donantes Activos por Provincia: {provincia_destino}</h1>\n")
            html.write(f"    <div class='meta-info'>Emitido el: {fecha_hora_sistema} | Taller de Programación (TEC)</div>\n")
            
            if not donantes_filtrados:
                html.write(f"    <div class='no-data'>No se encuentran registrados donantes activos procedentes de la provincia de {provincia_destino}.</div>\n")
            else:
                html.write("    <table>\n      <thead>\n        <tr>\n          <th>Cédula</th>\n          <th>Nombre Completo</th>\n          <th>Fecha Nacimiento</th>\n          <th>Teléfono</th>\n          <th>Correo Electrónico</th>\n        </tr>\n      </thead>\n      <tbody>\n")
                for donante in donantes_filtrados:
                    html.write(f"        <tr>\n          <td><strong>{donante[1]}</strong></td>\n          <td>{donante[0]}</td>\n          <td>{donante[3]}</td>\n          <td>No asignado</td>\n          <td>{donante[5]}</td>\n        </tr>\n")
                html.write("      </tbody>\n    </table>\n")
            html.write("  </div>\n</body>\n</html>")
        return True
    except Exception as e:
        print(f"Error al escribir HTML: {e}")
        return False

def generarReporteEdadLogica(edad_ini: int, edad_fin: int | None) -> bool:  #se usa | en vez de or
    donantes_filtrados = []
    for d in baseDonantes:
        edad_donante = calcularEdadExacta(d[3])
        if edad_fin is None:
            if edad_donante == edad_ini:
                donantes_filtrados.append(d)
        else:
            if edad_ini <= edad_donante <= edad_fin:
                donantes_filtrados.append(d)
                
    donantes_filtrados = sorted(donantes_filtrados, key=lambda x: x[0])
    fecha_hora_sistema = datetime.now().strftime("%d/%m/%Y %I:%M:%S %p")
    titulo_reporte = f"Análisis Científico de Donantes - Edad: {edad_ini}" if edad_fin is None else f"Análisis Científico de Donantes - Rango: {edad_ini} a {edad_fin} años"
    nombre_archivo = f"reporte_donantes_edad_{edad_ini}.html" if edad_fin is None else f"reporte_donantes_rango_{edad_ini}_{edad_fin}.html"
    
    try:
        with open(nombre_archivo, "w", encoding="utf-8") as html:
            html.write("<!DOCTYPE html>\n<html lang='es'>\n<head>\n  <meta charset='UTF-8'>\n")
            html.write(f"  <title>{titulo_reporte}</title>\n")
            html.write("  <style>\n")
            html.write("    body { font-family: 'Helvetica Neue', Arial, sans-serif; background-color: #f4f7f6; color: #1c2541; margin: 0; padding: 40px; }\n")
            html.write("    .container { max-width: 1000px; background: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-top: 8px solid #0f4c81; margin: 0 auto; }\n")
            html.write("    h1 { color: #0f4c81; margin-top: 0; font-size: 22px; text-transform: uppercase; border-bottom: 2px solid #aed9e0; padding-bottom: 10px; }\n")
            html.write("    .meta-info { font-size: 14px; color: #5e9ca7; margin-bottom: 30px; font-style: italic; }\n")
            html.write("    table { width: 100%; border-collapse: collapse; margin-top: 10px; }\n")
            html.write("    th { background-color: #0f4c81; color: white; padding: 12px; text-align: left; font-size: 14px; text-transform: uppercase; }\n")
            html.write("    td { padding: 12px; border-bottom: 1px solid #e1e8ed; font-size: 14px; }\n")
            html.write("    tr:nth-child(even) { background-color: #f8f9fa; }\n")
            html.write("    tr:hover { background-color: #eef7f9; }\n")
            html.write("    .no-data { text-align: center; color: #95a5a6; padding: 40px; font-size: 16px; }\n")
            html.write("  </style>\n</head>\n<body>\n  <div class='container'>\n")
            html.write(f"    <h1>{titulo_reporte}</h1>\n")
            html.write(f"    <div class='meta-info'>Emitido el: {fecha_hora_sistema} | Calidad de vida en Donantes | TEC</div>\n")
            
            if not donantes_filtrados:
                html.write("    <div class='no-data'>No se encontraron registros de donadores activos en los parámetros de edad evaluados.</div>\n")
            else:
                html.write("    <table>\n      <thead>\n        <tr>\n          <th>Cédula</th>\n          <th>Nombre Completo</th>\n          <th>Fecha Nacimiento</th>\n          <th>Teléfono</th>\n          <th>Correo Electrónico</th>\n        </tr>\n      </thead>\n      <tbody>\n")
                for donante in donantes_filtrados:
                    html.write(f"        <tr>\n          <td><strong>{donante[1]}</strong></td>\n          <td>{donante[0]}</td>\n          <td>{donante[3]}</td>\n          <td>No asignado</td>\n          <td>{donante[5]}</td>\n        </tr>\n")
                html.write("      </tbody>\n    </table>\n")
            html.write("  </div>\n</body>\n</html>")
        return True
    except Exception as e:
        print(f"Error al escribir HTML de edad: {e}")
        return False

def generarReporteSangreProvinciaLogica(tipoSangre: str, provinciaDestino: str) -> bool:
    """Filtra simultáneamente por tipo de sangre y por provincia de origen."""
    donantes_filtrados = []
    for d in baseDonantes:
        cedula = d[1]
        sangre_donante = d[6]
        prov_donante = registrarCedulaLogica(cedula)
        
        if sangre_donante == tipoSangre and prov_donante.lower() == provinciaDestino.lower():
            donantes_filtrados.append(d)
            
    # Ordenamiento alfabético por Nombre Completo
    donantes_filtrados = sorted(donantes_filtrados, key=lambda x: x[0])
    fecha_hora_sistema = datetime.now().strftime("%d/%m/%Y %I:%M:%S %p")
    
    # Formatear el nombre del archivo según la especificación
    sangre_limpia = tipoSangre.replace("+", "_pos").replace("-", "_neg")
    prov_limpia = provinciaDestino.lower().replace(" ", "_")
    nombre_archivo = f"reporte_emergencia_{sangre_limpia}_{prov_limpia}.html"
    
    try:
        with open(nombre_archivo, "w", encoding="utf-8") as html:
            html.write("<!DOCTYPE html>\n<html lang='es'>\n<head>\n  <meta charset='UTF-8'>\n")
            html.write(f"  <title>Localización de Emergencia - {tipoSangre}</title>\n")
            html.write("  <style>\n")
            html.write("    body { font-family: 'Helvetica Neue', Arial, sans-serif; background-color: #f4f7f6; color: #1c2541; margin: 0; padding: 40px; }\n")
            html.write("    .container { max-width: 1000px; background: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 4px 15px rgba(230,57,70,0.15); border-top: 8px solid #e63946; margin: 0 auto; }\n")
            html.write("    h1 { color: #e63946; margin-top: 0; font-size: 22px; text-transform: uppercase; border-bottom: 2px solid #f9dcc4; padding-bottom: 10px; }\n")
            html.write("    .meta-info { font-size: 14px; color: #5e9ca7; margin-bottom: 30px; font-style: italic; }\n")
            html.write("    table { width: 100%; border-collapse: collapse; margin-top: 10px; }\n")
            html.write("    th { background-color: #e63946; color: white; padding: 12px; text-align: left; font-size: 14px; text-transform: uppercase; }\n")
            html.write("    td { padding: 12px; border-bottom: 1px solid #e1e8ed; font-size: 14px; }\n")
            html.write("    tr:nth-child(even) { background-color: #f8f9fa; }\n")
            html.write("    tr:hover { background-color: #fdf0f0; }\n")
            html.write("    .no-data { text-align: center; color: #95a5a6; padding: 40px; font-size: 16px; font-weight: bold; }\n")
            html.write("  </style>\n</head>\n<body>\n  <div class='container'>\n")
            html.write(f"    <h1>Lista de Donadores Potenciales: Sangre {tipoSangre} en {provinciaDestino}</h1>\n")
            html.write(f"    <div class='meta-info'>Localización de Emergencia - Emitido el: {fecha_hora_sistema} | TEC</div>\n")
            
            if not donantes_filtrados:
                html.write(f"    <div class='no-data'>No se encuentran registrados donantes activos del tipo {tipoSangre} procedentes de {provinciaDestino}.</div>\n")
            else:
                html.write("    <table>\n      <thead>\n        <tr>\n          <th>Cédula</th>\n          <th>Nombre Completo</th>\n          <th>Fecha Nacimiento</th>\n          <th>Teléfono</th>\n          <th>Correo Electrónico</th>\n        </tr>\n      </thead>\n      <tbody>\n")
                for donante in donantes_filtrados:
                    html.write(f"        <tr>\n          <td><strong>{donante[1]}</strong></td>\n          <td>{donante[0]}</td>\n          <td>{donante[3]}</td>\n          <td>No asignado</td>\n          <td>{donante[5]}</td>\n        </tr>\n")
                html.write("      </tbody>\n    </table>\n")
            html.write("  </div>\n</body>\n</html>")
        return True
    except Exception as e:
        print(f"Error al generar reporte de emergencia: {e}")
        return False


#########################################################################
# ===================================================================== #
#            BLOQUE 2: INTERFAZ GRÁFICA COMPLETA CON MENÚS              #
# ===================================================================== #
#########################################################################

class AppDonacionesTEC:
    def __init__(self, root):
        self.root = root
        self.root.title("TEC - Control General de Donadores de Sangre")
        self.root.geometry("880x620")
        self.root.resizable(False, False)
        
        self.cBg = "#f4f7f6"
        self.cPanel = "#ffffff"
        self.cBrand = "#0f4c81"
        self.cCeleste = "#aed9e0"
        self.cTextDark = "#1c2541"
        self.cEntryBg = "#f8f9fa"
        
        self.root.configure(bg=self.cBg)
        self.contenedor_actual = None
        self.cargarMenuPrincipal()

    def limpiarVentanaAnterior(self):
        if self.contenedor_actual is not None:
            self.contenedor_actual.destroy()

    def cargarMenuPrincipal(self):
        self.limpiarVentanaAnterior()
        self.contenedor_actual = tk.Frame(self.root, bg=self.cBg)
        self.contenedor_actual.pack(fill=tk.BOTH, expand=True)
        
        panelIzq = tk.Frame(self.contenedor_actual, bg=self.cBrand, width=290, height=620)
        panelIzq.pack(side=tk.LEFT, fill=tk.Y)
        panelIzq.pack_propagate(False)
        
        tk.Label(panelIzq, text="TEC", font=("Helvetica", 36, "bold"), bg=self.cBrand, fg="#ffffff").pack(pady=(60, 5))
        tk.Label(panelIzq, text="Menú Principal\nde Operaciones", font=("Helvetica", 14), bg=self.cBrand, fg=self.cCeleste).pack(pady=5)
        
        panelDer = tk.Frame(self.contenedor_actual, bg=self.cBg)
        panelDer.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=50, pady=50)
        
        tk.Label(panelDer, text="Seleccione una Opción del Sistema", font=("Helvetica", 20, "bold"), bg=self.cBg, fg=self.cTextDark).pack(anchor=tk.W, pady=(0, 40))
        
        btnFormulario = tk.Button(panelDer, text="FORMULARIO DE INSCRIPCIÓN", command=self.cargarFormularioInscripcion, bg=self.cPanel, fg=self.cBrand, font=("Helvetica", 12, "bold"), bd=1, relief=tk.SOLID, highlightbackground=self.cCeleste, height=3, cursor="hand2")
        btnFormulario.pack(fill=tk.X, pady=15)
        
        btnReportesMenu = tk.Button(panelDer, text="SISTEMA DE REPORTES ELECTRÓNICOS", command=self.cargarVentanaMenuReportes, bg=self.cPanel, fg=self.cBrand, font=("Helvetica", 12, "bold"), bd=1, relief=tk.SOLID, highlightbackground=self.cCeleste, height=3, cursor="hand2")
        btnReportesMenu.pack(fill=tk.X, pady=15)
    
    #avance 6
        btnActualizar = tk.Button(
            panelDer,
            text="ACTUALIZAR DONANTE",
            command=self.cargarVentanaActualizarDonante,
            bg=self.cPanel,
            fg=self.cBrand,
            font=("Helvetica", 12, "bold"),
            bd=1,
            relief=tk.SOLID,
            highlightbackground=self.cCeleste,
            height=3,
            cursor="hand2"
        )
        btnActualizar.pack(fill=tk.X, pady=15)
        
        btnSalir = tk.Button(panelDer, text="Salir", command=self.root.quit, bg="#e63946", fg="#ffffff", font=("Helvetica", 11, "bold"), bd=0, height=2, width=15, cursor="hand2")
        btnSalir.pack(anchor=tk.E, pady=(100, 0))

    def cargarFormularioInscripcion(self):
        self.limpiarVentanaAnterior()
        self.contenedor_actual = tk.Frame(self.root, bg=self.cBg)
        self.contenedor_actual.pack(fill=tk.BOTH, expand=True)
        
        panelIzq = tk.Frame(self.contenedor_actual, bg=self.cBrand, width=290, height=620)
        panelIzq.pack(side=tk.LEFT, fill=tk.Y)
        panelIzq.pack_propagate(False)
        
        tk.Label(panelIzq, text="TEC", font=("Helvetica", 32, "bold"), bg=self.cBrand, fg="#ffffff").pack(pady=(40, 5))
        tk.Label(panelIzq, text="Inscripción Completa", font=("Helvetica", 12), bg=self.cBrand, fg=self.cCeleste).pack(pady=5)
        
        panelDer = tk.Frame(self.contenedor_actual, bg=self.cBg, width=590, height=620)
        panelDer.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        panelDer.pack_propagate(False)
        
        lblFormTitle = tk.Label(panelDer, text="Formulario de Inscripción de Donantes", font=("Helvetica", 18, "bold"), bg=self.cBg, fg=self.cTextDark)
        lblFormTitle.pack(anchor=tk.W, padx=35, pady=(20, 10))
        
        self.card = tk.Frame(panelDer, bg=self.cPanel, padx=25, pady=15, bd=1, relief=tk.SOLID, highlightbackground=self.cCeleste)
        self.card.pack(fill=tk.BOTH, expand=True, padx=35, pady=(0, 20))
        
        self.crearLabel("Nombre Completo:", 0, 0)
        self.txtNombre = self.crearEntry(0, 1)
        
        self.crearLabel("Cédula (#-####-####):", 1, 0)
        self.txtCedula = self.crearEntry(1, 1)
        
        self.crearLabel("Sexo / Género:", 2, 0)
        self.valSexo = tk.StringVar(value="Masculino")
        frameRadio = tk.Frame(self.card, bg=self.cPanel)
        frameRadio.grid(row=2, column=1, sticky=tk.W, pady=6)
        tk.Radiobutton(frameRadio, text="Masculino", variable=self.valSexo, value="Masculino", bg=self.cPanel, fg=self.cTextDark).pack(side=tk.LEFT, padx=(0, 20))
        tk.Radiobutton(frameRadio, text="Femenino", variable=self.valSexo, value="Femenino", bg=self.cPanel, fg=self.cTextDark).pack(side=tk.LEFT)

        self.crearLabel("Fecha Nacimiento (DD/MM/AAAA):", 3, 0)
        self.txtFecha = self.crearEntry(3, 1)

        self.crearLabel("Peso en Kilogramos (ej: 68.5):", 4, 0)
        self.txtPeso = self.crearEntry(4, 1)

        self.crearLabel("Correo Electrónico:", 5, 0)
        self.txtCorreo = self.crearEntry(5, 1)

        self.crearLabel("Tipo de Sangre:", 6, 0)
        self.comboSangre = ttk.Combobox(self.card, values=list(TIPOS_SANGRE_GLOBAL), state="readonly", font=("Helvetica", 11))
        self.comboSangre.grid(row=6, column=1, sticky=tk.EW, pady=8, ipady=2)
        self.comboSangre.set("Seleccione...")
        
        frameBotones = tk.Frame(self.card, bg=self.cPanel)
        frameBotones.grid(row=7, column=0, columnspan=2, pady=(20, 0), sticky=tk.EW)
        
        btnGuardar = tk.Button(frameBotones, text="REGISTRAR", command=self.procesarFormulario, bg=self.cBrand, fg="#ffffff", font=("Helvetica", 11, "bold"), bd=0, height=2, cursor="hand2")
        btnGuardar.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))
        
        btnVolver = tk.Button(frameBotones, text="Regresar al Menú", command=self.cargarMenuPrincipal, bg=self.cCeleste, fg=self.cTextDark, font=("Helvetica", 10, "bold"), bd=0, height=2, cursor="hand2")
        btnVolver.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))    
#Avance 6
    def cargarVentanaActualizarDonante(self):

        self.limpiarVentanaAnterior()

        self.contenedor_actual = tk.Frame(self.root, bg=self.cBg)
        self.contenedor_actual.pack(fill=tk.BOTH, expand=True)

        panelIzq = tk.Frame(
            self.contenedor_actual,
            bg=self.cBrand,
            width=290,
            height=620
        )

        panelIzq.pack(side=tk.LEFT, fill=tk.Y)
        panelIzq.pack_propagate(False)

        tk.Label(
            panelIzq,
            text="TEC",
            font=("Helvetica", 32, "bold"),
            bg=self.cBrand,
            fg="#ffffff"
        ).pack(pady=(40, 5))

        tk.Label(
            panelIzq,
            text="Actualizar Donante",
            font=("Helvetica", 12),
            bg=self.cBrand,
            fg=self.cCeleste
        ).pack(pady=5)

        panelDer = tk.Frame(
            self.contenedor_actual,
            bg=self.cBg,
            width=590,
            height=620
        )

        panelDer.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        panelDer.pack_propagate(False)

        tk.Label(
            panelDer,
            text="Actualización de Donantes",
            font=("Helvetica", 18, "bold"),
            bg=self.cBg,
            fg=self.cTextDark
        ).pack(anchor=tk.W, padx=35, pady=(20, 10))

        self.cardActualizar = tk.Frame(
            panelDer,
            bg=self.cPanel,
            padx=25,
            pady=15,
            bd=1,
            relief=tk.SOLID,
            highlightbackground=self.cCeleste
        )

        self.cardActualizar.pack(
            fill=tk.BOTH,
            expand=True,
            padx=35,
            pady=(0, 20)
        )

        tk.Label(
            self.cardActualizar,
            text="Buscar Cédula:",
            font=("Helvetica", 10, "bold"),
            bg=self.cPanel,
            fg=self.cTextDark
        ).grid(row=0, column=0, sticky=tk.W, pady=6)

        self.txtCedulaBuscar = tk.Entry(
            self.cardActualizar,
            font=("Helvetica", 11)
        )

        self.txtCedulaBuscar.grid(
            row=0,
            column=1,
            sticky=tk.EW,
            pady=6
        )

        btnBuscar = tk.Button(
            self.cardActualizar,
            text="Buscar",
            command=self.buscarDatosDonante,
            bg=self.cBrand,
            fg="#ffffff",
            font=("Helvetica", 10, "bold"),
            bd=0,
            cursor="hand2"
        )

        btnBuscar.grid(row=0, column=2, padx=10)

        self.cardActualizar.grid_columnconfigure(1, weight=1)

        self.crearLabelActualizar("Nombre Completo:", 1, 0)
        self.txtNombreActualizar = self.crearEntryActualizar(1, 1)

        self.crearLabelActualizar("Sexo / Género:", 2, 0)

        self.valSexoActualizar = tk.StringVar(value="Masculino")

        frameRadio = tk.Frame(self.cardActualizar, bg=self.cPanel)
        frameRadio.grid(row=2, column=1, sticky=tk.W)

        tk.Radiobutton(
            frameRadio,
            text="Masculino",
            variable=self.valSexoActualizar,
            value="Masculino",
            bg=self.cPanel
        ).pack(side=tk.LEFT)

        tk.Radiobutton(
            frameRadio,
            text="Femenino",
            variable=self.valSexoActualizar,
            value="Femenino",
            bg=self.cPanel
        ).pack(side=tk.LEFT)

        self.crearLabelActualizar("Fecha Nacimiento:", 3, 0)
        self.txtFechaActualizar = self.crearEntryActualizar(3, 1)

        self.crearLabelActualizar("Peso:", 4, 0)
        self.txtPesoActualizar = self.crearEntryActualizar(4, 1)

        self.crearLabelActualizar("Correo:", 5, 0)
        self.txtCorreoActualizar = self.crearEntryActualizar(5, 1)

        self.crearLabelActualizar("Tipo Sangre:", 6, 0)

        self.comboSangreActualizar = ttk.Combobox(
            self.cardActualizar,
            values=list(TIPOS_SANGRE_GLOBAL),
            state="readonly",
            font=("Helvetica", 11)
        )

        self.comboSangreActualizar.grid(
            row=6,
            column=1,
            sticky=tk.EW,
            pady=8
        )

        self.comboSangreActualizar.set("Seleccione...")

        frameBotones = tk.Frame(
            self.cardActualizar,
            bg=self.cPanel
        )

        frameBotones.grid(
            row=7,
            column=0,
            columnspan=3,
            pady=(20, 0),
            sticky=tk.EW
        )

        btnGuardar = tk.Button(
            frameBotones,
            text="Guardar Cambios",
            command=self.llamarActualizarDonante,
            bg=self.cBrand,
            fg="#ffffff",
            font=("Helvetica", 11, "bold"),
            bd=0,
            height=2,
            cursor="hand2"
        )

        btnGuardar.pack(
            side=tk.RIGHT,
            fill=tk.X,
            expand=True,
            padx=(10, 0)
        )

        btnRegresar = tk.Button(
            frameBotones,
            text="Regresar",
            command=self.cargarMenuPrincipal,
            bg=self.cCeleste,
            fg=self.cTextDark,
            font=("Helvetica", 10, "bold"),
            bd=0,
            height=2,
            cursor="hand2"
        )

        btnRegresar.pack(
            side=tk.LEFT,
            fill=tk.X,
            expand=True,
            padx=(0, 10)
        )


    def crearLabelActualizar(self, texto, fila, columna):

        lbl = tk.Label(
            self.cardActualizar,
            text=texto,
            font=("Helvetica", 10, "bold"),
            bg=self.cPanel,
            fg=self.cTextDark
        )

        lbl.grid(
            row=fila,
            column=columna,
            sticky=tk.W,
            pady=6,
            padx=(0, 15)
        )

        return lbl


    def crearEntryActualizar(self, fila, columna):

        entry = tk.Entry(
            self.cardActualizar,
            font=("Helvetica", 11),
            bg=self.cEntryBg,
            fg=self.cTextDark,
            bd=0,
            highlightthickness=1,
            highlightbackground="#d1d7e0",
            highlightcolor=self.cBrand
        )

        entry.grid(
            row=fila,
            column=columna,
            sticky=tk.EW,
            pady=6,
            ipady=4
        )

        return entry


    def buscarDatosDonante(self):

        cedulaBuscar = self.txtCedulaBuscar.get().strip()

        indiceDonante = buscarDonantePorCedula(cedulaBuscar)

        if indiceDonante is None:

            messagebox.showerror(
                "No encontrado",
                f"La persona con el número de cédula: {cedulaBuscar} no está registrado."
            )

            return

        donante = baseDonantes[indiceDonante]

        self.txtNombreActualizar.delete(0, tk.END)
        self.txtNombreActualizar.insert(0, donante[INDICENombre])

        self.valSexoActualizar.set(
            "Masculino" if donante[INDICESexo] else "Femenino"
        )

        self.txtFechaActualizar.delete(0, tk.END)
        self.txtFechaActualizar.insert(0, donante[INDICEFechaNacimiento])

        self.txtPesoActualizar.delete(0, tk.END)
        self.txtPesoActualizar.insert(0, str(donante[INDICEPeso]))

        self.txtCorreoActualizar.delete(0, tk.END)
        self.txtCorreoActualizar.insert(0, donante[INDICECorreo])

        self.comboSangreActualizar.set(donante[INDICESangre])


    def llamarActualizarDonante(self):

        cedulaBuscar = self.txtCedulaBuscar.get().strip()

        indiceDonante = buscarDonantePorCedula(cedulaBuscar)

        if indiceDonante is None:

            messagebox.showerror(
                "Error",
                "No existe un donante registrado con esa cédula."
            )

            return

        datosDonante = {
            "nombreCompleto": self.txtNombreActualizar.get().strip(),
            "sexo": self.valSexoActualizar.get(),
            "fechaNacimiento": self.txtFechaActualizar.get().strip(),
            "peso": self.txtPesoActualizar.get().strip(),
            "correo": self.txtCorreoActualizar.get().strip(),
            "sangre": self.comboSangreActualizar.get()
        }

        valido, mensaje = validarDatosActualizacion(datosDonante)

        if not valido:

            messagebox.showerror(
                "Validación",
                mensaje
            )

            return

        actualizado, mensajeFinal = procesarActualizacionDonante(
            indiceDonante,
            datosDonante
        )

        if actualizado:

            messagebox.showinfo(
                "Actualización Exitosa",
                mensajeFinal
            )

            self.cargarMenuPrincipal()

        else:

            messagebox.showerror(
                "Error",
                mensajeFinal
            )

    def crearLabel(self, texto, fila, columna):
        lbl = tk.Label(self.card, text=texto, font=("Helvetica", 10, "bold"), bg=self.cPanel, fg=self.cTextDark)
        lbl.grid(row=fila, column=columna, sticky=tk.W, pady=6, padx=(0, 15))
        return lbl
        
    def crearEntry(self, fila, column):
        entry = tk.Entry(self.card, font=("Helvetica", 11), bg=self.cEntryBg, fg=self.cTextDark, bd=0, highlightthickness=1, highlightbackground="#d1d7e0", highlightcolor=self.cBrand)
        entry.grid(row=fila, column=column, sticky=tk.EW, pady=6, ipady=4)
        self.card.grid_columnconfigure(column, weight=1)
        return entry

    def limpiarCampos(self):
        self.txtNombre.delete(0, tk.END)
        self.txtCedula.delete(0, tk.END)
        self.valSexo.set("Masculino")
        self.txtFecha.delete(0, tk.END)
        self.txtPeso.delete(0, tk.END) 
        self.txtCorreo.delete(0, tk.END)  
        self.comboSangre.set("Seleccione...")

    def procesarFormulario(self):
        datosFormulario = {
            "nombre": self.txtNombre.get().strip(),
            "cedula": self.txtCedula.get().strip(),
            "fecha_nacimiento": self.txtFecha.get().strip(),
            "peso": self.txtPeso.get().strip(),
            "correo": self.txtCorreo.get().strip(),
            "sangre": self.comboSangre.get()
        }

        if not auxVerificarCamposVacios(datosFormulario) or datosFormulario["sangre"] == "Seleccione...":
            messagebox.showerror("Campos Incompletos", "Por favor, rellene todos los campos obligatorios.")
            return

        valCed, resCed = llamarRegistrarCedulaLogica(self.txtCedula)
        if not valCed:
            messagebox.showerror("Validación Fallida", resCed)
            return

        valFecha, resFecha = llamadaValidarFecha(self.txtFecha)
        if not valFecha:
            messagebox.showerror("Validación Fallida", resFecha)
            return

        valPeso, resPeso = llamarEvaluarPesoDonacion(self.txtPeso)
        if not valPeso:
            messagebox.showerror("Validación Fallida", resPeso)
            return

        if not auxValidarCorreo(datosFormulario["correo"]):
            messagebox.showerror("Validación Fallida", "El formato del correo electrónico es inválido.")
            return

        sexoBool = True if self.valSexo.get() == "Masculino" else False
        nuevaFilaDonante = [
            datosFormulario["nombre"], datosFormulario["cedula"], sexoBool,
            datosFormulario["fecha_nacimiento"], float(datosFormulario["peso"]),
            datosFormulario["correo"], datosFormulario["sangre"]
        ]
        baseDonantes.append(nuevaFilaDonante)
        
        if guardarMatrizAArchivo():
            messagebox.showinfo("Inserción Exitosa", f"¡Donante '{datosFormulario['nombre']}' registrado con éxito!")
            self.limpiarCampos()
        else:
            messagebox.showerror("Error", "Error al escribir en el almacenamiento persistente.")

    # ==========================================
    # PANTALLA: MENÚ GENERAL DE REPORTES
    # ==========================================
    def cargarVentanaMenuReportes(self):
        self.limpiarVentanaAnterior()
        self.contenedor_actual = tk.Frame(self.root, bg=self.cBg)
        self.contenedor_actual.pack(fill=tk.BOTH, expand=True)
        
        panelIzq = tk.Frame(self.contenedor_actual, bg=self.cBrand, width=290, height=620)
        panelIzq.pack(side=tk.LEFT, fill=tk.Y)
        panelIzq.pack_propagate(False)
        
        tk.Label(panelIzq, text="TEC", font=("Helvetica", 32, "bold"), bg=self.cBrand, fg="#ffffff").pack(pady=(40, 5))
        tk.Label(panelIzq, text="Panel de Reportes\nDisponibles", font=("Helvetica", 13), bg=self.cBrand, fg=self.cCeleste).pack(pady=5)
        
        panelDer = tk.Frame(self.contenedor_actual, bg=self.cBg)
        panelDer.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=40, pady=40)
        
        tk.Label(panelDer, text="Módulos de Impresión HTML5", font=("Helvetica", 18, "bold"), bg=self.cBg, fg=self.cTextDark).pack(anchor=tk.W, pady=(0, 20))
        
        btnProvincia = tk.Button(panelDer, text="Reporte 1: Donantes por Provincia", command=self.cargarSubventanaReporteProvincia, bg=self.cPanel, fg=self.cTextDark, font=("Helvetica", 11, "bold"), bd=1, relief=tk.SOLID, highlightbackground=self.cCeleste, height=2, anchor=tk.W, padx=20, cursor="hand2")
        btnProvincia.pack(fill=tk.X, pady=6)
        
        btnEdad = tk.Button(panelDer, text="Reporte 2: Análisis Científico por Edad", command=self.cargarSubventanaReporteEdad, bg=self.cPanel, fg=self.cTextDark, font=("Helvetica", 11, "bold"), bd=1, relief=tk.SOLID, highlightbackground=self.cCeleste, height=2, anchor=tk.W, padx=20, cursor="hand2")
        btnEdad.pack(fill=tk.X, pady=6)
        
        # NUEVO BOTÓN AGREGADO SEGÚN LA GUÍA VISUAL ADJUNTADA
        btnEmergencia = tk.Button(panelDer, text="Reporte 3: Emergencia por Sangre y Provincia", command=self.cargarSubventanaReporteSangreProvincia, bg=self.cPanel, fg="#e63946", font=("Helvetica", 11, "bold"), bd=1, relief=tk.SOLID, highlightbackground="#f9dcc4", height=2, anchor=tk.W, padx=20, cursor="hand2")
        btnEmergencia.pack(fill=tk.X, pady=6)
        
        btnRegresarPrincipal = tk.Button(panelDer, text="REGRESAR AL MENÚ PRINCIPAL", command=self.cargarMenuPrincipal, bg=self.cBrand, fg="#ffffff", font=("Helvetica", 11, "bold"), bd=0, height=2, cursor="hand2")
        btnRegresarPrincipal.pack(fill=tk.X, pady=(70, 0))

    def cargarSubventanaReporteProvincia(self):
        self.limpiarVentanaAnterior()
        self.contenedor_actual = tk.Frame(self.root, bg=self.cBg)
        self.contenedor_actual.pack(fill=tk.BOTH, expand=True)
        
        panelIzq = tk.Frame(self.contenedor_actual, bg=self.cBrand, width=290, height=620)
        panelIzq.pack(side=tk.LEFT, fill=tk.Y)
        panelIzq.pack_propagate(False)
        
        tk.Label(panelIzq, text="TEC", font=("Helvetica", 32, "bold"), bg=self.cBrand, fg="#ffffff").pack(pady=(40, 5))
        tk.Label(panelIzq, text="Filtro Geográfico", font=("Helvetica", 13), bg=self.cBrand, fg=self.cCeleste).pack(pady=5)
        
        panelDer = tk.Frame(self.contenedor_actual, bg=self.cBg)
        panelDer.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=40, pady=50)
        
        tk.Label(panelDer, text="Donantes por Provincia", font=("Helvetica", 18, "bold"), bg=self.cBg, fg=self.cTextDark).pack(anchor=tk.W, pady=(0, 10))
        
        descripcion = "Permite clasificar y ordenar alfabéticamente a los donantes según su provincia de procedencia."
        lblDesc = tk.Label(panelDer, text=descripcion, font=("Helvetica", 10), bg=self.cBg, fg="#5e9ca7", justify=tk.LEFT, wraplength=480)
        lblDesc.pack(anchor=tk.W, pady=(0, 35))
        
        cardFiltro = tk.Frame(panelDer, bg=self.cPanel, padx=25, pady=25, bd=1, relief=tk.SOLID, highlightbackground=self.cCeleste)
        cardFiltro.pack(fill=tk.X)
        
        tk.Label(cardFiltro, text="Seleccione la Provincia destino:", font=("Helvetica", 11, "bold"), bg=self.cPanel, fg=self.cTextDark).pack(anchor=tk.W, pady=(0, 10))
        
        lista_provincias = list(provinciasCatalogo.values())
        self.comboFiltroProvincia = ttk.Combobox(cardFiltro, values=lista_provincias, state="readonly", font=("Helvetica", 11))
        self.comboFiltroProvincia.pack(fill=tk.X, ipady=3)
        self.comboFiltroProvincia.set("San José")
        
        frameAcciones = tk.Frame(panelDer, bg=self.cBg)
        frameAcciones.pack(fill=tk.X, pady=40)
        
        btnGenerar = tk.Button(frameAcciones, text="GENERAR REPORTE", command=self.procesarImpresionReporteProvincia, bg=self.cBrand, fg="#ffffff", font=("Helvetica", 11, "bold"), bd=0, height=2, cursor="hand2")
        btnGenerar.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))
        
        btnRegresarReportes = tk.Button(frameAcciones, text="Regresar", command=self.cargarVentanaMenuReportes, bg=self.cCeleste, fg=self.cTextDark, font=("Helvetica", 10, "bold"), bd=0, height=2, cursor="hand2")
        btnRegresarReportes.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

    def procesarImpresionReporteProvincia(self):
        provincia_seleccionada = self.comboFiltroProvincia.get()
        exito = generarReporteProvinciaLogica(provincia_seleccionada)
        if exito:
            nombre_plano = f"reporte_donantes_{provincia_seleccionada.lower().replace(' ', '_')}.html"
            messagebox.showinfo("Reporte Finalizado", f"Reporte creado satisfactoriamente.\nArchivo generado: '{nombre_plano}'")
        else:
            messagebox.showerror("Error de E/S", "Reporte no creado.")

    def cargarSubventanaReporteEdad(self):
        self.limpiarVentanaAnterior()
        self.contenedor_actual = tk.Frame(self.root, bg=self.cBg)
        self.contenedor_actual.pack(fill=tk.BOTH, expand=True)
        
        panelIzq = tk.Frame(self.contenedor_actual, bg=self.cBrand, width=290, height=620)
        panelIzq.pack(side=tk.LEFT, fill=tk.Y)
        panelIzq.pack_propagate(False)
        
        tk.Label(panelIzq, text="TEC", font=("Helvetica", 32, "bold"), bg=self.cBrand, fg="#ffffff").pack(pady=(40, 5))
        tk.Label(panelIzq, text="Filtro Etario", font=("Helvetica", 13), bg=self.cBrand, fg=self.cCeleste).pack(pady=5)
        
        panelDer = tk.Frame(self.contenedor_actual, bg=self.cBg)
        panelDer.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=40, pady=40)
        
        tk.Label(panelDer, text="Análisis por Rango de Edad", font=("Helvetica", 18, "bold"), bg=self.cBg, fg=self.cTextDark).pack(anchor=tk.W, pady=(0, 5))
        
        descripcion = "Análisis científico sobre la calidad de vida de los donadores. Digite una edad base (18-65). La segunda caja se habilitará solo si la primera es válida."
        lblDesc = tk.Label(panelDer, text=descripcion, font=("Helvetica", 10), bg=self.cBg, fg="#5e9ca7", justify=tk.LEFT, wraplength=480)
        lblDesc.pack(anchor=tk.W, pady=(0, 25))
        
        cardEdad = tk.Frame(panelDer, bg=self.cPanel, padx=25, pady=20, bd=1, relief=tk.SOLID, highlightbackground=self.cCeleste)
        cardEdad.pack(fill=tk.X)
        
        self.valEdadIni = tk.StringVar()
        self.valEdadFin = tk.StringVar()
        self.valEdadIni.trace_add("write", self.auxControlarEstadoSegundaCaja)
        
        tk.Label(cardEdad, text="Edad Inicial (Obligatoria):", font=("Helvetica", 10, "bold"), bg=self.cPanel, fg=self.cTextDark).grid(row=0, column=0, sticky=tk.W, pady=8)
        self.txtEdadIni = tk.Entry(cardEdad, textvariable=self.valEdadIni, font=("Helvetica", 11), bg=self.cEntryBg, fg=self.cTextDark, bd=1, relief=tk.SOLID)
        self.txtEdadIni.grid(row=0, column=1, sticky=tk.EW, padx=(15, 0), pady=8, ipady=3)
        
        tk.Label(cardEdad, text="Edad Final (Opcional):", font=("Helvetica", 10, "bold"), bg=self.cPanel, fg=self.cTextDark).grid(row=1, column=0, sticky=tk.W, pady=8)
        self.txtEdadFin = tk.Entry(cardEdad, textvariable=self.valEdadFin, font=("Helvetica", 11), bg="#e9ecef", fg=self.cTextDark, bd=1, relief=tk.SOLID, state=tk.DISABLED)
        self.txtEdadFin.grid(row=1, column=1, sticky=tk.EW, padx=(15, 0), pady=8, ipady=3)
        
        cardEdad.grid_columnconfigure(1, weight=1)
        
        frameAcciones = tk.Frame(panelDer, bg=self.cBg)
        frameAcciones.pack(fill=tk.X, pady=35)
        
        btnGenerar = tk.Button(frameAcciones, text="GENERAR REPORTE", command=self.procesarImpresionReporteEdad, bg=self.cBrand, fg="#ffffff", font=("Helvetica", 11, "bold"), bd=0, height=2, cursor="hand2")
        btnGenerar.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))
        
        btnRegresarReportes = tk.Button(frameAcciones, text="Regresar", command=self.cargarVentanaMenuReportes, bg=self.cCeleste, fg=self.cTextDark, font=("Helvetica", 10, "bold"), bd=0, height=2, cursor="hand2")
        btnRegresarReportes.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

    def auxControlarEstadoSegundaCaja(self, *args):
        valor = self.valEdadIni.get().strip()
        if valor.isdigit():
            num = int(valor)
            if 18 <= num <= 65:
                self.txtEdadFin.config(state=tk.NORMAL, bg=self.cEntryBg)
                return
        self.txtEdadFin.config(state=tk.DISABLED, bg="#e9ecef")
        self.valEdadFin.set("")

    def procesarImpresionReporteEdad(self):
        ini_str = self.valEdadIni.get().strip()
        fin_str = self.valEdadFin.get().strip()
        
        if not ini_str:
            messagebox.showerror("Error de Datos", "Debe completar al menos el campo 'Edad Inicial'.")
            return
            
        if not ini_str.isdigit() or not (18 <= int(ini_str) <= 65):
            messagebox.showerror("Error de Rango", "La Edad Inicial debe estar en el rango de 18 a 65 años.")
            return

        edad_inicial = int(ini_str)
        edad_final = None

        if fin_str:
            if not fin_str.isdigit():
                messagebox.showerror("Error de Datos", "La Edad Final debe ser un valor numérico.")
                return
            edad_final = int(fin_str)
            if edad_final < edad_inicial:
                messagebox.showerror("Rango Inválido", "La Edad Final no puede ser menor a la Edad Inicial.")
                return
            if not (18 <= edad_final <= 65):
                messagebox.showerror("Error de Rango", "La Edad Final debe estar en el rango de 18 a 65 años.")
                return

        exito = generarReporteEdadLogica(edad_inicial, edad_final)
        if exito:
            nombre_archivo = f"reporte_donantes_{edad_inicial}.html" if edad_final is None else f"reporte_donantes_rango_{edad_inicial}_{edad_final}.html"
            messagebox.showinfo("Reporte Finalizado", f"Análisis etario generado satisfactoriamente.\nArchivo: '{nombre_archivo}'")
        else:
            messagebox.showerror("Error de E/S", "Ocurrió un error inesperado al escribir el reporte científico.")

    # =========================================================================
    # NUEVA PANTALLA: REQUERIMIENTO PARTE 3 - DISPONIBILIDAD POR SANGRE Y PROVINCIA
    # =========================================================================
    def cargarSubventanaReporteSangreProvincia(self):
        self.limpiarVentanaAnterior()
        
        self.contenedor_actual = tk.Frame(self.root, bg=self.cBg)
        self.contenedor_actual.pack(fill=tk.BOTH, expand=True)
        
        # Panel Izquierdo con estética de Alerta Médica
        panelIzq = tk.Frame(self.contenedor_actual, bg="#e63946", width=290, height=620)
        panelIzq.pack(side=tk.LEFT, fill=tk.Y)
        panelIzq.pack_propagate(False)
        
        tk.Label(panelIzq, text="TEC", font=("Helvetica", 32, "bold"), bg="#e63946", fg="#ffffff").pack(pady=(40, 5))
        tk.Label(panelIzq, text="Módulo de\nEmergencias", font=("Helvetica", 13, "bold"), bg="#e63946", fg="#f9dcc4").pack(pady=5)
        
        panelDer = tk.Frame(self.contenedor_actual, bg=self.cBg)
        panelDer.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=40, pady=35)
        
        tk.Label(panelDer, text="Localización Inmediata de Donantes", font=("Helvetica", 18, "bold"), bg=self.cBg, fg="#e63946").pack(anchor=tk.W, pady=(0, 5))
        
        descripcion = "Caso de Emergencia: Filtra la lista global cruzando el Tipo de Sangre requerido con la Provincia de procedencia para una ubicación en tiempo récord."
        lblDesc = tk.Label(panelDer, text=descripcion, font=("Helvetica", 10), bg=self.cBg, fg=self.cTextDark, justify=tk.LEFT, wraplength=480)
        lblDesc.pack(anchor=tk.W, pady=(0, 20))
        
        # Tarjeta de Parámetros Solicitados
        cardEmergencia = tk.Frame(panelDer, bg=self.cPanel, padx=25, pady=25, bd=1, relief=tk.SOLID, highlightbackground="#f9dcc4")
        cardEmergencia.pack(fill=tk.X)
        
        # Combo 1: Tipo de Sangre leído directamente desde la tupla global obligatoria
        tk.Label(cardEmergencia, text="Seleccione el Tipo de Sangre requerido:", font=("Helvetica", 10, "bold"), bg=self.cPanel, fg=self.cTextDark).pack(anchor=tk.W, pady=(0, 5))
        self.comboEmergenciaSangre = ttk.Combobox(cardEmergencia, values=list(TIPOS_SANGRE_GLOBAL), state="readonly", font=("Helvetica", 11))
        self.comboEmergenciaSangre.pack(fill=tk.X, pady=(0, 15), ipady=3)
        self.comboEmergenciaSangre.set("O+")
        
        # Combo 2: Provincia destino
        tk.Label(cardEmergencia, text="Seleccione la Provincia geográfica:", font=("Helvetica", 10, "bold"), bg=self.cPanel, fg=self.cTextDark).pack(anchor=tk.W, pady=(0, 5))
        lista_provincias = list(provinciasCatalogo.values())
        self.comboEmergenciaProvincia = ttk.Combobox(cardEmergencia, values=lista_provincias, state="readonly", font=("Helvetica", 11))
        self.comboEmergenciaProvincia.pack(fill=tk.X, ipady=3)
        self.comboEmergenciaProvincia.set("San José")
        
        # Botones de Acción
        frameAcciones = tk.Frame(panelDer, bg=self.cBg)
        frameAcciones.pack(fill=tk.X, pady=35)
        
        btnGenerar = tk.Button(frameAcciones, text=" GENERAR REPORTE", command=self.procesarImpresionReporteSangreProvincia, bg="#e63946", fg="#ffffff", font=("Helvetica", 11, "bold"), bd=0, height=2, cursor="hand2")
        btnGenerar.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))
        
        btnRegresarReportes = tk.Button(frameAcciones, text="Regresar", command=self.cargarVentanaMenuReportes, bg=self.cCeleste, fg=self.cTextDark, font=("Helvetica", 10, "bold"), bd=0, height=2, cursor="hand2")
        btnRegresarReportes.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

    def procesarImpresionReporteSangreProvincia(self):
        sangre_sel = self.comboEmergenciaSangre.get()
        provincia_sel = self.comboEmergenciaProvincia.get()
        
        exito = generarReporteSangreProvinciaLogica(sangre_sel, provincia_sel)
        
        if exito:
            sangre_limpia = sangre_sel.replace("+", "_pos").replace("-", "_neg")
            prov_limpia = provincia_sel.lower().replace(" ", "_")
            nombre_final = f"reporte_emergencia_{sangre_limpia}_{prov_limpia}.html"
            
            messagebox.showinfo("Reporte creado satisfactoriamente", f"Búsqueda finalizada.\nArchivo de emergencia guardado como: '{nombre_final}'")
        else:
            messagebox.showerror("Error del Sistema", "Reporte no creado.")


# ==========================================
# INICIALIZACIÓN DE LA APLICACIÓN
# ==========================================
if __name__ == "__main__":
    cargarArchivoAMatriz()
    rootPrincipal = tk.Tk()
    app = AppDonacionesTEC(rootPrincipal)
    rootPrincipal.mainloop()