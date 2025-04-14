#------------------------------------------------------------------
#Librerias
#------------------------------------------------------------------
import streamlit as st
#Leer códigos QR
import cv2
import numpy as np
from PIL import Image
#Guardar los registros en un documento en la nube
from streamlit_gsheets import GSheetsConnection
import pandas as pd
#------------------------------------------------------------------
#Funciones
#------------------------------------------------------------------
#Limpiar y leer dataframe
def limpiar_y_leer(Libro,Hoja):
    try:
        st.cache_data.clear()
        conn = st.connection(Libro, type=GSheetsConnection)
        datosDeLibroHoja = conn.read(worksheet=Hoja)
        df = pd.DataFrame(datosDeLibroHoja)
        return df
    except:
        return
#Revisar Información
def revisarInfo(Libro,Hoja,FolioQR,LecturaQR,ValorPorBuscar):
    try:
        df = limpiar_y_leer(Libro,Hoja)
        if LecturaQR in df[FolioQR].values:
            valorObtenido = df.loc[df[FolioQR] == LecturaQR, ValorPorBuscar].iloc[0]
            return valorObtenido
    except:
        return
#Registrar asistencia
def registrarAsistencia(Libro,Hoja,LecturaQR,Duplicados,lineRegistro,tipoU,alias):
    df = limpiar_y_leer(Libro,Hoja)
    if LecturaQR in df[Duplicados].values:
        st.success(LecturaQR)
        st.warning("Ya ha sido registrado su asistencia")
        st.info(f"Usuario {tipoU}")
        st.info(f"Alias {alias}")
        st.stop()
    else:
        conexion = st.connection(Libro, type=GSheetsConnection)
        nuevaLinea = pd.concat([df, lineRegistro], ignore_index=False)
        conexion.update(worksheet=Hoja, data=nuevaLinea)
        st.success(LecturaQR)
        st.success("Se registro su asistencia correctamente")
        st.info(f"Usuario {tipoU}")
        st.info(f"Alias {alias}")
        st.stop()
#------------------------------------------------------------------
#Principal
#------------------------------------------------------------------
#Activar y desactivar la cámara
enable = st.checkbox("Activar camara")
#Función principal
picture = st.camera_input("Leer QR", disabled=not enable)
#Imagen guardada en el buffer
if picture is not None:
    # leer imagen
    image = Image.open(picture)
    image_np = np.array(image)
    gray_image = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
    detector = cv2.QRCodeDetector()
    #Decodificar QR
    data, points, _ = detector.detectAndDecode(gray_image)
    # Guardar registros
    if data:
        RevisarU = revisarInfo("gsheets_pagosregistrados","RespuestasPago","PreubasFormato",data,"Dirección de correo electrónico")
        if RevisarU is not None:
            tipoU = revisarInfo("gsheets_pagosregistrados","RespuestasPago","PreubasFormato",data,"TipoDeUsuario")
            alias = revisarInfo("gsheets_pagosregistrados","RespuestasPago","PreubasFormato",data,"¿Quieres usar tu nombre en tu gafete o personalizarlo?")
            lineRegistro = pd.DataFrame(
                [
                    {
                        "NombreCompleto" : data,
                        "Correo" : RevisarU,
                        "Tipo" : tipoU,
                        "Alias" : alias,
                    }
                ]
            )
            registrarAsistencia("gsheets_asistencia","Asistencia",data,"NombreCompleto",lineRegistro,tipoU,alias)
        else:
            st.warning("QR no corresponde al registro.")
    else:
        st.error("No hay códigos QR en la imagen.")
#Fin
