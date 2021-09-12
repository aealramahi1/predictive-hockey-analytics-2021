import pandas as pd
import numpy as np
import os

TOTAL_TESTS = 1


def main():
    """
    Asks user for data to analyze about hockey games.
    """
    filepath = None
    season = -1

    # Obtain valid filepath from user.
    while not filepath:
        inputted_file = input('Please enter filepath to all_teams.csv from MoneyPuck (relative or absolute): ')

        # Check for read permission on the file that we are trying to access.
        if os.access(inputted_file, os.R_OK):
            filepath = inputted_file
        else:
            print('Could not access file. Make sure the path is correct.\n')

    # Obtain valid season from the user.
    while season == -1:
        try:
            season = int(input('Please enter the beginning year of the season you want to analyze (2008 - 2017): '))

            # Make sure the season is in the right range.
            if season < 2008 or season > 2017:
                season = -1
                raise ValueError

        # Make sure the season is one year.
        except ValueError:
            print('Please enter a year between 2008 and 2017.\n')

    # Have the user select a variable to analyze from the menu.
    print_menu()

    # Make sure the selection made was valid.
    choice = -1
    while choice == -1:
        try:
            choice = int(input('Please make a selection: '))

            # Make sure the choice is in range.
            if choice < 0 or choice > TOTAL_TESTS:
                choice = -1
                raise ValueError
        except ValueError:
            print('Please select 1.\n')
            # print('Please enter a number between 1 and ' + str(TOTAL_TESTS) + '.\n')

    # Use a dictionary definition as a mock switch statement to choose the appropriate function.
    switch = {
        1: lambda: shots_on_goal(filepath, season),
    }
    f = switch.get(choice)
    f()


def shots_on_goal(filepath, season_year):
    """
    Calculate and print n and p values for hypothesis test regarding shots on goal.

    :param filepath: The path that contains the hockey data.
    :param season_year:The season to be analyzed.
    """

    # Extract the relevant data.
    df = extract_rows_and_cols(filepath,
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
    print('\nShots on goal n and p values: ')
    print('Wins with more shots on goal: ' + str(df['Result'].sum()))
    print('n value: ' + str(n))
    print('p value: ' + str(p))


def extract_rows_and_cols(filepath, columns, season_year):
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
    print('\n\nPlease choose one of the hypothesis tests below:')
    print('1. Effects of shots on goal on win percentage (all teams in the season)')
    print('More options coming soon :)\n')


if __name__ == "__main__":
    main()
    input("\nPress enter to exit.")
