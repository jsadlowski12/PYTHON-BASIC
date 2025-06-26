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
import time
import requests
from bs4 import BeautifulSoup
import random

USER_AGENTS = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.79 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A',
    'Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5355d Safari/8536.25',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/534.55.3 (KHTML, like Gecko) Version/5.1.3 Safari/534.53.10',
    'Opera/9.80 (X11; Linux i686; Ubuntu/14.10) Presto/2.12.388 Version/12.16',
    'Mozilla/5.0 (Windows NT 6.0; rv:2.0) Gecko/20100101 Firefox/4.0 Opera 12.14',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:77.0) Gecko/20100101 Firefox/77.0',
]

BASE_URL = "https://finance.yahoo.com/markets/stocks/most-active"

class RequestRefusedException(Exception):
    pass

def make_request(url: str) -> BeautifulSoup:
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
        "Connection": "keep-alive"
    }

    try:
        time.sleep(5)
        response = requests.get(url, headers=headers, timeout=15)
        print(f"URL Requested: {response.url}")
        print(f"Status Code: {response.status_code}")
        print(response.text[:500])
        response.raise_for_status()
        return BeautifulSoup(response.content, "html.parser")
    except requests.exceptions.HTTPError as e:
        raise RequestRefusedException(f"HTTP error: {e}")
    except requests.exceptions.RequestException as e:
        raise RequestRefusedException(f"Network error: {e}")


def get_stocks_codes() -> dict:
    soup = make_request(BASE_URL)
    rows = soup.find_all("tr", class_="row yf-ao6als")
    codes = {}

    for row in rows:
        code = row.find("span", class_="symbol yf-hwu3c7")
        company_name = row.find("div", class_="leftAlignHeader companyName yf-362rys enableMaxWidth")
        codes[code.text.rstrip()] = company_name.text.rstrip()

    return codes

def get_data_from_company_profile(codes: dict) -> dict:
    company_data = {
        "Name": [],
        "Code": [],
        "Country": [],
        "Employees": [],
        "CEO Name": [],
        "CEO Age": [],
    }

    for code, name in codes.items():
        soup = make_request(f"https://finance.yahoo.com/quote/{code}/profile")
        print(soup.prettify())
        address = soup.find("div", class_="address yf-wxp4ja")
        print(address.text)
        company_data["Country"].append(address.find_all("div")[-1].text)

    return company_data


def main():
    codes = get_stocks_codes()
    print(codes)
    print(get_data_from_company_profile(codes))

if __name__ == "__main__":
    main()
