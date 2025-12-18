import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
import time

st.set_page_config(page_title="AI Data Analyst", layout="wide")

# 1. THE FREE TIER MODEL FIX
# In Dec 2025, 'gemini-2.5-flash' is the most stable model for Free Tier keys
MODEL_NAME = 'gemini-2.5-flash'

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel(MODEL_NAME)
else:
    st.error("Missing API Key! Please add it to Streamlit Secrets.")

# 2. FAST LOADING
@st.cache_data
def load_data(file):
    if file.name.endswith('.csv'):
        return pd.read_csv(file, low_memory=False)
    else:
        return pd.read_excel(file, engine='openpyxl')

st.title("📊 Your AI Data Analyst")

uploaded_file = st.file_uploader("Upload your data", type=["csv", "xlsx"])

if uploaded_file is not None:
    df = load_data(uploaded_file)
    
    # --- AI ANALYSIS SECTION ---
    if st.button("Generate AI Insights"):
        with st.spinner("AI is thinking (Free Tier)..."):
            # Free tier has smaller limits; we only send a small snapshot
            stats_summary = df.describe().to_string()[:1000]
            
            try:
                # We add a 1-second delay to avoid "Rate Limit" errors on free keys
                time.sleep(1) 
                response = model.generate_content(f"Analyze these stats in 3 bullets: {stats_summary}")
                st.success("Analysis Complete!")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"AI Error: {e}")
                st.info("Check if your API Key is on a 'Free Project' in Google AI Studio.")

    # --- SPEED-OPTIMIZED CHARTS ---
    st.divider()
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    if numeric_cols:
        col1, col2 = st.columns(2)
        x = col1.selectbox("X Axis", df.columns)
        y = col2.selectbox("Y Axis", numeric_cols)
        
        # Plotting only 5,000 points to prevent browser freeze
        chart_df = df.sample(min(len(df), 5000))
        fig = px.scatter(chart_df, x=x, y=y, render_mode='webgl', template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

    st.dataframe(df.head(50))
