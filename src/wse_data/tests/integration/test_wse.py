from datetime import datetime, date
from decimal import Decimal

import httpx
import pytest

from wse_data.data_scrappers.gpw.company_model import CompanyModel, MarketEnum
from wse_data.data_scrappers.gpw.failed_parsing_element_model import FailedParsingElementModel
from wse_data.data_scrappers.gpw.report_model import ReportModel, ReportCategory, ReportType
from wse_data.data_scrappers.gpw.stock_quotes_model import StockQuotesModel

from wse_data.tests.data.gpw_responses import (
    GPW_COMPANIES_LIST_PAGE,
    COMPANIES_LIST_EMPTY_PAGE,
    GPW_COMPANIES_LIST_PAGE_MALFORMED,
    REPORTS_PAGE,
    REPORTS_EMPTY_PAGE,
    REPORTS_PAGE_MALFORMED,
    NEW_CONNECT_COMPANIES_LIST_PAGE,
    NEW_CONNECT_COMPANIES_LIST_PAGE_MALFORMED,
    GPW_STOCK_QUOTATIONS_XLS,
)
from wse_data.wse import WSE, DateRangeException


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
    gpw_companies = list(wse.get_companies(market=MarketEnum.GPW))
    new_connect_companies = list(wse.get_companies(market=MarketEnum.NEW_CONNECT))

    # then
    assert len(gpw_companies) == 60
    assert len(new_connect_companies) == 20


def test_get_companies_returns_model_object(wse, respx_mock):
    # given
    respx_mock.post(wse._gpw_client.config.companies_requests[0][0]).mock(
        return_value=httpx.Response(200, content=GPW_COMPANIES_LIST_PAGE)
    )

    # when
    gpw_company = next(wse.get_companies(market=MarketEnum.GPW))

    # then
    assert gpw_company == CompanyModel(
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

    # when
    all_records = list(wse.get_companies(market=MarketEnum.GPW))
    failed_records = [record for record in all_records if isinstance(record, FailedParsingElementModel)]

    # then
    assert len(all_records) == 60
    assert len(failed_records) == 3


def test_get_companies_search_query_param(wse, respx_mock):
    # given
    respx_mock.post(wse._gpw_client.config.companies_requests[0][0]).mock(
        httpx.Response(200, content=GPW_COMPANIES_LIST_PAGE)
    )

    # when
    next(wse.get_companies(market=MarketEnum.GPW, search="test-search"))

    # then
    assert b"filters%5Bsearch%5D=test-search" in respx_mock.calls[0].request.content


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
    gpw_reports = list(wse.get_reports(market=MarketEnum.GPW))
    new_connect_reports = list(wse.get_reports(market=MarketEnum.NEW_CONNECT))

    # then
    assert len(gpw_reports) == 20
    assert len(new_connect_reports) == 20


def test_get_reports_returns_model_object(wse, respx_mock):
    # given
    respx_mock.post(wse._gpw_client.config.reports_url).mock(return_value=httpx.Response(200, content=REPORTS_PAGE))

    # when
    report = next(wse.get_reports(market=MarketEnum.GPW))

    # then
    assert report == ReportModel(
        gpw_id="404679",
        company_isin="PL11BTS00015",
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

    # when
    reports = list(wse.get_reports(market=MarketEnum.GPW))

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

    # when
    list(wse.get_reports(market=MarketEnum.GPW))

    # then
    assert respx_mock.calls.call_count == 2


def test_get_reports_for_date_query_params(wse, respx_mock):
    # given
    respx_mock.post(wse._gpw_client.config.reports_url).side_effect = [
        httpx.Response(200, content=REPORTS_PAGE),
        httpx.Response(200, content=REPORTS_EMPTY_PAGE),
    ]

    # when
    list(wse.get_reports(market=MarketEnum.GPW, date_=date(2022, 1, 1)))

    # then
    assert respx_mock.calls.call_count == 2
    assert b"date=01-01-2022" in respx_mock.calls[0].request.content


def test_get_reports_search_query_param(wse, respx_mock):
    # given
    respx_mock.post(wse._gpw_client.config.reports_url).side_effect = [
        httpx.Response(200, content=REPORTS_PAGE),
        httpx.Response(200, content=REPORTS_EMPTY_PAGE),
    ]

    # when
    next(wse.get_reports(market=MarketEnum.GPW, search="test-search"))

    # then
    assert b"searchText=test-search" in respx_mock.calls[0].request.content


def test_get_stock_quotes_returns_proper_number_of_records(wse, respx_mock):
    # given
    date_ = date(2022, 10, 4)
    respx_mock.get("https://www.gpw.pl/archiwum-notowan?fetch=1&type=10&instrument=&date=04-10-2022").mock(
        return_value=httpx.Response(
            200, content=GPW_STOCK_QUOTATIONS_XLS, headers={"content-type": "application/vnd.ms-excel"}
        )
    )

    # when
    stock_quotes = list(wse.get_stock_quotes(date_))

    # then
    assert len(stock_quotes) == 418
    assert stock_quotes[0] == StockQuotesModel(
        date=date(2022, 10, 4),
        company_name="06MAGNA",
        company_isin="PLNFI0600010",
        opening=Decimal("2.565"),
        closing=Decimal("2.68"),
        max=Decimal("2.81"),
        min=Decimal("2.565"),
        volume=14099,
    )
    assert stock_quotes[417] == StockQuotesModel(
        date=date(2022, 10, 4),
        company_name="ZYWIEC",
        company_isin="PLZYWIC00016",
        opening=Decimal("478"),
        closing=Decimal("477"),
        max=Decimal("479"),
        min=Decimal("477"),
        volume=53,
    )
