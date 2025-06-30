from bs4 import BeautifulSoup
import pytest
import importlib

res = importlib.import_module('practice.6_web_scraping.stock_info')

STOCK_CODES = {"ABC": "ABC Corp", "XYZ": "XYZ Ltd"}

@pytest.mark.parametrize(
    "raw, expected",
    [
        ("25.30%", 25.30),
        ("-3.5%", -3.5),
        ("1,234.56%", 1234.56),
        ("N/A", float("-inf")),
        (None, float("-inf")),
    ],
)
def test_parse_percent(raw, expected):
    assert res.parse_percent(raw) == expected


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("$12.5B", 12_500_000_000),
        ("$965.4M", 965_400_000),
        ("$37.2K", 37_200),
        ("12345", 12345.0),
        ("N/A", float("-inf")),
    ],
)
def test_parse_value(raw, expected):
    assert res.parse_value(raw) == expected


def test_generate_sheet_basic():
    sheet = res.generate_sheet(
        "Dummy Sheet",
        ["Col1", "Col2"],
        [("a", "b"), ("longer", "row2")],
    )
    lines = sheet.splitlines()
    assert lines[0].startswith("=") and lines[0].endswith("=")
    assert "| Col1 " in lines[1] and "| Col2 " in lines[1]
    assert lines[-1] == ""


MOST_ACTIVE_HTML = """
<table>
  <tr class="row yf-ao6als">
    <td><span class="symbol yf-hwu3c7">ABC</span></td>
    <td><div class="leftAlignHeader companyName yf-362rys enableMaxWidth">ABC Corp</div></td>
  </tr>
  <tr class="row yf-ao6als">
    <td><span class="symbol yf-hwu3c7">XYZ</span></td>
    <td><div class="leftAlignHeader companyName yf-362rys enableMaxWidth">XYZ Ltd</div></td>
  </tr>
</table>
"""

PROFILE_ABC = """
<div>
  <div class="address yf-wxp4ja"><div>Street</div><div>United States</div></div>
  <dl class="company-stats yf-wxp4ja"><strong>10000</strong></dl>
  <div class="table-container yf-mj92za">
    <table><tbody>
      <tr class="yf-mj92za">
        <td class="yf-mj92za">John Doe</td>
        <td class="yf-mj92za">CEO</td>
        <td class="yf-mj92za">1985</td>
      </tr>
    </tbody></table>
  </div>
</div>
"""

PROFILE_XYZ = PROFILE_ABC.replace("United States", "Canada").replace("10000", "5000")\
                          .replace("John Doe", "Jane Smith").replace("1985", "1990")

STATS_ABC = """
<section class="yf-14j5zka">
  <!-- first (financial) section with 2 tables -->
  <table class="table yf-vaowmx"></table>
  <table class="table yf-vaowmx">
    <tbody>
      <tr class="row yf-vaowmx"><td>Total Cash</td><td>$12.5B</td></tr>
    </tbody>
  </table>
</section>
<section class="yf-14j5zka">
  <!-- second (trading) section -->
  <table class="table yf-vaowmx">
    <tbody>
      <tr class="row yf-vaowmx"><td>dummy</td><td>n/a</td></tr>
      <tr class="row yf-vaowmx"><td>52 Week Change</td><td>30.5%</td></tr>
    </tbody>
  </table>
</section>
"""

STATS_XYZ = STATS_ABC.replace("$12.5B", "$8.0B").replace("30.5%", "10%")

HOLDERS_ABC = """
<section data-testid="holders-top-institutional-holders">
  <table class="yf-idy1mk"><tbody>
    <tr class="yf-idy1mk"><td>Blackrock Inc.</td><td>50,000,000</td><td>2024‑12‑31</td><td>5.0%</td><td>$15.0B</td></tr>
    <tr class="yf-idy1mk"><td>Someone Else</td><td>1</td><td>2024‑12‑31</td><td>0.01%</td><td>$1.0M</td></tr>
  </tbody></table>
</section>
"""

HOLDERS_XYZ = HOLDERS_ABC.replace("50,000,000", "30,000,000")\
                         .replace("$15.0B", "$9.0B").replace("5.0%", "3.0%")

def fake_make_request(url: str):
    if "most-active" in url:
        return BeautifulSoup(MOST_ACTIVE_HTML, "html.parser")
    if "/profile" in url:
        code = url.split("/quote/")[1].split("/")[0]
        html = PROFILE_ABC if code == "ABC" else PROFILE_XYZ
        return BeautifulSoup(html, "html.parser")
    if "/key-statistics" in url:
        code = url.split("/quote/")[1].split("/")[0]
        html = STATS_ABC if code == "ABC" else STATS_XYZ
        return BeautifulSoup(html, "html.parser")
    if "/holders" in url:
        code = url.split("/quote/")[1].split("/")[0]
        html = HOLDERS_ABC if code == "ABC" else HOLDERS_XYZ
        return BeautifulSoup(html, "html.parser")
    raise ValueError(f"unhandled URL {url!r}")

@pytest.fixture
def patch_requests(monkeypatch):
    monkeypatch.setattr(res, "make_request", fake_make_request)
    return monkeypatch

def test_get_stock_codes(patch_requests):
    codes = res.get_stock_codes()
    assert codes == {"ABC": "ABC Corp", "XYZ": "XYZ Ltd"}


def test_get_youngest_ceos_from_profile_tab(patch_requests):
    result = res.get_youngest_ceos_from_profile_tab(STOCK_CODES)

    assert result["Name"] == ["XYZ Ltd", "ABC Corp"]
    assert result["CEO Year Born"] == [1990, 1985]
    assert result["Employees"] == ["5000", "10000"]


def test_get_stocks_with_best_statistics(patch_requests):
    stats = res.get_stocks_with_best_statistics(STOCK_CODES)

    assert stats["Code"] == ["ABC", "XYZ"]
    assert stats["52 Week Change"][0] == "30.5%"
    assert stats["Total Cash"][0] == "$12.5B"


def test_get_largest_blackrock_holds(patch_requests):
    holds = res.get_largest_blackrock_holds(STOCK_CODES)

    assert holds["Code"] == ["ABC", "XYZ"]
    assert holds["Shares"][0] == "50,000,000"
    assert holds["Value"][1] == "$9.0B"

def test_make_request_error(monkeypatch):

    class DummyResp:
        status_code = 404
        url = "http://example.com"
        def raise_for_status(self):
            import requests
            raise requests.exceptions.HTTPError("404 not found")

    monkeypatch.setattr("requests.get", lambda *a, **kw: DummyResp())

    with pytest.raises(res.RequestRefusedException):
        res.make_request("http://example.com/bad")
