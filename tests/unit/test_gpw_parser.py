from datetime import datetime
from unittest.mock import patch

import pytest
from bs4 import BeautifulSoup

from src.data_scrappers.gpw.failed_parsing_element_model import FailedParsingElementModel
from src.data_scrappers.gpw.report_model import ReportModel, ReportCategory, ReportType
from tests.data import gpw_responses
from src.data_scrappers.gpw.company_model import CompanyModel
from src.data_scrappers.gpw.gpw_parser import (
    GPWParser,
    EmptyPageException,
    CompanyIdNotFoundException,
    CompanyNameNotFoundException,
    CompanySymbolNotFoundException,
    _ReportData,
    FailedToParseReportDataException,
    ReportIdNotFoundException,
    ReportSummaryNotFoundException,
)


@pytest.fixture
def gpw_parser():
    return GPWParser()


@pytest.fixture
def company_row():
    return BeautifulSoup(gpw_responses.SINGLE_COMPANY_ROW, "html.parser")


def test_parse_companies_page_parses_page_properly(gpw_parser):
    # given
    parsed_page_generator = gpw_parser.parse_companies_page(gpw_responses.COMPANIES_LIST_PAGE)

    # when
    parsed_pages = list(parsed_page_generator)

    # then
    assert parsed_pages == [
        CompanyModel(
            gpw_id="PLROPCE00017",
            name="ZAKŁADY MAGNEZYTOWE ROPCZYCE SPÓŁKA AKCYJNA",
            ticker="RPC",
        ),
        CompanyModel(
            gpw_id="PLZPCOT00018",
            name="ZAKŁADY PRZEMYSŁU CUKIERNICZEGO OTMUCHÓW SPÓŁKA AKCYJNA",
            ticker="OTM",
        ),
        CompanyModel(
            gpw_id="PLELZAB00010",
            name="ZAKŁADY URZĄDZEŃ KOMPUTEROWYCH ELZAB SPÓŁKA AKCYJNA",
            ticker="ELZ",
        ),
        CompanyModel(
            gpw_id="PLSTPRK00019",
            name="ZAKŁADY URZĄDZEŃ KOTŁOWYCH STĄPORKÓW SPÓŁKA AKCYJNA",
            ticker="ZUK",
        ),
        CompanyModel(gpw_id="PLZAMET00010", name="ZAMET SPÓŁKA AKCYJNA", ticker="ZMT"),
        CompanyModel(gpw_id="PLZEPAK00012", name="ZE PAK SPÓŁKA AKCYJNA", ticker="ZEP"),
        CompanyModel(
            gpw_id="PLKGNRC00015",
            name="ZESPÓŁ ELEKTROCIEPŁOWNI WROCŁAWSKICH KOGENERACJA SPÓŁKA AKCYJNA",
            ticker="KGN",
        ),
        CompanyModel(gpw_id="PLZPUE000012", name="ZPUE SPÓŁKA AKCYJNA", ticker="PUE"),
        CompanyModel(gpw_id="PLZUE0000015", name="ZUE SPÓŁKA AKCYJNA", ticker="ZUE"),
    ]


def test_parse_companies_page_raises_on_empty_page(gpw_parser):
    # given
    parsed_page_generator = gpw_parser.parse_companies_page(gpw_responses.COMPANIES_LIST_EMPTY_PAGE)

    # then
    with pytest.raises(EmptyPageException):
        next(parsed_page_generator)


def test_parse_companies_page_returns_proper_model_on_failed_parsing(gpw_parser):
    # given
    parsed_page_generator = gpw_parser.parse_companies_page(gpw_responses.COMPANIES_LIST_PAGE)

    class Dummy:
        pass

    # when
    with patch.object(GPWParser, "_parse_company_id", return_value=Dummy()):
        failed_model = next(parsed_page_generator)

    # then
    assert isinstance(failed_model, FailedParsingElementModel)


def test_parse_company_id_properly_parses_data(gpw_parser, company_row):
    # given
    proper_company_id = "PLROPCE00017"

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
    proper_company_name = "ZAKŁADY MAGNEZYTOWE ROPCZYCE SPÓŁKA AKCYJNA"

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
    proper_company_ticker = "RPC"

    # when
    parsed_name = gpw_parser._parse_company_ticker(company_row)

    # then
    assert parsed_name == proper_company_ticker


def test_parse_company_ticker_raises_exception_when_no_company_ticker(gpw_parser):
    # given
    empty_name_data = BeautifulSoup(b"", "html.parser")
    empty_ticker_data = BeautifulSoup(b"<div class='name'></div>", "html.parser")

    # then
    with pytest.raises(CompanySymbolNotFoundException):
        gpw_parser._parse_company_ticker(empty_name_data)
    with pytest.raises(CompanySymbolNotFoundException):
        gpw_parser._parse_company_ticker(empty_ticker_data)


@pytest.mark.parametrize(
    "test_input, expected",
    [
        (
            "28-09-2021 19:16:14 | Bieżący | ESPI | 12/2021",
            _ReportData(
                datetime=datetime(2021, 9, 28, 19, 16, 14), category=ReportCategory.ESPI, type=ReportType.CURRENT
            ),
        ),
        (
            "30-04-2021 20:58:39 | Roczny | ESPI",
            _ReportData(datetime=datetime(2021, 4, 30, 20, 58, 39), category=ReportCategory.ESPI, type=ReportType.YEAR),
        ),
        (
            "24-09-2021 17:38:49 | ESPI | 55/2021",
            _ReportData(
                datetime=datetime(2021, 9, 24, 17, 38, 49), category=ReportCategory.ESPI, type=ReportType.OTHER
            ),
        ),
        (
            "24-03-2022 21:49:42 | Półroczny | ESPI | /2021",
            _ReportData(
                datetime=datetime(2022, 3, 24, 21, 49, 42), category=ReportCategory.ESPI, type=ReportType.HALF_YEAR
            ),
        ),
        (
            "24-02-2021 16:16:47 | Kwartalny | EBI | 1/2021",
            _ReportData(
                datetime=datetime(2021, 2, 24, 16, 16, 47), category=ReportCategory.EBI, type=ReportType.QUARTER
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
            name="11 BIT STUDIOS SPÓŁKA AKCYJNA (PL11BTS00015)",
            summary="Wstępne wyniki finansowe 11 bit studios S.A. za I półrocze 2022 roku",
            datetime=datetime(2022, 9, 23, 17, 1, 26),
            category=ReportCategory.ESPI,
            type=ReportType.CURRENT,
        ),
        ReportModel(
            gpw_id="402563",
            name="11 BIT STUDIOS SPÓŁKA AKCYJNA (PL11BTS00015)",
            summary="Zmiana terminu publikacji raportu okresowego",
            datetime=datetime(2022, 8, 18, 16, 35, 2),
            category=ReportCategory.ESPI,
            type=ReportType.CURRENT,
        ),
        ReportModel(
            gpw_id="402355",
            name="11 BIT STUDIOS SPÓŁKA AKCYJNA (PL11BTS00015)",
            summary="Powołanie Członków Zarządu Spółki",
            datetime=datetime(2022, 8, 11, 20, 46, 5),
            category=ReportCategory.ESPI,
            type=ReportType.CURRENT,
        ),
        ReportModel(
            gpw_id="401797",
            name="11 BIT STUDIOS SPÓŁKA AKCYJNA (PL11BTS00015)",
            summary="Nabycie akcji Starward Industries S.A.",
            datetime=datetime(2022, 7, 29, 17, 13, 31),
            category=ReportCategory.ESPI,
            type=ReportType.CURRENT,
        ),
        ReportModel(
            gpw_id="400792",
            name="11 BIT STUDIOS SPÓŁKA AKCYJNA (PL11BTS00015)",
            summary="Zawiadomienie akcjonariusza o zwiększeniu udziału w ogólnej liczbie głosów w Spółce",
            datetime=datetime(2022, 7, 7, 12, 47, 42),
            category=ReportCategory.ESPI,
            type=ReportType.CURRENT,
        ),
        ReportModel(
            gpw_id="399347",
            name="11 BIT STUDIOS SPÓŁKA AKCYJNA (PL11BTS00015)",
            summary="Powołanie Zarządu kolejnej kadencji",
            datetime=datetime(2022, 6, 21, 19, 52, 50),
            category=ReportCategory.ESPI,
            type=ReportType.CURRENT,
        ),
        ReportModel(
            gpw_id="399346",
            name="11 BIT STUDIOS SPÓŁKA AKCYJNA (PL11BTS00015)",
            summary="Wybór Przewodniczącego i Wiceprzewodniczącego Rady Nadzorczej oraz powołanie Komitetu Audytu",
            datetime=datetime(2022, 6, 21, 19, 48, 48),
            category=ReportCategory.ESPI,
            type=ReportType.CURRENT,
        ),
        ReportModel(
            gpw_id="399298",
            name="11 BIT STUDIOS SPÓŁKA AKCYJNA (PL11BTS00015)",
            summary="Wybór Rady Nadzorczej 11 bit studios S.A.",
            datetime=datetime(2022, 6, 21, 13, 46, 48),
            category=ReportCategory.ESPI,
            type=ReportType.CURRENT,
        ),
        ReportModel(
            gpw_id="399297",
            name="11 BIT STUDIOS SPÓŁKA AKCYJNA (PL11BTS00015)",
            summary="Wykaz akcjonariuszy posiadających co najmniej 5 proc. głosów na ZWZA Spółki w dniu 21 czerwca 2022 roku.",  # noqa
            datetime=datetime(2022, 6, 21, 13, 37, 44),
            category=ReportCategory.ESPI,
            type=ReportType.CURRENT,
        ),
        ReportModel(
            gpw_id="399290",
            name="11 BIT STUDIOS SPÓŁKA AKCYJNA (PL11BTS00015)",
            summary="Treść uchwał powziętych przez Zwyczajne Walne Zgromadzenie 11 bit studios S.A. w dniu 21 czerwca 2022 roku",  # noqa
            datetime=datetime(2022, 6, 21, 13, 24, 34),
            category=ReportCategory.ESPI,
            type=ReportType.CURRENT,
        ),
        ReportModel(
            gpw_id="398655",
            name="11 BIT STUDIOS SPÓŁKA AKCYJNA (PL11BTS00015)",
            summary="Zgłoszenie kandydatów na Członków Rady Nadzorczej 11 bit studios S.A.",
            datetime=datetime(2022, 6, 9, 11, 59, 14),
            category=ReportCategory.ESPI,
            type=ReportType.CURRENT,
        ),
        ReportModel(
            gpw_id="398491",
            name="11 BIT STUDIOS SPÓŁKA AKCYJNA (PL11BTS00015)",
            summary="Uzupełnienie dokumentacji na Zwyczajne Walne Zgromadzenie 11 bit studios S.A. zwołane na dzień 21 czerwca 2022 roku na godz. 11.00.",  # noqa
            datetime=datetime(2022, 6, 7, 13, 33, 16),
            category=ReportCategory.ESPI,
            type=ReportType.CURRENT,
        ),
        ReportModel(
            gpw_id="397285",
            name="11 BIT STUDIOS SPÓŁKA AKCYJNA (PL11BTS00015)",
            summary="",
            datetime=datetime(2022, 5, 25, 17, 0, 59),
            category=ReportCategory.ESPI,
            type=ReportType.QUARTER,
        ),
        ReportModel(
            gpw_id="396844",
            name="11 BIT STUDIOS SPÓŁKA AKCYJNA (PL11BTS00015)",
            summary="Ogłoszenie o zwołaniu Zwyczajnego Walnego Zgromadzenia 11 bit studios S.A. na dzień\n21 czerwca 2022 roku na godz. 11.00.",  # noqa
            datetime=datetime(2022, 5, 19, 15, 5, 24),
            category=ReportCategory.ESPI,
            type=ReportType.CURRENT,
        ),
        ReportModel(
            gpw_id="396364",
            name="11 BIT STUDIOS SPÓŁKA AKCYJNA (PL11BTS00015)",
            summary="Wybór audytora do badania i przeglądu sprawozdań finansowych Spółki.",
            datetime=datetime(2022, 5, 12, 11, 2, 45),
            category=ReportCategory.ESPI,
            type=ReportType.CURRENT,
        ),
        ReportModel(
            gpw_id="396206",
            name="11 BIT STUDIOS SPÓŁKA AKCYJNA (PL11BTS00015)",
            summary="Przekroczenie progu 5 proc. w ogólnej liczbie akcji i głosów w Spółce",
            datetime=datetime(2022, 5, 10, 15, 31, 18),
            category=ReportCategory.ESPI,
            type=ReportType.CURRENT,
        ),
        ReportModel(
            gpw_id="395113",
            name="11 BIT STUDIOS SPÓŁKA AKCYJNA (PL11BTS00015)",
            summary="Rekomendacja Rady Nadzorczej w sprawie podziału zysku netto wypracowanego w 2021 roku",
            datetime=datetime(2022, 4, 27, 11, 43, 7),
            category=ReportCategory.ESPI,
            type=ReportType.CURRENT,
        ),
        ReportModel(
            gpw_id="394600",
            name="11 BIT STUDIOS SPÓŁKA AKCYJNA (PL11BTS00015)",
            summary='Gra "Moonlighter" w serwisie Netflix',
            datetime=datetime(2022, 4, 20, 16, 1),
            category=ReportCategory.ESPI,
            type=ReportType.CURRENT,
        ),
        ReportModel(
            gpw_id="394566",
            name="11 BIT STUDIOS SPÓŁKA AKCYJNA (PL11BTS00015)",
            summary="Zawiadomienie w trybie art. 19 ust. 1 rozporządzenia MAR",
            datetime=datetime(2022, 4, 20, 10, 24, 22),
            category=ReportCategory.ESPI,
            type=ReportType.CURRENT,
        ),
        ReportModel(
            gpw_id="394386",
            name="11 BIT STUDIOS SPÓŁKA AKCYJNA (PL11BTS00015)",
            summary="Umowa wydawnicza ze State of Play Games Ltd.",
            datetime=datetime(2022, 4, 14, 17, 0, 12),
            category=ReportCategory.ESPI,
            type=ReportType.CURRENT,
        ),
    ]
