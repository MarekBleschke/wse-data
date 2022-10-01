from datetime import date

import pytest

from src.data_scrappers.gpw.failed_parsing_element_model import FailedParsingElementModel
from src.data_scrappers.gpw.report_model import ReportModel
from src.wse import WSE


@pytest.fixture
def wse() -> WSE:
    return WSE()


def test_get_companies(wse):
    # when
    companies = list(wse.get_companies())
    failed_parsing = [company for company in companies if isinstance(company, FailedParsingElementModel)]

    # then
    assert len(failed_parsing) < len(companies) * 0.05


def test_get_reports(wse):
    # when
    report = next(wse.get_reports())

    # then
    assert isinstance(report, ReportModel)


def test_get_reports_search(wse):
    # when
    # GPW company
    reports_generator = wse.get_reports(search="cd projekt")

    # then
    for i in range(10):
        report = next(reports_generator)
        assert "cd projekt" in report.name.lower()

    # when
    # NewConnect company
    reports_generator = wse.get_reports(search="CREATIVEFORGE GAMES")

    # then
    for i in range(10):
        report = next(reports_generator)
        assert "creativeforge games" in report.name.lower()


def test_get_reports_for_date_range(wse):
    # given
    date_from = date(2022, 6, 28)
    date_to = date(2022, 6, 29)
    search = "cd projekt"

    # when
    reports_generator = wse.get_reports(search=search, date_from=date_from, date_to=date_to)
    first = next(reports_generator)
    last = None
    while True:
        try:
            last = next(reports_generator)
        except StopIteration:
            break
        if last.datetime.date() < date_from:
            pytest.fail(f"Report with datetime: '{last.datetime}' is later than date_to: '{date_to}'")
            return

    # then
    assert first.datetime.date() == date_from
    assert last.datetime.date() == date_to
