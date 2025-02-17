import streamlit as st
import pandas as pd
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("🚀 Unicorn Analytics Pro")
uploaded_file = st.file_uploader("Upload your unicorn company dataset", type="csv")

def clean_valuation(value):
    """Convert valuation strings to numeric (handles $, commas, etc.)"""
    if isinstance(value, str):
        # Remove non-numeric characters except decimals
        return float(''.join(filter(lambda x: x.isdigit() or x == '.', value)))
    return float(value)

def analyze_data(df, question):
    # Auto-detect key columns
    valuation_col = next((col for col in df.columns if "valuation" in col.lower()), None)
    country_col = next((col for col in df.columns if "country" in col.lower()), None)
    industry_col = next((col for col in df.columns if "industry" in col.lower()), None)

    # Precompute stats
    context = {
        "columns": list(df.columns),
        "row_count": len(df),
        "top_countries": None,
        "top-Industries": None,
        "avg_valuation": None,
        "sample_companies": df.sample(3).to_dict("records") if "company" in df.columns else []
    }

    # Clean and calculate valuation if column exists
    if valuation_col:
        try:
            # Clean the valuation column
            df['cleaned_valuation'] = df[valuation_col].apply(clean_valuation)
            context["avg_valuation"] = df['cleaned_valuation'].mean()
        except Exception as e:
            st.error(f"Couldn't calculate valuation: {str(e)}")
            context["avg_valuation"] = None

    # Rest of the analysis (unchanged)
    if country_col:
        country_counts = df[country_col].value_counts().head(5).to_dict()
        context["top_countries"] = country_counts

    if industry_col:
        industry_counts = df[industry_col].value_counts().head(5).to_dict()
        context["top_industries"] = industry_counts

    # Build prompt (unchanged)
    prompt = f"""..."""  # Keep your existing prompt template
    return prompt

# Rest of the code remains the same...
