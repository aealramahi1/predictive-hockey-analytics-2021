import pandas as pd
import numpy as np

NUM_TEAMS = 31
NUM_SEASON_YEARS = 10

teams = ['all_teams', 'ANA', 'ARI', 'BOS', 'BUF', 'CAR', 'CBJ', 'CGY', 'CHI', 'COL', 'DAL', 'DET', 'EDM', 'FLA', 'L.A',
         'MIN', 'MTL', 'N.J', 'NSH', 'NYI', 'NYR', 'OTT', 'PHI', 'PIT', 'S.J', 'STL', 'T.B', 'TOR', 'VAN', 'VGK', 'WPG',
         'WSH']


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
    pass
