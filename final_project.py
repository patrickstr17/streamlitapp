"""
This streamlit application allows users to analyse and visualise video
game sales data.
Users can explore different video games organized by publisher,
explore game publications over the decades, and get video games summaries. 
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import requests

IGDB_CLIENT_ID = "r1djeudx1sd4tmw2354bs302ooear6"
IGDB_CLIENT_SECRET = "8bg867mcoccd4k0jroks4lgf0fvl6b"


@st.cache_data
def get_igdb_access_token():
    """
    Get an access token for the IGDB API.
    """
    auth_url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id":IGDB_CLIENT_ID,
        "client_secret":IGDB_CLIENT_SECRET,
        "grant_type": "client_credentials"
    }

    response = requests.post(auth_url, params=params, timeout=5)
    data = response.json()
    return data.get("access_token")


@st.cache_data
def search_game_summary(game_name, access_token):
    """
    Search for and display a game's summary using the IGDB API.
    """

    igdb_games_url = "https://api.igdb.com/v4/games"

    headers = {
        "Client-ID": IGDB_CLIENT_ID,
        "Authorization": f"Bearer {access_token}"
    }

    query = f'fields name,summary; search "{game_name}"; limit 1;'
    response = requests.post(igdb_games_url, headers=headers, data=query,timeout=5)
    data = response.json()

    if data and len(data) > 0:
        game_name = data[0].get("name")
        game_summary = data[0].get("summary")
        st.write(f"Game Name: {game_name}")
        st.write(f"Game Summary: {game_summary}")
    else:
        st.write("Game not found.")
        return


@st.cache_data
def read_file():
    """
    Read the video game sales data from a CSV file.
    """
    data = pd.read_csv('vgsales.csv', index_col=0)
    return data


@st.cache_data
def get_publisher(dataframe):
    """
    Get the top 20 video game publishers from the dataset.
    """
    dataframe['Publisher'].astype(str)
    return sorted(dataframe['Publisher'].unique().tolist()[:20])


def vg_publishers(dataframe):
    """
    Display the top 20 video game sales per publisher.
    """
    st.header('Top 20 Video Game Sales per Publisher')
    publisher_list = ['All'] + get_publisher(dataframe)
    selected_publisher = st.selectbox('Select Publisher', publisher_list)

    if selected_publisher == 'All':
        st.write('You want to see all data')
        sorted_data = dataframe.sort_values(by='Global_Sales', ascending=False)
        top_20 = sorted_data.head(20)
        st.write(top_20)
    else:
        st.write(f'You selected {selected_publisher}')
        vg_publisher = dataframe[dataframe['Publisher'] == selected_publisher]
        sorted_publisher_data = vg_publisher.sort_values(
            by='Global_Sales', ascending=False)
        top_20_publisher = sorted_publisher_data.head(20)
        st.write(top_20_publisher)


@st.cache_data
def compute_nb_games(dataframe):
    """
    Compute the number of games per decade.
    """
    return dataframe.groupby('Decade').count()['Name'].reset_index(name='nb_games')


def publication_year(dataframe):
    """
    Display the evolution of publications over time.
    """
    publisher_list = ['All'] + get_publisher(dataframe)
    selected_publisher = st.selectbox('Select Publisher', publisher_list)
    dataframe['Decade'] = dataframe['Year'] // 10 * 10

    if selected_publisher == 'All':
        st.write('Please select a specific publisher from the dropdown.')
        vg_publisher = dataframe
    else:
        vg_publisher = dataframe[dataframe['Publisher'] == selected_publisher]

    games_per_decade = compute_nb_games(vg_publisher)
    create_chart(games_per_decade)


@st.cache_data
def create_chart(dataframe):

    """
    Create bar chart of the evolution of publications over time.
    """
    fig = px.bar(dataframe,
                 x='Decade',
                 y='nb_games',
                 title='Number of games published',
                 text_auto=True)

    fig.update_layout(
        xaxis={'tickmode': 'linear', 'dtick': 10})
    st.plotly_chart(fig)
    st.write(dataframe)


def main():
    """
    Main function of streamlit app
    """
    # Opening csv file
    vg_data = read_file()
    st.title("Video Game Analysis")

    # Create side bar
    with st.sidebar:
        st.header('Menu')
        menu_selected = st.selectbox('Choose a menu',
                                     ['Publisher Details',
                                      'Evolution of Publications',
                                      'Game summary'])
    # Menu 1
    if menu_selected == 'Publisher Details':
        vg_publishers(vg_data)
    # Menu 2
    elif menu_selected == 'Evolution of Publications':
        st.title('Games Published per Publisher')
        publication_year(vg_data)
    # Menu 3
    else:
        st.header('Video Game Summary')
        game_name = st.text_input(
            "Enter the name of the game (ex: Pokemon Pearl):")
        if game_name:
            access_token = get_igdb_access_token()
            search_game_summary(game_name, access_token)
        else:
            st.write("Please enter a game name.")


if __name__ == '__main__':
    main()
