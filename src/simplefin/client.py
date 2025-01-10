import logging
from base64 import b64decode
from datetime import date, datetime, timezone
from functools import wraps
from typing import Optional

import httpx

logger = logging.getLogger(__name__)


def epoch_to_datetime(epoch: int) -> datetime:
    return datetime.fromtimestamp(epoch, tz=timezone.utc)


# TODO: Custom exception, if still required?
def ensure_client_initialized(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.client or not self.client.base_url:
            raise Exception(
                "Client not initialized. Be sure you pass an access_ur when initializing the client."
            )
        return func(self, *args, **kwargs)

    return wrapper


class SimpleFINClient(object):
    def __init__(
        self,
        access_url: Optional[str] = None,
        http_client: Optional[httpx.Client] = None,
    ):
        self.client = http_client or httpx.Client(base_url=access_url, timeout=30)

    @staticmethod
    def get_access_url(setup_token: str):
        claim_url = b64decode(setup_token).decode("utf-8")
        response = httpx.post(claim_url)

        if response.status_code == 403:
            raise Exception("Invalid setup token")
        else:
            response.raise_for_status()

        access_url = response.text
        return access_url

    @ensure_client_initialized
    def get_accounts(self):
        response = self.client.get("/accounts", params={"balances-only": 1})
        response.raise_for_status()
        return response.json()["accounts"]

    @ensure_client_initialized
    def get_account(self, account_id: str):
        response = self.client.get(
            "/accounts", params={"account": account_id, "balances-only": 1}
        )
        response.raise_for_status()
        accounts = response.json()["accounts"]
        return accounts[0] if accounts else None

    @ensure_client_initialized
    def get_transactions(self, account_id: str, start_date: date):
        dt = datetime.combine(start_date, datetime.min.time())
        response = self.client.get(
            "/accounts",
            params={"account": account_id, "start-date": int(dt.timestamp())},
        )
        response.raise_for_status()

        transactions = response.json()["accounts"][0]["transactions"]

        for transaction in transactions:
            if "posted" in transaction.keys():
                transaction["posted"] = epoch_to_datetime(transaction["posted"])
            if "transacted_at" in transaction.keys():
                transaction["transacted_at"] = epoch_to_datetime(
                    transaction["transacted_at"]
                )

        return transactions

    @ensure_client_initialized
    def get_info(self):
        response = self.client.get("/info")
        response.raise_for_status()
        return response.json()
