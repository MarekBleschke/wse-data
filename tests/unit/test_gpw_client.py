import httpx
import pytest
from httpx._content import encode_urlencoded_data

from src.data_scrappers.gpw.gpw_client import GPWClient, MarketEnum
from tests.data import gpw_responses


@pytest.fixture
def gpw_client():
    return GPWClient(market=MarketEnum.GPW)


@pytest.fixture
def new_connect_client():
    return GPWClient(market=MarketEnum.NEW_CONNECT)


def test_companies_list_returns_only_gpw_companies(gpw_client, new_connect_client, respx_mock):
    # given
    respx_mock.post(gpw_client.config.companies_url).side_effect = [
        httpx.Response(200, content=b"response"),
        httpx.Response(200, content=b""),
    ]
    respx_mock.post(new_connect_client.config.companies_url).side_effect = [
        httpx.Response(200, content=b"response"),
        httpx.Response(200, content=b""),
    ]

    # when
    list(gpw_client.companies_list())
    called_urls = [str(call.request.url) for call in respx_mock.calls]

    # then
    assert gpw_client.config.companies_url in called_urls
    assert new_connect_client.config.companies_url not in called_urls


def test_companies_list_returns_only_new_connect_companies(gpw_client, new_connect_client, respx_mock):
    # given
    respx_mock.post(gpw_client.config.companies_url).side_effect = [
        httpx.Response(200, content=b"response"),
        httpx.Response(200, content=b""),
    ]
    respx_mock.post(new_connect_client.config.companies_url).side_effect = [
        httpx.Response(200, content=b"response"),
        httpx.Response(200, content=b""),
    ]

    # when
    list(new_connect_client.companies_list())
    called_urls = [str(call.request.url) for call in respx_mock.calls]

    # then
    assert new_connect_client.config.companies_url in called_urls
    assert gpw_client.config.companies_url not in called_urls


def test_companies_list_paging_parameters_for_first_page(gpw_client, respx_mock):
    # given
    respx_mock.post(gpw_client.config.companies_url).mock(return_value=httpx.Response(200, content=b"<tr>response"))
    companies_list_generator = gpw_client.companies_list()

    # when
    next(companies_list_generator)

    # then
    assert b"limit=50" in respx_mock.calls.last.request.content
    assert b"offset=0" in respx_mock.calls.last.request.content


def test_companies_list_paging_parameters_for_second_page(gpw_client, respx_mock):
    # given
    respx_mock.post(gpw_client.config.companies_url).mock(
        return_value=httpx.Response(200, content=b"<tr>response" * 50)
    )

    companies_list_generator = gpw_client.companies_list()

    # when
    next(companies_list_generator)
    next(companies_list_generator)

    # then
    assert b"limit=50" in respx_mock.calls.last.request.content
    assert b"offset=50" in respx_mock.calls.last.request.content


def test_companies_list_static_params_are_in_request(gpw_client, respx_mock):
    # given
    respx_mock.post(gpw_client.config.companies_url).mock(return_value=httpx.Response(200, content=b"<tr>response"))
    companies_list_generator = gpw_client.companies_list()
    encoded_params = encode_urlencoded_data(gpw_client.config.companies_query_params)[1].read()

    # when
    next(companies_list_generator)

    # then
    assert encoded_params in respx_mock.calls.last.request.content


def test_companies_list_breaks_loop_when_empty_response(gpw_client, respx_mock):
    # given
    respx_mock.post(gpw_client.config.companies_url).mock(
        return_value=httpx.Response(200, content=gpw_responses.COMPANIES_LIST_EMPTY_PAGE)
    )
    companies_list_generator = gpw_client.companies_list()

    # then
    with pytest.raises(StopIteration):
        next(companies_list_generator)


def test_reports_list_makes_request_to_proper_url(gpw_client, respx_mock):
    # given
    respx_mock.post(gpw_client.config.reports_url).side_effect = [
        httpx.Response(200, content=b"response"),
        httpx.Response(200, content=b""),
    ]

    # when
    list(gpw_client.reports_list())
    called_urls = [str(call.request.url) for call in respx_mock.calls]

    # then
    assert gpw_client.config.reports_url in called_urls


def test_reports_list_returns_only_gpw_reports(respx_mock, new_connect_client, gpw_client):
    # given
    respx_mock.post(gpw_client.config.reports_url).side_effect = [
        httpx.Response(200, content=b"response"),
        httpx.Response(200, content=b""),
    ]
    respx_mock.post(new_connect_client.config.reports_url).side_effect = [
        httpx.Response(200, content=b"response"),
        httpx.Response(200, content=b""),
    ]

    # when
    list(gpw_client.reports_list())
    called_urls = [str(call.request.url) for call in respx_mock.calls]

    # then
    assert gpw_client.config.reports_url in called_urls
    assert new_connect_client.config.reports_url not in called_urls


def test_reports_list_returns_only_new_connect_reports(respx_mock, new_connect_client, gpw_client):
    # given
    respx_mock.post(gpw_client.config.reports_url).side_effect = [
        httpx.Response(200, content=b"response"),
        httpx.Response(200, content=b""),
    ]
    respx_mock.post(new_connect_client.config.reports_url).side_effect = [
        httpx.Response(200, content=b"response"),
        httpx.Response(200, content=b""),
    ]

    # when
    list(new_connect_client.reports_list())
    called_urls = [str(call.request.url) for call in respx_mock.calls]

    # then
    assert new_connect_client.config.reports_url in called_urls
    assert gpw_client.config.reports_url not in called_urls


def test_reports_list_paging_parameters_for_first_page(gpw_client, respx_mock):
    # given
    respx_mock.post(gpw_client.config.reports_url).mock(return_value=httpx.Response(200, content=b"<li>response"))
    reports_list_generator = gpw_client.reports_list()

    # when
    next(reports_list_generator)

    # then
    assert b"limit=20" in respx_mock.calls.last.request.content
    assert b"offset=0" in respx_mock.calls.last.request.content


def test_reports_list_paging_parameters_for_second_page(respx_mock, gpw_client):
    # given
    respx_mock.post(gpw_client.config.reports_url).mock(return_value=httpx.Response(200, content=b"<li>response" * 20))
    reports_list_generator = gpw_client.reports_list()

    # when
    next(reports_list_generator)
    next(reports_list_generator)

    # then
    assert b"limit=20" in respx_mock.calls.last.request.content
    assert b"offset=20" in respx_mock.calls.last.request.content


def test_reports_list_static_params_are_in_request(respx_mock, gpw_client):
    # given
    respx_mock.post(gpw_client.config.reports_url).mock(return_value=httpx.Response(200, content=b"<li>response"))
    reports_list_generator = gpw_client.reports_list()
    encoded_params = encode_urlencoded_data(gpw_client.config.reports_query_params)[1].read()

    # when
    next(reports_list_generator)

    # then
    assert encoded_params in respx_mock.calls.last.request.content


def test_reports_list_breaks_loop_when_empty_response(respx_mock, gpw_client):
    # given
    respx_mock.post(gpw_client.config.reports_url).mock(
        return_value=httpx.Response(200, content=gpw_responses.REPORTS_EMPTY_PAGE)
    )
    reports_list_generator = gpw_client.reports_list()

    # then
    with pytest.raises(StopIteration):
        next(reports_list_generator)
