import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="My Data Tool", layout="wide")
st.title("📊 Simple Data Analyzer")

# UPDATED: Added 'xlsx' to the types
uploaded_file = st.file_uploader("Step 1: Upload your CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file is not None:
    # UPDATED: Logic to handle both CSV and Excel
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.subheader("Step 2: Peek at your data")
        st.dataframe(df.head())

        st.subheader("Step 3: Visual Analytics")
        columns = df.columns.tolist()
        x_var = st.selectbox("Pick X-axis", columns)
        y_var = st.selectbox("Pick Y-axis", columns)
        
        fig = px.bar(df, x=x_var, y=y_var, title=f"{y_var} by {x_var}")
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Step 4: Summary Statistics")
        st.write(df.describe())
        
    except Exception as e:
        st.error("Wait, something went wrong. Make sure your file isn't empty!")
else:
    st.info("Waiting for you to upload a file...")
