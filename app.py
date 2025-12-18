import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import google.generativeai as genai
import time

st.set_page_config(page_title="AI Data Analyst", layout="wide")

# --- 1. AI SETUP ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # We use 1.5-flash as it is the most reliable for Free Tier usage
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("Missing API Key! Add it to Streamlit Secrets.")

@st.cache_data
def load_data(file):
    try:
        if file.name.endswith('.csv'):
            return pd.read_csv(file, low_memory=False)
        else:
            return pd.read_excel(file, engine='openpyxl')
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

st.title("🤖 AI Data Analyst")

uploaded_file = st.file_uploader("Upload your data", type=["csv", "xlsx"])

if uploaded_file is not None:
    df = load_data(uploaded_file)
    
    if df is not None:
        # SIDEBAR
        st.sidebar.header("Options")
        st.sidebar.download_button("Download Report", data=to_excel(df), file_name="report.xlsx")

        # --- 2. AI ANALYSIS SECTION (Optimized for Free Tier) ---
        st.header("🧠 AI Insights")
        if st.button("Analyze Data"):
            with st.spinner("Talking to Gemini (Free Tier)..."):
                # We only send a very small summary to stay within Free Tier limits
                # Large files (64MB) have huge summaries; we truncate here
                stats = df.describe().to_string()[:2000] # Limit to 2000 characters
                
                prompt = f"Analyze these stats and give 3 bullet points: {stats}"
                
                try:
                    # Added a small pause to help with rate limiting
                    time.sleep(1) 
                    response = model.generate_content(prompt)
                    st.success("Analysis complete!")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Gemini Free Tier Error: {e}")
                    st.info("Tip: If you get a 404, check that your API key is 'General Availability' in Google AI Studio.")

        # --- 3. CHART SECTION ---
        st.divider()
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        if numeric_cols:
            x = st.selectbox("X-Axis", df.columns)
            y = st.selectbox("Y-Axis", numeric_cols)
            fig = px.histogram(df, x=x, y=y, color_discrete_sequence=['#3366ff'])
            st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Raw Data Preview")
        st.dataframe(df.head(20))

else:
    st.info("Upload a file to start.")
