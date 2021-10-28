import pandas as pd
import numpy as np
import os
from colorama import Fore, Style

# Does not include "exit".
import produce_team_record

TOTAL_OPTIONS = 17


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
            1: lambda: single_col_for_and_against(filepath, season, 'shotsOnGoal'),
            2: lambda: single_col_for_and_against(filepath, season, 'highDangerShots'),
            3: lambda: single_col_for_and_against(filepath, season, 'mediumDangerShots'),
            4: lambda: single_col_for_and_against(filepath, season, 'lowDangerShots'),
            5: lambda: single_col_for_and_against(filepath, season, 'rebounds'),
            6: lambda: single_col_for_and_against(filepath, season, 'takeaways'),
            7: lambda: single_col_for_and_against(filepath, season, 'penalties'),
            8: lambda: single_col_for_and_against(filepath, season, 'penalityMinutes'),
            9: lambda: high_and_med_danger(filepath, season),
            10: lambda: high_and_low_danger(filepath, season),
            11: lambda: low_danger_and_rebounds_sum(filepath, season),
            12: lambda: rebounds_and_low_danger_shots_ratio(filepath, season),
            13: lambda: medium_and_high_danger_and_rebounds_sum(filepath, season),
            14: lambda: rebounds_and_medium_and_high_danger_shots_ratio(filepath, season),
            15: lambda: time_on_power_play(filepath, season),
            16: lambda: playoff_shots_on_goal(filepath, season)
        }

        if choice < TOTAL_OPTIONS:

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
            result = f()

            # Check to make sure we are not running our hypothesis tests on data that doesn't exist.
            if result.shape[0] != 0:
                calculate_and_display_results(filepath, result, season)
            else:
                print('Error. This team may not have played in the NHL during this season.')

        elif choice == TOTAL_OPTIONS:
            filepath = get_file()
        print()


def single_col_for_and_against(filepath, season_year, col_name):
    """
    Calculate and print n and p values for hypothesis test regarding a single variable with "for" and "against" columns
    in all_teams.csv. Checks if a win corresponds to having a higher value in the column than the other team.

    :param filepath: The path that contains the hockey data.
    :param season_year: The season to be analyzed.
    :param col_name: The name of the column to be analyzed
    :return A pandas Series containing the successes (as ones) and the losses (as zeros).
    """

    for_col = col_name + 'For'
    against_col = col_name + 'Against'

    # Extract the relevant data.
    df = extract_data(filepath,
                      ['season', 'situation', 'iceTime', 'shotsOnGoalFor', for_col, against_col, 'goalsAgainst'],
                      season_year)

    # Check if team with more goals has more of the column value.
    df['Result'] = 0

    if 'all_teams.csv' in filepath:
        df.loc[np.logical_or(
            np.logical_and(df.goalsFor > df.goalsAgainst, getattr(df, for_col) > getattr(df, against_col)),
            np.logical_and(df.goalsAgainst > df.goalsFor,
                           getattr(df, against_col) > getattr(df, for_col))), 'Result'] = 1
    else:
        df.loc[np.logical_and(df.goalsFor > df.goalsAgainst,
                              getattr(df, for_col) > getattr(df, against_col)), 'Result'] = 1

    return df['Result']


def high_and_med_danger(filepath, season_year):
    """
    Calculate and print n and p values for hypothesis test regarding medium and high danger shots combined.

    :param filepath: The path that contains the hockey data.
    :param season_year: The season to be analyzed.
    :return A pandas Series containing the successes (as ones) and the losses (as zeros).
    """

    # Extract the relevant data.
    df = extract_data(filepath, ['season', 'situation', 'iceTime', 'goalsFor', 'goalsAgainst', 'mediumDangerShotsFor',
                                 'highDangerShotsFor', 'mediumDangerShotsAgainst', 'highDangerShotsAgainst'],
                      season_year)

    # Check if team with more combined medium and high danger shots had more wins.
    df['Result'] = 0

    if 'all_teams.csv' in filepath:
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
    else:
        df.loc[np.logical_and(df.goalsFor > df.goalsAgainst,
                              df.highDangerShotsFor + df.mediumDangerShotsFor > df.highDangerShotsAgainst + df.mediumDangerShotsAgainst), 'Result'] = 1

        # If high and medium danger shots are equal, check if one team has more high danger shots.
        df.loc[np.logical_and(df.goalsFor > df.goalsAgainst,
                              np.logical_and(
                                  df.highDangerShotsFor + df.mediumDangerShotsFor == df.highDangerShotsAgainst + df.mediumDangerShotsAgainst,
                                  df.highDangerShotsFor > df.highDangerShotsAgainst)), 'Result'] = 1

    return df['Result']


def high_and_low_danger(filepath, season_year):
    """
    Calculate and print n and p values for hypothesis test regarding low and high danger shots combined.

    :param filepath: The path that contains the hockey data.
    :param season_year: The season to be analyzed.
    :return A pandas Series containing the successes (as ones) and the losses (as zeros).
    """

    # Extract the relevant data.
    df = extract_data(filepath, ['season', 'situation', 'iceTime', 'goalsFor', 'goalsAgainst', 'lowDangerShotsFor',
                                 'highDangerShotsFor', 'lowDangerShotsAgainst', 'highDangerShotsAgainst'],
                      season_year)

    # Check if team with more combined low and high danger shots had more wins.
    df['Result'] = 0

    if 'all_teams.csv' in filepath:
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
    else:
        df.loc[np.logical_and(df.goalsFor > df.goalsAgainst,
                              df.highDangerShotsFor + df.lowDangerShotsFor > df.highDangerShotsAgainst + df.lowDangerShotsAgainst), 'Result'] = 1

        # If high and medium danger shots are equal, check if one team has more high danger shots.
        df.loc[np.logical_and(df.goalsFor > df.goalsAgainst,
                              np.logical_and(
                                  df.highDangerShotsFor + df.lowDangerShotsFor == df.highDangerShotsAgainst + df.lowDangerShotsAgainst,
                                  df.highDangerShotsFor > df.highDangerShotsAgainst)), 'Result'] = 1

    return df['Result']


def low_danger_and_rebounds_sum(filepath, season_year):
    """
    Calculate and print n and p values for hypothesis test regarding the sum of low danger shots and rebounds for the
    winning team.

    :param filepath: The path that contains the hockey data.
    :param season_year: The season to be analyzed.
    :return A pandas Series containing the successes (as ones) and the losses (as zeros).
    """

    # Extract the relevant data.
    df = extract_data(filepath, ['season', 'situation', 'iceTime', 'goalsFor', 'goalsAgainst', 'lowDangerShotsFor',
                                 'reboundsFor', 'lowDangerShotsAgainst', 'reboundsAgainst'],
                      season_year)

    # Check if team with more combined low danger shots and rebounds had more wins. Equal sums counts as a failure.
    df['Result'] = 0

    if 'all_teams.csv' in filepath:
        df.loc[np.logical_or(np.logical_and(df.goalsFor > df.goalsAgainst,
                                            df.reboundsFor + df.lowDangerShotsFor > df.reboundsAgainst + df.lowDangerShotsAgainst),
                             np.logical_and(df.goalsAgainst > df.goalsFor,
                                            df.reboundsAgainst + df.lowDangerShotsAgainst > df.reboundsFor + df.lowDangerShotsFor)), 'Result'] = 1
    else:
        df.loc[np.logical_and(df.goalsFor > df.goalsAgainst,
                              df.reboundsFor + df.lowDangerShotsFor > df.reboundsAgainst + df.lowDangerShotsAgainst), 'Result'] = 1

    return df['Result']


def rebounds_and_low_danger_shots_ratio(filepath, season_year):
    """
    Calculate and print n and p values for hypothesis test regarding the ratio of rebounds to low danger shots for the
    winning team.

    :param filepath: The path that contains the hockey data.
    :param season_year: The season to be analyzed.
    :return A pandas Series containing the successes (as ones) and the losses (as zeros).
    """

    # Extract the relevant data.
    df = extract_data(filepath, ['season', 'situation', 'iceTime', 'goalsFor', 'goalsAgainst', 'lowDangerShotsFor',
                                 'reboundsFor', 'lowDangerShotsAgainst', 'reboundsAgainst'],
                      season_year)

    # Check if team with a higher ratio of rebounds to low danger shots had more wins. Equal ratios count as a failure.
    df['Result'] = 0

    if 'all_teams.csv' in filepath:
        df.loc[np.logical_or(np.logical_and(df.goalsFor > df.goalsAgainst,
                                            df.reboundsFor / df.lowDangerShotsFor > df.reboundsAgainst / df.lowDangerShotsAgainst),
                             np.logical_and(df.goalsAgainst > df.goalsFor,
                                            df.reboundsAgainst / df.lowDangerShotsAgainst > df.reboundsFor / df.lowDangerShotsFor)), 'Result'] = 1
    else:
        df.loc[np.logical_and(df.goalsFor > df.goalsAgainst,
                              df.reboundsFor / df.lowDangerShotsFor > df.reboundsAgainst / df.lowDangerShotsAgainst), 'Result'] = 1

    return df['Result']


def medium_and_high_danger_and_rebounds_sum(filepath, season_year):
    """
    Calculate and print n and p values for hypothesis test regarding the sum of medium/high danger shots and rebounds for the
    winning team.

    :param filepath: The path that contains the hockey data.
    :param season_year: The season to be analyzed.
    :return A pandas Series containing the successes (as ones) and the losses (as zeros).
    """

    # Extract the relevant data.
    df = extract_data(filepath, ['season', 'situation', 'iceTime', 'goalsFor', 'goalsAgainst', 'mediumDangerShotsFor',
                                 'highDangerShotsFor', 'reboundsFor', 'mediumDangerShotsAgainst',
                                 'highDangerShotsAgainst', 'reboundsAgainst'], season_year)

    # Check if team with more combined med/high danger shots and rebounds had more wins. Equal sums counts as a failure.
    df['Result'] = 0

    if 'all_teams.csv' in filepath:
        df.loc[np.logical_or(np.logical_and(df.goalsFor > df.goalsAgainst,
                                            df.reboundsFor + df.mediumDangerShotsFor + df.highDangerShotsFor > df.reboundsAgainst + df.mediumDangerShotsAgainst + df.highDangerShotsAgainst),
                             np.logical_and(df.goalsAgainst > df.goalsFor,
                                            df.reboundsAgainst + df.mediumDangerShotsAgainst + df.highDangerShotsAgainst > df.reboundsFor + df.mediumDangerShotsFor + df.highDangerShotsFor)), 'Result'] = 1
    else:
        df.loc[np.logical_and(df.goalsFor > df.goalsAgainst,
                              df.reboundsFor + df.mediumDangerShotsFor + df.highDangerShotsFor > df.reboundsAgainst + df.mediumDangerShotsAgainst + df.highDangerShotsAgainst), 'Result'] = 1

    return df['Result']


def rebounds_and_medium_and_high_danger_shots_ratio(filepath, season_year):
    """
    Calculate and print n and p values for hypothesis test regarding the ratio of rebounds to medium and high danger shots for the
    winning team.

    :param filepath: The path that contains the hockey data.
    :param season_year: The season to be analyzed.
    :return A pandas Series containing the successes (as ones) and the losses (as zeros).
    """

    # Extract the relevant data.
    df = extract_data(filepath, ['season', 'situation', 'iceTime', 'goalsFor', 'goalsAgainst', 'mediumDangerShotsFor',
                                 'highDangerShotsFor', 'reboundsFor', 'mediumDangerShotsAgainst',
                                 'highDangerShotsAgainst', 'reboundsAgainst'], season_year)

    # Check if team with a higher ratio of rebounds to low danger shots had more wins. Equal ratios count as a failure.
    df['Result'] = 0

    if 'all_teams.csv' in filepath:
        df.loc[np.logical_or(np.logical_and(df.goalsFor > df.goalsAgainst,
                                            df.reboundsFor / (
                                                    df.mediumDangerShotsFor + df.highDangerShotsFor) > df.reboundsAgainst / (
                                                    df.mediumDangerShotsAgainst + df.highDangerShotsAgainst)),
                             np.logical_and(df.goalsAgainst > df.goalsFor,
                                            df.reboundsAgainst / (
                                                    df.mediumDangerShotsAgainst + df.highDangerShotsAgainst) > df.reboundsFor / (
                                                    df.mediumDangerShotsFor + df.highDangerShotsFor))), 'Result'] = 1
    else:
        df.loc[np.logical_and(df.goalsFor > df.goalsAgainst, df.reboundsFor / (
                df.mediumDangerShotsFor + df.highDangerShotsFor) > df.reboundsAgainst / (
                                      df.mediumDangerShotsAgainst + df.highDangerShotsAgainst)), 'Result'] = 1

    return df['Result']


def time_on_power_play(filepath, season_year):
    """
    Calculate and print n and p values for hypothesis test regarding the time in power play (5 on 4) for the
    winning team.

    :param filepath: The path that contains the hockey data.
    :param season_year: The season to be analyzed.
    :return A pandas Series containing the successes (as ones) and the losses (as zeros).
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

    if 'all_teams.csv' in filepath:
        all_data_df.loc[np.logical_or(np.logical_and(all_data_df.goalsFor > all_data_df.goalsAgainst,
                                                     power_play_for.iceTime > power_play_against.iceTime),
                                      np.logical_and(all_data_df.goalsAgainst > all_data_df.goalsFor,
                                                     power_play_against.iceTime > power_play_for.iceTime)), 'Result'] = 1
    else:
        all_data_df.loc[np.logical_and(all_data_df.goalsFor > all_data_df.goalsAgainst,
                                       power_play_for.iceTime > power_play_against.iceTime), 'Result'] = 1

    return all_data_df['Result']


def playoff_shots_on_goal(filepath, season_year):
    """
    Calculate and print n and p values for hypothesis test regarding playoff shots on goal. Modified from code written
    by Will Debolt and Harvey Campos-Chavez.

    :param filepath: The path that contains the hockey data.
    :param season_year: The season to be analyzed.
    :return A pandas Series containing the successes (as ones) and the losses (as zeros).
    """

    index = filepath.find('.csv')
    team = filepath[index - 3:index]

    # Extract the relevant data.
    df = extract_data('all_teams.csv',
                      ['team', 'season', 'situation', 'iceTime', 'shotsOnGoalFor', 'goalsFor', 'shotsOnGoalAgainst',
                       'goalsAgainst', 'playoffGame'], season_year)

    # Only consider playoff games.
    df = df[df.playoffGame == 1]
    df['Result'] = 0

    if 'all_teams.csv' in filepath:
        df.loc[np.logical_or(np.logical_and(df.goalsFor > df.goalsAgainst, df.shotsOnGoalFor > df.shotsOnGoalAgainst),
                             np.logical_and(df.goalsAgainst > df.goalsFor,
                                            df.shotsOnGoalAgainst > df.shotsOnGoalFor)), 'Result'] = 1
    else:

        # Only look at the teams we are interested in.
        df = df[df.team == team]
        df.loc[np.logical_and(df.goalsFor > df.goalsAgainst, df.shotsOnGoalFor > df.shotsOnGoalAgainst), 'Result'] = 1

    return df['Result']


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


def get_file():
    """
    Obtains the filepath of the CSV from the user.

    :return: The path to the valid CSV file.
    """
    valid_filepath = False
    while not valid_filepath:
        inputted_file = input('Please enter filepath to all_teams.csv from MoneyPuck (relative or absolute): ')

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
    print('1. Shots on goal on win percentage')
    print('2. High danger shots on win percentage')
    print('3. Medium danger shots on win percentage')
    print('4. Low danger shots on win percentage')
    print('5. Having more rebounds on win percentage')
    print('6. Having more takeaways on win percentage')
    print('7. Having more penalties on win percentage')
    print('8. Having more penalty minutes on win percentage')
    print('9. Medium and high danger shots (combined) on win percentage')
    print('10. Low and high danger shots (combined) on win percentage')
    print('11. Low danger shots and rebounds (combined) on win percentage')
    print('12. Rebounds and low danger shots (ratio) on win percentage')
    print('13. Medium/high danger shots and rebounds (combined) on win percentage')
    print('14. Rebounds and medium/high danger shots (ratio) on win percentage')
    print('15. Time in power play on win percentage')
    print('16. Playoff shots on goal')
    print('17. Change file path.')
    print('18. Exit')
    print()


def calculate_and_display_results(filepath, results, season):
    """
    Calculates the n and p values of the hypothesis test.

    :param filepath: The filepath that these results came from.
    :param results: A pandas Series containing the results of the hypothesis tests.
    :param season: The season being analyzed.
    """

    # Calculate the number of successes as well as n and p. The all_teams file double counts each team so we must also
    # divide it by 2.
    if 'all_teams.csv' in filepath:
        s = results.sum() / 2
        n = results.size / 2
        p = float(results.sum()) / (n * 2)
    else:
        s = results.sum()
        n = results.size

        # Get the number of wins for this team.
        index = filepath.find('.csv')
        team = filepath[index - 3:index]

        p = float(results.sum()) / produce_team_record.produce_num_of_wins(team, season)

    # Print results.
    print(Fore.BLUE + '\nResultant n and p values: ')
    print(Style.RESET_ALL)
    print('Number of successes: ' + str(s))
    print('n value: ' + str(n))
    print('p value: ' + str(p))


if __name__ == "__main__":
    main()
