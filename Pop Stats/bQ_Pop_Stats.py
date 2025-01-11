import pandas as pd
import streamlit as st
from google.cloud import bigquery
import altair as alt

# Initialize the BigQuery client
key_path = r"D:\Self Work\marketmosaic-ab9d58c22805.json"
client = bigquery.Client.from_service_account_json(key_path)

# Query to fetch data from BigQuery
query = """
SELECT
  *
FROM
  `marketmosaic.census_2017_datamodel.Vw_Gender_Age_Group_Population`
"""
# Fetch data from BigQuery
@st.cache_data
def fetch_data():
    query_job = client.query(query)
    return query_job.to_dataframe()

data = fetch_data()

# Streamlit App
st.title("Population Statistics Dashboard")

# Cascading Filters
st.sidebar.header("Filters")

# Province Dropdown
province_filter = st.sidebar.selectbox(
    "Select Province", options=["All"] + data["province_name"].unique().tolist()
)

# Filter districts based on the selected province
if province_filter != "All":
    filtered_data_by_province = data[data["province_name"] == province_filter]
else:
    filtered_data_by_province = data

district_filter = st.sidebar.selectbox(
    "Select District", options=["All"] + filtered_data_by_province["district_name"].unique().tolist()
)

# Filter areas based on the selected district
if district_filter != "All":
    filtered_data_by_district = filtered_data_by_province[filtered_data_by_province["district_name"] == district_filter]
else:
    filtered_data_by_district = filtered_data_by_province

area_type_filter = st.sidebar.selectbox(
    "Select Area Type", options=["All"] + filtered_data_by_district["area_type"].unique().tolist()
)

# Filter genders based on the filtered data
if area_type_filter != "All":
    filtered_data = filtered_data_by_district[filtered_data_by_district["area_type"] == area_type_filter]
else:
    filtered_data = filtered_data_by_district

gender_filter = st.sidebar.selectbox(
    "Select Gender", options=["All"] + filtered_data["gender"].unique().tolist()
)

if gender_filter != "All":
    filtered_data = filtered_data[filtered_data["gender"] == gender_filter]

# Main Content: Display Filtered Data
st.subheader("Table")
st.dataframe(filtered_data)

# Calculate total population
total_population = filtered_data["group_all_ages"].sum()
st.subheader("Total Population")
# Display total population as a card
st.metric(label="", value=f"{total_population:,}")

# Visualization 1: Gender Distribution
st.subheader("Gender Distribution")
gender_distribution = filtered_data.groupby("gender")["group_all_ages"].sum().reset_index()
gender_pie = alt.Chart(gender_distribution).mark_arc().encode(
    theta=alt.Theta("group_all_ages:Q", title="Population"),
    color=alt.Color("gender:N", title="Gender"),
    tooltip=["gender", "group_all_ages"]
).properties(
    width=700,
    height=400
)
st.altair_chart(gender_pie)

# Visualization 2: Population by Province
st.subheader("Population by Province")
province_population = filtered_data.groupby("province_name")["group_all_ages"].sum().reset_index()
province_bar = alt.Chart(province_population).mark_bar().encode(
    x=alt.X("group_all_ages:Q", title="Population"),
    y=alt.Y("province_name:N", title="Province"),
    tooltip=["province_name", "group_all_ages"],
    color=alt.Color("province_name:N", legend=None)
).properties(
    width=700,
    height=400
)
st.altair_chart(province_bar)

# Visualization 3: Age Group Trends
st.subheader("Age Group Distribution")
age_group_cols = [col for col in filtered_data.columns if col.startswith("group_") and col != "group_all_ages"]
age_group_distribution = filtered_data[age_group_cols].sum().reset_index()
age_group_distribution.columns = ["Age Group", "Population"]
age_group_line = alt.Chart(age_group_distribution).mark_line(point=True).encode(
    x=alt.X("Age Group:N", title="Age Group"),
    y=alt.Y("Population:Q", title="Population"),
    tooltip=["Age Group", "Population"]
).properties(
    width=700,
    height=400
)
st.altair_chart(age_group_line)

# Visualization 4: Urban vs. Rural Population
st.subheader("Urban vs Rural Population")
area_population = filtered_data.groupby("area_type")["group_all_ages"].sum().reset_index()
area_bar = alt.Chart(area_population).mark_bar().encode(
    x=alt.X("area_type:N", title="Area Type"),
    y=alt.Y("group_all_ages:Q", title="Population"),
    tooltip=["area_type", "group_all_ages"],
    color=alt.Color("area_type:N", legend=None)
).properties(
    width=700,
    height=400
)
st.altair_chart(area_bar)

# Visualization 5: Senior Citizen Population
st.subheader("Senior Citizen Population by Province (60+ Age)")
senior_population = filtered_data.groupby("province_name")["group_60_and_up"].sum().reset_index()
senior_bar = alt.Chart(senior_population).mark_bar().encode(
    x=alt.X("group_60_and_up:Q", title="Population (60+)"),
    y=alt.Y("province_name:N", title="Province"),
    tooltip=["province_name", "group_60_and_up"],
    color=alt.Color("province_name:N", legend=None)
).properties(
    width=700,
    height=400
)
st.altair_chart(senior_bar)

# Visualization 6: Adult Population Analysis
st.subheader("Adult Population Analysis (18+ Age)")

# Total Adult Population
total_adult_population = filtered_data["group_18_and_up"].sum()
st.metric(label="Total Adult Population", value=f"{total_adult_population:,}")

# Adult Population by Gender (Pie Chart)
st.subheader("Adult Population by Gender (18+ Age)")
adult_by_gender = filtered_data.groupby("gender")["group_18_and_up"].sum().reset_index()

adult_gender_pie = alt.Chart(adult_by_gender).mark_arc().encode(
    theta=alt.Theta("group_18_and_up:Q", title="Adult Population"),
    color=alt.Color("gender:N", title="Gender"),
    tooltip=["gender", "group_18_and_up"]
).properties(
    width=700,
    height=400
)
st.altair_chart(adult_gender_pie)


# Adult Population by Province
adult_by_province = filtered_data.groupby("province_name")["group_18_and_up"].sum().reset_index()
adult_province_bar = alt.Chart(adult_by_province).mark_bar().encode(
    x=alt.X("group_18_and_up:Q", title="Adult Population"),
    y=alt.Y("province_name:N", title="Province"),
    tooltip=["province_name", "group_18_and_up"],
    color=alt.Color("province_name:N", legend=None)
).properties(
    width=700,
    height=400
)
st.altair_chart(adult_province_bar)

# Adult Population by Province (Stacked Bar Chart by Gender)
st.subheader("Adult Population by Province (Stacked by Gender)")

# Group data by province and gender for adult population
adult_by_province_gender = filtered_data.groupby(["province_name", "gender"])["group_18_and_up"].sum().reset_index()

adult_province_gender_bar = alt.Chart(adult_by_province_gender).mark_bar().encode(
    x=alt.X("group_18_and_up:Q", title="Adult Population"),
    y=alt.Y("province_name:N", title="Province"),
    color=alt.Color("gender:N", title="Gender"),
    tooltip=["province_name", "gender", "group_18_and_up"]
).properties(
    width=700,
    height=400
)
st.altair_chart(adult_province_gender_bar)
