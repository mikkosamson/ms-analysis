import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Title
st.set_page_config(page_title="MS Analysis", layout="wide")
st.title("📊 Simple Data Analyzer")
st.write("Upload a CSV file below to see charts and insights automatically!")

# 2. The File Uploader
uploaded_file = st.file_uploader("Step 1: Upload your CSV file here", type="csv")

if uploaded_file is not None:
    # Load the data
    df = pd.read_csv(uploaded_file)
    
    # 3. Show the data table
    st.subheader("Step 2: Peek at your data")
    st.dataframe(df.head())

    # 4. Automatic Visuals
    st.subheader("Step 3: Visual Analytics")
    
    # Let the user pick columns for a chart
    columns = df.columns.tolist()
    x_var = st.selectbox("Pick something for the bottom (X-axis)", columns)
    y_var = st.selectbox("Pick something for the side (Y-axis)", columns)
    
    # Create the chart
    fig = px.bar(df, x=x_var, y=y_var, title=f"{y_var} by {x_var}")
    st.plotly_chart(fig, use_container_width=True)
    
    # 5. Simple Stats
    st.subheader("Step 4: Summary Statistics")
    st.write(df.describe())
else:
    st.info("Waiting for you to upload a file...")
