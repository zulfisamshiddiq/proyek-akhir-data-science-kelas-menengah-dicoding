import streamlit as st
import pandas as pd
import plotly.express as px

# PAGE CONFIG
st.set_page_config(
    page_title="Customer Behavior & RFM Dashboard",
    page_icon="📊",
    layout="wide"
)

# LOAD DATA
@st.cache_data
def load_data():
    return pd.read_csv("dashboard/main_data.csv")

df = load_data()

# SIDEBAR FILTER
st.sidebar.title("🔎 Filter Data")

segment_filter = st.sidebar.multiselect(
    "Segment RFM",
    options=df["Segment"].unique(),
    default=df["Segment"].unique()
)

state_filter = st.sidebar.multiselect(
    "State",
    options=df["customer_state"].unique(),
    default=df["customer_state"].unique()
)

filtered_df = df[
    (df["Segment"].isin(segment_filter)) &
    (df["customer_state"].isin(state_filter))
]

# HEADER
st.title("📊 Customer Behavior Analysis Dashboard")
st.markdown(
    "Analisis perilaku pelanggan berbasis **RFM Segmentation** "
    "dan **distribusi geografis**."
)

# KPI METRICS
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Customers", f"{filtered_df['customer_unique_id'].nunique():,}")
col2.metric("Total Revenue", f"{filtered_df['monetary'].sum():,.2f}")
col3.metric("Avg Recency (days)", f"{filtered_df['recency'].mean():.1f}")
col4.metric("Avg Frequency", f"{filtered_df['frequency'].mean():.2f}")

st.markdown("---")

# 1. RECENCY DISTRIBUTION
fig_rec = px.histogram(
    filtered_df,
    x="recency",
    nbins=30,
    title="Distribusi Recency Pelanggan"
)
st.plotly_chart(fig_rec, use_container_width=True)

# 2. FREQUENCY DISTRIBUTION
fig_freq = px.histogram(
    filtered_df,
    x="frequency",
    title="Distribusi Frequency Transaksi"
)
st.plotly_chart(fig_freq, use_container_width=True)

# 3. MONETARY DISTRIBUTION
fig_mon = px.histogram(
    filtered_df,
    x="monetary",
    nbins=30,
    title="Distribusi Monetary Pelanggan"
)
st.plotly_chart(fig_mon, use_container_width=True)

# 4. SEGMENT DISTRIBUTION
segment_dist = (
    filtered_df
    .groupby("Segment")["customer_unique_id"]
    .nunique()
    .reset_index(name="total_customers")
)

fig_seg = px.bar(
    segment_dist,
    x="total_customers",
    y="Segment",
    orientation="h",
    title="Distribusi Segment Pelanggan (RFM)",
    color="Segment"
)
st.plotly_chart(fig_seg, use_container_width=True)

# 5. TOP 10 STATE BY CUSTOMERS
state_customer_df = (
    filtered_df
    .groupby("customer_state")["customer_unique_id"]
    .nunique()
    .sort_values(ascending=False)
    .head(10)
    .reset_index(name="total_customers")
)

fig_state_cust = px.bar(
    state_customer_df,
    x="customer_state",
    y="total_customers",
    title="Top 10 State berdasarkan Jumlah Pelanggan"
)
st.plotly_chart(fig_state_cust, use_container_width=True)

# 6. TOP 10 STATE BY REVENUE
state_revenue_df = (
    filtered_df
    .groupby("customer_state")["monetary"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index(name="total_revenue")
)

fig_state_rev = px.bar(
    state_revenue_df,
    x="customer_state",
    y="total_revenue",
    title="Top 10 State berdasarkan Total Revenue"
)
st.plotly_chart(fig_state_rev, use_container_width=True)

# 7. TOP 10 CITY BY CUSTOMERS
city_customer_df = (
    filtered_df
    .groupby("customer_city")["customer_unique_id"]
    .nunique()
    .sort_values(ascending=False)
    .head(10)
    .reset_index(name="total_customers")
)

fig_city = px.bar(
    city_customer_df,
    x="customer_city",
    y="total_customers",
    title="Top 10 Kota berdasarkan Jumlah Pelanggan"
)
st.plotly_chart(fig_city, use_container_width=True)

# 8. SEGMENT DISTRIBUTION IN TOP 5 STATES
top_states = (
    filtered_df
    .groupby("customer_state")["customer_unique_id"]
    .nunique()
    .sort_values(ascending=False)
    .head(5)
    .index
)

segment_state_df = (
    filtered_df[filtered_df["customer_state"].isin(top_states)]
    .groupby(["customer_state", "Segment"])["customer_unique_id"]
    .nunique()
    .reset_index(name="total_customers")
)

fig_seg_state = px.bar(
    segment_state_df,
    x="customer_state",
    y="total_customers",
    color="Segment",
    title="Distribusi Segment RFM pada Top 5 State",
    barmode="group"
)
st.plotly_chart(fig_seg_state, use_container_width=True)

# 9. GEO MAP DISTRIBUTION
geo_df = (
    filtered_df
    .groupby(["customer_state", "geolocation_lat", "geolocation_lng"])
    .agg(
        total_customers=("customer_unique_id", "nunique"),
        total_revenue=("monetary", "sum")
    )
    .reset_index()
)

fig_map = px.scatter_mapbox(
    geo_df,
    lat="geolocation_lat",
    lon="geolocation_lng",
    size="total_customers",
    color="total_revenue",
    hover_name="customer_state",
    zoom=3,
    height=600,
    title="Distribusi Geografis Pelanggan & Revenue"
)

fig_map.update_layout(
    mapbox_style="open-street-map",
    margin={"r":0,"t":40,"l":0,"b":0}
)

st.plotly_chart(fig_map, use_container_width=True)

# DATA PREVIEW
with st.expander("🔍 Preview Data"):
    st.dataframe(filtered_df.head(100))

st.markdown("---")
st.caption("Dashboard RFM & Geo Analysis | Data Science Workflow")
