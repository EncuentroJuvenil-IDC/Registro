import streamlit as st
#Leer códigos QR
import cv2
import numpy as np
from PIL import Image
#Guardar los registros en un documento en la nube
from streamlit_gsheets import GSheetsConnection
import pandas as pd

#Activar y desactivar la cámara
enable = st.checkbox("Enable camera")
#New
#Conectar los documentos de google
conn1 = st.connection("gsheets", type=GSheetsConnection)
preregistro = conn1.read(worksheet="RespuestasPRegistro")
conn2 = st.connection("gsheets_pagosregistrados", type=GSheetsConnection)
pagosregistrados = conn2.read(worksheet="RespuestasPago")
conn3 = st.connection("gsheets_asistencia", type=GSheetsConnection)
asistencia = conn3.read(worksheet="Asistencia")

def obtenerInfo(buscarNombre,column,bookname,sheetname,searching):
    st.cache_data.clear()
    conn = st.connection(bookname, type=GSheetsConnection)
    existing_data = conn.read(worksheet=sheetname)
    df = pd.DataFrame(existing_data)
    if buscarNombre in df[column].values:
        #Encontrar el index
        idx = df[df[column] == buscarNombre].index[0]
        return df.at[idx, searching]  #Regresa el valor guardado en la columna
    else:
        return None  #Nombre no esta en la lista

def registerABS(buscarNombre,registrar,tipo):
    st.cache_data.clear()
    conn3 = st.connection("gsheets_asistencia", type=GSheetsConnection)
    guardarasistencia = conn3.read(worksheet="Asistencia")
    if buscarNombre in guardarasistencia["NombreCompleto"].values:
        st.success(buscarNombre)
        st.warning("Ya ha sido registrado su asistencia")
        st.info(f"Usuario {tipo}")
        st.stop()
    else:
        new_to_add = registrar
        update_row = pd.concat([guardarasistencia, new_to_add], ignore_index=False)
        conn3.update(worksheet="Asistencia", data=update_row)
        st.success(buscarNombre)
        st.success("Se registro su asistencia correctamente")
        st.info(f"Usuario {tipo}")

#Función principal
picture = st.camera_input("Take a picture", disabled=not enable)

#Imagen guardada en el buffer
if picture is not None:
    # Convert the uploaded image to a format suitable for OpenCV
    image = Image.open(picture)
    image_np = np.array(image)
    # Convert to grayscale
    gray_image = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
    # Create a QRCodeDetector
    detector = cv2.QRCodeDetector()
    # Detect and decode the QR code
    data, points, _ = detector.detectAndDecode(gray_image)
    # Display the result
    if data:
        checkingName = obtenerInfo(data,"Nombre completo","gsheets_pagosregistrados","RespuestasPago","Dirección de correo electrónico")
        if checkingName is not None:
            tipoU = obtenerInfo(data,"Nombre completo","gsheets_pagosregistrados","RespuestasPago","TipoDeUsuario")
            new_row = pd.DataFrame(
                [
                    {
                        "NombreCompleto" : obtenerInfo(data,"Nombre completo","gsheets_pagosregistrados","RespuestasPago","Nombre completo"),
                        "Teléfono" : obtenerInfo(checkingName,"Dirección de correo electrónico","gsheets","RespuestasPRegistro","Teléfono"),
                        "Edad" : obtenerInfo(checkingName,"Dirección de correo electrónico","gsheets","RespuestasPRegistro","Edad"),
                        "Correo" : checkingName,
                        "Miembro o Visitante" : obtenerInfo(checkingName,"Dirección de correo electrónico","gsheets","RespuestasPRegistro","¿Miembro o Visitante?"),
                        "Tipo" : tipoU,
                    }
                ]
            )
            registerABS(data,new_row,tipoU)
        else:
            st.warning("No hay registros.")
    else:
        st.error("No hay códigos QR en la imagen.")
