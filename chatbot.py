import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import os
import time

st.set_page_config(page_title="UNIROMANA AI-Hub", layout="wide")
st.title("📚 UNIROMANA")

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
    
    # Mantenemos un límite alto pero seguro para evitar el error de cuota inmediato
    return texto_base[:600000] 

contexto_fijo = cargar_conocimiento_permanente()

if not contexto_fijo:
    st.warning("⚠️ No encontré archivos en la carpeta 'documentos'.")

user_question = st.text_input("Haz una pregunta  y te respondere usando los documentos de mi base de datos")

if user_question:
    if not contexto_fijo:
        st.error("El bot no tiene información cargada.")
    else:
        with st.spinner("Buscando en los archivos de UNIROMANA..."):
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # REINSERTAMOS TU PROMPT ORIGINAL CON LA IDENTIDAD
            prompt = f"Eres un asistente de UNIROMANA. Usa este contexto: {contexto_fijo}\n\nPregunta: {user_question}"
            
            intentos = 0
            while intentos < 3:
                try:
                    response = model.generate_content(prompt)
                    st.markdown("### Respuesta:")
                    st.write(response.text)
                    break # Si tiene éxito, sale del bucle
                except Exception as e:
                    if "429" in str(e):
                        intentos += 1
                        st.warning(f"Límite de tokens alcanzado. Reintentando en 10 segundos... (Intento {intentos}/3)")
                        time.sleep(10) # Espera un poco más para que la cuota se limpie
                    else:
                        st.error(f"Error: {e}")
                        break

