import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader

# 1. Configuración de la interfaz
st.set_page_config(page_title="UNIROMANA AI-Hub", layout="wide")
st.title("📚 UNIROMANA AI-Hub")

# 2. Conexión segura con la API Key
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("⚠️ Falta la API Key en los Secrets de Streamlit.")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# 3. Inicializar memoria
if "contexto_pdf" not in st.session_state:
    st.session_state["contexto_pdf"] = ""

# 4. Barra Lateral (Subida de archivos)
with st.sidebar:
    st.header("Entrenamiento del Bot")
    uploaded_files = st.file_uploader("Sube tus PDFs académicos", type="pdf", accept_multiple_files=True)
    process_button = st.button("Procesar y Aprender")

# 5. Lógica de procesamiento
if uploaded_files and process_button:
    with st.spinner("Procesando documentos con Gemini 2.5..."):
        texto_acumulado = ""
        for file in uploaded_files:
            pdf_reader = PdfReader(file)
            for page in pdf_reader.pages:
                texto_acumulado += page.extract_text() + "\n"
        
        st.session_state["contexto_pdf"] = texto_acumulado
        st.success("¡Documentos integrados con éxito!")

# 6. Chat con modelos actualizados
user_question = st.text_input("Haz una pregunta sobre los documentos:")

if user_question:
    if not st.session_state["contexto_pdf"]:
        st.warning("⚠️ Primero sube un PDF y presiona 'Procesar'.")
    else:
        try:
            # Usamos el modelo 2.5 Flash que viste en tu lista
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            prompt = f"Contexto: {st.session_state['contexto_pdf']}\n\nPregunta: {user_question}"
            response = model.generate_content(prompt)
            
            st.markdown("### Respuesta:")
            st.write(response.text)
            
        except Exception as e:
            # Si falla, intentamos con Gemini 3 como respaldo
            try:
                model_alt = genai.GenerativeModel('gemini-3')
                response = model_alt.generate_content(prompt)
                st.write(response.text)
            except:
                st.error(f"Error de conexión: {e}. Revisa que el modelo esté disponible en tu región.")
