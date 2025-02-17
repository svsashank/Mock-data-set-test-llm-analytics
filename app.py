import streamlit as st
import pandas as pd
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("🚀 Unicorn Analytics Pro")
uploaded_file = st.file_uploader("Upload your unicorn company dataset", type="csv")

def clean_valuation(value):
    """Convert valuation strings to numeric (handles $, commas, etc.)"""
    try:
        if isinstance(value, str):
            # Remove non-numeric characters except decimals
            return float(''.join(filter(lambda x: x.isdigit() or x == '.', value)))
        return float(value)
    except:
        return None  # Skip invalid values

def analyze_data(df, question):
    """Precompute stats with error handling"""
    context = {
        "columns": list(df.columns),
        "row_count": len(df),
        "top_countries": None,
        "top_industries": None,
        "avg_valuation": None,
        "sample_companies": []
    }

    try:
        # Auto-detect columns
        valuation_col = next((col for col in df.columns if "valuation" in col.lower()), None)
        country_col = next((col for col in df.columns if "country" in col.lower()), None)
        industry_col = next((col for col in df.columns if "industry" in col.lower()), None)

        # Calculate valuation stats
        if valuation_col:
            df['cleaned_valuation'] = df[valuation_col].apply(clean_valuation)
            context["avg_valuation"] = df['cleaned_valuation'].mean(skipna=True)

        # Calculate country/industry stats
        if country_col:
            context["top_countries"] = df[country_col].value_counts().head(5).to_dict()
        
        if industry_col:
            context["top_industries"] = df[industry_col].value_counts().head(5).to_dict()

        # Sample companies (if column exists)
        if "company" in df.columns:
            context["sample_companies"] = df.sample(3).to_dict("records")

    except Exception as e:
        st.error(f"Data analysis error: {str(e)}")

    return context

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        st.write("Data Preview:", df.head(2))

        # Always show the input box, even after errors
        question = st.text_input("Ask a question (e.g., 'Which country dominates in tech unicorns?'):")

        if question:
            with st.spinner("Analyzing..."):
                # Generate context
                context = analyze_data(df, question)

                # Build prompt
                prompt = f"""
                **Task**: Answer "{question}" using the data below. Be quantitative.

                **Context**:
                - Columns: {context['columns']}
                - Total companies: {context['row_count']}
                - Top countries: {context['top_countries'] or 'N/A'}
                - Top industries: {context['top_industries'] or 'N/A'}
                - Avg valuation: {context['avg_valuation'] or 'N/A'}
                Sample companies: {context['sample_companies']}
                """

                # Get answer
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": "You are a data analyst. Use the context below."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.1
                    )
                    st.subheader("Answer")
                    st.write(response.choices[0].message.content)

                except Exception as e:
                    st.error(f"API Error: {str(e)}")

    except Exception as e:
        st.error(f"Failed to load file: {str(e)}")
