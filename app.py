import streamlit as st
import pandas as pd
import plotly.express as px
import os
import logging

logging.getLogger('streamlit').setLevel(logging.ERROR)

csv_path = os.path.join(os.path.dirname(__file__), "daily.csv")
if not os.path.exists(csv_path):
    st.error("daily.csv file not found. Please ensure the CSV file is in the same directory.")
    st.stop()

daily = pd.read_csv(csv_path)

daily['date'] = pd.to_datetime(daily['date'], dayfirst=True, errors='coerce').dt.date
daily['risk_score'] = pd.to_numeric(daily['risk_score'], errors='coerce')
daily['pincode'] = daily['pincode'].astype(str)

daily = daily.dropna(subset=['date', 'risk_score'])

st.title("🚀 Aadhaar Risk Monitoring Dashboard 🚀")

pincode = st.selectbox(
    "Select Pincode",
    ["All"] + sorted(daily['pincode'].unique())
)

data = daily if pincode == "All" else daily[daily['pincode'] == pincode]

if data.empty:
    st.error("No data available for the selected pincode.")
    st.stop()

date_selection = st.date_input(
    "Select Date Range",
    value=[data['date'].min(), data['date'].max()]
)

if isinstance(date_selection, tuple) and len(date_selection) == 2:
    start_date, end_date = date_selection
else:
    start_date = end_date = date_selection

data = data[(data['date'] >= start_date) & (data['date'] <= end_date)]

if data.empty:
    st.warning("No data available for the selected date range.")
    st.stop()

min_risk = int(data['risk_score'].min())
max_risk = int(data['risk_score'].max())

if min_risk < max_risk:
    risk_min, risk_max = st.slider(
        "Filter by Risk Score",
        min_risk,
        max_risk,
        (min_risk, max_risk)
    )
    data = data[
        (data['risk_score'] >= risk_min) &
        (data['risk_score'] <= risk_max)
    ]
else:
    st.info(f"ℹ️ All records have the same risk score: {min_risk}")

col1, col2, col3 = st.columns(3)
col1.metric("Total Days", len(data))
col2.metric("Max Risk Score", int(data['risk_score'].max()))
col3.metric("Average Risk", round(data['risk_score'].mean(), 2))

high_risk_days = (data['risk_score'] >= 70).sum()

if high_risk_days > 0:
    st.warning(f"⚠️ {high_risk_days} high-risk days detected")
else:
    st.success("✅ No high-risk activity detected")

data = data.sort_values("date")

fig_trend = px.line(
    data,
    x="date",
    y="risk_score",
    title="📈 Risk Trend Over Time"
)

st.plotly_chart(fig_trend, width='stretch')

if min_risk < max_risk:
    fig_dist = px.histogram(
        data,
        x="risk_score",
        nbins=20,
        title="📊 Risk Score Distribution"
    )
    st.plotly_chart(fig_dist, width='stretch')

st.subheader("⚠️ High Risk Days")

st.dataframe(
    data.sort_values("risk_score", ascending=False).head(10),
    width='stretch'
)

highest = data.loc[data['risk_score'].idxmax()]

st.info(
    f"📌 Highest risk recorded on {highest['date']} "
    f"with a score of {int(highest['risk_score'])}"
)