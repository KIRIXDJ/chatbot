import streamlit as st
import os
import google.generativeai as genai
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate

# --- CONFIGURACIÓN DE API ---
API_KEY = "AIzaSyCkQN7jqBKBA-k45CRycIlkDJZNUH2uorc" 
os.environ["GOOGLE_API_KEY"] = API_KEY
genai.configure(api_key=API_KEY)

# --- FUNCIONES TÉCNICAS ---
def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def get_vector_store(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")

def get_conversational_chain():
    prompt_template = """
    Eres el asistente virtual oficial de UNIROMANA. Tu objetivo es ayudar a los estudiantes basándote 
    ESTRICTAMENTE en los documentos proporcionados.
    
    Instrucciones:
    1. Si la respuesta está en el contexto, explícala de forma clara y amable.
    2. Si la respuesta NO está en el contexto, di: "Lo siento, esa información no se encuentra en mis registros. Consulta con el departamento correspondiente."
    3. Mantén un tono académico y profesional.

    Contexto:\n {context}?\n
    Pregunta: \n{question}\n

    Respuesta Sugerida:
    """
    model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3)
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    return load_qa_chain(model, chain_type="stuff", prompt=prompt)

# --- INTERFAZ DE USUARIO ---
st.set_page_config(page_title="UNIROMANA AI-Hub", layout="wide")
st.title("🤖 UNIROMANA AI-Hub: Asistente de Consultas")

with st.sidebar:
    st.header("⚙️ Entrenamiento")
    uploaded_files = st.file_uploader("Sube los PDFs de Scholar/Reglamentos", accept_multiple_files=True, type="pdf")
    
    if st.button("Procesar y Aprender"):
        if uploaded_files:
            with st.spinner("Analizando documentos..."):
                raw_text = get_pdf_text(uploaded_files)
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
                chunks = text_splitter.split_text(raw_text)
                get_vector_store(chunks)
                st.success("¡Documentos integrados!")
        else:
            st.error("Sube al menos un PDF.")

user_question = st.text_input("Haz tu pregunta aquí:")

if user_question:
    if os.path.exists("faiss_index"):
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
        docs = new_db.similarity_search(user_question)
        chain = get_conversational_chain()
        response = chain({"input_documents": docs, "question": user_question}, return_only_outputs=True)
        st.markdown(f"**Respuesta:** {response['output_text']}")
    else:
        st.warning("Primero sube y procesa los documentos en la barra lateral.")