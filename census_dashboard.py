import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Set page configuration and favicon
favicon_path = "https://vrti-graph.adaptcentre.ie/static/images/favicon.png"
st.set_page_config(page_title="Census Dashboard", page_icon=favicon_path, layout="wide")

# Load Excel data with caching to enhance performance
@st.cache_data
def get_data_from_excel():
    df = pd.read_excel(
        io="census_data/Table 1. Dublin.xlsx",
        engine="openpyxl",
        sheet_name="Sheet1",
        nrows=1000,
        index_col=0,
    ).sort_values("Townland")
    return df

df = get_data_from_excel()

# Display main interface elements
st.title("Historic Census of Ireland (1841-1881) Database")
st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRk1mFERBLOC8aWDcM4OzkUo8omL5pJyTukPA&s", width=150)
st.markdown('''
<a href="https://vrti-graph.adaptcentre.ie/census" class="btn btn-outline-primary" target="">Return Home</a>
<a href="https://vrti-graph.adaptcentre.ie/census-map-explorer?view=townland" class="btn btn-outline-primary ms-2" target="">Census Map Explorer</a>
''', unsafe_allow_html=True)
st.write("#### Select a filter below to search the census")

townland_selected = st.selectbox(
    "Select a Townland in the Census",
    options=df["Townland"].sort_values().unique(),
    index=None,
)

census_years = [1841, 1851, 1861, 1871, 1881, 1891]

# Create filter selection columns
left_column, middle_column, right_column = st.columns([1, 1, 3])
with left_column:
    population_year_selected = st.selectbox(
        "Select a year to compare population",
        options=census_years,
    )
with middle_column:
    population_category_selected = st.selectbox(
        "Select a category to compare population",
        options=["Total", "Male", "Female"],
    )
with right_column:
    number = st.number_input("Total Population greater than", value=None, placeholder="Type a number...", step=1)

parish_selected = None

# Handle filter validation and warnings
if number and townland_selected:
    st.warning("Please use only one filter at a time")
    st.stop()

# Query and display filtered results based on population
if number:
    if population_category_selected == "Total":
        population_comparison_query = f"`{population_year_selected} Male` + `{population_year_selected} Female`"
    else:
        population_comparison_query = f"`{population_year_selected} {population_category_selected}`"
    df_selection = df.query(f"""
    ({population_comparison_query}) > @number & Townland != "TOTAL"
    """).sort_values("1841 Male")
    st.subheader(f"Census Results for {population_year_selected} {population_category_selected} Population greater than {number}")
    st.write(f"{len(df_selection)} results")
    st.dataframe(df_selection.drop(columns=['Code', "Parish"]))

# Plot population metrics for selected year
def plot_census_year(selected_year, delta=None):
    st.write(f"##### {selected_year} Statistics")
    try:
        left_column, middle_column, right_column = st.columns(3)
        total_population = int(df_selection[f"{selected_year} Female"].sum()) + int(df_selection[f"{selected_year} Male"].sum())
        if delta:
            left_column.metric(label=f"Total {selected_year} in {townland_selected_str}:", value=total_population, delta=total_population - delta)
        else:
            left_column.metric(label=f"Total {selected_year} in {townland_selected_str}:", value=total_population)
        middle_column.metric(label=f"Female {selected_year} in {townland_selected_str}:", value=int(df_selection[f"{selected_year} Female"].sum()))
        right_column.metric(label=f"Males {selected_year} in {townland_selected_str}:", value=int(df_selection[f"{selected_year} Male"].sum()))
        return total_population
    except:
        st.warning("Null values")

# Function to create a bar chart for population data
def create_population_bar_chart(df_selection_dict):
    male_population = [count for attribute, count in df_selection_dict.items() if "Male" in attribute and count != "null"]
    female_population = [count for attribute, count in df_selection_dict.items() if "Female" in attribute and count != "null"]
    x = [attribute.replace("Inhabited", "Population") for attribute, count in df_selection_dict.items() if "Inhabited" in attribute]
    fig = go.Figure(data=[
        go.Bar(name='Male', x=x, y=male_population),
        go.Bar(name='Female', x=x, y=female_population)
    ])
    return fig

# Function to create a line chart for population and habitation trends
def create_population_line_chart(df_selection_dict):
    census_years = [1841, 1851, 1861, 1871, 1881, 1891]
    inhabited = [count for attribute, count in df_selection_dict.items() if "Inhabited" in attribute]
    uninhabited = [None, None, None, None, 1, None]
    male_population = [count for attribute, count in df_selection_dict.items() if "Male" in attribute and count != "null"]
    female_population = [count for attribute, count in df_selection_dict.items() if "Female" in attribute and count != "null"]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=census_years, y=inhabited, mode='lines+markers', name='Inhabited Houses', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=census_years, y=uninhabited, mode='lines+markers', name='Uninhabited Houses', line=dict(color='grey', dash='dash')))
    fig.add_trace(go.Scatter(x=census_years, y=male_population, mode='lines+markers', name='Male Population', line=dict(color='green')))
    fig.add_trace(go.Scatter(x=census_years, y=female_population, mode='lines+markers', name='Female Population', line=dict(color='red')))
    fig.update_layout(xaxis_title='Year', yaxis_title='Count', legend_title='Legend', template='plotly_white')
    return fig

# Function to create and display the map based on selected townland
def create_map(df_selection, townland_selected_str):
    place_id = df_selection.iloc[0]["Code"]
    if place_id != "null":
        modern_place_df = pd.read_excel("census_data/Table 2. Modern_Place_Data_Stack.xlsx").fillna("-1")
        dublin_places_df = modern_place_df.loc[modern_place_df['OS_ID'] == int(place_id)].iloc[0]
        lat = dublin_places_df["CENTRE_LAT"]
        lng = dublin_places_df["CENTRE_LNG"]
        data = pd.DataFrame({'lat': [lat], 'lon': [lng]})
        st.write(f"##### Map of {townland_selected_str}")
        st.map(data)

# Display selected townland data and plot statistics
if townland_selected or parish_selected:
    townland_selected_str = parish_selected.title() if parish_selected else townland_selected.title()
    st.markdown('')
    st.markdown('<a href="http://127.0.0.1:5001/census" target="_blank">Knowledge Graph Link</a>', unsafe_allow_html=True)
    query = "Parish == @parish_selected & Townland == 'TOTAL'" if parish_selected else "Townland == @townland_selected"
    df_selection = df.query(query).fillna("null").head(1)
    st.dataframe(df_selection.drop(columns=['Code', "Parish"]))
    total_1841_population = plot_census_year("1841")
    total_1881_population = plot_census_year("1881", delta=total_1841_population)

    st.write("##### Population and Habitation (1841-1891)")
    df_selection_dict = df_selection.iloc[0].to_dict()

    # Display bar and line charts
    bar_chart = create_population_bar_chart(df_selection_dict)
    left_column, right_column = st.columns(2)
    left_column.plotly_chart(bar_chart, use_container_width=True)

    line_chart = create_population_line_chart(df_selection_dict)
    right_column.plotly_chart(line_chart, use_container_width=True)

    # Display the map of the selected townland
    create_map(df_selection, townland_selected_str)

# Hide default Streamlit elements
hide_st_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.viewerBadge_container__r5tak styles_viewerBadge__CvC9N {display: none;}
a {background-color: #ffffff;}
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)
st.markdown(f'<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">', unsafe_allow_html=True)
hide_streamlit_style = """
<script>
$(document).ready(function() {
    $(".viewerBadge_container__r5tak").remove();
});
</script>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
