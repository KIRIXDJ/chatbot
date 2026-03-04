import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader

st.set_page_config(page_title="UNIROMANA AI-Hub", layout="wide")
st.title("📚 UNIROMANA AI-Hub")

# Configurar API (Asegúrate de tener tu clave en los Secrets de Streamlit)
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

with st.sidebar:
    st.header("Entrenamiento del Bot")
    uploaded_files = st.file_uploader("Sube tus PDFs de Scholar/Reglamentos", type="pdf", accept_multiple_files=True)
    process_button = st.button("Procesar y Aprender")

if uploaded_files and process_button:
    context = ""
    for file in uploaded_files:
        pdf_reader = PdfReader(file)
        for page in pdf_reader.pages:
            context += page.extract_text()
    st.session_state['context'] = context
    st.success("¡Documentos integrados con éxito!")

user_question = st.text_input("Hazle una pregunta al bot sobre los documentos:")

if user_question:
    model = genai.GenerativeModel('gemini-1.5-flash')
    full_prompt = f"Basándote en este contenido académico: {st.session_state.get('context', '')}\n\nPregunta: {user_question}"
    response = model.generate_content(full_prompt)
    st.write(response.text)
