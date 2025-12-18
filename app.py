import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

st.set_page_config(page_title="Insight Pro", layout="wide")
st.title("🚀 Data Insight Generator")

@st.cache_data
def load_data(file):
    if file.name.endswith('.csv'):
        return pd.read_csv(file)
    else:
        return pd.read_excel(file)

# --- NEW FUNCTION: CONVERT TO EXCEL FOR DOWNLOAD ---
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Analysis')
    return output.getvalue()

uploaded_file = st.file_uploader("Upload your CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file is not None:
    df = load_data(uploaded_file)
    
    # --- DOWNLOAD SECTION ---
    st.sidebar.header("📥 Export Results")
    excel_data = to_excel(df)
    st.sidebar.download_button(
        label="Download Analysis as Excel",
        data=excel_data,
        file_name='my_analysis_report.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    # --- AUTOMATED INSIGHTS ---
    st.header("🤖 Key Findings")
    numeric_df = df.select_dtypes(include=['number'])
    
    if not numeric_df.empty:
        main_col = numeric_df.columns[0]
        total_sum = numeric_df[main_col].sum()
        avg_val = numeric_df[main_col].mean()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Count", f"{len(df):,}")
        col2.metric(f"Total {main_col}", f"{total_sum:,.2f}")
        col3.metric(f"Average {main_col}", f"{avg_val:,.2f}")
        
        st.info(f"**Insight:** Your largest **{main_col}** is {df[main_col].max()}, which is {round(df[main_col].max()/avg_val, 1)}x higher than the average.")

    # --- VISUALS ---
    st.divider()
    chart_col, data_col = st.columns([2, 1])
    
    with chart_col:
        st.subheader("Interactive Visual")
        x_var = st.selectbox("Category (X-axis)", df.columns)
        y_var = st.selectbox("Value (Y-axis)", numeric_df.columns)
        
        fig = px.scatter(df, x=x_var, y=y_var, color=x_var, template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

    with data_col:
        st.subheader("Data Search")
        search = st.text_input("Search records:")
        if search:
            filtered_df = df[df.apply(lambda row: search.lower() in row.astype(str).str.lower().values, axis=1)]
            st.dataframe(filtered_df, height=400)
        else:
            st.dataframe(df.head(100), height=400)

else:
    st.info("Upload a file to begin.")
