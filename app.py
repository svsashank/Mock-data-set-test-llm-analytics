import streamlit as st
import pandas as pd
from openai import OpenAI

# Configure OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Set app title
st.title("Analytics Copilot 🤖 (GPT-4 Version)")

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Function to generate data summary using OpenAI
def generate_summary(df, context):
    prompt = f"""
    You are a data analysis assistant. Generate a concise summary (3-5 bullet points) about this dataset.
    Context provided by user: {context}

    Dataset information:
    Number of rows: {df.shape[0]}
    Number of columns: {df.shape[1]}
    First 3 rows:
    {df.head(3)}
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content

# Function to handle user queries
def handle_query(user_query, context, summary):
    system_prompt = f"""
    You are an expert data analyst. Use the following context to answer questions.
    Data Context: {context}
    Data Summary: {summary}

    Follow these rules:
    1. Be concise and professional
    2. If calculation is needed, explain your approach
    3. Always mention data limitations if relevant
    4. Use markdown formatting for responses
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ],
        temperature=0.4
    )
    return response.choices[0].message.content

# File upload section
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("File uploaded successfully!")

        # Get data context from user
        context = st.text_input("Briefly describe the context of your data (e.g., 'Sales data for Q2 2023')")

        if context:
            # Generate and display summary
            if "summary" not in st.session_state:
                with st.spinner("Analyzing your data..."):
                    st.session_state.summary = generate_summary(df, context)
                    st.session_state.context = context

            st.subheader("Data Summary")
            st.markdown(st.session_state.summary)

            # Chat interface
            st.subheader("Ask me anything about your data")

            # Display previous messages
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            # Handle new query
            if user_query := st.chat_input("Type your question..."):
                # Add user message to history
                st.session_state.messages.append({"role": "user", "content": user_query})

                # Generate response
                with st.spinner("Thinking..."):
                    response = handle_query(
                        user_query,
                        st.session_state.context,
                        st.session_state.summary
                    )

                # Add assistant response to history
                st.session_state.messages.append({"role": "assistant", "content": response})

                # Display messages
                with st.chat_message("user"):
                    st.markdown(user_query)
                with st.chat_message("assistant"):
                    st.markdown(response)

    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
