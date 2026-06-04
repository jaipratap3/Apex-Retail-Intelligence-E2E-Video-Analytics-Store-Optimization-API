import streamlit as st
import requests
import time
import pandas as pd
import os

API_URL = os.environ.get("API_URL", "http://localhost:8000")
STORE_ID = "STORE_1"

st.set_page_config(page_title="Apex Retail Dashboard", layout="wide")

st.title(f"Apex Retail Live Dashboard - STORE_BLR_002")

# Layout
col1, col2, col3 = st.columns(3)

metrics_placeholder = st.empty()
funnel_placeholder = st.empty()
anomalies_placeholder = st.empty()

def fetch_data():
    try:
        m = requests.get(f"{API_URL}/stores/{STORE_ID}/metrics").json()
        f = requests.get(f"{API_URL}/stores/{STORE_ID}/funnel").json()
        a = requests.get(f"{API_URL}/stores/{STORE_ID}/anomalies").json()
        return m, f, a
    except:
        return None, None, None

while True:
    metrics, funnel, anomalies = fetch_data()
    
    if metrics:
        with metrics_placeholder.container():
            st.subheader("Live Metrics")
            c1, c2, c3 = st.columns(3)
            c1.metric("Unique Visitors", metrics.get("unique_visitors", 0))
            c2.metric("Conversion Rate", f"{metrics.get('conversion_rate_percent', 0)}%")
            c3.metric("Queue Depth", metrics.get("current_queue_depth", 0))
            
    with funnel_placeholder.container():
        st.subheader("Conversion Funnel")
        if funnel and "funnel" in funnel and funnel["funnel"]:
            df = pd.DataFrame(funnel["funnel"])
            if not df.empty:
                st.bar_chart(df.set_index("stage")["count"])
        else:
            st.info("Waiting for tracking data to generate funnel...")
                
    with anomalies_placeholder.container():
        st.subheader("Active Anomalies")
        if anomalies and "anomalies" in anomalies and anomalies["anomalies"]:
            for anom in anomalies["anomalies"]:
                if anom["severity"] == "CRITICAL":
                    st.error(f"{anom['type']}: {anom['message']}")
                elif anom["severity"] == "WARN":
                    st.warning(f"{anom['type']}: {anom['message']}")
                else:
                    st.info(f"{anom['type']}: {anom['message']}")
        else:
            st.success("✅ No anomalies detected. Store operating optimally.")
    
    time.sleep(2)
