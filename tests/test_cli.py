"""CLI orchestration unit testing."""

from unittest.mock import patch
from app.cli import AppCLI


@patch("app.cli.AppCLI.action1")
@patch("app.cli.AppCLI.action2")
def test_all_calls(mock_cli_action1, mock_cli_action2):
    """Test that the cli.all method calls all corresponding methods in order"""
    cli = AppCLI("test_folder")
    cli.all()
    mock_cli_action1.assert_called_once()
    mock_cli_action2.assert_called_once()
