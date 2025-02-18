import sys
!{sys.executable} -m pip install --upgrade chromadb==0.4.22


import streamlit as st
import pandas as pd
from openai import OpenAI
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
embeddings = OpenAIEmbeddings(openai_api_key=st.secrets["OPENAI_API_KEY"])

st.title("Enterprise Analytics Copilot 🚀")

def process_data(df):
    # Convert data to analyzable text chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    # Create document format
    docs = []
    for _, row in df.iterrows():
        doc = f"Row {_}: " + " | ".join([f"{col}={val}" for col, val in row.items()])
        docs.append(doc)

    # Split and embed
    chunks = text_splitter.create_documents(docs)
    vector_db = Chroma.from_documents(chunks, embeddings)
    return vector_db

def analyze_query(vector_db, user_query, context):
    # Retrieve relevant data chunks
    relevant_docs = vector_db.similarity_search(user_query, k=5)
    docs_text = "\n".join([doc.page_content for doc in relevant_docs])

    system_prompt = f"""
    Analyze this data subset for a user asking: {user_query}
    Context: {context}

    Data Subset:
    {docs_text}

    Required:
    1. Statistical analysis of relevant columns
    2. Trend identification
    3. Numerical examples from data
    4. Markdown formatting
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content

# File upload
uploaded_file = st.file_uploader("Upload Large CSV (100k+ rows)", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success(f"Loaded {len(df)} rows")

    if "vector_db" not in st.session_state:
        with st.spinner("Indexing dataset..."):
            st.session_state.vector_db = process_data(df)

    context = st.text_input("Business context")

    if context and (query := st.chat_input("Ask deep analytical questions")):
        with st.spinner("Analyzing..."):
            response = analyze_query(
                st.session_state.vector_db,
                query,
                context
            )

        st.markdown(f"""
        ### Analysis of {len(df)} rows
        **Your Question:** {query}
        {response}
        """)
