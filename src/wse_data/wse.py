import logging
from datetime import date
from typing import Iterator, Optional, Union

from wse_data.data_scrappers.gpw.company_model import CompanyModel, MarketEnum
from wse_data.data_scrappers.gpw.failed_parsing_element_model import (
    FailedParsingElementModel,
)
from wse_data.data_scrappers.gpw.gpw_client import GPWClient
from wse_data.data_scrappers.gpw.gpw_parser import GPWParser, EmptyPageException
from wse_data.data_scrappers.gpw.report_model import ReportModel
from wse_data.data_scrappers.gpw.stock_quotes_model import StockQuotesModel

logger = logging.getLogger(__name__)


class WSEException(Exception):
    pass


class DateRangeException(WSEException):
    pass


class UnknownMarketException(Exception):
    pass


class WSE:
    _gpw_client: GPWClient
    _new_connect_client: GPWClient
    _gpw_parser: GPWParser
    _new_connect_parser: GPWParser

    def __init__(self) -> None:
        self._gpw_client = GPWClient(market=MarketEnum.GPW)
        self._new_connect_client = GPWClient(market=MarketEnum.NEW_CONNECT)
        self._gpw_parser = GPWParser(market=MarketEnum.GPW)
        self._new_connect_parser = GPWParser(market=MarketEnum.NEW_CONNECT)

    def get_companies(
        self, market: MarketEnum, search: str = ""
    ) -> Iterator[Union[CompanyModel, FailedParsingElementModel]]:
        if market == MarketEnum.GPW:
            client = self._gpw_client
            parser = self._gpw_parser
        elif market == MarketEnum.NEW_CONNECT:
            client = self._new_connect_client
            parser = self._new_connect_parser
        else:
            raise UnknownMarketException(f"Unknown market: {market}.")

        for response_page in client.companies_list(search=search):
            try:
                yield from parser.parse_companies_page(response_page.content)
            except EmptyPageException:
                break

    # TODO: separate markets?
    def get_reports(
        self,
        market: MarketEnum,
        search: str = "",
        date_: Optional[date] = None,
    ) -> Iterator[Union[ReportModel, FailedParsingElementModel]]:
        if market == MarketEnum.GPW:
            client = self._gpw_client
            parser = self._gpw_parser
        elif market == MarketEnum.NEW_CONNECT:
            client = self._new_connect_client
            parser = self._new_connect_parser
        else:
            raise UnknownMarketException(f"Unknown market: {market}.")

        for report_page in client.reports_list(search=search, for_date=date_):
            try:
                yield from parser.parse_reports_page(report_page.content)
            except EmptyPageException:
                break

    def get_stock_quotes(self, date_: date) -> Iterator[StockQuotesModel]:
        # TODO: new connect
        gpw_response = self._gpw_client.stock_quotes(date_)
        if not gpw_response:
            return
        for company_quotes in self._gpw_parser.parse_stock_quotes_xls(gpw_response.content):
            yield company_quotes
