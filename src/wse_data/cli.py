"""Console script for wse-data."""
import logging
from datetime import datetime

import typer

from rich import print

from wse_data.data_scrappers.gpw.company_model import MarketEnum
from wse_data.data_scrappers.gpw.failed_parsing_element_model import (
    FailedParsingElementModel,
)
from wse_data.wse import WSE


app = typer.Typer()
companies_app = typer.Typer()
app.add_typer(companies_app, name="companies")
reports_app = typer.Typer()
app.add_typer(reports_app, name="reports")
quotes_app = typer.Typer()
app.add_typer(quotes_app, name="quotes")


@app.callback()
def main() -> None:
    """
    Welcome to WSE Data CLI.
    """
    # NOTE: logging only for WSE usage as library. We don't want to clutter console output.
    logging.disable(logging.CRITICAL)


@companies_app.command(name="list")
def companies_list(
    market: MarketEnum = typer.Option(MarketEnum.GPW, case_sensitive=False),
    search: str = typer.Option("", help="Search phrase."),
) -> None:
    wse = WSE()
    companies = wse.get_companies(market=market, search=search)
    failed_companies = []
    for company in companies:
        if isinstance(company, FailedParsingElementModel):
            failed_companies.append(company)
            continue
        print(company)
    if failed_companies:
        print(f"There were {len(failed_companies)} companies that failed parsing.")


@reports_app.command(name="list")
def report_list(
    market: MarketEnum = typer.Option(MarketEnum.GPW, case_sensitive=False),
    search: str = typer.Option("", help="Search phrase."),
    date_: datetime = typer.Option(None, "--date", formats=["%Y-%m-%d"], help="Search for date"),
) -> None:
    if date_:
        date_ = date_.date()  # type: ignore
    wse = WSE()
    reports = wse.get_reports(market=market, search=search, date_=date_)
    for report in reports:
        print(report)


@quotes_app.command(name="list")
def quotes(date_: datetime = typer.Option(None, "--date", formats=["%Y-%m-%d"], help="Search from")) -> None:
    date_ = date_.date()  # type: ignore
    wse = WSE()
    # TODO: print info when empty response from client
    for quote in wse.get_stock_quotes(date_):
        print(quote)


if __name__ == "__main__":
    app()  # pragma: no cover
