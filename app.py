{\rtf1\ansi\ansicpg1252\cocoartf2639
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\froman\fcharset0 Times-Roman;\f1\fnil\fcharset0 AppleColorEmoji;}
{\colortbl;\red255\green255\blue255;\red0\green0\blue0;}
{\*\expandedcolortbl;;\cssrgb\c0\c0\c0;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\deftab720
\pard\pardeftab720\partightenfactor0

\f0\fs24 \cf0 \expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 import streamlit as st\
import pandas as pd\
import openai\
\
# Load your OpenAI API key\
openai.api_key = "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"  # Replace with your key from Step A\
\
# Load your mock data\
df = pd.read_csv("mock_data.csv")\
\
# Chat interface\
st.title("Analytics Co-Pilot 
\f1 \uc0\u55357 \u56960 
\f0 ")\
user_input = st.text_input("Ask a question about your data:")\
\
if user_input:\
    # Ask GPT-4 to analyze the data\
    response = openai.ChatCompletion.create(\
        model="gpt-4",\
        messages=[\
            \{"role": "system", "content": f"Analyze this data: \{df\}. Answer concisely in plain text."\},\
            \{"role": "user", "content": user_input\}\
        ]\
    )\
    st.write("**Answer:**")\
    st.write(response.choices[0].message.content)}