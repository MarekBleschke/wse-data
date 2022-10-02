from datetime import datetime, date

import httpx
import pytest

from src.data_scrappers.gpw.failed_parsing_element_model import (
    FailedParsingElementModel,
)
from src.data_scrappers.gpw.report_model import ReportModel, ReportCategory, ReportType
from tests.data.gpw_responses import (
    GPW_COMPANIES_LIST_PAGE,
    COMPANIES_LIST_EMPTY_PAGE,
    GPW_COMPANIES_LIST_PAGE_MALFORMED,
    REPORTS_PAGE,
    REPORTS_EMPTY_PAGE,
    REPORTS_PAGE_MALFORMED,
    NEW_CONNECT_COMPANIES_LIST_PAGE,
    NEW_CONNECT_COMPANIES_LIST_PAGE_MALFORMED,
)
from src.data_scrappers.gpw.company_model import CompanyModel, MarketEnum
from src.wse import WSE, DateRangeException


@pytest.fixture
def wse():
    return WSE()


def test_get_companies_returns_proper_number_of_companies(wse, respx_mock):
    # given
    respx_mock.post(wse._gpw_client.config.companies_requests[0][0]).mock(
        return_value=httpx.Response(200, content=GPW_COMPANIES_LIST_PAGE)
    )
    respx_mock.post(wse._new_connect_client.config.companies_requests[0][0]).mock(
        return_value=httpx.Response(200, content=NEW_CONNECT_COMPANIES_LIST_PAGE)
    )

    # when
    companies = list(wse.get_companies())

    # then
    assert len(companies) == 80


def test_get_companies_returns_model_object(wse, respx_mock):
    # given
    respx_mock.post(wse._gpw_client.config.companies_requests[0][0]).mock(
        return_value=httpx.Response(200, content=GPW_COMPANIES_LIST_PAGE)
    )
    respx_mock.post(wse._new_connect_client.config.companies_requests[0][0]).mock(
        return_value=httpx.Response(200, content=COMPANIES_LIST_EMPTY_PAGE)
    )

    # when
    company = next(wse.get_companies())

    # then
    assert company == CompanyModel(
        isin="PLNFI0600010",
        name="06MAGNA",
        ticker="06N",
        market=MarketEnum.GPW,
    )


def test_get_companies_continues_after_known_parsing_exception(wse, respx_mock):
    # given
    respx_mock.post(wse._gpw_client.config.companies_requests[0][0]).mock(
        httpx.Response(200, content=GPW_COMPANIES_LIST_PAGE_MALFORMED)
    )
    respx_mock.post(wse._new_connect_client.config.companies_requests[0][0]).mock(
        return_value=httpx.Response(200, content=NEW_CONNECT_COMPANIES_LIST_PAGE_MALFORMED)
    )

    # when
    all_records = list(wse.get_companies())
    failed_records = [record for record in all_records if isinstance(record, FailedParsingElementModel)]

    # then
    assert len(all_records) == 80
    assert len(failed_records) == 4


def test_get_reports_returns_proper_number_of_reports(wse, respx_mock):
    # given
    respx_mock.post(wse._gpw_client.config.reports_url).side_effect = [
        httpx.Response(200, content=REPORTS_PAGE),
        httpx.Response(200, content=REPORTS_EMPTY_PAGE),
    ]
    respx_mock.post(wse._new_connect_client.config.reports_url).side_effect = [
        httpx.Response(200, content=REPORTS_PAGE),
        httpx.Response(200, content=REPORTS_EMPTY_PAGE),
    ]

    # when
    reports = list(wse.get_reports())

    # then
    assert len(reports) == 40


def test_get_reports_returns_model_object(wse, respx_mock):
    # given
    respx_mock.post(wse._gpw_client.config.reports_url).mock(return_value=httpx.Response(200, content=REPORTS_PAGE))

    # when
    report = next(wse.get_reports())

    # then
    assert report == ReportModel(
        gpw_id="404679",
        name="11 BIT STUDIOS SPÓŁKA AKCYJNA (PL11BTS00015)",
        summary="Wstępne wyniki finansowe 11 bit studios S.A. za I półrocze 2022 roku",
        datetime=datetime(2022, 9, 23, 17, 1, 26),
        category=ReportCategory.ESPI,
        type=ReportType.CURRENT,
    )


def test_get_reports_continues_after_known_parsing_exception(wse, respx_mock):
    # given
    respx_mock.post(wse._gpw_client.config.reports_url).side_effect = [
        httpx.Response(200, content=REPORTS_PAGE_MALFORMED),
        httpx.Response(200, content=REPORTS_EMPTY_PAGE),
    ]
    respx_mock.post(wse._new_connect_client.config.reports_url).mock(
        return_value=httpx.Response(200, content=REPORTS_EMPTY_PAGE)
    )

    # when
    reports = list(wse.get_reports())

    # then
    assert len(reports) == 15


def test_get_reports_break_after_reaching_empty_page(wse, respx_mock):
    # given
    respx_mock.post(wse._gpw_client.config.reports_url).side_effect = [
        httpx.Response(200, content=REPORTS_PAGE),
        # Putting empty page in the middle of responses should prevent making more requests.
        httpx.Response(200, content=REPORTS_EMPTY_PAGE),
        httpx.Response(200, content=REPORTS_PAGE),
    ]
    respx_mock.post(wse._new_connect_client.config.reports_url).mock(
        return_value=httpx.Response(200, content=REPORTS_EMPTY_PAGE)
    )

    # when
    list(wse.get_reports())

    # then
    #  two requests to WSE od one to NewConnect
    assert respx_mock.calls.call_count == 3


def test_get_reports_date_range_query_params(wse, respx_mock):
    # given
    respx_mock.post(wse._gpw_client.config.reports_url).side_effect = [
        httpx.Response(200, content=REPORTS_PAGE),
        httpx.Response(200, content=REPORTS_EMPTY_PAGE),
        httpx.Response(200, content=REPORTS_PAGE),
        httpx.Response(200, content=REPORTS_EMPTY_PAGE),
    ]
    respx_mock.post(wse._new_connect_client.config.reports_url).mock(
        return_value=httpx.Response(200, content=REPORTS_EMPTY_PAGE)
    )

    # when
    list(wse.get_reports(date_from=date(2022, 1, 1), date_to=date(2022, 1, 2)))

    # then
    assert respx_mock.calls.call_count == 6  # 2 x 2 for GPW and 2 x 1 for NewConnect
    assert b"date=01-01-2022" in respx_mock.calls[0].request.content
    assert b"date=02-01-2022" in respx_mock.calls[3].request.content


def test_get_reports_raises_when_only_single_date_given(wse, respx_mock):
    # given
    respx_mock.post(wse._gpw_client.config.reports_url).side_effect = [httpx.Response(200, content=REPORTS_EMPTY_PAGE)]

    # then
    with pytest.raises(DateRangeException):
        next(wse.get_reports(date_from=date(2022, 1, 1)))
    with pytest.raises(DateRangeException):
        next(wse.get_reports(date_to=date(2022, 1, 1)))


def test_get_reports_search_query_param(wse, respx_mock):
    # given
    respx_mock.post(wse._gpw_client.config.reports_url).side_effect = [
        httpx.Response(200, content=REPORTS_PAGE),
        httpx.Response(200, content=REPORTS_EMPTY_PAGE),
    ]
    respx_mock.post(wse._new_connect_client.config.reports_url).mock(
        return_value=httpx.Response(200, content=REPORTS_EMPTY_PAGE)
    )

    # when
    next(wse.get_reports(search="test-search"))

    # then
    assert b"searchText=test-search" in respx_mock.calls[0].request.content
