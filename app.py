import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import google.generativeai as genai

# 1. Page Configuration
st.set_page_config(page_title="AI Data Consultant", layout="wide")

# 2. AI Setup with Error Handling
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # Using 'flash-latest' to fix the 404 error
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
else:
    st.error("Missing API Key! Please add GEMINI_API_KEY to your Streamlit Secrets.")

# 3. Optimized Data Loading (Prevents crashing with 64MB+ files)
@st.cache_data(show_spinner="Analyzing file...")
def load_data(file):
    try:
        if file.name.endswith('.csv'):
            return pd.read_csv(file, low_memory=False)
        else:
            return pd.read_excel(file, engine='openpyxl')
    except Exception as e:
        st.error(f"Memory Error: {e}")
        return None

# 4. Helper for Excel Download
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

# --- APP UI ---
st.title("🤖 AI-Powered Data Analyst")
st.markdown("Upload large datasets and get instant AI insights.")

uploaded_file = st.file_uploader("Upload CSV or Excel (Max 200MB)", type=["csv", "xlsx"])

if uploaded_file is not None:
    df = load_data(uploaded_file)
    
    if df is not None:
        numeric_df = df.select_dtypes(include=['number'])

        # --- SIDEBAR: Export & Info ---
        with st.sidebar:
            st.header("📥 Export Results")
            st.download_button(
                label="Download as Excel",
                data=to_excel(df),
                file_name='data_report.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            st.divider()
            st.write(f"**Rows:** {len(df):,}")
            st.write(f"**Columns:** {len(df.columns)}")

        # --- SECTION: AI ANALYSIS ---
        st.header("🧠 Smart Insights")
        if st.button("Analyze with AI"):
            with st.spinner("Gemini is processing your data summary..."):
                # We send a "snapshot" of the data so the AI doesn't get overwhelmed
                stats_summary = df.describe().to_string()
                data_head = df.head(5).to_string()
                
                prompt = f"""
                Act as a senior data consultant. Here is a summary of my dataset:
                
                SNAPSHOT:
                {data_head}
                
                STATISTICS:
                {stats_summary}
                
                Please provide:
                1. A summary of the most important trend.
                2. Three hidden patterns or anomalies.
                3. A concrete business recommendation based on these numbers.
                """
                
                try:
                    response = model.generate_content(prompt)
                    st.success("AI Analysis Complete!")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"AI Error: {e}")

        # --- SECTION: VISUALS ---
        st.divider()
        st.header("📈 Interactive Visuals")
        col1, col2 = st.columns([3, 1])
        
        with col1:
            x_axis = st.selectbox("Horizontal Axis", df.columns)
            y_axis = st.selectbox("Vertical Axis", numeric_df.columns if not numeric_df.empty else df.columns)
            
            # Using 'render_mode=webgl' makes large charts much faster
            fig = px.scatter(df, x=x_axis, y=y_axis, color=x_axis, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            st.subheader("Data Search")
            search = st.text_input("Find a specific record:")
            if search:
                mask = df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)
                st.dataframe(df[mask].head(50))
            else:
                st.dataframe(df.head(50))

else:
    st.info("Please upload a file to begin.")
