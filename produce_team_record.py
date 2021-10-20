import pandas as pd
import numpy as np

NUM_TEAMS = 31
NUM_SEASON_YEARS = 12

teams = ['ANA', 'ARI', 'BOS', 'BUF', 'CAR', 'CBJ', 'CGY', 'CHI', 'COL', 'DAL', 'DET', 'EDM', 'FLA', 'L.A', 'MIN', 'MTL',
         'N.J', 'NSH', 'NYI', 'NYR', 'OTT', 'PHI', 'PIT', 'S.J', 'STL', 'T.B', 'TOR', 'VAN', 'VGK', 'WPG', 'WSH']


def main():
    """
    Extracts information about the wins and losses of each NHL team season-by-season.
    """

    # Extract relevant columns from the all_teams.csv file (which must be in the same folder as this script).
    df = pd.read_csv(filepath_or_buffer='all_teams.csv', delimiter=',', header=0, usecols=['team', 'season', 'situation',
                                                                                           'iceTime', 'goalsFor',
                                                                                           'goalsAgainst'])

    # Extract rows of games that didn't go into overtime if the situation is 'all'.
    df = df[np.logical_and(df.situation == 'all', df.iceTime == 3600)]

    # Create a list of lists with the collected data that we will write to an Excel spreadsheet at the end.
    collected_data = []

    # Generate the record for each team for the number of seasons specified since 2017.
    for team in teams:
        for year in range(2008, 2008 + NUM_SEASON_YEARS):
            total_games = df.loc[np.logical_and(df.team == team, df.season == year)].shape[0]
            wins = df.loc[np.logical_and(np.logical_and(df.team == team, df.season == year), df.goalsFor > df.goalsAgainst)].shape[0]
            losses = total_games - wins

            print(str(team) + ' ' + str(year))
            # print(df.loc[np.logical_and(df.team == team, df.season == year)])

            # Some teams did not play in all seasons.
            if total_games > 0:
                win_percentage = wins / total_games
                collected_data.append([team, year, wins, losses, win_percentage])

    # Put data into a data frame and save to an Excel file.
    df = pd.DataFrame(collected_data, columns=['Team', 'Season', 'Number of Wins', 'Number of Losses', 'Season Win Percentage'])
    df.to_csv('team_records.csv', encoding='utf-8')


if __name__ == "__main__":
    main()