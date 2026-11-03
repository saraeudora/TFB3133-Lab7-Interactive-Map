
import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np


# ==========================================
# 1. LOAD NATURAL EARTH DATASET
# ==========================================

@st.cache_data
def load_data():

    gdf = gpd.read_file(
        "ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp"
    )

    # Use actual population estimates if available
    if 'pop_est' not in gdf.columns:

        if 'POP_EST' in gdf.columns:
            gdf['pop_est'] = gdf['POP_EST']

        else:
            np.random.seed(0)

            gdf['pop_est'] = np.random.randint(
                1e6, 1e9, size=len(gdf)
            )

    # Calculate country area using an equal-area projection
    gdf_area = gdf.to_crs("ESRI:54009")

    # Calculate population density (people per square metre)
    gdf['pop_density'] = (
        gdf['pop_est'] / gdf_area.geometry.area
    )

    return gdf


gdf = load_data()


# ==========================================
# 2. STREAMLIT SETUP
# ==========================================

st.set_page_config(
    page_title="Interactive Map Visualization",
    layout="wide"
)

st.title("Interactive Map Visualization Examples")

st.sidebar.header("Choose a Map Type")

map_type = st.sidebar.radio(
    "Select Map Type",
    [
        "Map Cosmetics",
        "Map Visual Hierarchy",
        "Choropleth Map",
        "Geo Projection"
    ]
)


# ==========================================
# 3. MAP COSMETICS
# ==========================================

if map_type == "Map Cosmetics":

    st.subheader("Map Cosmetics")

    st.write(
        "This example demonstrates basic map customization "
        "using different colors and background styles."
    )

    fig, ax = plt.subplots(figsize=(10, 6))

    gdf.plot(
        ax=ax,
        color='skyblue',
        edgecolor='black',
        linewidth=0.5
    )

    ax.set_title(
        "Styled Map Example",
        fontsize=15,
        fontweight="bold"
    )

    ax.set_facecolor("lightgrey")
    ax.set_axis_off()

    st.pyplot(fig)

    plt.close(fig)


# ==========================================
# 4. MAP VISUAL HIERARCHY
# ==========================================

elif map_type == "Map Visual Hierarchy":

    st.subheader("Map Visual Hierarchy")

    st.write(
        "Select countries below to highlight them in red. "
        "Other countries will remain sky blue."
    )

    # Identify country name column
    country_col = (
        'NAME' if 'NAME' in gdf.columns
        else 'name' if 'name' in gdf.columns
        else 'ADMIN'
    )

    highlighted_countries = st.multiselect(
        "Select countries to highlight in red",

        sorted(gdf[country_col].dropna().unique()),

        default=[
            "Brazil",
            "India",
            "China",
            "Australia",
            "South Africa",
            "Russia"
        ]
    )

    # Assign colors based on selection
    gdf['color'] = gdf[country_col].apply(
        lambda x: 'red'
        if x in highlighted_countries
        else 'skyblue'
    )

    fig, ax = plt.subplots(figsize=(10, 6))

    gdf.plot(
        color=gdf['color'],
        edgecolor='black',
        linewidth=0.5,
        ax=ax
    )

    ax.set_title(
        "Map Visual Hierarchy with Selected Countries Highlighted in Red"
    )

    ax.set_axis_off()

    st.pyplot(fig)

    plt.close(fig)


# ==========================================
# 5. CHOROPLETH MAP
# ==========================================

elif map_type == "Choropleth Map":

    st.subheader("Choropleth Map")

    st.write(
        "This map displays population density using "
        "different color intensities."
    )

    color_choice = st.selectbox(
        "Choose Color Scheme",
        ['OrRd', 'YlGn', 'Blues', 'Purples', 'Greens'],
        index=0
    )

    use_log_scale = st.checkbox(
        "Use Log Transformation",
        value=True
    )

    # Use the population density calculated in equal-area coordinates
    gdf_plot = gdf.copy()

    if use_log_scale:

        gdf_plot['display_density'] = np.log1p(
            gdf_plot['pop_density']
        )

    else:

        gdf_plot['display_density'] = (
            gdf_plot['pop_density']
        )

    fig, ax = plt.subplots(figsize=(10, 6))

    gdf_plot.plot(
        column='display_density',
        cmap=color_choice,
        edgecolor='black',
        legend=True,
        ax=ax
    )

    ax.set_title(
        f"Population Density by Country (Color Scheme: {color_choice})"
    )

    ax.set_axis_off()

    st.pyplot(fig)

    plt.close(fig)


# ==========================================
# 6. GEO PROJECTION
# ==========================================

elif map_type == "Geo Projection":

    st.subheader("Geo Projection")

    st.write(
        "Explore different geographical projections "
        "and color schemes to see how they affect "
        "the appearance of the world map."
    )

    # Available geographical projections
    projection_options = {

        "Mercator": "EPSG:3395",

        "Robinson": "+proj=robin +datum=WGS84 +units=m +no_defs",

        "Mollweide": "+proj=moll +datum=WGS84 +units=m +no_defs",

        "Equal Earth": "+proj=eqearth +datum=WGS84 +units=m +no_defs"

    }

    proj_choice = st.selectbox(
        "Select a Projection",
        list(projection_options.keys())
    )

    color_choice = st.selectbox(
        "Choose Color Scheme",
        ['OrRd', 'YlGn', 'Blues', 'Purples', 'Greens'],
        index=0
    )

    use_log_scale = st.checkbox(
        "Use Log Transformation for Population Density",
        value=True
    )

    # Apply log transformation if selected
    gdf_plot = gdf.copy()

    if use_log_scale:

        gdf_plot['display_density'] = np.log1p(
            gdf_plot['pop_density']
        )

    else:

        gdf_plot['display_density'] = (
            gdf_plot['pop_density']
        )

    # Transform the geographical projection
    gdf_proj = gdf_plot.to_crs(
        projection_options[proj_choice]
    )

    fig, ax = plt.subplots(figsize=(10, 6))

    gdf_proj.plot(
        column='display_density',
        cmap=color_choice,
        edgecolor='black',
        legend=True,
        ax=ax
    )

    ax.set_title(
        f"Map in {proj_choice} Projection"
    )

    ax.set_axis_off()

    st.pyplot(fig)

    plt.close(fig)
