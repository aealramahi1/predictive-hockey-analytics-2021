import pandas as pd
import numpy as np
import os
from colorama import Fore, Style

# Does not include "exit".
TOTAL_OPTIONS = 5


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

            if choice == 1:

                p_results = [0] * 100

                # Parametric analysis changing the weight on medium/high danger shots.
                for weight in range(5, 505, 5):
                    mh_weight = weight / 100.0
                    p_results[int(weight / 5 - 1)] = last_five_med_high_low_danger_formula(filepath, season, mh_weight, 1)

                # Write the results to an Excel file.
                writer = pd.ExcelWriter('Medium High Danger Weights.xlsx')
                results = pd.Series(p_results)
                results.to_excel(writer, sheet_name=filepath[:-4])
                writer.save()

            elif choice == 2:

                p_results = [0] * 100

                # Parametric analysis changing the weight on low danger shots.
                for weight in range(5, 505, 5):
                    l_weight = weight / 100.0
                    p_results[int(weight / 5 - 1)] = last_five_med_high_low_danger_formula(filepath, season, 1, l_weight)

                # Write the results to an Excel file.
                writer = pd.ExcelWriter('Low Danger Weights.xlsx')
                results = pd.Series(p_results)
                results.to_excel(writer, sheet_name=filepath[:-4])
                writer.save()

            elif choice == 3:

                p_results = [0] * 100

                # Parametric analysis changing the weight on penalty minutes.
                for weight in range(5, 505, 5):
                    mh_weight = weight / 100.0
                    p_results[int(weight / 5 - 1)] = last_five_med_high_danger_penalty_minutes_formula(filepath, season, mh_weight, 1)

                # Write the results to an Excel file.
                writer = pd.ExcelWriter('Penalty Minutes Weights.xlsx')
                results = pd.Series(p_results)
                results.to_excel(writer, sheet_name=filepath[:-4])
                writer.save()

            elif choice == 4:
                p_results = [0] * 100

                # Parametric analysis changing the weight on penalty minutes.
                for weight in range(5, 505, 5):
                    s_weight = weight / 100.0
                    p_results[int(weight / 5 - 1)] = last_five_med_high_danger_shots_on_goal_formula(filepath, season,
                                                                                                       s_weight)

                # Write the results to an Excel file.
                writer = pd.ExcelWriter('Shots On Goal Weights.xlsx')
                results = pd.Series(p_results)
                results.to_excel(writer, sheet_name=filepath[:-4])
                writer.save()

        elif choice == TOTAL_OPTIONS:
            filepath = get_file()
        print()


def last_five_med_high_low_danger_formula(filepath, season_year, mh_weight, l_weight):
    """
    Calculate the percentage of winning games in the given season (except the first five games) that abide by a
    formula involving low, medium, and high danger shots: (medium danger shots + high danger shots) * (mh_weight) -
    (low danger shots) * (l_weight).

    :param filepath: The filepath to the team that is being analyzed.
    :param season_year: The season to be analyzed.
    :param mh_weight: The weight on the medium/high danger shots in the formula.
    :param l_weight: The weight on the low danger shots in the formula.
    :return p: The percentage of wins/losses that were accurately predicted using our formula.
    """

    # Extract the relevant data.
    df = extract_data(filepath, ['season', 'situation', 'goalsFor', 'goalsAgainst', 'mediumDangerShotsFor',
                                 'mediumDangerShotsAgainst', 'highDangerShotsFor', 'highDangerShotsAgainst',
                                 'lowDangerShotsFor', 'lowDangerShotsAgainst'],
                      season_year)

    # Calculate prefix sums for medium/high danger shots (for and against) and low danger shots (for and against).
    for_team = mh_weight * (df['mediumDangerShotsFor'] + df['highDangerShotsFor']) - l_weight * df['lowDangerShotsFor']
    against_team = mh_weight * (df['mediumDangerShotsAgainst'] + df['highDangerShotsAgainst']) - l_weight * df['lowDangerShotsAgainst']

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

    return p / n


def last_five_med_high_danger_penalty_minutes_formula(filepath, season_year, mh_weight, p_weight):
    """
    Calculate the percentage of winning games in the given season (except the first five games) that abide by a
    formula involving medium and high danger shots and penalty minutes: mh_weight *
    (medium_danger_shots + high_danger_shots) * (penalty_minutes) / (p_weight * (penalty_minutes + 1) ** 2)

    :param filepath: The filepath to the team that is being analyzed.
    :param season_year: The season to be analyzed.
    :param mh_weight: The weight on the medium/high danger shots in the formula.
    :param p_weight: The weight on the penalty minutes in the formula.
    :return p: The percentage of wins/losses that were accurately predicted using our formula.
    """

    # Extract the relevant data.
    df = extract_data(filepath, ['season', 'situation', 'goalsFor', 'goalsAgainst', 'mediumDangerShotsFor',
                                 'mediumDangerShotsAgainst', 'highDangerShotsFor', 'highDangerShotsAgainst',
                                 'penalityMinutesFor', 'penalityMinutesAgainst'],
                      season_year)

    # Calculate prefix sums for medium/high danger shots (for and against) and low danger shots (for and against).
    for_team = mh_weight * (df['mediumDangerShotsFor'] + df['highDangerShotsFor']) * df['penalityMinutesFor'] / (p_weight * (df['penalityMinutesFor'] + 1) ** 2)
    against_team = mh_weight * (df['mediumDangerShotsAgainst'] + df['highDangerShotsAgainst']) * df['penalityMinutesAgainst']  / (p_weight * (df['penalityMinutesAgainst'] + 1) ** 2)

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

    return p / n


def last_five_med_high_danger_shots_on_goal_formula(filepath, season_year, s_weight):
    """
    Calculate the percentage of winning games in the given season (except the first five games) that abide by a
    formula involving medium and high danger shots and shots on goal: medium danger shots + high danger shots
    + s_weight * shots_on_gaol.

    :param filepath: The filepath to the team that is being analyzed.
    :param season_year: The season to be analyzed.
    :param s_weight: The weight on the shots on goal in the formula.
    :return p: The percentage of wins/losses that were accurately predicted using our formula.
    """

    # Extract the relevant data.
    df = extract_data(filepath, ['season', 'situation', 'goalsFor', 'goalsAgainst', 'mediumDangerShotsFor',
                                 'mediumDangerShotsAgainst', 'highDangerShotsFor', 'highDangerShotsAgainst',
                                 'shotsOnGoalFor', 'shotsOnGoalAgainst'],
                      season_year)

    # Calculate prefix sums for medium/high danger shots (for and against) and low danger shots (for and against).
    for_team = (df['mediumDangerShotsFor'] + df['highDangerShotsFor']) - s_weight * df['shotsOnGoalFor']
    against_team = (df['mediumDangerShotsAgainst'] + df['highDangerShotsAgainst']) - s_weight * df['shotsOnGoalAgainst']

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

    return p / n


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
    print('1. Produce medium/high danger shots weight plots.')
    print('2. Produce low danger shots weight plots.')
    print('3. Produce penalty minutes weight plots.')
    print('4. Produce shots on goal weight plots.')
    print('5. Switch filepath')
    print('6. Exit')
    print()


if __name__ == "__main__":
    main()
