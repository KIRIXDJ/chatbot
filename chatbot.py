import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import os
import time

st.set_page_config(page_title="UNIROMANA AI-Hub", layout="wide")
st.title("📚 UNIROMANA AI-Hub")

# Conexión con Gemini 2.5 Flash
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

@st.cache_resource
def cargar_conocimiento_permanente():
    texto_base = ""
    carpeta = "documentos"
    if os.path.exists(carpeta):
        for archivo in os.listdir(carpeta):
            if archivo.endswith(".pdf"):
                path = os.path.join(carpeta, archivo)
                try:
                    reader = PdfReader(path)
                    for page in reader.pages:
                        texto_base += page.extract_text() + "\n"
                except Exception as e:
                    st.error(f"Error leyendo {archivo}: {e}")
    
    # LIMITADOR DE EMERGENCIA: 
    # Si el texto es demasiado largo, lo recortamos para no quemar la cuota de 250k tokens.
    # 500,000 caracteres son aprox 125,000 tokens (la mitad del límite por minuto).
    return texto_base[:500000] 

contexto_fijo = cargar_conocimiento_permanente()

if not contexto_fijo:
    st.warning("⚠️ No encontré archivos en la carpeta 'documentos'.")

user_question = st.text_input("Haz una pregunta sobre los documentos universitarios:")

if user_question:
    if not contexto_fijo:
        st.error("El bot no tiene información cargada.")
    else:
        with st.spinner("Consultando a la IA..."):
            model = genai.GenerativeModel('gemini-2.5-flash')
            # Reducimos un poco el prompt para ser más eficientes
            prompt = f"Contexto: {contexto_fijo}\n\nPregunta: {user_question}\nRespuesta corta y precisa:"
            
            exito = False
            intentos = 0
            
            while not exito and intentos < 3:
                try:
                    response = model.generate_content(prompt)
                    st.markdown("### Respuesta:")
                    st.write(response.text)
                    exito = True
                except Exception as e:
                    if "429" in str(e):
                        intentos += 1
                        st.warning(f"Límite de cuota alcanzado. Reintentando en 5 segundos... (Intento {intentos}/3)")
                        time.sleep(5)
                    else:
                        st.error(f"Error crítico: {e}")
                        break
