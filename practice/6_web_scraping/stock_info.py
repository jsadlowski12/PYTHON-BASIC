"""
There is a list of most active Stocks on Yahoo Finance https://finance.yahoo.com/most-active.
You need to compose several sheets based on data about companies from this list.
To fetch data from webpage you can use requests lib. To parse html you can use beautiful soup lib or lxml.
Sheets which are needed:
1. 5 stocks with most youngest CEOs and print sheet to output. You can find CEO info in Profile tab of concrete stock.
    Sheet's fields: Name, Code, Country, Employees, CEO Name, CEO Year Born.
2. 10 stocks with best 52-Week Change. 52-Week Change placed on Statistics tab.
    Sheet's fields: Name, Code, 52-Week Change, Total Cash
3. 10 largest holds of Blackrock Inc. You can find related info on the Holders tab.
    Blackrock Inc is an investment management corporation.
    Sheet's fields: Name, Code, Shares, Date Reported, % Out, Value.
    All fields except first two should be taken from Holders tab.


Example for the first sheet (you need to use same sheet format):
==================================== 5 stocks with most youngest CEOs ===================================
| Name        | Code | Country       | Employees | CEO Name                             | CEO Year Born |
---------------------------------------------------------------------------------------------------------
| Pfizer Inc. | PFE  | United States | 78500     | Dr. Albert Bourla D.V.M., DVM, Ph.D. | 1962          |
...

About sheet format:
- sheet title should be aligned to center
- all columns should be aligned to the left
- empty line after sheet

Write at least 2 tests on your choose.
Links:
    - requests docs: https://docs.python-requests.org/en/latest/
    - beautiful soup docs: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
    - lxml docs: https://lxml.de/
"""

import requests
from bs4 import BeautifulSoup

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
URL = "https://finance.yahoo.com/most-active"

class RequestRefusedException(Exception):
    pass

def make_request(url: str):
    page = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=15)
    if page.status_code == 200:
        return BeautifulSoup(page.content, "html.parser")
    else:
        raise RequestRefusedException("Request was refused.")

def get_stocks_codes() -> dict:
    soup = make_request(URL)
    rows = soup.find_all("tr", class_="row yf-1570k0a")
    codes = {}

    for row in rows:
        code = row.find("span", class_="symbol yf-1jsynna")
        company_name = row.find("div", class_="leftAlignHeader companyName yf-362rys enableMaxWidth")
        codes[code.text.rstrip()] = company_name.text.rstrip()

    return codes

def main():
    print(get_stocks_codes())

if __name__ == "__main__":
    main()
