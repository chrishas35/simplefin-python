import datetime
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from simplefin.cli import cli


@pytest.fixture
def mock_accounts():
    """Sample accounts response."""
    return [
        {
            "org": {
                "domain": "beta-bridge.simplefin.org",
                "name": "SimpleFIN Demo",
            },
            "id": "ACT-savings-123",
            "name": "SimpleFIN Savings",
            "currency": "USD",
            "balance": "1000.00",
            "balance-date": 1736553600,
        },
        {
            "org": {
                "domain": "beta-bridge.simplefin.org",
                "name": "SimpleFIN Demo",
            },
            "id": "ACT-checking-456",
            "name": "SimpleFIN Checking",
            "currency": "USD",
            "balance": "500.00",
            "balance-date": 1736553600,
        },
    ]


@pytest.fixture
def mock_transactions():
    """Sample transactions response."""
    return [
        {
            "id": "TRN-001",
            "posted": datetime.datetime(2025, 1, 10, 12, 0, 0),
            "amount": "-50.00",
            "description": "Test transaction",
            "payee": "Test Payee",
        },
    ]


class TestFetchCommand:
    """Tests for the fetch CLI command."""

    def test_fetch_creates_directory_structure(self, mock_accounts, mock_transactions):
        """Test that fetch creates the correct directory structure."""
        runner = CliRunner()

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict(os.environ, {"SIMPLEFIN_ACCESS_URL": "https://mock"}):
                with patch("simplefin.cli.SimpleFINClient") as MockClient:
                    mock_client = MockClient.return_value
                    mock_client.get_accounts.return_value = mock_accounts
                    mock_client.get_transactions.return_value = mock_transactions

                    result = runner.invoke(
                        cli,
                        ["fetch", "--output-dir", tmpdir, "--lookback-days", "7"],
                    )

                    assert result.exit_code == 0
                    assert "Found 2 accounts" in result.output

                    # Check directory structure
                    inst_dir = Path(tmpdir) / "beta-bridge.simplefin.org"
                    assert inst_dir.exists()

                    savings_dir = inst_dir / "SimpleFIN-Savings"
                    checking_dir = inst_dir / "SimpleFIN-Checking"
                    assert savings_dir.exists()
                    assert checking_dir.exists()

    def test_fetch_creates_json_files_with_correct_naming(
        self, mock_accounts, mock_transactions
    ):
        """Test that JSON files are created with correct naming convention."""
        runner = CliRunner()
        today = datetime.date.today().isoformat()

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict(os.environ, {"SIMPLEFIN_ACCESS_URL": "https://mock"}):
                with patch("simplefin.cli.SimpleFINClient") as MockClient:
                    mock_client = MockClient.return_value
                    mock_client.get_accounts.return_value = mock_accounts
                    mock_client.get_transactions.return_value = mock_transactions

                    result = runner.invoke(
                        cli,
                        ["fetch", "--output-dir", tmpdir, "--lookback-days", "7"],
                    )

                    assert result.exit_code == 0

                    # Check file naming
                    savings_file = (
                        Path(tmpdir)
                        / "beta-bridge.simplefin.org"
                        / "SimpleFIN-Savings"
                        / f"ACT-savings-123_{today}.json"
                    )
                    assert savings_file.exists()

    def test_fetch_json_contains_account_and_transactions(
        self, mock_accounts, mock_transactions
    ):
        """Test that JSON files contain both account metadata and transactions."""
        runner = CliRunner()
        today = datetime.date.today().isoformat()

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict(os.environ, {"SIMPLEFIN_ACCESS_URL": "https://mock"}):
                with patch("simplefin.cli.SimpleFINClient") as MockClient:
                    mock_client = MockClient.return_value
                    mock_client.get_accounts.return_value = mock_accounts
                    mock_client.get_transactions.return_value = mock_transactions

                    result = runner.invoke(
                        cli,
                        ["fetch", "--output-dir", tmpdir, "--lookback-days", "7"],
                    )

                    assert result.exit_code == 0

                    # Read and verify JSON content
                    savings_file = (
                        Path(tmpdir)
                        / "beta-bridge.simplefin.org"
                        / "SimpleFIN-Savings"
                        / f"ACT-savings-123_{today}.json"
                    )

                    with open(savings_file) as f:
                        data = json.load(f)

                    # Check account metadata
                    assert data["id"] == "ACT-savings-123"
                    assert data["name"] == "SimpleFIN Savings"
                    assert data["currency"] == "USD"
                    assert data["balance"] == "1000.00"

                    # Check transactions were merged
                    assert "transactions" in data
                    assert len(data["transactions"]) == 1
                    assert data["transactions"][0]["id"] == "TRN-001"

    def test_fetch_handles_duplicate_account_names(self, mock_transactions):
        """Test that accounts with the same name get unique files."""
        runner = CliRunner()
        today = datetime.date.today().isoformat()

        # Two accounts with the same name but different IDs
        accounts_with_duplicates = [
            {
                "org": {"domain": "example.com", "name": "Example Bank"},
                "id": "ACT-111",
                "name": "Checking",
                "currency": "USD",
                "balance": "100.00",
                "balance-date": 1736553600,
            },
            {
                "org": {"domain": "example.com", "name": "Example Bank"},
                "id": "ACT-222",
                "name": "Checking",
                "currency": "USD",
                "balance": "200.00",
                "balance-date": 1736553600,
            },
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict(os.environ, {"SIMPLEFIN_ACCESS_URL": "https://mock"}):
                with patch("simplefin.cli.SimpleFINClient") as MockClient:
                    mock_client = MockClient.return_value
                    mock_client.get_accounts.return_value = accounts_with_duplicates
                    mock_client.get_transactions.return_value = []

                    result = runner.invoke(
                        cli,
                        ["fetch", "--output-dir", tmpdir, "--lookback-days", "7"],
                    )

                    assert result.exit_code == 0

                    # Both files should exist in the same directory
                    checking_dir = Path(tmpdir) / "example.com" / "Checking"
                    files = list(checking_dir.glob("*.json"))
                    assert len(files) == 2

                    # Files should have different account IDs in names
                    file_names = [f.name for f in files]
                    assert f"ACT-111_{today}.json" in file_names
                    assert f"ACT-222_{today}.json" in file_names

    def test_fetch_requires_output_dir(self):
        """Test that --output-dir is required."""
        runner = CliRunner()

        with patch.dict(os.environ, {"SIMPLEFIN_ACCESS_URL": "https://mock"}):
            result = runner.invoke(cli, ["fetch"])

            assert result.exit_code != 0
            assert "Missing option '--output-dir'" in result.output

    def test_fetch_requires_access_url_env(self):
        """Test that SIMPLEFIN_ACCESS_URL environment variable is required."""
        runner = CliRunner()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Ensure env var is not set
            env = os.environ.copy()
            env.pop("SIMPLEFIN_ACCESS_URL", None)

            with patch.dict(os.environ, env, clear=True):
                result = runner.invoke(
                    cli,
                    ["fetch", "--output-dir", tmpdir],
                )

                # Should fail because no access URL
                assert result.exit_code != 0
