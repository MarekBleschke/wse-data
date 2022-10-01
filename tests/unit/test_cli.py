import io
from typing import Any

from typer.testing import CliRunner
from unittest.mock import patch
from datetime import datetime
from rich import print

from src.cli import app, WSE
from src.data_scrappers.gpw.company_model import CompanyModel, MarketEnum
from src.data_scrappers.gpw.report_model import ReportModel, ReportCategory, ReportType

runner = CliRunner()


def test_companies_list_prints_companies():
    # given
    get_companies_return_value = [
        CompanyModel(gpw_id="1", name="11 BIT", ticker="11B", market=MarketEnum.GPW),
        CompanyModel(gpw_id="2", name="Ambra", ticker="AMB", market=MarketEnum.GPW),
    ]

    # when
    with patch.object(WSE, "get_companies", return_value=get_companies_return_value) as mocked:
        result = runner.invoke(app, ["companies", "list"])

        # then
        assert mocked.call_count == 1
        assert _get_rich_print_text(get_companies_return_value[0]) in result.stdout
        assert _get_rich_print_text(get_companies_return_value[1]) in result.stdout


def test_reports_list_prints_reports():
    # given
    get_reports_return_value = [
        ReportModel(
            gpw_id="1",
            name="report 1",
            summary="summary 1",
            datetime=datetime(2022, 2, 23, 11, 12, 43),
            category=ReportCategory.ESPI,
            type=ReportType.CURRENT,
        ),
        ReportModel(
            gpw_id="2",
            name="report 2",
            summary="summary 2",
            datetime=datetime(2021, 5, 12, 12, 32, 1),
            category=ReportCategory.EBI,
            type=ReportType.QUARTER,
        ),
    ]

    # when
    with patch.object(WSE, "get_reports", return_value=get_reports_return_value) as mocked:
        result = runner.invoke(app, ["reports", "list"])

        # then
        assert mocked.call_count == 1
        assert _get_rich_print_text(get_reports_return_value[0]) in result.stdout
        assert _get_rich_print_text(get_reports_return_value[1]) in result.stdout


def _get_rich_print_text(to_print: Any) -> str:
    stream = io.StringIO()
    print(to_print, file=stream, flush=True)
    stream.seek(0)
    return stream.read()
