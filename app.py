import streamlit as st
import pandas as pd
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("🧠 Smart Data Assistant")
uploaded_file = st.file_uploader("Upload CSV", type="csv")

def get_data_context(df, question):
    """Dynamic context builder - no static summaries"""
    context = {
        "schema": str(df.dtypes.to_dict()),
        "num_rows": len(df),
        # Auto-detect key columns using LLM pattern recognition
        "likely_metrics": [col for col in df.columns if df[col].dtype in ['int64', 'float64']],
        "likely_dimensions": [col for col in df.columns if df[col].dtype == 'object'],
        # Smart sample: 0.5% of data or 50 rows, whichever smaller
        "sample": df.sample(min(50, len(df)//200)).to_dict("records")
    }

    # Auto-focus on relevant columns
    if "country" in question.lower():
        context["country_data"] = df[[c for c in df.columns if "country" in c.lower()]].value_counts().to_dict()

    return context

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if prompt := st.chat_input("Ask about your data:"):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.spinner("Analyzing..."):
            # Step 1: Build dynamic context based on question
            context = get_data_context(df, prompt)

            # Step 2: Construct focused prompt
            messages = [
                {
                    "role": "system",
                    "content": f"""You're a data analyst. Use these clues about the dataset:
                    - Schema: {context['schema']}
                    - Size: {context['num_rows']} rows
                    - Likely Metrics: {context['likely_metrics']}
                    - Sample Rows: {context['sample'][:3]}

                    Rules:
                    1. First identify which columns answer the question
                    2. Consider full dataset patterns, not just samples
                    3. Handle units/formatting natively (e.g., $1B = 1000M)
                    """
                },
                *st.session_state.messages
            ]

            # Step 3: Get AI response
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0
            )

            # Display response
            with st.chat_message("assistant"):
                st.write(response.choices[0].message.content)
            st.session_state.messages.append({
                "role": "assistant",
                "content": response.choices[0].message.content
            })
