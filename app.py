import streamlit as st
import pandas as pd
import openai
import tiktoken
import time
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Configure Streamlit
st.title("Analytics Co-Pilot")
st.write("Upload your CSV and ask questions!")

# Token counting function
def count_tokens(text, model="gpt-4-1106-preview"):
    encoder = tiktoken.encoding_for_model(model)
    return len(encoder.encode(text))

# Process data in chunks with retries
def analyze_data(df, user_question):
    results = []
    CHUNK_ROWS = 50  # Adjust based on your data density
    MAX_TOKENS = 28000  # Stay under 30k TPM limit

    for i in range(0, len(df), CHUNK_ROWS):
        chunk = df[i:i+CHUNK_ROWS]
        chunk_text = chunk.to_csv(index=False)

        # Check token count
        if count_tokens(chunk_text) > MAX_TOKENS:
            st.warning(f"Chunk {i//CHUNK_ROWS+1} too large. Reducing rows...")
            CHUNK_ROWS = max(1, CHUNK_ROWS // 2)
            continue

        # Build prompt
        prompt = f"""
        Analyze this data chunk (rows {i+1}-{i+len(chunk)}):
        {chunk_text}

        User question: {user_question}
        Provide concise insights and numbers only.
        """

        # Retry logic with exponential backoff
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = client.chat.completions.create(
                    model="gpt-4-1106-preview",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1000,
                    temperature=0.3
                )
                results.append(response.choices[0].message.content)
                st.write(f"Processed chunk {i//CHUNK_ROWS+1}/{len(df)//CHUNK_ROWS+1}")
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    st.error(f"Failed chunk {i//CHUNK_ROWS+1}: {str(e)}")
                    results.append(f"Error in chunk {i//CHUNK_ROWS+1}")
                else:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)

    return "\n\n".join(results)

# Main app logic
uploaded_file = st.file_uploader("Upload CSV", type="csv")
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("Data Preview:", df.head(3))

    if "processed" not in st.session_state:
        st.session_state.processed = False

    user_question = st.text_input("Ask your analytics question:")

    if user_question and not st.session_state.processed:
        with st.spinner("Analyzing..."):
            analysis = analyze_data(df, user_question)
            st.session_state.processed = True
            st.subheader("Insights")
            st.write(analysis)

    if st.button("Reset"):
        st.session_state.processed = False
        st.experimental_rerun()
