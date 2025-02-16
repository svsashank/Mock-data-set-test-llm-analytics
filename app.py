import streamlit as st
import pandas as pd
import openai

# Load your OpenAI API key
openai.api_key = "YOUR_API_KEY"  # Replace with your actual API key

# Load your mock data
df = pd.read_csv("mock_data.csv")

# Chat interface
st.title("Analytics Co-Pilot 🚀")
user_input = st.text_input("Ask a question about your data:")

if user_input:
    try:
        # Ask GPT-4 to analyze the data
        response = openai.ChatCompletion.acreate(
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
