import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import google.generativeai as genai

st.set_page_config(page_title="AI Data Consultant", layout="wide")

# --- 1. AI SETUP ---
# This pulls the key from the "Secrets"
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
else:
    st.error("Please add your GEMINI_API_KEY to Streamlit Secrets!")

@st.cache_data
def load_data(file):
    if file.name.endswith('.csv'):
        return pd.read_csv(file)
    else:
        return pd.read_excel(file)

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

st.title("🤖 AI-Powered Data Analyst")

uploaded_file = st.file_uploader("Upload your data", type=["csv", "xlsx"])

if uploaded_file is not None:
    df = load_data(uploaded_file)
    numeric_df = df.select_dtypes(include=['number'])

    # --- 2. SIDEBAR EXPORT ---
    st.sidebar.header("📥 Export")
    st.sidebar.download_button("Download Excel Report", data=to_excel(df), file_name='report.xlsx')

    # --- 3. AI INSIGHTS GENERATION ---
    st.header("🧠 AI Analysis")
    
    if st.button("Generate AI Insights"):
        with st.spinner("The AI is studying your data..."):
            # We send a text summary of the data to the AI
										# Instead of sending everything, we only send a snapshot to keep it fast
									 data_summary = df.head(10).to_string() + "\n" + df.describe().to_string()
            prompt = f"""
            You are a professional data analyst. Here is a summary of a dataset:
            {data_summary}
            
            Please provide:
            1. A 2-sentence summary of the overall trend.
            2. Three specific bullet points of interesting observations.
            3. One 'Warning' or 'Action Item' for the business owner.
            """
            
            try:
                response = model.generate_content(prompt)
                st.markdown(response.text)
            except Exception as e:
                st.error(f"AI Error: {e}")

    # --- 4. VISUALS ---
    st.divider()
    st.header("📈 Interactive Charts")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        x_axis = st.selectbox("Select X-Axis", df.columns)
        y_axis = st.selectbox("Select Y-Axis", numeric_df.columns if not numeric_df.empty else df.columns)
        fig = px.bar(df, x=x_axis, y=y_axis, color_discrete_sequence=['#00CC96'])
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.subheader("Data Preview")
        st.dataframe(df.head(50))

else:
    st.info("Upload a file to unlock AI insights!")
