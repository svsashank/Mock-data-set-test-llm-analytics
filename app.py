import streamlit as st
import pandas as pd
from openai import OpenAI
import plotly.express as px  # For visualizations

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("🚀 Unicorn Analytics Pro")
uploaded_file = st.file_uploader("Upload your unicorn company dataset", type="csv")

def analyze_data(df, question):
    """Precompute critical metrics and prepare context."""
    # Auto-detect key columns (expand this logic as needed)
    country_col = next((col for col in df.columns if "country" in col.lower()), None)
    valuation_col = next((col for col in df.columns if "valuation" in col.lower()), None)
    industry_col = next((col for col in df.columns if "industry" in col.lower()), None)

    # Precompute stats (modularize this for scalability)
    context = {
        "columns": list(df.columns),
        "row_count": len(df),
        "top_countries": None,
        "top_industries": None,
        "avg_valuation": None,
        "sample_companies": df.sample(3).to_dict("records") if "company" in df.columns else []
    }

    if country_col:
        country_counts = df[country_col].value_counts().head(5).to_dict()
        context["top_countries"] = country_counts

    if industry_col:
        industry_counts = df[industry_col].value_counts().head(5).to_dict()
        context["top_industries"] = industry_counts

    if valuation_col:
        context["avg_valuation"] = df[valuation_col].mean()

    # Build a rich, structured prompt
    prompt = f"""
    **Task**: Answer the question "{question}" using the dataset below. Prioritize *quantitative accuracy*.

    **Dataset Context**:
    - Columns: {context['columns']}
    - Total companies: {context['row_count']}
    - Top countries: {context['top_countries'] or "N/A"}
    - Top industries: {context['top_industries'] or "N/A"}
    - Average valuation: ${context['avg_valuation']:,.2f} (if applicable)
    - Sample companies: {context['sample_companies']}

    **Rules**:
    1. If the data is insufficient, say so and suggest what’s needed.
    2. Include specific numbers (e.g., "5 companies") and trends.
    3. Compare against precomputed stats like top countries/industries.
    """

    return prompt

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("Data Preview:", df.head(2))

    question = st.text_input("Ask a question (e.g., 'Which country dominates in tech unicorns?'):")

    if question:
        with st.spinner("Crunching numbers..."):
            # Step 1: Precompute stats and build prompt
            prompt = analyze_data(df, question)

            # Step 2: Call OpenAI with prioritized analytics
            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are a data analyst. Use the context below."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1
                )
                answer = response.choices[0].message.content

                # Step 3: Display results with visualizations (example)
                st.subheader("Answer")
                st.write(answer)

                # Add a simple visualization (e.g., top countries)
                country_col = next((col for col in df.columns if "country" in col.lower()), None)
                if country_col:
                    fig = px.bar(df[country_col].value_counts().head(5), title="Top Countries by Unicorn Count")
                    st.plotly_chart(fig)

            except Exception as e:
                st.error(f"Error: {str(e)}")
