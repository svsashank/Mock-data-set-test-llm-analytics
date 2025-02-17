import streamlit as st
import pandas as pd
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("Unicorn Analytics Pro")
uploaded_file = st.file_uploader("Upload your unicorn company dataset", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("Data Preview:", df.head(2))

    question = st.text_input("Ask your question (e.g., 'Which country has the most unicorns?'):")

    if question:
        # Step 1: Auto-detect key columns
        country_col = next((col for col in df.columns if "country" in col.lower()), None)
        company_col = next((col for col in df.columns if "company" in col.lower()), None)

        # Step 2: Generate critical summary stats
        summary = []
        if country_col:
            country_counts = df[country_col].value_counts().head(10).to_dict()
            summary.append(f"Top countries by company count: {country_counts}")
        if company_col:
            summary.append(f"Total companies: {len(df)}")

        # Step 3: Build bulletproof prompt
        prompt = f"""Analyze this business data to answer: "{question}"

        Context:
        - Columns available: {list(df.columns)}
        - Key stats: {summary if summary else 'No summary generated'}

        Rules:
        1. NEVER mention "the dataset doesn't contain"
        2. If unclear, GUESS based on column names
        3. Answer in 3 sentences max
        """

        # Step 4: Get answer
        response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )

        st.subheader("Answer")
        st.write(response.choices[0].message.content)
