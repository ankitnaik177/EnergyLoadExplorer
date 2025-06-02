import streamlit as st
import pandas as pd
import plotly.express as px

# --- Load Data ---
raw_city_df = pd.read_csv("city_data.csv")

cityNames_df = raw_city_df["City"].str.replace('"','',regex=False)
lat_df = raw_city_df["Lat"]
lon_df = raw_city_df["Lon"]
month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
month_df = pd.Categorical(raw_city_df["Month"], categories=month_order, ordered=True)
month_df = raw_city_df["Month"]
monthHeatData_df = raw_city_df["MonthHeat"]
monthColdData_df = raw_city_df["MonthCold"]
monthWaterData_df = raw_city_df["MonthWater"]
monthElecData_df = raw_city_df["MonthElec"]
monthSolarData_df = raw_city_df["MonthSolar"]

city_df = pd.DataFrame({
    "City": cityNames_df,
    "Lat": lat_df,
    "Lon": lon_df,
    "Month": month_df,
    "Heating Load (kWh)":monthHeatData_df,
    "Cooling Load (kWh)":monthColdData_df,
    "Water Heating (kWh)":monthWaterData_df,
    "Electrical Appliance (kWh)":monthElecData_df,
    "Total Electrical Load (kWh)": monthHeatData_df + monthColdData_df + monthWaterData_df + monthElecData_df,
    "Solar Energy Production (kWh)":monthSolarData_df,
    "Grid Dependency (kWh)": (monthHeatData_df + monthColdData_df + monthWaterData_df + monthElecData_df - monthSolarData_df).clip(lower=0)
})

# --- Set GUI ---

st.set_page_config(layout="wide")
st.title("🌍 Global Energy Load Explorer")

st.markdown(
    "> **Note:** Simulations are based on a 100 m² home with a 50 m² rooftop solar."
)

st.markdown(
    """
    🔗 **Related Resources**  
    - 📖 [Read the full blog post on Medium](https://medium.com/@ankitnaik177/should-i-invest-in-rooftop-solar-for-my-home-94e6402a61f5)
    - 🎥 [Watch the video walkthrough on YouTube](https://www.youtube.com/watch?v=koYohL7LdgE&t=1s)
    """,
    unsafe_allow_html=True
)

# Sidebar filters
cities = city_df["City"].unique()
default_city = "Paris" if "Paris" in cities else cities[0]
selected_cities = st.sidebar.multiselect("Select Cities", cities, default=[default_city])

# Filter data
filtered_df = city_df[city_df["City"].isin(selected_cities)]

st.markdown("### Global Load Heatmap")

# Load type selector
load_type = st.sidebar.selectbox("Select Load Type",["Heating Load (kWh)", "Cooling Load (kWh)", "Water Heating (kWh)","Electrical Appliance (kWh)","Total Electrical Load (kWh)","Solar Energy Production (kWh)","Grid Dependency (kWh)"],index=5)


map_data = city_df[["City", "Lat", "Lon", "Month", load_type]]

# Dark-themed map with bubble heatmap
fig_map = px.scatter_geo(
    map_data,
    lat="Lat",
    lon="Lon",
    color=load_type,
    size=load_type,
    hover_name="City",
    range_color=[city_df[load_type].min(), city_df[load_type].max()],
    animation_frame="Month",
    color_continuous_scale="thermal",  # Use "viridis" or "hot" or "thermal" for dark mode
    projection="natural earth",
    template="plotly_dark",  # Dark theme
    title=f"{load_type.replace('_', ' ')} by City and Month"
)

fig_map.update_layout(
    height=700,
    geo=dict(
        bgcolor='rgba(0,0,0,0)',
        showland=True,
        landcolor="rgba(40,40,40,0.5)",
        showcountries=True,
        countrycolor="rgba(200,200,200,0.9)",  # Light gray borders
        showframe=False,
        showcoastlines=True,
        coastlinecolor="rgba(180,180,180,0.3)"
    ),
    margin=dict(t=20, b=10, l=0, r=0) 
)

st.plotly_chart(fig_map, use_container_width=True)

if st.session_state.get('client_width', 1200) < 600:
    fig_map.update_layout(height=500)


# Time-series comparison
st.markdown("### Monthly Load Comparison")

for metric in ["Heating Load (kWh)", "Cooling Load (kWh)", "Water Heating (kWh)","Electrical Appliance (kWh)","Total Electrical Load (kWh)","Solar Energy Production (kWh)","Grid Dependency (kWh)"]:
    st.markdown(f"#### {metric.replace('_', ' ')}")
    fig = px.line(
        filtered_df,
        x="Month",
        y=metric,
        color="City",
        markers=True
    )
    st.plotly_chart(fig)

st.markdown("### Download Data")

csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download filtered data as CSV",
    data=csv,
    file_name='filtered_climate_loads.csv',
    mime='text/csv',
)
