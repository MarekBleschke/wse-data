import logging
import re
from decimal import Decimal
from typing import Iterator, Union
from datetime import datetime
from urllib.parse import parse_qs, urlparse

import xlrd
from bs4 import BeautifulSoup, NavigableString, Tag
from pydantic import ValidationError, BaseModel

from wse_data.data_scrappers.gpw.company_model import MarketEnum, CompanyModel
from wse_data.data_scrappers.gpw.failed_parsing_element_model import FailedParsingElementModel
from wse_data.data_scrappers.gpw.report_model import ReportCategory, ReportType, ReportModel
from wse_data.data_scrappers.gpw.stock_quotes_model import StockQuotesModel

logger = logging.getLogger(__name__)


class GPWParserException(Exception):
    message: str

    def __init__(self, message: str = ""):
        self.message = message


class EmptyPageException(GPWParserException):
    pass


class CompanyIdNotFoundException(GPWParserException):
    pass


class CompanyNameNotFoundException(GPWParserException):
    pass


class CompanySymbolNotFoundException(GPWParserException):
    pass


class FailedToParseReportDataException(GPWParserException):
    pass


class ReportDataTagNotFound(GPWParserException):
    pass


class ReportIdNotFoundException(GPWParserException):
    pass


class ReportSummaryNotFoundException(GPWParserException):
    pass


class ReportNameNotFoundException(GPWParserException):
    pass


class _ReportData(BaseModel):
    datetime: datetime
    category: ReportCategory
    type: ReportType


REPORT_COMPANY_ISIN_RE = re.compile("\(([a-z,A-Z,0-9]*)\)")


class GPWParser:
    market: MarketEnum

    def __init__(self, market: MarketEnum):
        self.market = market

    def parse_companies_page(self, response_page: bytes) -> Iterator[Union[CompanyModel, FailedParsingElementModel]]:
        soup = BeautifulSoup(response_page, "html.parser", from_encoding="utf-8")
        for row in soup.find_all("tr", class_="trclass"):
            try:
                yield CompanyModel(
                    isin=self._parse_company_id(row),
                    name=self._parse_company_name(row),
                    ticker=self._parse_company_ticker(row),
                    market=self.market,
                )
            except (GPWParserException, ValidationError) as exc:
                logger.exception(exc)
                yield FailedParsingElementModel(raw_data=response_page)

    # TODO: consider splitting parsers per page, as they do not have a lot in common.
    def parse_reports_page(self, response_page: bytes) -> Iterator[Union[ReportModel, FailedParsingElementModel]]:
        soup = BeautifulSoup(response_page, "html.parser", from_encoding="utf-8")

        if soup.li is None:
            logger.warning("Parser received empty page.")
            raise EmptyPageException()

        for row in soup.find_all("li"):
            try:
                report_data = self._parse_report_data(row)
                yield ReportModel(
                    gpw_id=self._parse_report_id(row),
                    company_isin=self._parse_report_company_isin(row),
                    name=self._parse_report_name(row),
                    summary=self._parse_report_summary(row),
                    datetime=report_data.datetime,
                    category=report_data.category,
                    type=report_data.type,
                )
            except (GPWParserException, ValidationError) as exc:
                logger.exception(exc)
                yield FailedParsingElementModel(raw_data=response_page)

    def parse_stock_quotes_xls(self, xls_content: bytes) -> Iterator[StockQuotesModel]:
        # TODO: handle empty data (closed market day)
        book = xlrd.open_workbook(file_contents=xls_content)
        sheet = book.sheet_by_index(0)
        # TODO: handle error
        for i in range(1, sheet.nrows):
            row = sheet.row(i)
            yield StockQuotesModel(
                date=datetime.strptime(row[0].value, "%Y-%m-%d"),
                company_name=row[1].value,
                company_isin=row[2].value,
                opening=Decimal(self._parse_xls_float(row[4].value)),
                closing=Decimal(self._parse_xls_float(row[7].value)),
                max=Decimal(self._parse_xls_float(row[5].value)),
                min=Decimal(self._parse_xls_float(row[6].value)),
                volume=int(row[9].value),
            )

    def _parse_xls_float(self, cell_value: float) -> str:
        return str("%0.15g" % cell_value)

    def _parse_company_id(self, company_row: Tag) -> str:
        if self.market == MarketEnum.GPW:
            isin_tag = company_row.find("td", class_="col3")
        else:
            isin_tag = company_row.find("td", class_="col2")
        if not isin_tag:
            raise CompanyIdNotFoundException(f"Failed to parse company id: {company_row}")
        return isin_tag.get_text(strip=True)

    def _parse_company_name(self, company_row: Tag) -> str:
        if self.market == MarketEnum.GPW:
            name_tag = company_row.select(".col2 a")
        else:
            name_tag = company_row.select(".col1 a")
        if not name_tag:
            raise CompanyNameNotFoundException(f"Failed to parse company name: {company_row}")
        return name_tag[0].get_text(strip=True)

    def _parse_company_ticker(self, company_row: Tag) -> str:
        if self.market == MarketEnum.GPW:
            ticker_tag = company_row.find("td", class_="col4")
        else:
            ticker_tag = company_row.find("td", class_="col3")
        if not ticker_tag:
            raise CompanySymbolNotFoundException(f"Failed to parse company ticker: {company_row}")
        return ticker_tag.get_text(strip=True)

    def _parse_report_data(self, report_row: Tag) -> _ReportData:
        data_tag = report_row.find(class_="date")
        if not data_tag:
            raise ReportDataTagNotFound(f"Failed to find data tag: {report_row}")

        cleaned_data = self._get_text_from_soup(data_tag).split(" | ")
        report_date = report_type = report_category = None

        if len(cleaned_data) == 4:
            report_date, report_type, report_category, _ = cleaned_data
        elif len(cleaned_data) == 3:
            report_date, data_elem_1, data_elem_2 = cleaned_data
            for data_elem in [data_elem_1, data_elem_2]:
                if ReportType.has_value(data_elem):
                    report_type = data_elem
                elif ReportCategory.has_value(data_elem):
                    report_category = data_elem
        else:
            raise FailedToParseReportDataException(f"Failed to parse report data: {report_row}")

        if report_category is None:
            report_category = "Inny"
        if report_type is None:
            report_type = "Inny"

        return _ReportData(
            datetime=datetime.strptime(report_date, "%d-%m-%Y %H:%M:%S"),
            category=report_category,
            type=report_type,
        )

    def _parse_report_id(self, report_row: Tag) -> str:
        anchor = report_row.find("a", href=re.compile("geru_id="))
        if not anchor:
            raise ReportIdNotFoundException(f"Failed to find report id: {report_row}")
        return parse_qs(urlparse(anchor["href"]).query)["geru_id"][0]  # type: ignore

    def _parse_report_company_isin(self, report_row: Tag) -> str:
        name_tag = report_row.select(".name a")
        if not name_tag:
            raise ReportNameNotFoundException(f"Failed to find report company isin: {report_row}")
        name_str = self._get_text_from_soup(name_tag[0])
        groups = re.search(REPORT_COMPANY_ISIN_RE, name_str)
        try:
            return groups[1]
        except IndexError:
            raise ReportNameNotFoundException(f"Failed to match report company isin: {report_row}")

    def _parse_report_name(self, report_row: Tag) -> str:
        name_tag = report_row.select(".name a")
        if not name_tag:
            raise ReportNameNotFoundException(f"Failed to find report name: {report_row}")
        return self._get_text_from_soup(name_tag[0])

    def _parse_report_summary(self, report_row: Tag) -> str:
        summary = report_row.find("p")
        if not summary:
            raise ReportSummaryNotFoundException(f"Failed to find report summary: {report_row}")
        return self._get_text_from_soup(summary)

    def _get_text_from_soup(self, soup: Union[Tag, NavigableString]) -> str:
        return "".join([t for t in soup if isinstance(t, NavigableString)]).strip()
