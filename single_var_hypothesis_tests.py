import pandas as pd
import numpy as np
import os
from colorama import Fore, Style

TOTAL_TESTS = 8


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
            1: lambda: shots_on_goal(filepath, season),
            2: lambda: single_danger_shot(filepath, season, 'high'),
            3: lambda: single_danger_shot(filepath, season, 'medium'),
            4: lambda: single_danger_shot(filepath, season, 'low'),
            5: lambda: high_and_med_danger(filepath, season),
            6: lambda: high_and_low_danger(filepath, season),
            7: lambda: low_danger_and_rebounds_sum(filepath, season),
            8: lambda: rebounds_and_low_danger_shots_ratio(filepath, season)
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


def shots_on_goal(filepath, season_year):
    """
    Calculate and print n and p values for hypothesis test regarding shots on goal.

    :param filepath: The path that contains the hockey data.
    :param season_year: The season to be analyzed.
    """

    # Extract the relevant data.
    df = extract_data(filepath,
                      ['season', 'situation', 'iceTime', 'shotsOnGoalFor', 'goalsFor', 'shotsOnGoalAgainst',
                       'goalsAgainst'], season_year)

    # Check if team with more goals has more shots on goal.
    df['Result'] = 0
    df.loc[np.logical_or(np.logical_and(df.goalsFor > df.goalsAgainst, df.shotsOnGoalFor > df.shotsOnGoalAgainst),
                         np.logical_and(df.goalsAgainst > df.goalsFor,
                                        df.shotsOnGoalAgainst > df.shotsOnGoalFor)), 'Result'] = 1

    # Calculate n (number of rows) and p (sum of the result column divided by n).
    n = df.shape[0]
    p = float(df['Result'].sum()) / n

    # Print results.
    print(Fore.BLUE + '\nShots on goal n and p values: ')
    print(Style.RESET_ALL)
    print('Wins with more shots on goal: ' + str(df['Result'].sum()))
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


def single_danger_shot(filepath, season_year, danger):
    """
    Calculate and print n and p values for hypothesis test regarding low, medium, or high danger shots.

    :param filepath: The path that contains the hockey data.
    :param season_year: The season to be analyzed.
    :param danger: A string of the danger to be analyzed (low, medium, or high)
    :raise ValueError if dangers is not 'low', 'medium', or 'high'
    """

    # Universal columns to be extracted.
    cols = ['season', 'situation', 'iceTime', 'goalsFor', 'goalsAgainst']

    # Add the columns relevant to each danger.
    if 'low' in danger:
        cols.append('lowDangerShotsFor')
        cols.append('lowDangerShotsAgainst')
    elif 'medium' in danger:
        cols.append('mediumDangerShotsFor')
        cols.append('mediumDangerShotsAgainst')
    elif 'high' in danger:
        cols.append('highDangerShotsFor')
        cols.append('highDangerShotsAgainst')
    else:
        raise ValueError('Danger must be low, medium, or high.')

    # Extract the relevant data.
    df = extract_data(filepath, cols, season_year)

    # Check if team with more danger shots of the specified type had more wins.
    if 'low' in danger:
        shots_for = df.lowDangerShotsFor
        shots_against = df.lowDangerShotsAgainst
    elif 'medium' in danger:
        shots_for = df.mediumDangerShotsFor
        shots_against = df.mediumDangerShotsAgainst
    else:
        shots_for = df.highDangerShotsFor
        shots_against = df.highDangerShotsAgainst

    df['Result'] = 0
    df.loc[np.logical_or(np.logical_and(df.goalsFor > df.goalsAgainst, shots_for > shots_against),
                         np.logical_and(df.goalsAgainst > df.goalsFor, shots_against > shots_for)), 'Result'] = 1

    # Calculate n (number of rows) and p (sum of the result column divided by n).
    n = df.shape[0]
    p = float(df['Result'].sum()) / n

    # Print results.
    print(Fore.BLUE + '\n' + danger + ' danger shots n and p values: ')
    print(Style.RESET_ALL)
    print('Wins with more' + danger + ' danger shots: ' + str(df['Result'].sum() / 2))
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


def extract_data(filepath, columns, season_year):
    """
    Extract the relevant data from the CSV file.

    :param filepath: The path that contains the hockey data.
    :param columns: The column names that should be included.
    :param season_year: The season to be included.
    :return: A dataframe containing only the relevant rows and columns.
    """

    # Extract relevant columns.
    df = pd.read_csv(filepath_or_buffer=filepath, delimiter=',', header=0, usecols=columns)

    # Extract rows of games that didn't go into overtime in the specified seasons. Data includes 'all' situation only.
    return df[np.logical_and(np.logical_and(df.situation == 'all', df.season == season_year), df.iceTime == 3600)]


def print_menu():
    """
    Prints a menu of options for the user to choose from.
    """
    print('\n\nPlease choose one of the hypothesis tests below (all teams in the season):')
    print('1. Shots on goal on win percentage')
    print('2. High danger shots on win percentage')
    print('3. Medium danger shots on win percentage')
    print('4. Low danger shots on win percentage')
    print('5. Medium and high danger shots (combined) on win percentage')
    print('6. Low and high danger shots (combined) on win percentage')
    print('7. Low danger shots and rebounds (combined) on win percentage')
    print('8. Rebounds and low danger shots (ratio) on win percentage')
    print('9. Exit')
    print()


if __name__ == "__main__":
    main()
