
import pandas as pd  # pip install pandas openpyxl
import plotly.graph_objects as go

import streamlit as st  # pip install streamlit

# Include custom favicon using HTML
favicon_path = "https://vrti-graph.adaptcentre.ie/static/images/favicon.png"  # Replace with your favicon path or URL


# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title="Census Dashboard", page_icon=favicon_path, layout="wide")

# ---- READ EXCEL ----
@st.cache_data
def get_data_from_excel():
    df = pd.read_excel(
        io="census_data/Table 1. Dublin.xlsx",
        engine="openpyxl",
        sheet_name="Sheet1",
        # skiprows=3,
        # usecols="B:R",
        nrows=1000,
        index_col=0,
    ).sort_values("Townland")
    # Add 'hour' column to dataframe
    # df['Code'] = df['Code'].astype(str)
    # df = df.drop(columns=['Code'])
    print(df.columns)
    # df["hour"] = pd.to_datetime(df["Time"], format="%H:%M:%S").dt.hour
    return df

df = get_data_from_excel()

# st.markdown("## Overview of Census")
st.title("Historic Census of Ireland (1841-1881)")
st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRk1mFERBLOC8aWDcM4OzkUo8omL5pJyTukPA&s", width=150)
# st.link_button("Homepage", "http://127.0.0.1:5001/census", type="secondary")
st.markdown('''
<a href="https://vrti-graph.adaptcentre.ie/census" class="btn btn-outline-primary" target="">Return Home</a>
<a href="https://vrti-graph.adaptcentre.ie/census-map-explorer?view=townland" class="btn btn-outline-primary ms-2" target="">Census Map Explorer</a>
''',unsafe_allow_html=True)

st.write("#### Select a filter below to search the census")

# st.markdown('<a class="btn btn-secondary text-white" href="http://127.0.0.1:5001/census" target="_self">Return Home</a>',unsafe_allow_html=True)

# html("""
# <script>
#          document.getElementsByTagName("a")[0].target = "";
# </script>
# """)
# st.dataframe(df)

# st.sidebar.header("Select an option to filter census:")
# townland_selected = st.sidebar.selectbox(
#     "Select a Townland in the Census",
#     options=df["Townland"].sort_values().unique(),
#     index=None,
# )
#
#
# number = st.sidebar.number_input("Total Population greater than", value=None, placeholder="Type a number...", step=1)
# st.header("Select an option to filter census:")
townland_selected = st.selectbox(
    "Select a Townland in the Census",
    options=df["Townland"].sort_values().unique(),
    index=None,
)

census_years = [1841, 1851, 1861, 1871, 1881, 1891]

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
        # options= [attribute.replace("Inhabited", "") for attribute in df.columns if
        #  "Inhabited" in attribute],
        # index=None,
    )
with right_column:
    number = st.number_input("Total Population greater than", value=None, placeholder="Type a number...", step=1)

# parish_selected = st.selectbox(
#     "Select a Parish in the Census",
#     options=df["Parish"].sort_values().unique(),
#     index=None,
# )

parish_selected = None

# def validate_df_empty(df):
#     if df.empty:
#         st.warning("No results found")
#         st.stop()

if number and townland_selected:
    # if number and (townland_selected and parish_selected):
    st.warning("Please use only one fiter at a time")
    st.stop()


if number:
    if population_category_selected == "Total":
        population_comparison_query = f"`{population_year_selected} Male` + `{population_year_selected} Female`"
    else:
        population_comparison_query = f"`{population_year_selected} {population_category_selected}`"
    # df_selection = df[df["1841 Male"] > number].sort_values("1841 Male")
    df_selection = df.query(f"""
    ({population_comparison_query}) > @number & Townland != "TOTAL"
    
    """).sort_values("1841 Male")
    # validate_df_empty(df)
    # df_selection = df_selection[df_selection["Townland"] != "Total"]
    st.subheader(f"Census Results for {population_year_selected} {population_category_selected} Population greater than {number}")
    st.write(f"{len(df_selection)} results")
    st.dataframe(df_selection.drop(columns=['Code', "Parish"]))

    # st.dataframe(df_selection)

    # st.write("The current number is ", number)
# def plot_df_selection(df_selection):


def plot_census_year(selected_year, delta=None):
    st.write('')
    st.write(f"##### {selected_year} Statistics")
    print(delta)
    try:
        left_column, middle_column, right_column = st.columns(3)
        total_1881_population = int(df_selection[f"{selected_year} Female"].sum()) + int(df_selection[f"{selected_year} Male"].sum())
        if delta:
            left_column.metric(label=f"Total {selected_year} in {townland_selected_str}:", value=total_1881_population, delta=total_1881_population-delta)
        else:
            left_column.metric(label=f"Total {selected_year} in {townland_selected_str}:", value=total_1881_population)

        middle_column.metric(label=f"Female {selected_year} in {townland_selected_str}:",
                             value=int(df_selection[f"{selected_year} Female"].sum()))
        right_column.metric(label=f"Males {selected_year} in {townland_selected_str}:",
                            value=int(df_selection[f"{selected_year} Male"].sum()))
        return total_1881_population
    except:
        st.warning("Null values")




if townland_selected or parish_selected:
    if parish_selected:
        townland_selected_str = parish_selected.title()
    else:
        townland_selected_str = townland_selected.title()
    #
    # st.subheader(f"Census Results for {townland_selected_str}")
    st.markdown('')

    # st.link_button("Knowledge Graph Link", "https://streamlit.io/gallery")
    st.markdown('<a href="http://127.0.0.1:5001/census" target="_blank">Knowledge Graph Link</a>',unsafe_allow_html=True)


    if parish_selected:
        query = "Parish == @parish_selected & Townland == 'TOTAL'"
    else:
        query = "Townland == @townland_selected"
    df_selection = df.query(query).fillna("null").head(1)


    # df_selection = df.query(
    #     "Townland == @townland_selected"
    # ).fillna("null").head(1)

    st.dataframe(df_selection.drop(columns=['Code', "Parish"]))


    # total_sales = int(df_selection["1881 Male"].sum())
    # average_rating = round(df_selection["Rating"].mean(), 1)
    # star_rating = ":star:" * int(round(average_rating, 0))
    # average_sale_by_transaction = round(df_selection["Total"].mean(), 2)
    #
    # left_column, right_column = st.columns(2)
    # st.write('')
    # st.write("##### 1841 Statistics")
    # left_column, middle_column, right_column = st.columns(3)
    # total_1841_population = int(df_selection["1841 Female"].sum()) + int(df_selection["1841 Male"].sum())
    #
    # left_column.metric(label=f"Total 1841 in {townland_selected_str}:", value=total_1841_population)
    # middle_column.metric(label=f"Female 1841 in {townland_selected_str}:", value=int(df_selection["1841 Female"].sum()))
    # right_column.metric(label=f"Males 1841 in {townland_selected_str}:", value=int(df_selection["1841 Male"].sum()))
    #
    total_1841_population = plot_census_year("1841")
    # plot_census_year("1851")
    total_1881_population = plot_census_year("1881", delta=total_1841_population)

    # try:
    #     st.write("##### 1881 Statistics")
    #     left_column, middle_column, right_column = st.columns(3)
    #     total_1881_population = int(df_selection["1881 Female"].sum()) + int(df_selection["1881 Male"].sum())
    #
    #     left_column.metric(label=f"Total 1881 in {townland_selected_str}:", value=total_1881_population, delta=total_1881_population-total_1841_population)
    #     middle_column.metric(label=f"Female 1881 in {townland_selected_str}:", value=int(df_selection["1881 Female"].sum()))
    #     right_column.metric(label=f"Males 1881 in {townland_selected_str}:", value=int(df_selection["1881 Male"].sum()))
    # except:
    #     st.warning("Null values")

    # with left_column:
    #     st.markdown(f"Males 1881 in {townland_selected_str}: {int(df_selection["1881 Male"].sum())}")
    # with middle_column:
    #     st.markdown(f"Female 1881 in {townland_selected_str}: {int(df_selection["1881 Female"].sum())}")
    # with right_column:
    #     st.markdown(f"Total 1881: {total_1881_population}")
    st.write('')
    st.write("##### Population and Habitation (1841-1891)")
    # st.write(total_1881_population)
    df_selection_dict = df_selection.iloc[0].to_dict()
    # print(df_selection_dict)
    male_population = [count for attribute, count in df_selection_dict.items() if "Male" in attribute and count != "null"]
    female_population = [count for attribute, count in df_selection_dict.items() if "Female" in attribute  and count != "null"]
    x = [attribute.replace("Inhabited", "Population") for attribute, count in df_selection_dict.items() if
         "Inhabited" in attribute]
    # print(x)
    # print(male_population)
    total_population_fig = go.Figure(data=[go.Bar(
        name='Male',
        x=x,
        y=male_population,
    ),
        go.Bar(
            name='Female',
            x=x,
            y=female_population,
        )
    ],
        # template="plotly_white",
        # title=f'Population and Habitation (1841-1891)',

    )
    left_column, right_column = st.columns(2)
    left_column.plotly_chart(total_population_fig, use_container_width=True)
    inhabited = [count for attribute, count in df_selection_dict.items() if "Inhabited" in attribute]
    uninhabited = [None, None, None, None, 1, None]


    # Create traces for the plot
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=census_years, y=inhabited, mode='lines+markers', name='Inhabited Houses',
                             line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=census_years, y=uninhabited, mode='lines+markers', name='Uninhabited Houses',
                             line=dict(color='grey', dash='dash')))
    fig.add_trace(go.Scatter(x=census_years, y=male_population, mode='lines+markers', name='Male Population',
                             line=dict(color='green')))
    fig.add_trace(go.Scatter(x=census_years, y=female_population, mode='lines+markers', name='Female Population',
                             line=dict(color='red')))
    fig.update_layout(
        # title=f'Population and Habitation (1841-1891)',
        xaxis_title='Year',
        yaxis_title='Count',
        legend_title='Legend',
        template='plotly_white'
    )

    right_column.plotly_chart(fig, use_container_width=True)
    place_id = df_selection.iloc[0]["Code"]
    print(place_id)
    if place_id != "null":
        modern_place_df = pd.read_excel("census_data/Table 2. Modern_Place_Data_Stack.xlsx").fillna("-1")
        dublin_places_df = modern_place_df.loc[modern_place_df['OS_ID'] == int(place_id)].iloc[0]
        lat = dublin_places_df["CENTRE_LAT"]
        lng = dublin_places_df["CENTRE_LNG"]
        print(lat)
        data = pd.DataFrame({
            'lat': [lat],
            'lon': [lng]
        })

        st.write(f"##### Map of {townland_selected_str}")
        st.map(data)

    # st.subheader(total_sales)
    # with middle_column:
    #     st.subheader("Average Rating:")
    #     st.subheader(f"{average_rating} {star_rating}")
    # with right_column:
    #     st.subheader("Average Sales Per Transaction:")
    #     st.subheader(f"US $ {average_sale_by_transaction}")
    #
    # st.markdown("""---""")


hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .viewerBadge_container__r5tak {display: none;}
            a {background-color: #ffffff;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
st.markdown(f'    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">', unsafe_allow_html=True)
hide_streamlit_style = """
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script>
    $(document).ready(function() {
        $(".viewerBadge_container__r5tak").remove();
    });
    </script>
"""

st.markdown(hide_streamlit_style, unsafe_allow_html=True)