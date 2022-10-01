import logging
from datetime import date
from enum import Enum, auto
from typing import Iterator, Optional, Union

import httpx
from httpx import Timeout

from src.data_scrappers.gpw.gpw_config import GPWConfig
from src.data_scrappers.gpw.new_connect_config import NewConnectConfig

logger = logging.getLogger(__name__)


class UnmappedEnumException(Exception):
    pass


class MarketEnum(Enum):
    GPW = auto()
    NEW_CONNECT = auto()


class GPWClient:
    _market: MarketEnum
    config: Union[GPWConfig, NewConnectConfig]

    def __init__(self, market: MarketEnum) -> None:
        self._market = market
        if market == MarketEnum.GPW:
            self.config = GPWConfig()
        elif market == MarketEnum.NEW_CONNECT:
            self.config = NewConnectConfig()

    def companies_list(self) -> Iterator[httpx.Response]:
        limit = 50
        offset = 0
        company_entry_str = b"<tr>"  # for checking of empty responses and counting entries for paging

        while True:
            query_params: dict[str, str | int] = {
                "offset": offset,
                "limit": limit,
            }
            query_params.update(self.config.companies_query_params)
            response = httpx.post(self.config.companies_url, data=query_params, timeout=Timeout(timeout=10.0))

            company_entries_count = self._get_entries_count(response.content, company_entry_str)

            # Empty page.
            if company_entries_count == 0:
                break

            offset += limit

            yield response

            # Last page.
            if company_entries_count < limit:
                break

    # TODO: a lot of code the same as companies_list. Abstract common code, add retry and other stuff.
    def reports_list(self, search: str = "", for_date: Optional[date] = None) -> Iterator[httpx.Response]:
        limit = 20
        offset = 0
        report_entry_str = b"<li"

        while True:
            query_params = {
                "limit": limit,
                "offset": offset,
                "searchText": search,
            }
            if for_date:
                query_params["date"] = for_date.strftime("%d-%m-%Y")
            query_params.update(self.config.reports_query_params)
            response = httpx.post(self.config.reports_url, data=query_params, timeout=Timeout(timeout=10.0))

            report_entries_count = self._get_entries_count(response.content, report_entry_str)

            # Empty page.
            if report_entries_count == 0:
                break

            offset += limit

            yield response

            # Last page.
            if report_entries_count < limit:
                break

    def _get_entries_count(self, content: bytes, entry_string: bytes) -> int:
        return content.count(entry_string)
