import streamlit as st
from langchain.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings

@st.cache_resource
def loading(api_key):
    loader = PyPDFLoader("tea.pdf")
    documents = loader.load()
    
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(documents)

    embeddings_model = OpenAIEmbeddings(model="text-embedding-ada-002", api_key=api_key)
    vectorstore = FAISS.from_texts(
        [chunk.page_content for chunk in chunks], embeddings_model
    )
    return vectorstore.as_retriever(search_kwargs={"k": 3})

def chatbot_page():
    if not st.session_state["api_key"]:
        st.warning("Please enter the API key on the page 'API Key'.")
        st.stop()

    st.title("Tea-chatbot")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "bot", "content": "Hello! I can answer questions about the book by V. V. Pokhlebkin 'Tea, its history, properties and use'. Ask questions, and I will try to help!"}
        ]

    retriever = loading(st.session_state["api_key"])
    llm = ChatOpenAI(model="gpt-4o-mini", api_key=st.session_state["api_key"], temperature=0.9)
    prompt_template = '''
    You are a chatbot named "tea-chatbot", who has read only one book by V. V. Pokhlebkin "Tea, its history, properties and use".

    Do not answer questions that do not concern the book.

    Answer only in Russian, if they write in another language, then say that you only know the language of this book - Russian.

    Given the given context and history, answer the question at the end.

    History: {history}
    Context: {context}
    Question: {question}
    '''
    prompt = PromptTemplate(input_variables=["history", "context", "question"], template=prompt_template)
    chain = prompt | llm

    user_input = st.chat_input("Enter your question:")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        with st.spinner("Rereading the book..."):
            context = "\n".join([doc.page_content for doc in retriever.invoke(user_input)])
            history = "\n".join(
                f"Question: {entry['content']}" if entry["role"] == "user" else f"Ответ: {entry['content']}"
                for entry in st.session_state.chat_history
            )
            result = chain.invoke({"history": history, "context": context, "question": user_input})

        st.session_state.chat_history.append({"role": "bot", "content": result.content})

    for entry in st.session_state.chat_history:
        if entry["role"] == "user":
            with st.chat_message("user"):
                st.markdown(entry["content"])
        else:
            with st.chat_message("assistant"):
                st.markdown(entry["content"])
