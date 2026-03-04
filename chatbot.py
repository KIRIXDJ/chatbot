import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader

# Configuración inicial de la página
st.set_page_config(page_title="UNIROMANA AI-Hub", layout="wide")
st.title("📚 UNIROMANA AI-Hub")

# Conexión con la API Key de los Secrets de Streamlit
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("⚠️ Falta la API Key en los Secrets de Streamlit.")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Inicializar el estado de la sesión si no existe
if "contexto_pdf" not in st.session_state:
    st.session_state["contexto_pdf"] = ""

# Barra lateral para subir archivos
with st.sidebar:
    st.header("Entrenamiento del Bot")
    st.info("Sube aquí tus reglamentos de UNIROMANA o artículos de Scholar.")
    uploaded_files = st.file_uploader("Selecciona archivos PDF", type="pdf", accept_multiple_files=True)
    process_button = st.button("Procesar y Aprender")

# Lógica para extraer texto de los PDFs
if uploaded_files and process_button:
    with st.spinner("Leyendo documentos..."):
        texto_acumulado = ""
        for file in uploaded_files:
            pdf_reader = PdfReader(file)
            for page in pdf_reader.pages:
                texto_acumulado += page.extract_text() + "\n"
        
        # Guardamos el texto en la sesión para que no se pierda al preguntar
        st.session_state["contexto_pdf"] = texto_acumulado
        st.success("¡Documentos integrados con éxito! Ya puedes preguntar.")

# Área de chat
user_question = st.text_input("Hazle una pregunta al bot sobre los documentos subidos:")

if user_question:
    # Verificamos si hay contenido para responder
    if not st.session_state["contexto_pdf"]:
        st.warning("⚠️ El bot está vacío. Primero sube un PDF y dale a 'Procesar y Aprender'.")
    else:
        try:
            model = genai.GenerativeModel('gemini-pro')
            # Creamos el prompt con el contexto de los PDFs
            prompt_final = f"""
            Eres un asistente académico experto. Utiliza el siguiente contexto para responder la pregunta.
            Si la respuesta no está en el texto, dilo amablemente.
            
            Contexto: {st.session_state['contexto_pdf']}
            
            Pregunta: {user_question}
            """
            
            response = model.generate_content(prompt_final)
            st.markdown("### Respuesta del Bot:")
            st.write(response.text)
        except Exception as e:
            st.error(f"Hubo un error con la IA: {e}")

