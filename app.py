import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Insight Pro", layout="wide")
st.title("📊 Data Insight Generator")

uploaded_file = st.file_uploader("Upload your CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success("File analyzed successfully!")

        # --- INSIGHTS SECTION ---
        st.header("🤖 Automated Insights")
        
        # Identify numeric columns for analysis
        numeric_df = df.select_dtypes(include=['number'])
        
        if not numeric_df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Finding the "Top" performer/value
                top_col = numeric_df.columns[0] # Takes the first number column
                max_val = df[top_col].max()
                max_row = df[df[top_col] == max_val].iloc[0]
                
                st.metric(label=f"Highest {top_col}", value=f"{max_val}")
                st.write(f"👉 The maximum value for **{top_col}** was found in the record indexed at **{df[top_col].idxmax()}**.")

            with col2:
                # Finding the Average
                avg_val = round(df[top_col].mean(), 2)
                st.metric(label=f"Average {top_col}", value=f"{avg_val}")
                st.write(f"👉 On average, your **{top_col}** sits at **{avg_val}** across all entries.")

        # --- VISUALS SECTION ---
        st.divider()
        st.header("📈 Visual Exploration")
        columns = df.columns.tolist()
        
        c1, c2 = st.columns(2)
        with c1:
            x_var = st.selectbox("Horizontal Axis (Categories)", columns)
        with c2:
            y_var = st.selectbox("Vertical Axis (Numbers)", numeric_df.columns.tolist())

        fig = px.bar(df, x=x_var, y=y_var, color=x_var, title=f"Comparison of {y_var} across {x_var}")
        st.plotly_chart(fig, use_container_width=True)

        # --- DATA VIEW ---
        with st.expander("View Raw Data Table"):
            st.dataframe(df)

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("Please upload a file to begin the analysis.")
