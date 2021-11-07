import pandas as pd
import numpy as np

NUM_TEAMS = 31
NUM_SEASON_YEARS = 10

teams = ['ANA', 'ARI', 'BOS', 'BUF', 'CAR', 'CBJ', 'CGY', 'CHI', 'COL', 'DAL', 'DET', 'EDM', 'FLA', 'L.A',
         'MIN', 'MTL', 'N.J', 'NSH', 'NYI', 'NYR', 'OTT', 'PHI', 'PIT', 'S.J', 'STL', 'T.B', 'TOR', 'VAN', 'VGK', 'WPG',
         'WSH']


def main():
    """
    Runner method.
    """
    variable_sets = [['shotsOnGoalFor'], ['mediumDangerShotsFor', 'highDangerShotsFor']]
    save_names = ['Shots On Goal', 'Medium And High Danger Shots']
    save_data(variable_sets, save_names, True)
    save_data(variable_sets, save_names, False)


def save_data(variable_sets, save_names, by_team):
    """
    Saves data in an Excel file about the sets of variables passed in where each set is in a separate sheet. Each sheet
    is organized by team if by_team is True, otherwise it is organized by year.

    :param variable_sets: List of lists containing the variable sets
    :param save_names: List of Strings containing the names of the variable sets (parallel to variable_sets)
    :param by_team: Boolean indicating whether the data within each sheet should be organized by team or by year.
    """
    for i in range(0, len(variable_sets)):
        if by_team:
            writer = pd.ExcelWriter('Produced Totals By Team.xlsx')
            collected_data = collect_var_data_by_team(variable_sets[i])
            df = pd.DataFrame(collected_data, columns=['Team', 'Year', 'Totals'])
        else:
            writer = pd.ExcelWriter('Produced Totals By Year.xlsx')
            collected_data = collect_var_data_by_year(variable_sets[i])
            df = pd.DataFrame(collected_data, columns=['Year', 'Team', 'Totals'])
        df.to_excel(writer, sheet_name=save_names[i])
    writer.save()


def collect_var_data_by_team(variables):
    """
    Returns a list of lists, where the first column contains the team name, the second column contains the year, and
    the third column contains the totals for the variables.

    :param variables: A list containing the variables to be analyzed.
    :return: A list of lists containing the aggregated data.
    """
    collected_data = []

    for team in teams:
        for year in range(2008, 2008 + NUM_SEASON_YEARS):
            print(team + ' ' + str(year))
            total = total_var(team, year, variables)
            collected_data.append([team, year, total])
    return collected_data


def collect_var_data_by_year(variables):
    """
    Returns a list of lists, where the first column contains the year, the second column contains the team name, and
    the third column contains the totals for the variables.

    :param variables: A list containing the variables to be analyzed.
    :return: A list of lists containing the aggregated data.
    """
    collected_data = []
    for year in range(2008, 2008 + NUM_SEASON_YEARS):
        for team in teams:
            print(team + ' ' + str(year))
            total = total_var(team, year, variables)
            collected_data.append([year, team, total])
    return collected_data


def total_var(team, year, variables):
    """
    Returns the total count for the specified variable(s) during the specified year for the specified team.

    :param team: A string of the three-letter team name.
    :param year: An int of the year being analyzed. Must be between 2008 and 2017.
    :param variables: A list of strings with the variables being summed
    :return: An integer sum of the counts for this variable during this season. -1 if invalid variable(s), team, or year
    """

    # Validate input.
    if team not in teams or year < 2008 or year > 2017:
        return -1

    # Handles invalid variable names.
    try:
        df = pd.read_csv(filepath_or_buffer='all_teams.csv', delimiter=',', header=0,
                         usecols=['team', 'season', 'situation', 'playoffGame'].append(variables))

        # Extract all non-playoff games that this team played in during the specified year.
        df = df[
            np.logical_and(np.logical_and(np.logical_and(df.team == team, df.situation == 'all'), df.playoffGame == 0),
                           df.season == year)]
        df = df[variables]

        total = 0
        for var in variables:
            total = total + df[var].sum()
        return total
    except KeyError:
        return -1


if __name__ == "__main__":
    main()
