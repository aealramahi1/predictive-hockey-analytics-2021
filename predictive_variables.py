import pandas as pd
import numpy as np
import os
from colorama import Fore, Style

# Does not include "exit".
TOTAL_OPTIONS = 3


def main():
    """
    Asks user for data to analyze about hockey games.
    """
    season = -1
    choice = -1

    # Obtain valid filepath from user.
    filepath = get_file()

    # Keep getting input from the user until the select exit.
    while choice != TOTAL_OPTIONS + 1:

        # Have the user select a variable to analyze from the menu.
        print_menu()

        # Make sure the selection made was valid.
        valid_choice = False
        while not valid_choice:
            try:
                choice = int(input('Please make a selection: '))

                # Make sure the choice is in range.
                if choice < 0 or choice > TOTAL_OPTIONS + 1:
                    choice = -1
                    raise ValueError
                valid_choice = True
            except ValueError:
                print(Fore.RED + 'Please enter a number between 1 and ' + str(TOTAL_OPTIONS) + '.\n')
                print(Style.RESET_ALL)

        # Use a dictionary definition as a mock switch statement to choose the appropriate function.
        switch = {
            1: lambda: last_five_med_high_low_danger(filepath, season),
            2: lambda: last_five_med_high_low_danger_formula(filepath, season)
        }

        if choice < TOTAL_OPTIONS:

            # Obtain valid season from the user.
            valid_season = False
            while not valid_season:
                try:
                    season = int(
                        input('Please enter the beginning year of the season you want to analyze (2008 - 2018): '))

                    # Make sure the season is in the right range.
                    if season < 2008 or season > 2018:
                        season = -1
                        raise ValueError
                    valid_season = True

                # Make sure the season is one year.
                except ValueError:
                    print(Fore.RED + 'Please enter a year between 2008 and 2017.\n')
                    print(Style.RESET_ALL)

            f = switch.get(choice)
            f()

        elif choice == TOTAL_OPTIONS:
            filepath = get_file()
        print()


def last_five_med_high_low_danger(filepath, season_year):
    """
    Calculate the percentage of winning games in the given season (except the first five games) where the first previous
    five games had more medium/high danger shots combined as well as less low danger shots. Prints this result.

    :param filepath: The filepath to the team that is being analyzed.
    :param season_year: The season to be analyzed.
    """

    # Extract the relevant data.
    df = extract_data(filepath, ['season', 'situation', 'goalsFor', 'goalsAgainst', 'mediumDangerShotsFor',
                                 'mediumDangerShotsAgainst', 'highDangerShotsFor', 'highDangerShotsAgainst',
                                 'lowDangerShotsFor', 'lowDangerShotsAgainst'],
                      season_year)

    # Calculate prefix sums for medium/high danger shots (for and against) and low danger shots (for and against).
    mh_for = df['mediumDangerShotsFor'] + df['highDangerShotsFor']
    mh_against = df['mediumDangerShotsAgainst'] + df['highDangerShotsAgainst']

    med_high_for = np.cumsum(mh_for)
    low_for = np.cumsum(df['lowDangerShotsFor'])

    med_high_against = np.cumsum(mh_against)
    low_against = np.cumsum(df['lowDangerShotsAgainst'])

    n = med_high_for.size - 5
    p = 0

    for i in range(6, n):

        mf = med_high_for[i] - med_high_for[i - 5]
        ma = med_high_against[i] - med_high_against[i - 5]

        lf = low_for[i] - low_for[i - 5]
        la = low_against[i] - low_against[i - 5]

        if df['goalsFor'][i] > df['goalsAgainst'][i] and mf > ma and lf < la:
            p += 1
        elif df['goalsFor'][i] < df['goalsAgainst'][i] and mf < ma and lf > la:
            p += 1

    print(p / n)


def last_five_med_high_low_danger_formula(filepath, season_year):
    """
    Calculate the percentage of winning games in the given season (except the first five games) that abide by a
    formula involving low, medium, and high danger shots (medium danger shots + high danger shots - low danger shots).

    :param filepath: The filepath to the team that is being analyzed.
    :param season_year: The season to be analyzed.
    """

    # Extract the relevant data.
    df = extract_data(filepath, ['season', 'situation', 'goalsFor', 'goalsAgainst', 'mediumDangerShotsFor',
                                 'mediumDangerShotsAgainst', 'highDangerShotsFor', 'highDangerShotsAgainst',
                                 'lowDangerShotsFor', 'lowDangerShotsAgainst'],
                      season_year)

    # Calculate prefix sums for medium/high danger shots (for and against) and low danger shots (for and against).
    for_team = df['mediumDangerShotsFor'] + df['highDangerShotsFor'] - df['lowDangerShotsFor']
    against_team = df['mediumDangerShotsAgainst'] + df['highDangerShotsAgainst'] - df['lowDangerShotsAgainst']

    fteam = np.cumsum(for_team)
    ateam = np.cumsum(against_team)

    n = fteam.size - 5
    p = 0

    for i in range(6, n):

        f = fteam[i] - fteam[i - 5]
        a = ateam[i] - ateam[i - 5]

        if df['goalsFor'][i] > df['goalsAgainst'][i] and f > a:
            p += 1
        elif df['goalsFor'][i] < df['goalsAgainst'][i] and f < a:
            p += 1

    print(p / n)


def extract_data(filepath, columns, season_year):
    """
    Extract the relevant data from the CSV file. Games are indexed by their ID automatically (do not pass in as column).

    :param filepath: The path that contains the hockey data.
    :param columns: The column names that should be included.
    :param season_year: The season to be included.
    :return: A DataFrame containing only the relevant rows and columns.
    """

    # Extract relevant columns.
    df = pd.read_csv(filepath_or_buffer=filepath, delimiter=',', header=0, usecols=columns.append('gameId'))

    # Only extract the rows containing all data for each game.
    df = df[np.logical_and(df.situation == 'all', df.season == season_year)]

    df = df.reset_index()
    return df


def get_file():
    """
    Obtains the filepath of the CSV for the specific team from the user.

    :return: The path to the valid CSV file.
    """
    valid_filepath = False
    while not valid_filepath:
        inputted_file = input(
            'Please enter filepath to CSV file for the team you would like to analyze from MoneyPuck (relative or absolute): ')

        # Check for read permission on the file that we are trying to access.
        if os.access(inputted_file, os.R_OK):
            return inputted_file
        else:
            print(Fore.RED + 'Could not access file. Make sure the path is correct.\n', 'red')
            print(Style.RESET_ALL)


def print_menu():
    """
    Prints a menu of options for the user to choose from.
    """
    print('\n\nPlease choose one of the hypothesis tests below (all teams in the season):')
    print('1. Medium/High Danger Shots and Low Danger Shots (previous five games)')
    print('2. Medium/High Danger Shots and Low Danger Shots (previous five games) Formula')
    print('3. Switch filepath')
    print('4. Exit')
    print()


if __name__ == "__main__":
    main()
