import pandas as pd

import produce_team_record
import single_var_hypothesis_tests as hyp_tests

NUM_TEAMS = 31
NUM_SEASON_YEARS = 10

teams = ['all_teams', 'ANA', 'ARI', 'BOS', 'BUF', 'CAR', 'CBJ', 'CGY', 'CHI', 'COL', 'DAL', 'DET', 'EDM', 'FLA', 'L.A',
         'MIN', 'MTL', 'N.J', 'NSH', 'NYI', 'NYR', 'OTT', 'PHI', 'PIT', 'S.J', 'STL', 'T.B', 'TOR', 'VAN', 'VGK', 'WPG',
         'WSH']


def main():
    """
    Performs hypothesis tests in single_var_hypothesis_tests.py for each team during each season. The Excel file
    contains sheets with each of the team names and has the following columns within each sheet: Year, Wins, Losses,
    Win Percentage, n-value, p-value.
    """

    # Open up the Excel file and create a writer for the new data we are producing.
    xls = pd.ExcelFile('Hypothesis Tests.xlsx')
    writer = pd.ExcelWriter('Produced Hypothesis Tests UPDATED.xlsx')

    # Produce the data for each sheet.
    for team in teams:
        sheet = pd.read_excel(xls, team, header=2)

        # List of lists that we will place into the sheet.
        n_values = []
        p_values = []

        # Define a dictionary containing all of the hypothesis tests.
        tests = {
            1: lambda filepath, season: hyp_tests.single_col_for_and_against(filepath, season, 'shotsOnGoal'),
            2: lambda filepath, season: hyp_tests.single_col_for_and_against(filepath, season, 'highDangerShots'),
            3: lambda filepath, season: hyp_tests.single_col_for_and_against(filepath, season, 'mediumDangerShots'),
            4: lambda filepath, season: hyp_tests.single_col_for_and_against(filepath, season, 'lowDangerShots'),
            5: lambda filepath, season: hyp_tests.high_and_med_danger(filepath, season),
            6: lambda filepath, season: hyp_tests.high_and_low_danger(filepath, season),
            7: lambda filepath, season: hyp_tests.low_danger_and_rebounds_sum(filepath, season),
            8: lambda filepath, season: hyp_tests.rebounds_and_low_danger_shots_ratio(filepath, season),
            9: lambda filepath, season: hyp_tests.time_on_power_play(filepath, season),
            10: lambda filepath, season: hyp_tests.medium_and_high_danger_and_rebounds_sum(filepath, season),
            11: lambda filepath, season: hyp_tests.rebounds_and_medium_and_high_danger_shots_ratio(filepath, season),
            12: lambda filepath, season: hyp_tests.single_col_for_and_against(filepath, season, 'takeaways'),
            13: lambda filepath, season: hyp_tests.single_col_for_and_against(filepath, season, 'penalityMinutes'),
            14: lambda filepath, season: hyp_tests.single_col_for_and_against(filepath, season, 'penalties'),
            15: lambda filepath, season: hyp_tests.playoff_shots_on_goal(filepath, season),
            16: lambda filepath, season: hyp_tests.single_col_for_and_against(filepath, season, 'rebounds')
        }

        # Run each hypothesis test for every season year.
        for i in range(1, hyp_tests.TOTAL_OPTIONS):
            f = tests.get(i)

            for year in range(2008, 2008 + NUM_SEASON_YEARS):
                print(team + ' ' + str(year) + ' ' + str(i))
                results = f(team + '.csv', year)

                # Get the n and p values to put into the spreadsheet.
                if results.shape[0] != 0:

                    if team == 'all_teams':
                        n = results.size / 2
                        p = float(results.sum()) / n
                    else:
                        n = results.size
                        p = float(results.sum()) / produce_team_record.produce_num_of_wins(team, year)
                else:
                    n = 0
                    p = 0

                n_values.append(n)
                p_values.append(p)

            # Account for an empty row between each hypothesis test.
            n_values.append([])
            p_values.append([])

        # Produce the team record and add it to the sheet.
        if team != 'all_teams':
            team_record = produce_team_record.produce_team_record(team)
            team_record.append([])
            team_record = team_record * hyp_tests.TOTAL_OPTIONS
            tr = pd.DataFrame(team_record, columns=['Wins', 'Losses', 'Win Percentage'])

            sheet['Wins'] = tr['Wins']
            sheet['Losses'] = tr['Losses']
            sheet['Win Percentage'] = tr['Win Percentage']

        # Add the produced n and p values to the sheet.
        sheet['n-value'] = pd.Series(n_values)
        sheet['p-value'] = pd.Series(p_values)
        sheet.to_excel(writer, sheet_name=team)

    writer.save()


if __name__ == "__main__":
    main()
