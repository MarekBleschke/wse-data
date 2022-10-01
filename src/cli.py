"""Console script for wse-data."""
import logging
from datetime import datetime

import typer

from rich import print

from src.data_scrappers.gpw.failed_parsing_element_model import FailedParsingElementModel
from src.wse import WSE


app = typer.Typer()
companies_app = typer.Typer()
app.add_typer(companies_app, name="companies")
reports_app = typer.Typer()
app.add_typer(reports_app, name="reports")


@app.callback()
def main() -> None:
    """
    Welcome to WSE Data CLI.
    """
    # NOTE: logging only for WSE usage as library. We don't want to clutter console output.
    logging.disable(logging.CRITICAL)


@companies_app.command(name="list")
def companies_list() -> None:
    wse = WSE()
    companies = wse.get_companies()
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
    search: str = typer.Option("", help="Search phrase."),
    date_from: datetime = typer.Option(None, "--from", formats=["%Y-%m-%d"], help="Search from"),
    date_to: datetime = typer.Option(None, "--to", formats=["%Y-%m-%d"], help="Search to"),
) -> None:
    if date_from:
        date_from = date_from.date()  # type: ignore
    if date_to:
        date_to = date_to.date()  # type: ignore
    wse = WSE()
    reports = wse.get_reports(search=search, date_from=date_from, date_to=date_to)
    for report in reports:
        print(report)


if __name__ == "__main__":
    app()  # pragma: no cover
