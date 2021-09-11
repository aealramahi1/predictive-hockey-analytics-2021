import pandas as pd
import numpy as np


def extract_rows_and_cols(filepath, columns, season_year):
    """
    Extract the relevant data from the CSV file.

    :param filepath: The path that contains the hockey data.
    :param columns: The column names that should be included.
    :param season_year: The season to be included.
    :return: A dataframe containing only the relevant rows and columns.
    """
    df = pd.read_csv(filepath_or_buffer=filepath, delimiter=',', header=0, usecols=columns)
    return df[np.logical_and(np.logical_and(df.situation == 'all', df.season == season_year), df.iceTime == 3600)]


def shots_on_goal(filepath, season_year):
    """
    Calculate and print n and p values for hypothesis test regarding shots on goal.

    :param filepath: The path that contains the hockey data.
    :param season_year:The season to be analyzed.
    """
    df = extract_rows_and_cols(filepath,
                               ['season', 'situation', 'iceTime', 'shotsOnGoalFor', 'goalsFor', 'shotsOnGoalAgainst',
                                'goalsAgainst'], season_year)

    # Check if team with more goals has more shots
    df['Result'] = 0
    df.loc[np.logical_or(np.logical_and(df.goalsFor > df.goalsAgainst, df.shotsOnGoalFor > df.shotsOnGoalAgainst),
                         np.logical_and(df.goalsAgainst > df.goalsFor,
                                        df.shotsOnGoalAgainst > df.shotsOnGoalFor)), 'Result'] = 1

    n = df.shape[0]
    p = float(df['Result'].sum()) / n

    print('Wins with more shots on goal: ' + str(df['Result'].sum()))
    print('n value: ' + str(n))
    print('p value: ' + str(p))


def main():
    """
    Asks user for data to analyze about hockey games.
    """

    filepath = input('Please enter filepath to all_teams.csv from MoneyPuck (relative or absolute): ')
    season = int(
        input('Please enter the beginning year of the season you want to analyze (currently only 2008 - 2017): '))
    print('Shots on goal n and p values: ')
    shots_on_goal(filepath, season)


main()
input("Press enter to exit.")
