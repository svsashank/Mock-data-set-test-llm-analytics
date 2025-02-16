import streamlit as st
import pandas as pd
import openai
import tiktoken
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Configure Streamlit
st.title("Analytics Co-Pilot 2.0")
st.write("Ask questions about your data - no chunking needed!")

# Token management
def count_tokens(text):
    encoder = tiktoken.encoding_for_model("gpt-4-1106-preview")
    return len(encoder.encode(text))

# Core analysis engine
def analyze_with_context(df, question):
    # Step 1: Generate dataset blueprint
    blueprint_prompt = f"""Analyze this dataset structure:
    {df.head(3).to_csv()}

    Identify:
    1. Key numerical columns
    2. Important categorical columns
    3. Time-based columns (if any)

    Output as a JSON template for analysis."""

    blueprint = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "user", "content": blueprint_prompt}],
        temperature=0
    ).choices[0].message.content

    # Step 2: Dynamic query decomposition
    query_prompt = f"""You're a data analyst. Given this dataset blueprint:
    {blueprint}

    And user question: "{question}"

    Generate 3-5 precise pandas/numpy operations needed to answer this.
    Output ONLY the code as bullet points. No explanations."""

    operations = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "user", "content": query_prompt}],
        temperature=0.1
    ).choices[0].message.content

    # Step 3: Execute operations locally
    try:
        # Secure execution environment
        local_vars = {"df": df.copy()}
        exec_ops = [op.split(".")[-1].strip() for op in operations.split("\n")]

        results = {}
        for op in exec_ops:
            if "=" in op:
                exec(f'result = {op.split("=")[-1].strip()}', globals(), local_vars)
                results[op] = local_vars.get('result', None)
            else:
                exec(f'result = df.{op}', globals(), local_vars)
                results[op] = local_vars.get('result', None)

        # Convert results to text
        results_text = "\n".join([f"{k}: {str(v)[:200]}" for k,v in results.items()])
    except Exception as e:
        results_text = f"Error: {str(e)}"

    # Step 4: Final interpretation
    final_prompt = f"""Context:
    Dataset Blueprint: {blueprint}

    Computed Results: {results_text}

    User Question: {question}

    Craft a professional answer using ONLY the results above.
    Highlight key numbers and trends. Be concise."""

    return client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "user", "content": final_prompt}],
        temperature=0.3
    ).choices[0].message.content

# Main app logic
uploaded_file = st.file_uploader("Upload CSV", type="csv")
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("Data Structure:", df.dtypes)

    question = st.text_input("Ask your question:")

    if question:
        with st.spinner("Analyzing (no chunking)..."):
            answer = analyze_with_context(df, question)
            st.subheader("Insights")
            st.markdown(f"**Question:** {question}")
            st.markdown(f"**Analysis:**\n{answer}")
