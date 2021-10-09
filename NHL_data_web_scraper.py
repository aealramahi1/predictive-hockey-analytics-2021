from bs4 import BeautifulSoup
from urllib.request import urlopen
import pandas as pd
import re


def main():
    """
    Creates a CSV file named penalties_YYYY.csv containing all the penalty information from hockey-reference.com games
    in the year (YYYY) specified by the user.
    """
    year = 0
    valid_year = False

    while not valid_year:
        try:
            year = int(input('Please enter the year to analyze the penalties: '))

            if 1917 > year > 2021:
                raise ValueError
            valid_year = True
        except ValueError:
            print('Please enter a number between 1917 and 2021.')

    df = extract_season_penalties('https://www.hockey-reference.com/leagues/NHL_' + str(year) + '_games.html')
    df.to_csv('penalties_' + str(year) + '.csv', encoding='utf-8')


def extract_season_penalties(url):
    """
    Extract all the penalties from this season and return it as a pandas dataframe.

    :param url: The hockey-reference URL containing all the games for the season of interest.
    :return: Return all the penalties from this season as a pandas dataframe.
    """

    # Open up the website with all the hockey games of interest (listed under "Date" column).
    html = urlopen(url).read().decode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')

    # Include regular season games and playoffs.
    all_games = soup.find('table', id='games').select('a[href*=boxscores]')
    all_games.extend(soup.find('table', id='games_playoffs').select('a[href*=boxscores]'))

    # Extract the penalty data for each game and save it in a list
    all_penalties = []
    for link in all_games:
        all_penalties.extend(
            extract_game_penalties('https://www.hockey-reference.com' + link.get('href'), link.get_text()))

    return pd.DataFrame(all_penalties, columns=['Date', 'Period', 'Time', 'Team', 'Player', 'Summary', 'Duration'])


def extract_game_penalties(url, date):
    """
    Extracts the penalty table from box scores pages on www.hockey-reference.com.

    :param url: The URL of the page containing the penalties table.
    :param date: A String representing the date that the game occurred on in the form YYYY-MM-DD
    :return: A list of lists containing the penalties for that game and which period they occurred in.
    """

    # Extract the HTML from the page and create a BeautifulSoup objects.
    html = urlopen(url).read().decode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')

    # Get all the rows in the penalty tables (<tr> elements).
    penalty_rows = soup.find('table', id='penalty').find_all('tr', recursive=False)
    penalty_data = []

    # Extract the current period from the first row of the table. Make sure there are penalties first.
    if penalty_rows:
        period = int(re.search(r'\d|', penalty_rows[0].get_text()).group())

        # Skip the first row since we already used it to find the column.
        for row in penalty_rows[1:]:

            # If this row does not contain the game period, it contains data which we need to aggregate.
            if row.get('class') is None:

                # Add the contents of this row to a list that we will put inside of penalty data.
                row_data = [date, period]
                data = row.find_all('td', recursive=False)

                for d in data:
                    row_data.append(d.get_text())

                penalty_data.append(row_data)

            # This is the case for the row containing the game period.
            elif isinstance(row.get('class'), list) and row.get('class')[0] == 'thead' or row.get('class')[0] == 'onecell':

                # Change the period of the game.
                period = int(re.search(r'\d|', row.get_text()).group())

                # If this is an overtime period, add three to it (i.e., first overtime period is represented as the 4th period).
                if 'OT' in row.get_text():
                    period += 3
    return penalty_data


if __name__ == "__main__":
    main()
