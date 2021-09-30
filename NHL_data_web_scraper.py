from bs4 import BeautifulSoup
from urllib.request import urlopen
import re


def main():
    # Extract the HTML from the page and create a BeautifulSoup objects.
    html = urlopen('https://www.hockey-reference.com/boxscores/201310010CHI.html').read().decode('utf-8')
    soup = BeautifulSoup(html, "html.parser")

    # Get all the rows in the penalty tables (<tr> elements).
    penalty_rows = soup.find('table', id='penalty').find_all('tr', recursive=False)
    penalty_data = []

    # Extract the current period from the first row of the table.
    period = int(re.search(r'\d|', penalty_rows[0].get_text()).group())

    # Skip the first row since we already used it to find the column.
    for row in penalty_rows[1:]:

        # If this row does not contain the game period, it contains data which we need to aggregate.
        if row.get('class') is None:

            # Add the contents of this row to a list that we will put inside of penalty data.
            row_data = [period]
            data = row.find_all('td', recursive=False)

            for d in data:
                row_data.append(d.get_text())

            penalty_data.append(row_data)

        # This is the case for the row containing the game period.
        elif isinstance(row.get('class'), list) and row.get('class')[0] == 'thead' or row.get('class')[0] == 'onecell':

            # Change the period of the game.
            period = int(re.search(r'\d|', row.get_text()).group())

if __name__ == "__main__":
    main()