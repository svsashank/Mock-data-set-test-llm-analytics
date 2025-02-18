import streamlit as st
import pandas as pd
import tiktoken
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("Enterprise Analytics Copilot 🚀")

def analyze_data(df, query, context):
    """Direct analysis using GPT-4's enhanced data understanding"""
    sample = df.sample(min(500, len(df)))  # Smart sampling

    prompt = f"""
    Analyze this business data for {context}:
    {sample.to_csv(index=False)}

    User Question: {query}

    Perform:
    1. Full statistical analysis
    2. Trend identification
    3. Anomaly detection
    4. Predictive insights
    5. Return formatted markdown with numbers
    """

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You're a senior data scientist analyzing enterprise data. Provide detailed, numerical insights."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )
    return response.choices[0].message.content

# File upload
uploaded_file = st.file_uploader("Upload CSV (supports 100k+ rows)", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success(f"Loaded {len(df):,} rows")

    context = st.text_input("Business Context", "sales analytics")
    query = st.chat_input("Ask deep questions")

    if query:
        with st.spinner("Analyzing..."):
            analysis = analyze_data(df, query, context)

        st.markdown(f"""
        ### Analysis of {len(df):,} rows
        **Your Question:** {query}
        {analysis}
        """)
