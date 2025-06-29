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
    'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
    'Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)',
    'Mozilla/5.0 (compatible; Yahoo! Slurp; http://help.yahoo.com/help/us/ysearch/slurp)'
]

BASE_URL = "https://finance.yahoo.com/markets/stocks/most-active"

class RequestRefusedException(Exception):
    pass

def make_request(url: str) -> BeautifulSoup:
    user_agent = random.choice(USER_AGENTS)
    headers = {
        "User-Agent": user_agent,
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
        "Connection": "keep-alive"
    }
    try:
        time.sleep(2)
        print(f"Using User-Agent: {user_agent}")
        response = requests.get(url, headers=headers, timeout=15)
        print(f"Requested URL: {response.url}")
        print(f"Status code: {response.status_code}")
        response.raise_for_status()
        return BeautifulSoup(response.content, "html.parser")
    except requests.exceptions.HTTPError as e:
        raise RequestRefusedException(f"HTTP error: {e}")
    except requests.exceptions.RequestException as e:
        raise RequestRefusedException(f"Network error: {e}")


def get_stock_codes() -> dict:
    soup = make_request(BASE_URL)
    rows = soup.find_all("tr", class_="row yf-ao6als")
    stock_codes = {}

    for row in rows:
        code = row.find("span", class_="symbol yf-hwu3c7")
        company_name = row.find("div", class_="leftAlignHeader companyName yf-362rys enableMaxWidth")
        stock_codes[code.text.rstrip()] = company_name.text.rstrip()

    return stock_codes

def get_youngest_ceo_from_profile_tab(stock_codes: dict) -> dict:
    company_data = {
        "Name": [],
        "Code": [],
        "Country": [],
        "Employees": [],
        "CEO Name": [],
        "CEO Year Born": [],
    }

    for code, name in stock_codes.items():
        soup = make_request(f"https://finance.yahoo.com/quote/{code}/profile")

        company_data["Name"].append(stock_codes[code])
        company_data["Code"].append(code)

        address = soup.find("div", class_="address yf-wxp4ja")
        company_data["Country"].append(address.find_all("div")[-1].text)

        employees_count = soup.find("dl", class_="company-stats yf-wxp4ja")
        company_data["Employees"].append(
            employees_count.find("strong").text if employees_count and employees_count.find("strong") else "N/A"
        )

        employee_table = soup.find("div", class_="table-container yf-mj92za")
        table_body = employee_table.find("tbody")
        first_row = table_body.find("tr", class_="yf-mj92za")
        print(first_row.text)
        first_row = first_row.find_all("td", class_="yf-mj92za")
        name = first_row[0].text.strip()
        year_text = first_row[-1].text.strip()
        year_born = int(year_text) if year_text.isdigit() else "N/A"

        company_data["CEO Name"].append(name)
        company_data["CEO Year Born"].append(year_born)

    return company_data


def main():
    codes = get_stock_codes()
    print(codes)
    print(get_youngest_ceo_from_profile_tab(codes))

if __name__ == "__main__":
    main()
