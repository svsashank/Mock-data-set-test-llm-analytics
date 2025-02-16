import streamlit as st
import pandas as pd
import openai

# Load your OpenAI API key
openai.api_key = "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"  # Replace with your key from Step A

# Load your mock data
df = pd.read_csv("mock_data.csv")

# Chat interface
st.title("Analytics Co-Pilot 🚀")
user_input = st.text_input("Ask a question about your data:")

if user_input:
    # Ask GPT-4 to analyze the data
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": f"Analyze this data: {df}. Answer concisely in plain text."},
            {"role": "user", "content": user_input}
        ]
    )
    st.write("**Answer:**")
    st.write(response.choices[0].message.content)