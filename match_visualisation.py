# Data Handling & Analysis
import datetime

import numpy as np
import pandas as pd

# Data Visualisation
import matplotlib.pyplot as plt
import matplotlib.image as image

from matplotlib.patches import Arc
from matplotlib.offsetbox import AnnotationBbox, OffsetImage

# Web Scraping
import json
import requests

from bs4 import BeautifulSoup

# Custom functions for extracting match info
import match_scraper

# Custom function for drawing a football pitch
from draw_football_pitch import draw_pitch


def create_figure(match_id, fig, ax):
    """Add the figure to the given axes object."""
    soup_object, data_dict = match_scraper.scrape_script_data(match_id)

    df_summary = match_scraper.extract_summary_stats(soup_object)

    date = match_scraper.extract_date(data_dict)
    headline = match_scraper.extract_headline(df_summary)

    home_team, away_team = match_scraper.extract_team_names(df_summary)
    crest_home, crest_away = match_scraper.get_crest_img(df_summary)

    df_home = pd.DataFrame(data_dict['h'])
    df_away = pd.DataFrame(data_dict['a'])

    # Convert numeric columns to floats
    float_cols = ['X', 'Y', 'xG']
    for df in [df_home, df_away]:
        df[float_cols] = df[float_cols].astype('float64')

    # Isolate goals and shot data for both teams
    goals_home = df_home[df_home['result'] == 'Goal']
    shots_home = df_home[df_home['result'] != 'Goal']

    goals_away = df_away[df_away['result'] == 'Goal']
    shots_away = df_away[df_away['result'] != 'Goal']

    bg_color = '#0f253a'
    goal_color = 'red'
    edgecolor = 'white'
    plt.rcParams['text.color'] = 'white'

    plt.rcParams['font.family'] = 'Century Gothic'
    plt.rcParams.update({'font.size': 24})

    fig.patch.set_facecolor(bg_color)
    draw_pitch(pitch_color=bg_color, line_color='lightgrey', ax=ax)

    ### 01 - Shots and Goals ###
    for i, df in enumerate([shots_home, goals_home]):
        ax.scatter(x=105 - df['X'] * 105,
                   y=68 - df['Y'] * 68,
                   s=df['xG'] * 1024,
                   lw=[2, 1][i],
                   alpha=0.7,
                   facecolor=['none', goal_color][i],
                   edgecolor=edgecolor)

    for i, df in enumerate([shots_away, goals_away]):
        ax.scatter(x=df['X'] * 105,
                   y=df['Y'] * 68,
                   s=df['xG'] * 1024,
                   lw=[2, 1][i],
                   alpha=0.7,
                   facecolor=['none', goal_color][i],
                   edgecolor=edgecolor)

    ### 02 - Title & Subtitle ###
    ax.text(x=0, y=75, s=headline, size=35, weight='bold')
    ax.text(x=0, y=71, s='Premier League 2021-22  |  {}'.format(date), size=20)

    ### 03 - Team Names ###
    for i, team in zip([-1, 1], [home_team, away_team]):
        ax.text(x=105 / 2 + i * 14,
                y=63,
                s=team,
                size=35,
                ha='center',
                weight='bold')

    ### 04 - Team Logos ###
    for i, img in zip([-1, 1], [crest_home, crest_away]):

        imagebox = OffsetImage(img, zoom=0.4)
        ab = AnnotationBbox(imagebox, (105 / 2 + i * 14, 56), frameon=False)
        ax.add_artist(ab)

    ### 05 - Stats ###
    features = ['Goals', 'xG', 'Shots', 'On Target', 'DEEP', 'xPTS']
    for i, feature in enumerate(features):
        if float(df_summary.loc[feature, 'Home']) > float(df_summary.loc[feature, 'Away']):
            weights = ['bold', 'normal']
        elif float(df_summary.loc[feature, 'Home']) < float(df_summary.loc[feature, 'Away']):
            weights = ['normal', 'bold']
        else:
            weights = ['normal', 'normal']

        ax.text(x=105 / 2,
                y=46 - i * 8,
                s=feature,
                size=22,
                ha='center',
                va='center',
                bbox=dict(facecolor='darkgray',
                          edgecolor=edgecolor,
                          alpha=0.85,
                          pad=0.6,
                          boxstyle='round'))

        ax.text(x=105 / 2 - 14,
                y=46 - i * 8,
                s=df_summary.loc[feature, 'Home'],
                size=20,
                ha='center',
                va='center',
                weight=weights[0],
                bbox=dict(facecolor='firebrick',
                          edgecolor='w',
                          alpha=0.6,
                          pad=0.6,
                          boxstyle='round'))

        ax.text(x=105 / 2 + 14,
                y=46 - i * 8,
                s=df_summary.loc[feature, 'Away'],
                size=20,
                ha='center',
                va='center',
                weight=weights[1],
                bbox=dict(facecolor='firebrick',
                          edgecolor='w',
                          alpha=0.6,
                          pad=0.6,
                          boxstyle='round'))

    ### 06 - Legend - Outcome ###
    ax.text(x=105 / 4 + 0, y=-5, s='Outcome:', ha='center')
    ax.text(x=105 / 4 - 8, y=-10, s='Shot', ha='center')
    ax.text(x=105 / 4 + 8, y=-10, s='Goal', ha='center')

    for i in range(2):
        ax.scatter(x=[105 / 4 - 14, 105 / 4 + 1.5][i],
                   y=-8.8,
                   s=500,
                   lw=[2, 1][i],
                   alpha=0.7,
                   facecolor=[bg_color, goal_color][i],
                   edgecolor=edgecolor)

    ### 07 - Legend - xG value ###
    ax.text(x=3 * 105 / 4, y=-5, s='xG Value:', ha='center')

    for i in range(0, 5):
        ax.scatter(x=[69.8, 73.4, 77.7, 82.4, 87.5][i],
                   y=-8.5,
                   s=((i + 1) * 0.2) * 500,
                   lw=2,
                   color=bg_color,
                   edgecolor=edgecolor)

    ### 08 - Legend - Credit ###
    credit_text = 'Data: Understat | Orfanakis Konstantinos'
    ax.text(x=105, y=-14, s=credit_text, size=16, ha='right')
