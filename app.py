import streamlit as st
import pandas as pd
import openai

# Load your OpenAI API key
openai.api_key = "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"  # Replace with your actual API key

# Load your mock data
df = pd.read_csv("mock_data.csv")

# Chat interface
st.title("Analytics Co-Pilot 🚀")
user_input = st.text_input("Ask a question about your data:")

if user_input:
    try:
        # Ask GPT-4 to analyze the data
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Use "gpt-3.5-turbo" if you don't have access to GPT-4
            messages=[
                {"role": "system", "content": "You are a helpful assistant for analyzing data."},
                {"role": "user", "content": f"Here is the data: {df.to_csv(index=False)}. {user_input}"}
            ]
        )
        st.write("**Answer:**")
        st.write(response['choices'][0]['message']['content'])
    except Exception as e:
        st.error(f"An error occurred: {e}")
