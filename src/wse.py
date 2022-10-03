import logging
from datetime import date
from itertools import chain
from typing import Iterator, Optional, Union

from src.data_scrappers.gpw.company_model import CompanyModel, MarketEnum
from src.data_scrappers.gpw.failed_parsing_element_model import (
    FailedParsingElementModel,
)
from src.data_scrappers.gpw.gpw_client import GPWClient
from src.data_scrappers.gpw.gpw_parser import GPWParser, EmptyPageException
from src.data_scrappers.gpw.report_model import ReportModel
from src.data_scrappers.utils import date_range

logger = logging.getLogger(__name__)


class WSEException(Exception):
    pass


class DateRangeException(WSEException):
    pass


class WSE:
    _gpw_client: GPWClient
    _new_connect_client: GPWClient
    _gpw_parser: GPWParser

    def __init__(self) -> None:
        self._gpw_client = GPWClient(market=MarketEnum.GPW)
        self._new_connect_client = GPWClient(market=MarketEnum.NEW_CONNECT)
        self._gpw_parser = GPWParser(market=MarketEnum.GPW)
        self._new_connect_parser = GPWParser(market=MarketEnum.NEW_CONNECT)

    def get_companies(self, search: str = "") -> Iterator[Union[CompanyModel, FailedParsingElementModel]]:
        for response_page in self._gpw_client.companies_list(search=search):
            try:
                yield from self._gpw_parser.parse_companies_page(response_page.content)
            except EmptyPageException:
                break
        for response_page in self._new_connect_client.companies_list(search=search):
            try:
                yield from self._new_connect_parser.parse_companies_page(response_page.content)
            except EmptyPageException:
                break

    def get_reports(
        self,
        search: str = "",
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> Iterator[Union[ReportModel, FailedParsingElementModel]]:
        if any([date_from, date_to]) and not all([date_from, date_to]):
            raise DateRangeException(
                f"When passing date_from or date_to both are required: date_from - '{date_from}', date_to: '{date_to}'"
            )

        if date_from and date_to:
            for search_date in date_range(date_from, date_to):
                yield from self._get_reports(search, search_date)
        else:
            yield from self._get_reports(search)

    def _get_reports(
        self, search: str = "", search_date: Optional[date] = None
    ) -> Iterator[Union[ReportModel, FailedParsingElementModel]]:
        reports_generators = chain(
            self._gpw_client.reports_list(search=search, for_date=search_date),
            self._new_connect_client.reports_list(search=search, for_date=search_date),
        )
        for response_page in reports_generators:
            try:
                yield from self._gpw_parser.parse_reports_page(response_page.content)
            except EmptyPageException:
                break
