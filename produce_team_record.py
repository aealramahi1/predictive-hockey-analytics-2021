import pandas as pd
import numpy as np

NUM_TEAMS = 31
NUM_SEASON_YEARS = 10

teams = ['ANA', 'ARI', 'BOS', 'BUF', 'CAR', 'CBJ', 'CGY', 'CHI', 'COL', 'DAL', 'DET', 'EDM', 'FLA', 'L.A', 'MIN', 'MTL',
         'N.J', 'NSH', 'NYI', 'NYR', 'OTT', 'PHI', 'PIT', 'S.J', 'STL', 'T.B', 'TOR', 'VAN', 'VGK', 'WPG', 'WSH']


def save_all_data(include_overtime=False):
    """
    Extracts information about the wins and losses of each NHL team season-by-season.

    :param include_overtime A boolean indicating whether games that went into overtime (but not shootout) should be
    included.
    """

    # Extract relevant columns from the all_teams.csv file (which must be in the same folder as this script).
    df = pd.read_csv(filepath_or_buffer='all_teams.csv', delimiter=',', header=0,
                     usecols=['team', 'season', 'situation',
                              'iceTime', 'goalsFor',
                              'goalsAgainst', 'playoffGame'])

    # Extract rows of games if the situation is 'all'.
    if include_overtime:
        df = df[np.logical_and(np.logical_and(df.situation == 'all', df.iceTime < 3900), df.playoffGame == 0)]
    else:
        df = df[np.logical_and(np.logical_and(df.situation == 'all', df.iceTime == 3600), df.playoffGame == 0)]

    # Create a list of lists with the collected data that we will write to an Excel spreadsheet at the end.
    collected_data = []

    # Generate the record for each team for the number of seasons specified since 2017.
    for team in teams:
        for year in range(2008, 2008 + NUM_SEASON_YEARS):
            total_games = df.loc[np.logical_and(df.team == team, df.season == year)].shape[0]
            wins = df.loc[np.logical_and(np.logical_and(df.team == team, df.season == year),
                                         df.goalsFor > df.goalsAgainst)].shape[0]
            losses = total_games - wins

            # Some teams did not play in all seasons.
            if total_games > 0:
                win_percentage = wins / total_games
                collected_data.append([team, year, wins, losses, win_percentage])

    # Put data into a data frame and save to an Excel file.
    df = pd.DataFrame(collected_data,
                      columns=['Team', 'Season', 'Number of Wins', 'Number of Losses', 'Season Win Percentage'])
    df.to_csv('team_records.csv', encoding='utf-8')


def produce_team_record(team, include_overtime=False):
    """
    Extracts information about the wins and losses of the specified team season-by-season.

    :param team: The team of interest.
    :param include_overtime A boolean indicating whether games that went into overtime (but not shootout) should be
    included.
    :return: A list of lists containing wins, losses, and win percentage for the specified team.
    """

    # Extract relevant columns from the all_teams.csv file (which must be in the same folder as this script).
    df = pd.read_csv(filepath_or_buffer='all_teams.csv', delimiter=',', header=0,
                     usecols=['team', 'season', 'situation',
                              'iceTime', 'goalsFor',
                              'goalsAgainst', 'playoffGame'])

    # Extract rows of games that didn't go into overtime if the situation is 'all'.
    if include_overtime:
        df = df[np.logical_and(np.logical_and(df.situation == 'all', df.iceTime < 3900), df.playoffGame == 0)]
    else:
        df = df[np.logical_and(np.logical_and(df.situation == 'all', df.iceTime == 3600), df.playoffGame == 0)]
    df = df[df.team == team]

    # Create a list of lists with the collected data that we will return.
    collected_data = []

    for year in range(2008, 2008 + NUM_SEASON_YEARS):
        total_games = df.loc[df.season == year].shape[0]
        wins = df.loc[np.logical_and(df.season == year, df.goalsFor > df.goalsAgainst)].shape[0]
        losses = total_games - wins

        # Some teams did not play in all seasons.
        if total_games > 0:
            win_percentage = wins / total_games
            collected_data.append([wins, losses, win_percentage])
        else:
            collected_data.append([])

    return collected_data


def produce_all_team_records_by_year(year, include_overtime=False):
    """
    Extracts information about the wins and losses of each individual team (in alphabetical order) season-by-season.

    :param year: The year of interest.
    :param include_overtime A boolean indicating whether games that went into overtime (but not shootout) should be
    included.
    :return: A list of lists containing wins, losses, and win percentage for each team during the specified year.
    """

    # Extract relevant columns from the all_teams.csv file (which must be in the same folder as this script).
    df = pd.read_csv(filepath_or_buffer='all_teams.csv', delimiter=',', header=0,
                     usecols=['team', 'season', 'situation',
                              'iceTime', 'goalsFor',
                              'goalsAgainst', 'playoffGame'])

    # Extract rows of games if the situation is 'all'.
    if include_overtime:
        df = df[np.logical_and(np.logical_and(df.situation == 'all', df.iceTime < 3900), df.playoffGame == 0)]
    else:
        df = df[np.logical_and(np.logical_and(df.situation == 'all', df.iceTime == 3600), df.playoffGame == 0)]
    df = df[df.season == year]

    # Create a list of lists with the collected data that we will return.
    collected_data = []

    for team in teams:
        total_games = df.loc[df.team == team].shape[0]
        wins = df.loc[np.logical_and(df.team == team, df.goalsFor > df.goalsAgainst)].shape[0]
        losses = total_games - wins

        # Some teams did not play in all seasons.
        if total_games > 0:
            win_percentage = wins / total_games
            collected_data.append([wins, losses, win_percentage])
        else:
            collected_data.append([])

    return collected_data


def produce_num_of_wins(team, year, include_overtime=False):
    """
    Return the number of wins for the specified team in the specified season.

    :param team: The three-letter name of the team.
    :param year: The season year to be analyzed for this team.
    :param include_overtime A boolean indicating whether games that went into overtime (but not shootout) should be
    included.
    :return: The number of wins for this team in this season.
    """

    # Extract relevant columns from the all_teams.csv file (which must be in the same folder as this script).
    df = pd.read_csv(filepath_or_buffer='all_teams.csv', delimiter=',', header=0,
                     usecols=['team', 'season', 'situation', 'iceTime', 'goalsFor', 'goalsAgainst', 'playoffGame'])

    # Extract rows of games if the situation is 'all'.
    if include_overtime:
        df = df[np.logical_and(np.logical_and(df.situation == 'all', df.iceTime < 3900), df.playoffGame == 0)]
    else:
        df = df[np.logical_and(np.logical_and(df.situation == 'all', df.iceTime == 3600), df.playoffGame == 0)]
    df = df[df.team == team]
    return df.loc[np.logical_and(df.season == year, df.goalsFor > df.goalsAgainst)].shape[0]


if __name__ == "__main__":
    save_all_data(True)
