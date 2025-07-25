from task_3 import is_http_domain
import pytest

def test_is_http_domain_http():
    result = is_http_domain('http://wikipedia.org')
    assert result == True

def test_is_http_domain_https():
    result = is_http_domain('https://ru.wikipedia.org/')
    assert result == True

def test_is_http_domain_wrong_domain():
    result = is_http_domain('griddynamics.com')
    assert result == False