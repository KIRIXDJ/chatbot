import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import os

st.set_page_config(page_title="UNIROMANA AI-Hub", layout="wide")
st.title("📚 UNIROMANA")

# Conexión con Gemini 2.5 Flash
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# FUNCIÓN MÁGICA: Lee los archivos locales automáticamente
@st.cache_resource
def cargar_conocimiento_permanente():
    texto_base = ""
    carpeta = "documentos"
    if os.path.exists(carpeta):
        for archivo in os.listdir(carpeta):
            if archivo.endswith(".pdf"):
                path = os.path.join(carpeta, archivo)
                reader = PdfReader(path)
                for page in reader.pages:
                    texto_base += page.extract_text() + "\n"
    return texto_base

# Cargamos el contexto al iniciar la app
contexto_fijo = cargar_conocimiento_permanente()

if not contexto_fijo:
    st.warning("⚠️ No encontré archivos en la carpeta 'documentos'. Súbelos a GitHub para que el bot tenga memoria.")

user_question = st.text_input("Haz una pregunta y te respondere segun los documentos de mi base de datos")

if user_question:
    if not contexto_fijo:
        st.error("El bot no tiene información cargada.")
    else:
        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
            prompt = f"Eres un asistente de UNIROMANA. Usa este contexto: {contexto_fijo}\n\nPregunta: {user_question}"
            response = model.generate_content(prompt)
            st.markdown("### Respuesta:")
            st.write(response.text)
        except Exception as e:
            st.error(f"Error: {e}")

