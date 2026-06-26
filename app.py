import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Care Load Analytics", layout="wide")

st.title("📊 System Capacity & Care Load Analytics for Unaccompanied Children")

# Upload Dataset
uploaded_file = st.file_uploader(
    "Upload CSV File",
    type=["csv"]
)

if uploaded_file is not None:

    df = pd.read_csv(uploaded_file)

    df.columns = df.columns.str.strip()

    st.write("Columns found:")
    st.write(df.columns.tolist())

    # Convert Date
    df["Date"] = pd.to_datetime(df["Date"])

    df = df.sort_values("Date")

    # Derived Metrics
    df["Total System Load"] = (
        df["Children in CBP custody"]
        + df["Children in HHS Care"]
    )

    df["Net Intake Pressure"] = (
        df["Children transferred out of CBP custody"]
        - df["Children discharged from HHS Care"]
    )

    df["Growth Rate (%)"] = (
        df["Total System Load"].pct_change() * 100
    )

    df["Backlog Accumulation"] = (
        df["Net Intake Pressure"].cumsum()
    )

    # Sidebar Filters
    st.sidebar.header("Filters")

    start_date = st.sidebar.date_input(
        "Start Date",
        df["Date"].min()
    )

    end_date = st.sidebar.date_input(
        "End Date",
        df["Date"].max()
    )

    filtered_df = df[
        (df["Date"] >= pd.to_datetime(start_date))
        &
        (df["Date"] <= pd.to_datetime(end_date))
    ]

    # KPI Cards
    st.subheader("Key Performance Indicators")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Children Under Care",
        int(filtered_df["Total System Load"].iloc[-1])
    )

    col2.metric(
        "Net Intake Pressure",
        round(filtered_df["Net Intake Pressure"].mean(), 2)
    )

    col3.metric(
        "Backlog Accumulation",
        int(filtered_df["Backlog Accumulation"].iloc[-1])
    )

    col4.metric(
        "Growth Rate %",
        round(filtered_df["Growth Rate (%)"].mean(), 2)
    )

    st.markdown("---")

    # System Load Trend
    st.subheader("📈 Total System Load Trend")

    fig1 = px.line(
        filtered_df,
        x="Date",
        y="Total System Load",
        title="Total System Load Over Time"
    )

    st.plotly_chart(fig1, use_container_width=True)

    # CBP vs HHS
    st.subheader("🏢 CBP vs HHS Load Comparison")

    fig2 = go.Figure()

    fig2.add_trace(
        go.Scatter(
            x=filtered_df["Date"],
            y=filtered_df["Children in CBP custody"],
            name="CBP Custody"
        )
    )

    fig2.add_trace(
        go.Scatter(
            x=filtered_df["Date"],
            y=filtered_df["Children in HHS Care"],
            name="HHS Care"
        )
    )

    st.plotly_chart(fig2, use_container_width=True)

    # Net Intake
    st.subheader("⚠️ Net Intake Pressure")

    fig3 = px.bar(
        filtered_df,
        x="Date",
        y="Net Intake Pressure",
        title="Transfers - Discharges"
    )

    st.plotly_chart(fig3, use_container_width=True)

    # Backlog
    st.subheader("📌 Backlog Accumulation")

    fig4 = px.line(
        filtered_df,
        x="Date",
        y="Backlog Accumulation",
        title="Backlog Trend"
    )

    st.plotly_chart(fig4, use_container_width=True)

    # Rolling Average Stress Analysis
    filtered_df["7-Day Rolling Load"] = (
        filtered_df["Total System Load"]
        .rolling(7)
        .mean()
    )

    st.subheader("🔥 Capacity Stress Analysis")

    fig5 = px.line(
        filtered_df,
        x="Date",
        y="7-Day Rolling Load",
        title="7-Day Rolling Average Load"
    )

    st.plotly_chart(fig5, use_container_width=True)

    # Project Insights
    st.subheader("Project Insights")

    st.write("""
    • The dashboard shows the overall system load over time.
    • Higher Net Intake Pressure indicates increasing burden on the care system.
    • Backlog Accumulation helps identify long-term capacity issues.
    • Decision-makers can use these insights for resource planning.
    """)

    # Raw Data
    st.subheader("Dataset Preview")
    st.dataframe(filtered_df)

else:
    st.info("Upload a CSV dataset to begin analysis.")