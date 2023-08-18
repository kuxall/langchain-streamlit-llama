# Bring in deps
import streamlit as st 
from langchain.llms import LlamaCpp
from langchain.embeddings import LlamaCppEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma

# Customize the layout
st.set_page_config(page_title="संविधान AI", page_icon="🤖", layout="wide", )     
st.markdown(f"""
            <style>
            .stApp {{background-image: url("https://images.unsplash.com/photo-1509537257950-20f875b03669?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1469&q=80"); 
                     background-attachment: fixed;
                     background-size: cover}}
         </style>
         """, unsafe_allow_html=True)

# function for writing uploaded file in temp
def write_text_file(content, file_path):
    try:
        with open(file_path, 'w') as file:
            file.write(content)
        return True
    except Exception as e:
        print(f"Error occurred while writing the file: {e}")
        return False

# set prompt template
prompt_template = """
    तल दिइएको context प्रयोग गरेर question को answer अन्त्यमा दिनुहोस्। यदि तपाईंलाई थाहा छैन भने, सजिलै तरिकाले थाहा छैन भनेर भन्नुहोस्, कृपया अनावश्यक उत्तर नबनाउनुहोला।


    {context}

    Question: {question}
    Answer:
"""
prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

# initialize the LLM & Embeddings
llm = LlamaCpp(model_path="./models/llama-7b.ggmlv3.q4_0.bin", max_tokens=2000)
embeddings = LlamaCppEmbeddings(model_path="./models/llama-7b.ggmlv3.q4_0.bin")
llm_chain = LLMChain(llm=llm, prompt=prompt)

st.title("📄 Document Conversation 🤖")
uploaded_file = st.file_uploader("Upload an article", type="txt")

if uploaded_file is not None:
    content = uploaded_file.read().decode('utf-8')
    # st.write(content)
    file_path = "data/NepaliConstitution.txt"
    write_text_file(content, file_path)   
    
    loader = TextLoader(file_path)
    docs = loader.load()    
    text_splitter = CharacterTextSplitter(chunk_size=100, chunk_overlap=0)
    texts = text_splitter.split_documents(docs)
    db = Chroma.from_documents(texts, embeddings)    
    st.success("File Loaded Successfully!!")
    
    # Query through LLM    
    question = st.text_input("फाइल बाट केही सोध्नुहोस्...", placeholder="उस्तै उस्तै लाग्ने खोज्नुहोस..", disabled=not uploaded_file,)  
    
    
    if question:
        similar_doc = db.similarity_search(question, k=2)
        context = similar_doc[0].page_content
        query_llm = LLMChain(llm=llm, prompt=prompt)
        response = query_llm.run({"context": context, "question": question})        
        st.write(response)