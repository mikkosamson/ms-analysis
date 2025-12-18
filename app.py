import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import google.generativeai as genai
import time

# 1. Page Config
st.set_page_config(page_title="AI Data Analyst", layout="wide")

# 2. AI Initialization with Smart Fallback
def get_ai_response(prompt):
    """Tries multiple model versions to bypass 404/version errors"""
    # List of models from newest to most compatible
    models_to_try = ['gemini-3-flash', 'gemini-2.0-flash', 'gemini-1.5-flash']
    
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            if "404" in str(e):
                continue # Try the next model in the list
            else:
                return f"AI Error: {e}"
    return "Unable to connect to any Gemini models. Please check your API key."

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Missing GEMINI_API_KEY in Streamlit Secrets!")

# 3. Fast Data Loading
@st.cache_data(show_spinner="Processing large dataset...")
def load_data(file):
    if file.name.endswith('.csv'):
        return pd.read_csv(file, low_memory=False)
    else:
        return pd.read_excel(file, engine='openpyxl')

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

# --- APP UI ---
st.title("🤖 AI-Powered Data Analyst")
st.markdown("Automated insights and interactive charts for CSV/Excel files.")

uploaded_file = st.file_uploader("Upload your file (Max 200MB)", type=["csv", "xlsx"])

if uploaded_file is not None:
    df = load_data(uploaded_file)
    
    # Sidebar for Export
    st.sidebar.header("📥 Export Options")
    st.sidebar.download_button("Download Report", data=to_excel(df), file_name="analysis.xlsx")
    st.sidebar.info(f"Loaded {len(df):,} rows.")

    # AI Section
    st.header("🧠 AI Insights")
    if st.button("Generate Analysis"):
        with st.spinner("Consulting the AI..."):
            # Truncate summary to keep it safe for Free Tier limits
            summary = df.describe().to_string()[:1500]
            prompt = f"Act as a data analyst. Provide 3 key business takeaways from these stats:\n{summary}"
            
            # Use the fallback function
            result = get_ai_response(prompt)
            st.markdown(result)

    # Visuals Section
    st.divider()
    st.header("📈 Data Visualization")
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    if numeric_cols:
        col1, col2 = st.columns([2, 1])
        with col1:
            x = st.selectbox("Select X-Axis", df.columns)
            y = st.selectbox("Select Y-Axis", numeric_cols)
            fig = px.bar(df, x=x, y=y, color_discrete_sequence=['#0083B0'])
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.subheader("Search Data")
            term = st.text_input("Search keywords:")
            if term:
                display_df = df[df.apply(lambda r: term.lower() in r.astype(str).str.lower().values, axis=1)]
            else:
                display_df = df.head(100)
            st.dataframe(display_df)
    else:
        st.warning("No numeric data found to create charts.")

else:
    st.info("Upload a dataset to begin your analysis.")
