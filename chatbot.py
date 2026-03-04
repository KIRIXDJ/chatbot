import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import os
import time

# 1. Configuración de la página
st.set_page_config(page_title="UNIROMANA AI-Hub", layout="wide")

# 2. Inyección de CSS para fondo blanco y textos oscuros
st.markdown(
    """
    <style>
    .stApp {
        background-color: #ffffff;
    }
    /* Aseguramos que los textos sean oscuros para buen contraste */
    h1, h2, h3, p, span, label {
        color: #1a1a1a !important;
    }
    /* Estilo para la caja de texto */
    .stTextInput input {
        background-color: #f9f9f9 !important;
        color: #1a1a1a !important;
        border: 1px solid #cccccc !important;
    }
    /* Estilo para el área de respuesta */
    .stMarkdown {
        background-color: #fdfdfd;
        padding: 10px;
        border-radius: 5px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("📚 MarceloV46")

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
    
    # Límite de seguridad para tokens (aprox 150k tokens)
    return texto_base[:600000] 

contexto_fijo = cargar_conocimiento_permanente()

if not contexto_fijo:
    st.warning("⚠️ No encontré archivos en la carpeta 'documentos'.")

user_question = st.text_input("Haz una pregunta y te respondere segun mi base de datos")

if user_question:
    if not contexto_fijo:
        st.error("El bot no tiene información cargada.")
    else:
        with st.spinner("Buscando en los archivos de UNIROMANA..."):
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # Tu prompt original con identidad
            prompt = f"Eres un asistente de UNIROMANA. Usa este contexto: {contexto_fijo}\n\nPregunta: {user_question}"
            
            intentos = 0
            while intentos < 3:
                try:
                    response = model.generate_content(prompt)
                    st.markdown("### Respuesta:")
                    st.write(response.text)
                    break 
                except Exception as e:
                    if "429" in str(e):
                        intentos += 1
                        st.warning(f"Límite alcanzado. Reintentando en 10 segundos... (Intento {intentos}/3)")
                        time.sleep(10)
                    else:
                        st.error(f"Error: {e}")
                        break

