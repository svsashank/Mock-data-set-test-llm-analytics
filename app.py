import streamlit as st
import pandas as pd
from openai import OpenAI  # Use the new client initialization

# Initialize OpenAI client with your API key
client = OpenAI(api_key="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")  # Replace with your key

# Load mock data
df = pd.read_csv("mock_data.csv")

# Chat interface
st.title("Analytics Co-Pilot 🚀")
user_input = st.text_input("Ask a question about your data:")

if user_input:
    try:
        # Generate a response using the latest API syntax
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Use "gpt-4" if you have access
            messages=[
                {"role": "system", "content": "You are a data analyst assistant. Answer concisely."},
                {"role": "user", "content": f"Data: {df.to_csv(index=False)}. Question: {user_input}"}
            ]
        )
        # Display the answer
        st.write("**Answer:**")
        st.write(response.choices[0].message.content)
    except Exception as e:
        st.error(f"Error: {e}")
