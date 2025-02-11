
#2025.02.11.13 med filtervariabek o breakvariabler

import streamlit as st
import pandas as pd
from collections import Counter

st.title("Multi-Response Survey Analyzer")

# Upload Excel file
uploaded_file = st.file_uploader("Upload your survey data (Excel format)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write("### Preview of Data:")
    st.dataframe(df.head())
    
    # User selects ID variable
    id_variable = st.selectbox("Select ID Variable:", df.columns)
    
    # User selects optional break variables
    break_variables = st.multiselect("Select Break Variables (Optional):", df.columns)
    
    # User selects optional filter variable
    filter_variable = st.selectbox("Select Filter Variable (Optional):", [None] + list(df.columns))
    filter_values = None
    if filter_variable:
        unique_values = df[filter_variable].dropna().unique()
        filter_values = st.multiselect("Select Filter Values:", unique_values)
        if filter_values:
            df = df[df[filter_variable].isin(filter_values)]
    
    # User selects columns with multi-response answers
    multiresponse_columns = st.multiselect("Select Multi-Response Columns:", df.columns)
    
    if st.checkbox("Analyze Data"):
        if not multiresponse_columns:
            st.warning("Please select at least one multi-response column.")
        else:
            # Flatten responses across selected columns
            all_responses = []
            for col in multiresponse_columns:
                all_responses.extend(df[col].dropna().astype(str).str.split(",").sum())
                
            # Count occurrences of each response
            response_counts = Counter(all_responses)
            
            # Convert to DataFrame
            results_df = pd.DataFrame(
                {
                    "Category": response_counts.keys(),
                    "Count": response_counts.values(),
                    "% Mentioned": [round((count / len(df)) * 100, 2) for count in response_counts.values()]
                }
            ).sort_values(by="Count", ascending=False)
            
            st.write("### Overall Analysis Results")
            st.dataframe(results_df)
            
            # Bar Chart
            st.bar_chart(results_df.set_index("Category")[["Count"]])
            
            # Analyze by break variables
            if break_variables:
                for break_var in break_variables:
                    st.write(f"### Analysis by {break_var}")
                    break_groups = df[break_var].dropna().unique()
                    for group in break_groups:
                        group_df = df[df[break_var] == group]
                        group_responses = []
                        for col in multiresponse_columns:
                            group_responses.extend(group_df[col].dropna().astype(str).str.split(",").sum())
                        group_counts = Counter(group_responses)
                        group_results_df = pd.DataFrame(
                            {
                                "Category": group_counts.keys(),
                                "Count": group_counts.values(),
                                "% Mentioned": [round((count / len(group_df)) * 100, 2) for count in group_counts.values()]
                            }
                        ).sort_values(by="Count", ascending=False)
                        st.write(f"#### {break_var}: {group}")
                        st.dataframe(group_results_df)
                        st.bar_chart(group_results_df.set_index("Category")[["Count"]])
