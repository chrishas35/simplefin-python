import datetime
import json
import os
from datetime import date

import click
from rich.console import Console
from rich.pretty import pprint
from rich.table import Table

from simplefin.client import SimpleFINClient


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return super().default(obj)


@click.group()
def cli():
    pass


@cli.command()
def setup() -> None:
    setup_token = click.prompt("Please provide your setup token", type=str)
    access_url = SimpleFINClient.get_access_url(setup_token)

    console = Console()
    console.print(f"\nAccess URL: {access_url}\n")
    console.print(
        "For security reasons we do not store the access_url on disk for you."
    )
    console.print(
        "Please securely store for future usage of simplefin as setup tokens are not reusable."
    )


@cli.command()
def accounts() -> None:
    c = SimpleFINClient(access_url=os.getenv("SIMPLEFIN_ACCESS_URL"))
    accounts = c.get_accounts()
    table = Table(title="SimpleFIN Accounts")
    table.add_column("Institution")
    table.add_column("Account")
    table.add_column("Balance")
    table.add_column("Account ID")

    for account in accounts:
        table.add_row(
            account["org"]["name"],
            account["name"],
            str(account["balance"]),
            account["id"],
        )

    console = Console()
    console.print(table)


# TODO: Add date range option
@cli.command()
@click.argument("account_id", type=str)
@click.option(
    "lookback_days",
    "--lookback-days",
    type=int,
    default=7,
    help="Number of days to look back for transactions",
)
@click.option(
    "--format",
    type=click.Choice(["json", "table"], case_sensitive=False),
    default="table",
    help="Specify output format",
)
def transactions(account_id: str, format: str, lookback_days: int) -> None:
    c = SimpleFINClient(access_url=os.getenv("SIMPLEFIN_ACCESS_URL"))
    start_dt = date.today() - datetime.timedelta(days=lookback_days)
    transactions = c.get_transactions(account_id, start_dt)

    if format == "json":
        console = Console()
        console.print(json.dumps(transactions, indent=4, cls=DateTimeEncoder))
    else:
        table = Table(title=f"Transactions for {account_id}")
        table.add_column("Date")
        table.add_column("Payee")
        table.add_column("Amount")

        for txn in transactions:
            table.add_row(
                txn["posted"].strftime("%d %b %Y"), txn["payee"], str(txn["amount"])
            )

        console = Console()
        console.print(table)


@cli.command()
def info() -> None:
    c = SimpleFINClient(access_url=os.getenv("SIMPLEFIN_ACCESS_URL"))
    info = c.get_info()
    pprint(info)


if __name__ == "__main__":
    cli()
