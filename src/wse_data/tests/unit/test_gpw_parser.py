from datetime import datetime
from unittest.mock import patch

import pytest
from bs4 import BeautifulSoup

from wse_data.data_scrappers.gpw.company_model import CompanyModel, MarketEnum
from wse_data.data_scrappers.gpw.failed_parsing_element_model import FailedParsingElementModel
from wse_data.data_scrappers.gpw.gpw_parser import (
    GPWParser,
    CompanyIdNotFoundException,
    CompanyNameNotFoundException,
    CompanySymbolNotFoundException,
    _ReportData,
    FailedToParseReportDataException,
    ReportIdNotFoundException,
    ReportSummaryNotFoundException,
)
from wse_data.data_scrappers.gpw.report_model import ReportModel, ReportCategory, ReportType

from wse_data.tests.data import gpw_responses


@pytest.fixture
def gpw_parser():
    return GPWParser(market=MarketEnum.GPW)


@pytest.fixture
def new_connect_parser():
    return GPWParser(market=MarketEnum.NEW_CONNECT)


@pytest.fixture
def company_row():
    return BeautifulSoup(gpw_responses.GPW_SINGLE_COMPANY_ROW, "html.parser")


def test_parse_companies_page_parses_gpw_page_properly(gpw_parser):
    # given
    parsed_page_generator = gpw_parser.parse_companies_page(gpw_responses.GPW_COMPANIES_LIST_PAGE)

    # when
    parsed_pages = list(parsed_page_generator)

    # then
    assert parsed_pages == [
        CompanyModel(isin="PLNFI0600010", name="06MAGNA", ticker="06N", market=MarketEnum.GPW),
        CompanyModel(isin="PL11BTS00015", name="11BIT", ticker="11B", market=MarketEnum.GPW),
        CompanyModel(isin="PLGRNKT00019", name="3RGAMES", ticker="3RG", market=MarketEnum.GPW),
        CompanyModel(isin="PLAB00000019", name="ABPL", ticker="ABE", market=MarketEnum.GPW),
        CompanyModel(isin="PLACSA000014", name="ACAUTOGAZ", ticker="ACG", market=MarketEnum.GPW),
        CompanyModel(isin="PLACTIN00018", name="ACTION", ticker="ACT", market=MarketEnum.GPW),
        CompanyModel(isin="PLADVIV00015", name="ADIUVO", ticker="ADV", market=MarketEnum.GPW),
        CompanyModel(isin="PLAGORA00067", name="AGORA", ticker="AGO", market=MarketEnum.GPW),
        CompanyModel(isin="CY0101062111", name="AGROTON", ticker="AGT", market=MarketEnum.GPW),
        CompanyModel(isin="PLSNTFG00017", name="AIGAMES", ticker="ALG", market=MarketEnum.GPW),
        CompanyModel(isin="PLWNDMB00010", name="AILLERON", ticker="ALL", market=MarketEnum.GPW),
        CompanyModel(isin="PLAIRWY00017", name="AIRWAY", ticker="AWM", market=MarketEnum.GPW),
        CompanyModel(isin="PLALIOR00045", name="ALIOR", ticker="ALR", market=MarketEnum.GPW),
        CompanyModel(isin="LU2237380790", name="ALLEGRO", ticker="ALE", market=MarketEnum.GPW),
        CompanyModel(isin="PLTRNSU00013", name="ALTA", ticker="AAT", market=MarketEnum.GPW),
        CompanyModel(isin="PLATTFI00018", name="ALTUS", ticker="ALI", market=MarketEnum.GPW),
        CompanyModel(isin="PLALMTL00023", name="ALUMETAL", ticker="AML", market=MarketEnum.GPW),
        CompanyModel(isin="PLAMBRA00013", name="AMBRA", ticker="AMB", market=MarketEnum.GPW),
        CompanyModel(isin="PLAMICA00010", name="AMICA", ticker="AMC", market=MarketEnum.GPW),
        CompanyModel(isin="PLZYWIC00016", name="ZYWIEC", ticker="ZWC", market=MarketEnum.GPW),
    ]


def test_parse_companies_page_parses_new_connect_page_properly(new_connect_parser):
    # given
    parsed_page_generator = new_connect_parser.parse_companies_page(gpw_responses.NEW_CONNECT_COMPANIES_LIST_PAGE)

    # when
    parsed_pages = list(parsed_page_generator)

    # then
    assert parsed_pages == [
        CompanyModel(isin="PLVCAOC00015", name="01CYBATON", ticker="01C", market=MarketEnum.NEW_CONNECT),
        CompanyModel(isin="PLONESL00011", name="1SOLUTION", ticker="ONE", market=MarketEnum.NEW_CONNECT),
        CompanyModel(isin="PL2CPRT00030", name="2CPARTNER /Z\xa0/1", ticker="2CP", market=MarketEnum.NEW_CONNECT),
        CompanyModel(isin="PL4MASS00011", name="4MASS", ticker="4MS", market=MarketEnum.NEW_CONNECT),
        CompanyModel(isin="PLESLTN00010", name="4MOBILITY", ticker="4MB", market=MarketEnum.NEW_CONNECT),
        CompanyModel(isin="PLTRCPS00016", name="7FIT", ticker="7FT", market=MarketEnum.NEW_CONNECT),
        CompanyModel(isin="PL7LVLS00017", name="7LEVELS", ticker="7LV", market=MarketEnum.NEW_CONNECT),
        CompanyModel(isin="PLMIDVN00017", name="AALLIANCE", ticker="AAS", market=MarketEnum.NEW_CONNECT),
        CompanyModel(isin="PLABAK000013", name="ABAK", ticker="ABK", market=MarketEnum.NEW_CONNECT),
        CompanyModel(isin="PLABSIN00012", name="ABSINVEST", ticker="AIN", market=MarketEnum.NEW_CONNECT),
        CompanyModel(isin="PLACRTS00018", name="ACARTUS", ticker="ACA", market=MarketEnum.NEW_CONNECT),
        CompanyModel(isin="PLPIK0000018", name="ADATEX", ticker="ADX", market=MarketEnum.NEW_CONNECT),
        CompanyModel(isin="PLADMSC00013", name="ADVERTIGO", ticker="AVE", market=MarketEnum.NEW_CONNECT),
        CompanyModel(isin="GB00B42V2T10", name="AERFINANC /Z", ticker="AER", market=MarketEnum.NEW_CONNECT),
        CompanyModel(isin="PLMNTHL00016", name="AFHOL", ticker="AFH", market=MarketEnum.NEW_CONNECT),
        CompanyModel(isin="CY0101452114", name="AGROLIGA", ticker="AGL", market=MarketEnum.NEW_CONNECT),
        CompanyModel(isin="PLAGRMP00010", name="AGROMEP", ticker="AGP", market=MarketEnum.NEW_CONNECT),
        CompanyModel(isin="PLATCDL00013", name="AITON", ticker="AIT", market=MarketEnum.NEW_CONNECT),
        CompanyModel(isin="PLAKCFN00013", name="AKCEPTFIN /Z", ticker="AFC", market=MarketEnum.NEW_CONNECT),
        CompanyModel(isin="PLONLIN00013", name="ANALIZY", ticker="AOL", market=MarketEnum.NEW_CONNECT),
    ]


def test_parse_companies_page_doesnt_yield_for_empty_page(gpw_parser):
    # given
    parsed_page_generator = gpw_parser.parse_companies_page(gpw_responses.COMPANIES_LIST_EMPTY_PAGE)

    # then
    with pytest.raises(StopIteration):
        next(parsed_page_generator)


def test_parse_companies_page_returns_proper_model_on_failed_parsing(gpw_parser):
    # given
    parsed_page_generator = gpw_parser.parse_companies_page(gpw_responses.GPW_COMPANIES_LIST_PAGE)

    # when
    with patch.object(GPWParser, "_parse_company_id", return_value=""):
        failed_model = next(parsed_page_generator)

    # then
    assert isinstance(failed_model, FailedParsingElementModel)


def test_parse_company_id_properly_parses_data(gpw_parser, company_row):
    # given
    proper_company_id = "PLNFI0600010"

    # when
    parsed_id = gpw_parser._parse_company_id(company_row)

    # then
    assert parsed_id == proper_company_id


def test_parse_company_id_raises_exception_when_no_company_id(gpw_parser):
    # given
    empty_data = BeautifulSoup(b"", "html.parser")

    # then
    with pytest.raises(CompanyIdNotFoundException):
        gpw_parser._parse_company_id(empty_data)


def test_parse_company_name_properly_parses_data(gpw_parser, company_row):
    # given
    proper_company_name = "06MAGNA"

    # when
    parsed_name = gpw_parser._parse_company_name(company_row)

    # then
    assert parsed_name == proper_company_name


def test_parse_company_name_raises_exception_when_no_company_name(gpw_parser):
    # given
    empty_data = BeautifulSoup(b"", "html.parser")

    # then
    with pytest.raises(CompanyNameNotFoundException):
        gpw_parser._parse_company_name(empty_data)


def test_parse_company_ticker_properly_parses_data(gpw_parser, company_row):
    # given
    proper_company_ticker = "06N"

    # when
    parsed_name = gpw_parser._parse_company_ticker(company_row)

    # then
    assert parsed_name == proper_company_ticker


def test_parse_company_ticker_raises_exception_when_no_company_ticker(gpw_parser):
    # given
    empty_ticker_data = BeautifulSoup(b"<tr><td></td></tr>", "html.parser")

    # then
    with pytest.raises(CompanySymbolNotFoundException):
        gpw_parser._parse_company_ticker(empty_ticker_data)


@pytest.mark.parametrize(
    "test_input, expected",
    [
        (
            "28-09-2021 19:16:14 | Bieżący | ESPI | 12/2021",
            _ReportData(
                datetime=datetime(2021, 9, 28, 19, 16, 14),
                category=ReportCategory.ESPI,
                type=ReportType.CURRENT,
            ),
        ),
        (
            "30-04-2021 20:58:39 | Roczny | ESPI",
            _ReportData(
                datetime=datetime(2021, 4, 30, 20, 58, 39),
                category=ReportCategory.ESPI,
                type=ReportType.YEAR,
            ),
        ),
        (
            "24-09-2021 17:38:49 | ESPI | 55/2021",
            _ReportData(
                datetime=datetime(2021, 9, 24, 17, 38, 49),
                category=ReportCategory.ESPI,
                type=ReportType.OTHER,
            ),
        ),
        (
            "24-03-2022 21:49:42 | Półroczny | ESPI | /2021",
            _ReportData(
                datetime=datetime(2022, 3, 24, 21, 49, 42),
                category=ReportCategory.ESPI,
                type=ReportType.HALF_YEAR,
            ),
        ),
        (
            "24-02-2021 16:16:47 | Kwartalny | EBI | 1/2021",
            _ReportData(
                datetime=datetime(2021, 2, 24, 16, 16, 47),
                category=ReportCategory.EBI,
                type=ReportType.QUARTER,
            ),
        ),
    ],
)
def test_parse_report_data_parses_properly(test_input, expected, gpw_parser):
    # given
    test_row = BeautifulSoup(f'<li><span class="date">{test_input}</span></li>', "html.parser")

    # when
    output = gpw_parser._parse_report_data(test_row)

    # then
    assert output == expected


def test_parse_report_data_throws_exception_on_malformed_data(gpw_parser):
    # given
    test_row = BeautifulSoup('<li><span class="date">"24-02-2021 16:16:47 | "</span></li>', "html.parser")

    # then
    with pytest.raises(FailedToParseReportDataException):
        gpw_parser._parse_report_data(test_row)


def test_parse_report_id_parses_properly(gpw_parser):
    # given
    test_row = BeautifulSoup(
        '<strong class="name"> <a href="komunikat?geru_id=396206&amp;title=Przekroczenie+progu+5+proc.+w+og%C3%B3lnej+liczbie+akcji+i+g%C5%82os%C3%B3w+w+Sp%C3%B3%C5%82ce"> 11 BIT STUDIOS SPÓŁKA AKCYJNA (PL11BTS00015) </a> </strong>',  # noqa: E501
        # noqa
        "html.parser",
    )
    expected = "396206"

    # when
    output = gpw_parser._parse_report_id(test_row)

    # then
    assert output == expected


def test_parse_report_company_isin_parses_properly(gpw_parser):
    # given
    test_row = BeautifulSoup(
        '<strong class="name"> <a href="komunikat?geru_id=396206&amp;title=Przekroczenie+progu+5+proc.+w+og%C3%B3lnej+liczbie+akcji+i+g%C5%82os%C3%B3w+w+Sp%C3%B3%C5%82ce"> 11 BIT STUDIOS SPÓŁKA AKCYJNA (PL11BTS00015) </a> </strong>',  # noqa: E501
        # noqa
        "html.parser",
    )
    expected = "PL11BTS00015"

    # when
    output = gpw_parser._parse_report_company_isin(test_row)

    # then
    assert output == expected


def test_parse_report_id_throws_exception_when_not_found(gpw_parser):
    # given
    test_row = BeautifulSoup(
        '<strong class="name"> <a href="komunikat?title=Przekroczenie+progu+5+proc.+w+og%C3%B3lnej+liczbie+akcji+i+g%C5%82os%C3%B3w+w+Sp%C3%B3%C5%82ce"> 11 BIT STUDIOS SPÓŁKA AKCYJNA (PL11BTS00015) </a> </strong>',  # noqa: E501
        # noqa
        "html.parser",
    )

    # then
    with pytest.raises(ReportIdNotFoundException):
        gpw_parser._parse_report_id(test_row)


def test_parse_report_summary_parses_properly(gpw_parser):
    # given
    expected = "Przekroczenie progu 5 proc. w ogólnej liczbie akcji i głosów w Spółce"
    test_row = BeautifulSoup(f"<li><p>{expected}</p></li>", "html.parser")

    # when
    output = gpw_parser._parse_report_summary(test_row)

    # then
    assert output == expected


def test_parse_report_summary_throws_exception_when_not_found(gpw_parser):
    # given
    test_row = BeautifulSoup("<li></li>", "html.parser")

    # then
    with pytest.raises(ReportSummaryNotFoundException):
        gpw_parser._parse_report_summary(test_row)


def test_parse_reports_page_parses_page_properly(gpw_parser):
    # given
    parsed_page_generator = gpw_parser.parse_reports_page(gpw_responses.REPORTS_PAGE)

    # when
    parsed_pages = list(parsed_page_generator)

    # then
    assert parsed_pages == [
        ReportModel(
            gpw_id="404679",
            company_isin="PL11BTS00015",
            name="11 BIT STUDIOS SPÓŁKA AKCYJNA (PL11BTS00015)",
            summary="Wstępne wyniki finansowe 11 bit studios S.A. za I półrocze 2022 roku",
            datetime=datetime(2022, 9, 23, 17, 1, 26),
            category=ReportCategory.ESPI,
            type=ReportType.CURRENT,
        ),
        ReportModel(
            gpw_id="402563",
            company_isin="PL11BTS00015",
            name="11 BIT STUDIOS SPÓŁKA AKCYJNA (PL11BTS00015)",
            summary="Zmiana terminu publikacji raportu okresowego",
            datetime=datetime(2022, 8, 18, 16, 35, 2),
            category=ReportCategory.ESPI,
            type=ReportType.CURRENT,
        ),
        ReportModel(
            gpw_id="402355",
            company_isin="PL11BTS00015",
            name="11 BIT STUDIOS SPÓŁKA AKCYJNA (PL11BTS00015)",
            summary="Powołanie Członków Zarządu Spółki",
            datetime=datetime(2022, 8, 11, 20, 46, 5),
            category=ReportCategory.ESPI,
            type=ReportType.CURRENT,
        ),
        ReportModel(
            gpw_id="401797",
            company_isin="PL11BTS00015",
            name="11 BIT STUDIOS SPÓŁKA AKCYJNA (PL11BTS00015)",
            summary="Nabycie akcji Starward Industries S.A.",
            datetime=datetime(2022, 7, 29, 17, 13, 31),
            category=ReportCategory.ESPI,
            type=ReportType.CURRENT,
        ),
        ReportModel(
            gpw_id="400792",
            company_isin="PL11BTS00015",
            name="11 BIT STUDIOS SPÓŁKA AKCYJNA (PL11BTS00015)",
            summary="Zawiadomienie akcjonariusza o zwiększeniu udziału w ogólnej liczbie głosów w Spółce",
            datetime=datetime(2022, 7, 7, 12, 47, 42),
            category=ReportCategory.ESPI,
            type=ReportType.CURRENT,
        ),
        ReportModel(
            gpw_id="399347",
            company_isin="PL11BTS00015",
            name="11 BIT STUDIOS SPÓŁKA AKCYJNA (PL11BTS00015)",
            summary="Powołanie Zarządu kolejnej kadencji",
            datetime=datetime(2022, 6, 21, 19, 52, 50),
            category=ReportCategory.ESPI,
            type=ReportType.CURRENT,
        ),
        ReportModel(
            gpw_id="399346",
            company_isin="PL11BTS00015",
            name="11 BIT STUDIOS SPÓŁKA AKCYJNA (PL11BTS00015)",
            summary="Wybór Przewodniczącego i Wiceprzewodniczącego Rady Nadzorczej oraz powołanie Komitetu Audytu",
            datetime=datetime(2022, 6, 21, 19, 48, 48),
            category=ReportCategory.ESPI,
            type=ReportType.CURRENT,
        ),
        ReportModel(
            gpw_id="399298",
            company_isin="PL11BTS00015",
            name="11 BIT STUDIOS SPÓŁKA AKCYJNA (PL11BTS00015)",
            summary="Wybór Rady Nadzorczej 11 bit studios S.A.",
            datetime=datetime(2022, 6, 21, 13, 46, 48),
            category=ReportCategory.ESPI,
            type=ReportType.CURRENT,
        ),
        ReportModel(
            gpw_id="399297",
            company_isin="PL11BTS00015",
            name="11 BIT STUDIOS SPÓŁKA AKCYJNA (PL11BTS00015)",
            summary="Wykaz akcjonariuszy posiadających co najmniej 5 proc. głosów na ZWZA Spółki w dniu 21 czerwca 2022 roku.",  # noqa
            datetime=datetime(2022, 6, 21, 13, 37, 44),
            category=ReportCategory.ESPI,
            type=ReportType.CURRENT,
        ),
        ReportModel(
            gpw_id="399290",
            company_isin="PL11BTS00015",
            name="11 BIT STUDIOS SPÓŁKA AKCYJNA (PL11BTS00015)",
            summary="Treść uchwał powziętych przez Zwyczajne Walne Zgromadzenie 11 bit studios S.A. w dniu 21 czerwca 2022 roku",  # noqa
            datetime=datetime(2022, 6, 21, 13, 24, 34),
            category=ReportCategory.ESPI,
            type=ReportType.CURRENT,
        ),
        ReportModel(
            gpw_id="398655",
            company_isin="PL11BTS00015",
            name="11 BIT STUDIOS SPÓŁKA AKCYJNA (PL11BTS00015)",
            summary="Zgłoszenie kandydatów na Członków Rady Nadzorczej 11 bit studios S.A.",
            datetime=datetime(2022, 6, 9, 11, 59, 14),
            category=ReportCategory.ESPI,
            type=ReportType.CURRENT,
        ),
        ReportModel(
            gpw_id="398491",
            company_isin="PL11BTS00015",
            name="11 BIT STUDIOS SPÓŁKA AKCYJNA (PL11BTS00015)",
            summary="Uzupełnienie dokumentacji na Zwyczajne Walne Zgromadzenie 11 bit studios S.A. zwołane na dzień 21 czerwca 2022 roku na godz. 11.00.",  # noqa
            datetime=datetime(2022, 6, 7, 13, 33, 16),
            category=ReportCategory.ESPI,
            type=ReportType.CURRENT,
        ),
        ReportModel(
            gpw_id="397285",
            company_isin="PL11BTS00015",
            name="11 BIT STUDIOS SPÓŁKA AKCYJNA (PL11BTS00015)",
            summary="",
            datetime=datetime(2022, 5, 25, 17, 0, 59),
            category=ReportCategory.ESPI,
            type=ReportType.QUARTER,
        ),
        ReportModel(
            gpw_id="396844",
            company_isin="PL11BTS00015",
            name="11 BIT STUDIOS SPÓŁKA AKCYJNA (PL11BTS00015)",
            summary="Ogłoszenie o zwołaniu Zwyczajnego Walnego Zgromadzenia 11 bit studios S.A. na dzień\n21 czerwca 2022 roku na godz. 11.00.",  # noqa
            datetime=datetime(2022, 5, 19, 15, 5, 24),
            category=ReportCategory.ESPI,
            type=ReportType.CURRENT,
        ),
        ReportModel(
            gpw_id="396364",
            company_isin="PL11BTS00015",
            name="11 BIT STUDIOS SPÓŁKA AKCYJNA (PL11BTS00015)",
            summary="Wybór audytora do badania i przeglądu sprawozdań finansowych Spółki.",
            datetime=datetime(2022, 5, 12, 11, 2, 45),
            category=ReportCategory.ESPI,
            type=ReportType.CURRENT,
        ),
        ReportModel(
            gpw_id="396206",
            company_isin="PL11BTS00015",
            name="11 BIT STUDIOS SPÓŁKA AKCYJNA (PL11BTS00015)",
            summary="Przekroczenie progu 5 proc. w ogólnej liczbie akcji i głosów w Spółce",
            datetime=datetime(2022, 5, 10, 15, 31, 18),
            category=ReportCategory.ESPI,
            type=ReportType.CURRENT,
        ),
        ReportModel(
            gpw_id="395113",
            company_isin="PL11BTS00015",
            name="11 BIT STUDIOS SPÓŁKA AKCYJNA (PL11BTS00015)",
            summary="Rekomendacja Rady Nadzorczej w sprawie podziału zysku netto wypracowanego w 2021 roku",
            datetime=datetime(2022, 4, 27, 11, 43, 7),
            category=ReportCategory.ESPI,
            type=ReportType.CURRENT,
        ),
        ReportModel(
            gpw_id="394600",
            company_isin="PL11BTS00015",
            name="11 BIT STUDIOS SPÓŁKA AKCYJNA (PL11BTS00015)",
            summary='Gra "Moonlighter" w serwisie Netflix',
            datetime=datetime(2022, 4, 20, 16, 1),
            category=ReportCategory.ESPI,
            type=ReportType.CURRENT,
        ),
        ReportModel(
            gpw_id="394566",
            company_isin="PL11BTS00015",
            name="11 BIT STUDIOS SPÓŁKA AKCYJNA (PL11BTS00015)",
            summary="Zawiadomienie w trybie art. 19 ust. 1 rozporządzenia MAR",
            datetime=datetime(2022, 4, 20, 10, 24, 22),
            category=ReportCategory.ESPI,
            type=ReportType.CURRENT,
        ),
        ReportModel(
            gpw_id="394386",
            company_isin="PL11BTS00015",
            name="11 BIT STUDIOS SPÓŁKA AKCYJNA (PL11BTS00015)",
            summary="Umowa wydawnicza ze State of Play Games Ltd.",
            datetime=datetime(2022, 4, 14, 17, 0, 12),
            category=ReportCategory.ESPI,
            type=ReportType.CURRENT,
        ),
    ]
