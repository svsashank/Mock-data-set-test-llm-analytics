import streamlit as st
import pandas as pd
from openai import OpenAI  # Use the new client initialization

# Initialize OpenAI client with your API key
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])  # ✅ Correct method

# Load mock data
df = pd.read_csv("mock_data.csv")

# Chat interface
st.title("Analytics Co-Pilot 🚀")
user_input = st.text_input("Ask a question about your data:")

if user_input:
    try:
        # Generate a response using the latest API syntax
        response = client.chat.completions.create(
            model="gpt-4-1106-preview",  # Use "gpt-4" if you have access
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
