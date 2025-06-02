"""CLI orchestration unit testing."""

import pytest
from unittest.mock import patch
from app.cli import AppCLI


@patch("app.cli.AppCLI.generatedb")
@patch("app.cli.AppCLI.ask")
@pytest.mark.filterwarnings("ignore:DeprecationWarning")
def test_all_calls(mock_cli_generatedb, mock_cli_ask):
    """Test that the cli.all method calls all corresponding methods in order"""
    cli = AppCLI("test_folder")
    cli.all()
    mock_cli_generatedb.assert_called_once()
    mock_cli_ask.assert_called_once()
