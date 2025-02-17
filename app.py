import streamlit as st
import pandas as pd
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("📊 Zero-Code Analytics AI")
uploaded_file = st.file_uploader("Upload any CSV", type="csv")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat input always visible
if prompt := st.chat_input("Ask about your data..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Process data and generate response
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        data_sample = df.head(3).to_markdown(index=False)

        # Build context-aware prompt
        messages = [
            {"role": "system", "content": f"""
            You're a data analyst working with this dataset sample:
            {data_sample}

            Rules:
            1. Answer questions using column names from the table
            2. Never assume data you haven't seen
            3. If calculations are needed, explain your reasoning
            """},
            *st.session_state.messages
        ]

        # Get AI response
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0
        )

        # Display assistant response
        with st.chat_message("assistant"):
            st.markdown(response.choices[0].message.content)
        st.session_state.messages.append({"role": "assistant", "content": response.choices[0].message.content})
