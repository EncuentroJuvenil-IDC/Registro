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

#Conectar el documento de google
conn = st.connection("gsheets", type=GSheetsConnection)
#Conectar las hojas
existing_data = conn.read(worksheet="RespuestasFormulario")
asistencia = conn.read(worksheet="Asistencia")
otros = conn.read(worksheet="Otros")
df = pd.DataFrame(existing_data)

#Funcion de registro
def registerABS(Nombre = "Hola",lugarHoja = "Otros"):
    st.cache_data.clear()
    conn = st.connection("gsheets", type=GSheetsConnection)
    guardarEnHoja = conn.read(worksheet=lugarHoja)
    if Nombre in guardarEnHoja["RegistrosQR"].values:
        st.warning("El usario ya ha sido registrado")
        st.stop()
    else:
        new_to_add = pd.DataFrame([{"RegistrosQR": Nombre}])
        update_row = pd.concat([guardarEnHoja, new_to_add], ignore_index=False)
        conn.update(worksheet="Sabado", data=update_row)
        st.success("Se registro su asistencia correctamente")

#Funcion de revisar pago
def get_payment_for_name(df, name_to_check):
    st.cache_data.clear()
    conn = st.connection("gsheets", type=GSheetsConnection)
    existing_data = conn.read(worksheet="RespuestasFormulario")
    df = pd.DataFrame(existing_data)
    # Revisar el nombre en la lista
    if name_to_check in df['VariableAuxiliar'].values:
        #Encontrar el index
        idx = df[df['VariableAuxiliar'] == name_to_check].index[0]
        return df.at[idx, 'Pago']  #Regresa el valor guardado en la columna de pagos
    else:
        return None  #Nombre no esta en la lista

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
        st.write("Información del QR:/n", data)
        checkingPay = get_payment_for_name(df, data)
        if checkingPay is not None:
            st.success(f"¿El pago ha sido realizado?: {checkingPay}")
            registerABS(data,"Asistencia")
        else:
            st.warning(f"No hay registros")
            registerABS(data,"Otros")
    else:
        st.write("No QR code found in the image.")
