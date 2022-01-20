# Data Handling & Analysis
import datetime

import numpy as np
import pandas as pd

# Data Visualisation
import matplotlib.pyplot as plt
import matplotlib.image as image

# Web Scraping
import json
import requests

from bs4 import BeautifulSoup


def scrape_script_data(match_id):
    """Web scrape the match info and return the Beautiful object and a dictionary for the home and away team's data."""
    url = 'https://understat.com/match/{}'.format(match_id)

    response = requests.get(url)
    soup_object = BeautifulSoup(response.content, 'lxml')

    # Retrieve all data with a <script> tag - Field data are in the second <script> group
    script_data = soup_object.find_all('script')
    field_stats = script_data[1].string

    # Strip unnecessary symbols and get only JSON data
    ind_start = field_stats.index("('") + 2
    ind_end = field_stats.index("')")

    json_data = field_stats[ind_start:ind_end]
    json_data = json_data.encode('utf8').decode('unicode_escape')

    # Convert string to json format
    data_dict = json.loads(json_data)

    return soup_object, data_dict


def extract_date(data_dict):
    """Return the date of the football match (Format: Day - Name of Month - Year)."""
    date = data_dict['h'][0]['date'].split()[0]
    date = datetime.datetime.strptime(date, '%Y-%m-%d').date()

    return date.strftime('%d %B %Y')


def extract_summary_stats(soup_object):
    """Return the game's summary statistics in a separate Pandas DataFrame."""
    table = soup_object.find('div', {'class': 'scheme-block', 'data-scheme': 'stats'})

    cols = [val.text for val in table.find_all('div', {'class': 'progress-title'})]
    vals = [val.text for val in table.find_all('div', {'class': 'progress-value'})]

    summary_dict = {}
    j = 0
    for i in range(len(cols)):
        summary_dict[cols[i]] = vals[j:j + 2]

        increment = 3 if i == 1 else 2
        j += increment

    df_summary = pd.DataFrame(summary_dict, index=['Home', 'Away']).T
    df_summary.drop(['CHANCES'], inplace=True)
    df_summary.index = ['Teams', 'Goals', 'xG',
                        'Shots', 'On Target', 'DEEP', 'PPDA', 'xPTS']

    return df_summary


def extract_headline(df_summary):
    """Return the headline of the figure."""
    headline = '{} {} - {} {}'.format(
        df_summary.loc['Teams', 'Home'],
        df_summary.loc['Goals', 'Home'],
        df_summary.loc['Teams', 'Away'],
        df_summary.loc['Goals', 'Away'])

    return headline


def extract_team_names(df_summary):
    """Return a shortened version of the team names (e.g. 'Manchester United' to 'Man. United').
    Also, pad right & left with spaces so that all short names have the same length (11 characters).
    """
    teams_full = [
        'Manchester City', 'Liverpool', 'Chelsea', 'Arsenal', 'West Ham',
        'Tottenham', 'Manchester United', 'Wolverhampton Wanderers', 'Brighton',
        'Leicester', 'Crystal Palace', 'Brentford', 'Aston Villa', 'Southampton',
        'Everton', 'Leeds', 'Watford', 'Burnley', 'Newcastle United', 'Norwich']

    teams_short = [
        'Man. City', 'Liverpool', 'Chelsea', 'Arsenal', 'West Ham', 'Tottenham',
        'Man. United', 'Wolves', 'Brighton', 'Leicester', 'Cr. Palace',
        'Brentford', 'Aston Villa', 'Southampton', 'Everton', 'Leeds', 'Watford',
        'Burnley', 'Newcastle', 'Norwich']

    # Pad right & left so that all short names have the same length
    teams_short = [f'{string:^11}' for string in teams_short]

    idx = [i for i, v in enumerate(teams_full) if v == df_summary.loc['Teams', 'Home']]
    home_team_short = teams_short[idx[0]]

    idx = [i for i, v in enumerate(teams_full) if v == df_summary.loc['Teams', 'Away']]
    away_team_short = teams_short[idx[0]]

    return home_team_short, away_team_short


def get_crest_img(df_summary):
    """Return the crests for both teams."""
    url_home = 'Crests\{}.png'.format(df_summary.loc['Teams', 'Home'])
    img_home = image.imread(url_home)

    url_away = 'Crests\{}.png'.format(df_summary.loc['Teams', 'Away'])
    img_away = image.imread(url_away)

    return img_home, img_away
