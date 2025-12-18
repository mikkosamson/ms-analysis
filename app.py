import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import google.generativeai as genai

st.set_page_config(page_title="High-Speed AI Analyst", layout="wide")

# --- AI SETUP ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("Missing API Key in Secrets!")

# --- FAST DATA LOADING ---
@st.cache_data(show_spinner="Loading data...")
def load_data(file):
    if file.name.endswith('.csv'):
        # low_memory=True helps with speed on large CSVs
        return pd.read_csv(file, low_memory=True)
    else:
        # Excel is slow; caching here is critical
        return pd.read_excel(file, engine='openpyxl')

st.title("🚀 High-Speed Data Analyst")

uploaded_file = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])

if uploaded_file is not None:
    df = load_data(uploaded_file)
    
    # 1. SIDEBAR STATS
    st.sidebar.header("Dataset Overview")
    st.sidebar.write(f"Total Rows: **{len(df):,}**")
    
    # 2. AI INSIGHTS (Uses a sample for speed)
    if st.button("Generate AI Report"):
        with st.spinner("AI is analyzing a sample of your data..."):
            # We only send 500 rows to the AI to keep it instant and free
            sample_summary = df.sample(min(len(df), 500)).describe().to_string()
            try:
                response = model.generate_content(f"Analyze these stats and give 3 takeaways: {sample_summary}")
                st.info(response.text)
            except Exception as e:
                st.error(f"AI Error: {e}")

    # 3. SPEED-OPTIMIZED VISUALS
    st.divider()
    st.header("📈 Fast Visualizations")
    
    num_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    if num_cols:
        col1, col2 = st.columns(2)
        with col1:
            x_axis = st.selectbox("X-Axis", df.columns)
        with col2:
            y_axis = st.selectbox("Y-Axis", num_cols)
        
        # SPEED TRICK: If data is large, we sample it for the chart
        chart_df = df
        if len(df) > 5000:
            st.warning("Large dataset detected: Plotting a random 5,000 point sample for speed.")
            chart_df = df.sample(5000)
        
        fig = px.scatter(chart_df, x=x_axis, y=y_axis, template="plotly_white")
        # Use_container_width makes it fit the screen
        st.plotly_chart(fig, use_container_width=True)

    # 4. COLLAPSIBLE DATA TABLE
    with st.expander("🔍 Click to View/Search Raw Data"):
        search = st.text_input("Search records:")
        if search:
            st.dataframe(df[df.apply(lambda r: search.lower() in r.astype(str).str.lower().values, axis=1)].head(100))
        else:
            st.dataframe(df.head(100))

else:
    st.info("Upload a file to begin.")
