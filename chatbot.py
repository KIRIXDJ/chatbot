import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import os
import time

# 1. Configuración de la página
st.set_page_config(page_title="UNIROMANA AI-Hub", layout="wide")

# 2. Inyección de CSS para fondo blanco y textos NEGROS INTENSOS
st.markdown(
    """
    <style>
    /* Fondo principal */
    .stApp {
        background-color: #ffffff !important;
    }
    
    /* Forzar negro en TODO tipo de texto y contenedores */
    .stApp, .stApp p, .stApp li, .stApp span, .stApp label, .stApp div {
        color: #000000 !important;
    }

    /* Títulos en negro */
    h1, h2, h3 {
        color: #000000 !important;
    }

    /* Arreglo específico para las listas (donde se ve el texto claro) */
    ul, ol, li {
        color: #000000 !important;
    }

    /* Asegurar que el texto dentro del markdown de respuesta sea negro */
    .stMarkdown div p {
        color: #000000 !important;
    }

    /* Caja de entrada de texto */
    .stTextInput input {
        background-color: #f0f2f6 !important;
        color: #000000 !important;
        border: 2px solid #dcdcdc !important;
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


