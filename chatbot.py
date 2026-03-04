import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader

# 1. Configuración de la interfaz
st.set_page_config(page_title="UNIROMANA AI-Hub", layout="wide")
st.title("📚 UNIROMANA AI-Hub")

# 2. Conexión segura con la API Key (Desde los Secrets de Streamlit)
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("⚠️ Configuración pendiente: Agregue su 'GOOGLE_API_KEY' en los Secrets de Streamlit.")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# 3. Inicializar la memoria de la sesión
if "contexto_pdf" not in st.session_state:
    st.session_state["contexto_pdf"] = ""

# 4. Barra Lateral para Entrenamiento
with st.sidebar:
    st.header("Entrenamiento del Bot")
    st.info("Sube aquí tus reglamentos de UNIROMANA o artículos de Scholar.")
    uploaded_files = st.file_uploader("Selecciona archivos PDF", type="pdf", accept_multiple_files=True)
    process_button = st.button("Procesar y Aprender")

# 5. Lógica de extracción de texto
if uploaded_files and process_button:
    with st.spinner("Leyendo y aprendiendo de los documentos..."):
        texto_acumulado = ""
        try:
            for file in uploaded_files:
                pdf_reader = PdfReader(file)
                for page in pdf_reader.pages:
                    texto_acumulado += page.extract_text() + "\n"
            
            # Guardamos el contenido en la sesión
            st.session_state["contexto_pdf"] = texto_acumulado
            st.success("¡Documentos integrados! Ya puedes hacer preguntas.")
        except Exception as e:
            st.error(f"Error al leer el archivo: {e}")

# 6. Chat Principal
user_question = st.text_input("Hazle una pregunta al bot sobre la información subida:")

if user_question:
    if not st.session_state["contexto_pdf"]:
        st.warning("⚠️ El bot no tiene datos. Primero sube un PDF en la izquierda y presiona 'Procesar'.")
    else:
        try:
            # Usamos gemini-1.5-flash por ser el más rápido y ligero
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt_final = f"""
            Actúa como un asistente académico para un estudiante de UNIROMANA.
            Responde basándote exclusivamente en este contexto:
            {st.session_state['contexto_pdf']}
            
            Pregunta del usuario: {user_question}
            """
            
            response = model.generate_content(prompt_final)
            st.markdown("### Respuesta del Bot:")
            st.write(response.text)
            
        except Exception as e:
            st.error(f"Error en la respuesta de la IA: {e}")
