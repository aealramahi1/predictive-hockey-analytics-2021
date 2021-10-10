import pandas as pd
import numpy as np
import os
from colorama import Fore, Style

TOTAL_TESTS = 12


def main():
    """
    Asks user for data to analyze about hockey games.
    """
    filepath = None
    season = -1
    choice = -1

    # Obtain valid filepath from user.
    valid_filepath = False
    while not valid_filepath:
        inputted_file = input('Please enter filepath to all_teams.csv from MoneyPuck (relative or absolute): ')

        # Check for read permission on the file that we are trying to access.
        if os.access(inputted_file, os.R_OK):
            filepath = inputted_file
            valid_filepath = True
        else:
            print(Fore.RED + 'Could not access file. Make sure the path is correct.\n', 'red')
            print(Style.RESET_ALL)

    # Keep getting input from the user until the select exit.
    while choice != TOTAL_TESTS + 1:

        # Have the user select a variable to analyze from the menu.
        print_menu()

        # Make sure the selection made was valid.
        valid_choice = False
        while not valid_choice:
            try:
                choice = int(input('Please make a selection: '))

                # Make sure the choice is in range.
                if choice < 0 or choice > TOTAL_TESTS + 1:
                    choice = -1
                    raise ValueError
                valid_choice = True
            except ValueError:
                print(Fore.RED + 'Please enter a number between 1 and ' + str(TOTAL_TESTS) + '.\n')
                print(Style.RESET_ALL)

        # Use a dictionary definition as a mock switch statement to choose the appropriate function.
        switch = {
            1: lambda: single_col_for_and_against(filepath, season, 'shotsOnGoal'),
            2: lambda: single_col_for_and_against(filepath, season, 'highDangerShots'),
            3: lambda: single_col_for_and_against(filepath, season, 'mediumDangerShots'),
            4: lambda: single_col_for_and_against(filepath, season, 'lowDangerShots'),
            5: lambda: single_col_for_and_against(filepath, season, 'rebounds'),
            6: lambda: high_and_med_danger(filepath, season),
            7: lambda: high_and_low_danger(filepath, season),
            8: lambda: low_danger_and_rebounds_sum(filepath, season),
            9: lambda: rebounds_and_low_danger_shots_ratio(filepath, season),
            10: lambda: medium_and_high_danger_and_rebounds_sum(filepath, season),
            11: lambda: rebounds_and_medium_and_high_danger_shots_ratio(filepath, season),
            12: lambda: time_on_power_play(filepath, season)
        }

        if choice != TOTAL_TESTS + 1:

            # Obtain valid season from the user.
            valid_season = False
            while not valid_season:
                try:
                    season = int(
                        input('Please enter the beginning year of the season you want to analyze (2008 - 2017): '))

                    # Make sure the season is in the right range.
                    if season < 2008 or season > 2017:
                        season = -1
                        raise ValueError
                    valid_season = True

                # Make sure the season is one year.
                except ValueError:
                    print(Fore.RED + 'Please enter a year between 2008 and 2017.\n')
                    print(Style.RESET_ALL)

            f = switch.get(choice)
            f()
        print()


def single_col_for_and_against(filepath, season_year, col_name):
    """
    Calculate and print n and p values for hypothesis test regarding a single variable with "for" and "against" columns
    in all_teams.csv. Checks if a win corresponds to having a higher value in the column than the other team.

    :param filepath: The path that contains the hockey data.
    :param season_year: The season to be analyzed.
    :param col_name: The name of the column to be analyzed
    """

    for_col = col_name + 'For'
    against_col = col_name + 'Against'

    # Extract the relevant data.
    df = extract_data(filepath,
                      ['season', 'situation', 'iceTime', 'shotsOnGoalFor', for_col, against_col, 'goalsAgainst'],
                      season_year)

    # Check if team with more goals has more of the column value.
    df['Result'] = 0
    df.loc[np.logical_or(np.logical_and(df.goalsFor > df.goalsAgainst, getattr(df, for_col) > getattr(df, against_col)),
                         np.logical_and(df.goalsAgainst > df.goalsFor,
                                        getattr(df, against_col) > getattr(df, for_col))), 'Result'] = 1

    # Calculate n (number of rows) and p (sum of the result column divided by n).
    n = df.shape[0]
    p = float(df['Result'].sum()) / n

    # Print results.
    print(Fore.BLUE + '\nn and p values: ')
    print(Style.RESET_ALL)
    print('Number of successes: ' + str(df['Result'].sum()))
    print('n value: ' + str(n / 2))
    print('p value: ' + str(p))


def high_and_med_danger(filepath, season_year):
    """
    Calculate and print n and p values for hypothesis test regarding medium and high danger shots combined.

    :param filepath: The path that contains the hockey data.
    :param season_year: The season to be analyzed.
    """

    # Extract the relevant data.
    df = extract_data(filepath, ['season', 'situation', 'iceTime', 'goalsFor', 'goalsAgainst', 'mediumDangerShotsFor',
                                 'highDangerShotsFor', 'mediumDangerShotsAgainst', 'highDangerShotsAgainst'],
                      season_year)

    # Check if team with more combined medium and high danger shots had more wins.
    df['Result'] = 0
    df.loc[np.logical_or(np.logical_and(df.goalsFor > df.goalsAgainst,
                                        df.highDangerShotsFor + df.mediumDangerShotsFor > df.highDangerShotsAgainst + df.mediumDangerShotsAgainst),
                         np.logical_and(df.goalsAgainst > df.goalsFor,
                                        df.highDangerShotsAgainst + df.mediumDangerShotsAgainst > df.highDangerShotsFor + df.mediumDangerShotsFor)), 'Result'] = 1

    # If high and medium danger shots are equal, check if one team has more high danger shots.
    df.loc[np.logical_or(np.logical_and(df.goalsFor > df.goalsAgainst,
                                        np.logical_and(
                                            df.highDangerShotsFor + df.mediumDangerShotsFor == df.highDangerShotsAgainst + df.mediumDangerShotsAgainst,
                                            df.highDangerShotsFor > df.highDangerShotsAgainst)),
                         np.logical_and(df.goalsAgainst > df.goalsFor,
                                        np.logical_and(
                                            df.highDangerShotsAgainst + df.mediumDangerShotsAgainst == df.highDangerShotsFor + df.mediumDangerShotsFor,
                                            df.highDangerShotsAgainst > df.highDangerShotsFor))), 'Result'] = 1

    # Calculate n (number of rows) and p (sum of the result column divided by n).
    n = df.shape[0]
    p = float(df['Result'].sum()) / n

    # Print results.
    print(Fore.BLUE + '\nHigh and medium danger shots n and p values: ')
    print(Style.RESET_ALL)
    print('Wins with more high and medium danger shots combined: ' + str(df['Result'].sum() / 2))
    print('n value: ' + str(n / 2))
    print('p value: ' + str(p))


def high_and_low_danger(filepath, season_year):
    """
    Calculate and print n and p values for hypothesis test regarding low and high danger shots combined.

    :param filepath: The path that contains the hockey data.
    :param season_year: The season to be analyzed.
    """

    # Extract the relevant data.
    df = extract_data(filepath, ['season', 'situation', 'iceTime', 'goalsFor', 'goalsAgainst', 'lowDangerShotsFor',
                                 'highDangerShotsFor', 'lowDangerShotsAgainst', 'highDangerShotsAgainst'],
                      season_year)

    # Check if team with more combined low and high danger shots had more wins.
    df['Result'] = 0
    df.loc[np.logical_or(np.logical_and(df.goalsFor > df.goalsAgainst,
                                        df.highDangerShotsFor + df.lowDangerShotsFor > df.highDangerShotsAgainst + df.lowDangerShotsAgainst),
                         np.logical_and(df.goalsAgainst > df.goalsFor,
                                        df.highDangerShotsAgainst + df.lowDangerShotsAgainst > df.highDangerShotsFor + df.lowDangerShotsFor)), 'Result'] = 1

    # If high and medium danger shots are equal, check if one team has more high danger shots.
    df.loc[np.logical_or(np.logical_and(df.goalsFor > df.goalsAgainst,
                                        np.logical_and(
                                            df.highDangerShotsFor + df.lowDangerShotsFor == df.highDangerShotsAgainst + df.lowDangerShotsAgainst,
                                            df.highDangerShotsFor > df.highDangerShotsAgainst)),
                         np.logical_and(df.goalsAgainst > df.goalsFor,
                                        np.logical_and(
                                            df.highDangerShotsAgainst + df.lowDangerShotsAgainst == df.highDangerShotsFor + df.lowDangerShotsFor,
                                            df.highDangerShotsAgainst > df.highDangerShotsFor))), 'Result'] = 1

    # Calculate n (number of rows) and p (sum of the result column divided by n).
    n = df.shape[0]
    p = float(df['Result'].sum()) / n

    # Print results.
    print(Fore.BLUE + '\nHigh and low danger shots n and p values: ')
    print(Style.RESET_ALL)
    print('Wins with more high and low danger shots combined: ' + str(df['Result'].sum() / 2))
    print('n value: ' + str(n / 2))
    print('p value: ' + str(p))


def low_danger_and_rebounds_sum(filepath, season_year):
    """
    Calculate and print n and p values for hypothesis test regarding the sum of low danger shots and rebounds for the
    winning team.

    :param filepath: The path that contains the hockey data.
    :param season_year: The season to be analyzed.
    """

    # Extract the relevant data.
    df = extract_data(filepath, ['season', 'situation', 'iceTime', 'goalsFor', 'goalsAgainst', 'lowDangerShotsFor',
                                 'reboundsFor', 'lowDangerShotsAgainst', 'reboundsAgainst'],
                      season_year)

    # Check if team with more combined low danger shots and rebounds had more wins. Equal sums counts as a failure.
    df['Result'] = 0
    df.loc[np.logical_or(np.logical_and(df.goalsFor > df.goalsAgainst,
                                        df.reboundsFor + df.lowDangerShotsFor > df.reboundsAgainst + df.lowDangerShotsAgainst),
                         np.logical_and(df.goalsAgainst > df.goalsFor,
                                        df.reboundsAgainst + df.lowDangerShotsAgainst > df.reboundsFor + df.lowDangerShotsFor)), 'Result'] = 1

    # Calculate n (number of rows) and p (sum of the result column divided by n).
    n = df.shape[0]
    p = float(df['Result'].sum()) / n

    # Print results.
    print(Fore.BLUE + '\nLow danger shots and rebounds (sum) n and p values: ')
    print(Style.RESET_ALL)
    print('Wins with more low danger shots and rebounds combined: ' + str(df['Result'].sum() / 2))
    print('n value: ' + str(n / 2))
    print('p value: ' + str(p))


def rebounds_and_low_danger_shots_ratio(filepath, season_year):
    """
    Calculate and print n and p values for hypothesis test regarding the ratio of rebounds to low danger shots for the
    winning team.

    :param filepath: The path that contains the hockey data.
    :param season_year: The season to be analyzed.
    """

    # Extract the relevant data.
    df = extract_data(filepath, ['season', 'situation', 'iceTime', 'goalsFor', 'goalsAgainst', 'lowDangerShotsFor',
                                 'reboundsFor', 'lowDangerShotsAgainst', 'reboundsAgainst'],
                      season_year)

    # Check if team with a higher ratio of rebounds to low danger shots had more wins. Equal ratios count as a failure.
    df['Result'] = 0
    df.loc[np.logical_or(np.logical_and(df.goalsFor > df.goalsAgainst,
                                        df.reboundsFor / df.lowDangerShotsFor > df.reboundsAgainst / df.lowDangerShotsAgainst),
                         np.logical_and(df.goalsAgainst > df.goalsFor,
                                        df.reboundsAgainst / df.lowDangerShotsAgainst > df.reboundsFor / df.lowDangerShotsFor)), 'Result'] = 1

    # Calculate n (number of rows) and p (sum of the result column divided by n).
    n = df.shape[0]
    p = float(df['Result'].sum()) / n

    # Print results.
    print(Fore.BLUE + '\nRebounds and low danger shots (ratio) n and p values: ')
    print(Style.RESET_ALL)
    print('Wins with a higher ratio of rebounds to low danger shots: ' + str(df['Result'].sum() / 2))
    print('n value: ' + str(n / 2))
    print('p value: ' + str(p))


def medium_and_high_danger_and_rebounds_sum(filepath, season_year):
    """
    Calculate and print n and p values for hypothesis test regarding the sum of medium/high danger shots and rebounds for the
    winning team.

    :param filepath: The path that contains the hockey data.
    :param season_year: The season to be analyzed.
    """

    # Extract the relevant data.
    df = extract_data(filepath, ['season', 'situation', 'iceTime', 'goalsFor', 'goalsAgainst', 'mediumDangerShotsFor',
                                 'highDangerShotsFor', 'reboundsFor', 'mediumDangerShotsAgainst',
                                 'highDangerShotsAgainst', 'reboundsAgainst'], season_year)

    # Check if team with more combined med/high danger shots and rebounds had more wins. Equal sums counts as a failure.
    df['Result'] = 0
    df.loc[np.logical_or(np.logical_and(df.goalsFor > df.goalsAgainst,
                                        df.reboundsFor + df.mediumDangerShotsFor + df.highDangerShotsFor > df.reboundsAgainst + df.mediumDangerShotsAgainst + df.highDangerShotsAgainst),
                         np.logical_and(df.goalsAgainst > df.goalsFor,
                                        df.reboundsAgainst + df.mediumDangerShotsAgainst + df.highDangerShotsAgainst > df.reboundsFor + df.mediumDangerShotsFor + df.highDangerShotsFor)), 'Result'] = 1

    # Calculate n (number of rows) and p (sum of the result column divided by n).
    n = df.shape[0]
    p = float(df['Result'].sum()) / n

    # Print results.
    print(Fore.BLUE + '\nMedium and high danger shots and rebounds (sum) n and p values: ')
    print(Style.RESET_ALL)
    print('Wins with more medium and high danger shots and rebounds combined: ' + str(df['Result'].sum() / 2))
    print('n value: ' + str(n / 2))
    print('p value: ' + str(p))


def rebounds_and_medium_and_high_danger_shots_ratio(filepath, season_year):
    """
    Calculate and print n and p values for hypothesis test regarding the ratio of rebounds to medium and high danger shots for the
    winning team.

    :param filepath: The path that contains the hockey data.
    :param season_year: The season to be analyzed.
    """

    # Extract the relevant data.
    df = extract_data(filepath, ['season', 'situation', 'iceTime', 'goalsFor', 'goalsAgainst', 'mediumDangerShotsFor',
                                 'highDangerShotsFor', 'reboundsFor', 'mediumDangerShotsAgainst',
                                 'highDangerShotsAgainst', 'reboundsAgainst'], season_year)

    # Check if team with a higher ratio of rebounds to low danger shots had more wins. Equal ratios count as a failure.
    df['Result'] = 0
    df.loc[np.logical_or(np.logical_and(df.goalsFor > df.goalsAgainst,
                                        df.reboundsFor / (
                                                df.mediumDangerShotsFor + df.highDangerShotsFor) > df.reboundsAgainst / (
                                                df.mediumDangerShotsAgainst + df.highDangerShotsAgainst)),
                         np.logical_and(df.goalsAgainst > df.goalsFor,
                                        df.reboundsAgainst / (
                                                df.mediumDangerShotsAgainst + df.highDangerShotsAgainst) > df.reboundsFor / (
                                                df.mediumDangerShotsFor + df.highDangerShotsFor))), 'Result'] = 1

    # Calculate n (number of rows) and p (sum of the result column divided by n).
    n = df.shape[0]
    p = float(df['Result'].sum()) / n

    # Print results.
    print(Fore.BLUE + '\nRebounds and medium/high danger shots (ratio) n and p values: ')
    print(Style.RESET_ALL)
    print('Wins with a higher ratio of rebounds to medium/high danger shots: ' + str(df['Result'].sum() / 2))
    print('n value: ' + str(n / 2))
    print('p value: ' + str(p))


def time_on_power_play(filepath, season_year):
    """
    Calculate and print n and p values for hypothesis test regarding the time in power play (5 on 4) for the
    winning team.

    :param filepath: The path that contains the hockey data.
    :param season_year: The season to be analyzed.
    """

    # Extract the data from the "all" row to check for the winner of the game.
    all_data_df = extract_data(filepath, ['season', 'gameId', 'situation', 'iceTime', 'goalsFor', 'goalsAgainst'],
                               season_year)
    power_play_for = extract_data(filepath, ['season', 'gameId', 'situation', 'iceTime'], season_year, '5on4')
    power_play_against = extract_data(filepath, ['season', 'gameId', 'situation', 'iceTime'], season_year, '4on5')

    # Only find games that did not go into overtime.
    power_play_for = power_play_for[power_play_for.gameId.isin(all_data_df.gameId)]
    power_play_against = power_play_against[power_play_against.gameId.isin(all_data_df.gameId)]

    # Check if team with more goals had more time in power play (more time in 5 on 4 than the other team).
    all_data_df['Result'] = 0
    all_data_df.loc[np.logical_or(np.logical_and(all_data_df.goalsFor > all_data_df.goalsAgainst,
                                                 power_play_for.iceTime > power_play_against.iceTime),
                                  np.logical_and(all_data_df.goalsAgainst > all_data_df.goalsFor,
                                                 power_play_against.iceTime > power_play_for.iceTime)), 'Result'] = 1

    # Calculate n (number of rows) and p (sum of the result column divided by n).
    n = all_data_df.shape[0]
    p = float(all_data_df['Result'].sum()) / n

    # Print results.
    print(Fore.BLUE + '\nTime in power play n and p values: ')
    print(Style.RESET_ALL)
    print('Wins with more time in power play: ' + str(all_data_df['Result'].sum() / 2))
    print('n value: ' + str(n / 2))
    print('p value: ' + str(p))


def extract_data(filepath, columns, season_year, situation='all'):
    """
    Extract the relevant data from the CSV file. Games are indexed by their ID automatically (do not pass in as column).
    If 'all' situation specified, only games that did not go into overtime are returned.

    :param filepath: The path that contains the hockey data.
    :param columns: The column names that should be included.
    :param season_year: The season to be included.
    :param situation: The situation to be analyzed (default is 'all').
    :return: A DataFrame containing only the relevant rows and columns.
    """

    # Extract relevant columns.
    df = pd.read_csv(filepath_or_buffer=filepath, delimiter=',', header=0, usecols=columns.append('gameId'))

    # Extract rows of games that didn't go into overtime if the situation is 'all'
    if situation == 'all':
        df = df[np.logical_and(np.logical_and(df.situation == situation, df.season == season_year), df.iceTime == 3600)]
    else:
        df = df[np.logical_and(df.situation == situation, df.season == season_year)]

    df.index = df.gameId
    return df


def print_menu():
    """
    Prints a menu of options for the user to choose from.
    """
    print('\n\nPlease choose one of the hypothesis tests below (all teams in the season):')
    print('1. Shots on goal on win percentage')
    print('2. High danger shots on win percentage')
    print('3. Medium danger shots on win percentage')
    print('4. Low danger shots on win percentage')
    print('5. Having more rebounds on win percentage')
    print('6. Medium and high danger shots (combined) on win percentage')
    print('7. Low and high danger shots (combined) on win percentage')
    print('8. Low danger shots and rebounds (combined) on win percentage')
    print('9. Rebounds and low danger shots (ratio) on win percentage')
    print('10. Medium/high danger shots and rebounds (combined) on win percentage')
    print('11. Rebounds and medium/high danger shots (ratio) on win percentage')
    print('12. Time in power play on win percentage')
    print('13. Exit')
    print()


if __name__ == "__main__":
    main()
