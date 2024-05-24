import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

# Set the title of the Streamlit app
st.title("Algorithm Performance Viewer")

# Set a markdown description
st.markdown("This app shows a bar chart comparing how different algorithms perform.")

# Load the benchmark results from the CSV file
data = pd.read_csv("benchmark_results.csv")

# Display the raw data as a table
st.subheader("Benchmark Results")
st.dataframe(data)

# Create a bar chart using Altair
bar_chart = (
    alt.Chart(data)
    .mark_bar()
    .encode(
        x=alt.X("Algorithm", sort="-y", title="Algorithm"),
        y=alt.Y("Execution Time (seconds)", title="Execution Time (seconds)"),
        color="Algorithm",
    )
    .properties(title="Algorithm Performance Comparison")
)

# Display the bar chart
st.altair_chart(bar_chart, use_container_width=True)

# Create a pie chart using Plotly
st.subheader("Pie Chart of Execution Time Consumed by Algorithms")
pie_chart = px.pie(
    data,
    values="Execution Time (seconds)",
    names="Algorithm",
    title="Execution Time Distribution",
)

# Display the pie chart
st.plotly_chart(pie_chart)
