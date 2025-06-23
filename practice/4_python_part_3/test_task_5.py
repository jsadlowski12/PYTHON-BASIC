from unittest.mock import patch, Mock
from urllib import error
from task_5 import make_request

@patch('task_5.request.urlopen')
def test_successful_request(mock_urlopen):
    mock_resp = Mock()
    mock_resp.code = 200
    mock_resp.read.return_value = b'Hello World'
    mock_resp.headers.get_content_charset.return_value = 'utf-8'
    mock_urlopen.return_value = mock_resp

    status, content = make_request('http://fakeurl.com')

    assert status == 200
    assert content == 'Hello World'

@patch('task_5.request.urlopen')
def test_http_error(mock_urlopen):
    http_err = error.HTTPError(
        url='http://fakeurl.com',
        code=404,
        msg='Not Found',
        hdrs=None,
        fp=Mock()
    )
    http_err.read = lambda: b'Error page content'
    mock_urlopen.side_effect = http_err

    status, content = make_request('http://fakeurl.com')

    assert status == 404
    assert content == 'Error page content'

@patch('task_5.request.urlopen')
def test_url_error(mock_urlopen):
    mock_request = Mock()
    mock_request.errno = 1
    mock_request.strerror = 'No route to host'

    url_err = error.URLError(mock_request)
    mock_urlopen.side_effect = url_err

    status, content = make_request('http://fakeurl.com')

    assert status == 1
    assert content == 'No route to host'