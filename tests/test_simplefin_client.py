import base64
import datetime
import json

import httpx
import pytest_httpx

from simplefin.client import SimpleFINClient


def test_get_access_url(httpx_mock: pytest_httpx.HTTPXMock):
    claim_url = "https://mock-simplefin/claim"
    setup_token = base64.b64encode(claim_url.encode("utf-8")).decode("utf-8")
    access_url = "https://mock-simplefin/access"

    httpx_mock.add_response(method="POST", url=claim_url, text=access_url)

    result = SimpleFINClient.get_access_url(setup_token)
    assert result == access_url


def test_get_accounts(httpx_mock: pytest_httpx.HTTPXMock):
    access_url = "https://mock-simplefin/access"
    client = SimpleFINClient(access_url=access_url)
    with open("tests/fixtures/accounts.json") as f:
        accounts_response = json.load(f)

    httpx_mock.add_response(
        method="GET",
        url=f"{access_url}/accounts?balances-only=1",
        json=accounts_response,
    )

    accounts = client.get_accounts()
    assert len(accounts) == 2
    assert accounts[0]["name"] == "SimpleFIN Savings"
    assert accounts[1]["name"] == "SimpleFIN Checking"


def test_get_account(httpx_mock: pytest_httpx.HTTPXMock):
    access_url = "https://mock-simplefin/access"
    client = SimpleFINClient(access_url=access_url)
    account_id = "Demo Savings"
    with open("tests/fixtures/account.json") as f:
        account_response = json.load(f)

    httpx_mock.add_response(
        method="GET",
        url=f"{access_url}/accounts?account={account_id}&balances-only=1",
        json=account_response,
    )

    account = client.get_account(account_id)
    assert account["name"] == "SimpleFIN Savings"
    assert account["id"] == account_id


def test_get_transactions(httpx_mock: pytest_httpx.HTTPXMock):
    access_url = "https://mock-simplefin/access"
    client = SimpleFINClient(access_url=access_url)
    account_id = "Demo Savings"
    start_date = datetime.date(2025, 1, 9)
    with open("tests/fixtures/transactions.json") as f:
        transactions_response = json.load(f)

    httpx_mock.add_response(
        method="GET",
        url=f"{access_url}/accounts?account={account_id}&start-date={int(datetime.datetime.combine(start_date, datetime.time.min).timestamp())}",
        json=transactions_response,
    )

    transactions = client.get_transactions(account_id, start_date)
    assert len(transactions) == 4
    assert transactions[0]["payee"] == "John's Fishin Shack"
    assert transactions[1]["payee"] == "Grocery store"


def test_get_info(httpx_mock: httpx.MockTransport):
    access_url = "https://mock-simplefin/access"
    client = SimpleFINClient(access_url=access_url)
    with open("tests/fixtures/info.json") as f:
        info_response = json.load(f)

    httpx_mock.add_response(method="GET", url=f"{access_url}/info", json=info_response)

    info = client.get_info()
    assert info["versions"] == ["1.0"]
