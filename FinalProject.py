"""

Name: Abdul Eddaif
CS230: Section 6
Data: New England Airports

Description: A web app that analyzes New England Airports and provides a deeper understanding on the many aspects of these airports
and gives a better outlook into them based on the dataset provided.
"""


import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px


# [PY3] Error handling with try/except
@st.cache_data
def load_data():
    try:
        df = pd.read_csv(
            r"C:\Users\eddai\OneDrive - Bentley University\CS230\Class Downloads\Week12\map_file\new_england_airports1.csv")

        # [DA1] Data cleaning with lambda function
        df['state'] = df['iso_region'].str.split('-').str[-1]
        df['scheduled_service'] = df['scheduled_service'].fillna('no')
        df['name'] = df['name'].apply(lambda x: x.strip().title() if pd.notnull(x) else x)

        return df
    except FileNotFoundError:
        st.error("Data file not found!")
        return pd.DataFrame()

# [PY1] Function with default parameters
def filter_data(df, state='All', airport_type='All', min_elevation=0):
    # [DA5] Multiple condition filtering
    if state != 'All':
        df = df[df['state'] == state]
    if airport_type != 'All':
        df = df[df['type'] == airport_type]
    # [DA3] Filter by elevation
    df = df[df['elevation_ft'] >= min_elevation]
    # [DA2] Sort data
    return df.sort_values('elevation_ft', ascending=False)

df = load_data()

# [ST1-ST3] Streamlit widgets
st.sidebar.header("Filters")
selected_state = st.sidebar.selectbox('State', ['All'] + list(df['state'].unique()))  # [ST1]
selected_type = st.sidebar.selectbox('Type', ['All'] + list(df['type'].unique()))  # [ST2]
min_elevation = st.sidebar.slider("Min Elevation (ft)", 0, 2000, 0)  # [ST3]

# Apply filters
filtered_df = filter_data(df,
                          state=selected_state,
                          airport_type=selected_type,
                          min_elevation=min_elevation)

# [ST4] Page design
st.title("✈️ New England Airports Analysis")
st.markdown("---")

# Visualizations in columns
col1, col2 = st.columns(2)

with col1:
    # [CHART1] Bar chart
    st.header("Airports by State")
    state_counts = filtered_df['state'].value_counts()

    # Create figure with integrated axis labels
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(state_counts.index, state_counts.values, color='steelblue')

    # Proper axis labels
    ax.set_xlabel("State", labelpad=10)
    ax.set_ylabel("Number of Airports", labelpad=10)

    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    st.pyplot(fig)
    plt.close()

with col2:
    # [CHART2] Pie Chart with Legend
    st.header("Airport Types")
    type_counts = filtered_df['type'].value_counts()

    # Create figure and calculate percentages
    fig, ax = plt.subplots(figsize=(8, 6))
    total = sum(type_counts)
    percentages = [(count / total) * 100 for count in type_counts]

    # PIE CHART
    wedges = ax.pie(type_counts,
                    colors=plt.cm.Pastel1.colors,
                    startangle=90,
                    wedgeprops={'linewidth': 1, 'edgecolor': 'white'})[0]

    # Create legend with percentages
    legend_labels = [f"{label} ({pct:.1f}%)"
                     for label, pct in zip(type_counts.index, percentages)]
    ax.legend(wedges, legend_labels,
              title="Airport Types",
              loc="center left",
              bbox_to_anchor=(1, 0.5))

    # Adjust layout for legend
    plt.subplots_adjust(right=0.65)
    st.pyplot(fig)
    plt.close()

# [CHART3] Table
st.header("Elevation Statistics")
stats_df = filtered_df.groupby('type')['elevation_ft'].agg(['mean', 'max']).reset_index()
stats_df.columns = ['Type', 'Average Elevation', 'Max Elevation']
st.table(stats_df.round(2))

# [MAP] Interactive map
st.header("Airport Locations")
fig = px.scatter_mapbox(filtered_df,
                        lat="latitude_deg",
                        lon="longitude_deg",
                        hover_name="name",
                        hover_data=['type', 'elevation_ft'],
                        zoom=5)
fig.update_layout(mapbox_style="open-street-map")
st.plotly_chart(fig)

# [DA4] Display filtered results
st.write(f"Showing {len(filtered_df)} airports matching filters")