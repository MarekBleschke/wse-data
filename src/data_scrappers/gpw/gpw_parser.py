import logging
import re
from typing import Iterator, Union
from datetime import datetime
from urllib.parse import parse_qs, urlparse

from bs4 import BeautifulSoup, NavigableString, Tag
from pydantic import ValidationError, BaseModel

from src.data_scrappers.gpw.company_model import CompanyModel, MarketEnum
from src.data_scrappers.gpw.failed_parsing_element_model import (
    FailedParsingElementModel,
)
from src.data_scrappers.gpw.report_model import ReportModel, ReportCategory, ReportType

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


class GPWParser:
    market: MarketEnum

    def __init__(self, market: MarketEnum):
        self.market = market

    def parse_companies_page(self, response_page: bytes) -> Iterator[Union[CompanyModel, FailedParsingElementModel]]:
        soup = BeautifulSoup(response_page, "html.parser", from_encoding="utf-8")

        if soup.tr is None:
            logger.warning("Parser received empty page.")
            raise EmptyPageException()

        for row in soup.find_all("tr"):
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
                    name=self._parse_report_name(row),
                    summary=self._parse_report_summary(row),
                    datetime=report_data.datetime,
                    category=report_data.category,
                    type=report_data.type,
                )
            except (GPWParserException, ValidationError) as exc:
                logger.exception(exc)
                yield FailedParsingElementModel(raw_data=response_page)

    def _parse_company_id(self, company_row: Tag) -> str:
        anchor = company_row.find("a", href=re.compile("isin="))
        if not anchor:
            raise CompanyIdNotFoundException(f"Failed to parse company id: {company_row}")
        return anchor["href"].strip("spolka?isin=")  # type: ignore

    def _parse_company_name(self, company_row: Tag) -> str:
        name_tag = company_row.find(class_="name")
        if not name_tag:
            raise CompanyNameNotFoundException(f"Failed to parse company name: {company_row}")
        return self._get_text_from_soup(name_tag)

    def _parse_company_ticker(self, company_row: Tag) -> str:
        ticker_tag = company_row.select(".name > span")
        if not ticker_tag:
            raise CompanySymbolNotFoundException(f"Failed to parse company ticker: {company_row}")
        return ticker_tag[0].get_text(strip=True).replace("(", "").replace(")", "")

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
