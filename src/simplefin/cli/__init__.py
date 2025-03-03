import datetime
import json
import os
from typing import Optional

# from datetime import date
import click
from rich.console import Console
from rich.pretty import pprint
from rich.table import Table

from simplefin.client import SimpleFINClient


def epoch_to_datetime(epoch: int) -> datetime:
    return datetime.datetime.fromtimestamp(epoch, tz=datetime.timezone.utc)


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
@click.option(
    "--format",
    type=click.Choice(["json", "table"], case_sensitive=False),
    default="table",
    help="Specify output format",
)
def accounts(format: str) -> None:
    c = SimpleFINClient(access_url=os.getenv("SIMPLEFIN_ACCESS_URL"))
    accounts = c.get_accounts()

    if format == "json":
        console = Console()
        console.print(json.dumps(accounts, indent=4, cls=DateTimeEncoder))
    else:
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
    help="Number of days to look back for transactions (default: 7, ignored if --start-date is provided)",
)
@click.option(
    "--start-date",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    help="Specific start date for transactions (YYYY-MM-DD format). Takes precedence over lookback-days.",
)
@click.option(
    "--end-date",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    help="Specific end date for transactions (YYYY-MM-DD format). If provided, --start-date must also be provided.",
)
@click.option(
    "--format",
    type=click.Choice(["json", "table"], case_sensitive=False),
    default="table",
    help="Specify output format",
)
def transactions(
    account_id: str,
    format: str,
    lookback_days: int,
    start_date: Optional[datetime.datetime],
    end_date: Optional[datetime.datetime],
) -> None:
    c = SimpleFINClient(access_url=os.getenv("SIMPLEFIN_ACCESS_URL"))

    # Validate that if end_date is provided, start_date is also provided
    if end_date and not start_date:
        raise click.UsageError(
            "If --end-date is provided, --start-date must also be provided."
        )

    # Use the specific start_date if provided, otherwise calculate from lookback days
    if start_date:
        start_dt = start_date.date()
    else:
        start_dt = datetime.date.today() - datetime.timedelta(days=lookback_days)

    # Use provided end_date or default to today
    end_dt = end_date.date() if end_date else datetime.date.today()

    # Validate that end_date is not before start_date
    if end_dt < start_dt:
        raise click.UsageError("End date cannot be before start date.")

    resp = c.get_transactions(account_id, start_dt, end_dt)

    console = Console()

    if format == "json":
        console.print(json.dumps(resp, indent=4))
    else:
        if len(resp["accounts"]) == 0:
            console.print("No transactions found")
            return

        table = Table(title=f"Transactions for {account_id}")
        table.add_column("Date")
        table.add_column("Payee")
        table.add_column("Amount")

        for txn in resp["accounts"][0]["transactions"]:
            table.add_row(
                epoch_to_datetime(txn["posted"]).strftime("%d %b %Y"),
                txn["payee"],
                str(txn["amount"]),
            )

        console.print(table)


@cli.command()
def info() -> None:
    c = SimpleFINClient(access_url=os.getenv("SIMPLEFIN_ACCESS_URL"))
    info = c.get_info()
    pprint(info)


if __name__ == "__main__":
    cli()
