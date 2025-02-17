import streamlit as st
import pandas as pd
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("🤖 Analytics Co-Pilot")
uploaded_file = st.file_uploader("Upload your dataset (CSV)", type="csv")

# ----------------------
# Core Analysis Engine
# ----------------------
def clean_currency(value):
    """Convert values like '$1.2B' or '500M' to numeric (in millions)"""
    if pd.isna(value) or value == "":
        return None
    try:
        if isinstance(value, str):
            value = value.replace(",", "").upper()
            multiplier = 1
            if "B" in value:  # Billion
                multiplier = 1000
                value = value.replace("B", "")
            elif "M" in value:  # Million
                multiplier = 1
                value = value.replace("M", "")
            return float(''.join(filter(lambda x: x.isdigit() or x == '.', value))) * multiplier
        return float(value)
    except:
        return None

def analyze_dataset(df):
    """Auto-analyze ANY dataset (general-purpose)"""
    context = {"columns": [], "numeric_stats": {}, "categorical_stats": {}}

    # Auto-classify columns
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    for col in df.columns:
        # Detect numeric columns hidden as strings (e.g., "Valuation")
        if df[col].apply(lambda x: isinstance(x, str) and any(c.isdigit() for c in x)).any():
            cleaned = df[col].apply(clean_currency).dropna()
            if not cleaned.empty:
                numeric_cols.append(col)
                df[f"cleaned_{col}"] = cleaned
                context["numeric_stats"][col] = {
                    "mean": cleaned.mean(),
                    "max": cleaned.max(),
                    "min": cleaned.min()
                }

    # Categorical analysis
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    for col in categorical_cols:
        context["categorical_stats"][col] = df[col].value_counts().head(5).to_dict()

    # Sample records
    context["sample_records"] = df.sample(min(3, len(df))).to_dict("records")
    return context

# ----------------------
# Streamlit UI
# ----------------------
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("## Data Preview")
    st.write(df.head(3))

    # Always show input box
    question = st.text_input("Ask a question about your data:")

    if question:
        with st.spinner("Analyzing..."):
            # Step 1: Auto-analyze dataset
            context = analyze_dataset(df)

            # Step 2: Build general-purpose prompt
            prompt = f"""
            **Task**: Answer the user's question: "{question}"

            **Dataset Context**:
            - Columns: {context['columns'] or list(df.columns)}
            - Numeric Columns: {list(context['numeric_stats'].keys())}
            {f"- Numeric Stats: {context['numeric_stats']}" if context['numeric_stats'] else ""}
            {f"- Categorical Stats: {context['categorical_stats']}" if context['categorical_stats'] else ""}
            - Sample Records: {context['sample_records']}

            **Rules**:
            1. Use ONLY the data and stats above.
            2. If values need conversion (e.g., $1B = 1000M), do it explicitly.
            3. For comparisons, use max/min values from numeric_stats.
            4. Never assume columns exist - verify first.
            """

            # Step 3: Get AI response
            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are a general-purpose data analyst. Use the context below."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1
                )
                st.write("## Answer")
                st.write(response.choices[0].message.content)

            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")
