import datetime
import json
import os

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
    start_dt = datetime.date.today() - datetime.timedelta(days=lookback_days)
    resp = c.get_transactions(account_id, start_dt)

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


@cli.command()
@click.option(
    "--output-dir",
    type=click.Path(file_okay=False, dir_okay=True),
    required=True,
    help="Directory to output per-account JSON files",
)
@click.option(
    "lookback_days",
    "--lookback-days",
    type=int,
    default=30,
    help="Number of days to look back for transactions (default: 30)",
)
def fetch(output_dir: str, lookback_days: int) -> None:
    """Fetch all accounts with transactions to separate JSON files.

    Creates one JSON file per account in the output directory, organized by
    institution and account name:

        <output-dir>/<institution-domain>/<account-name>/<account-id>_<date>.json

    This structure is human-navigable and preserves history. It's useful for
    integration with tools like beangulp that expect one file per account.
    """
    import pathlib

    def sanitize_path(name: str) -> str:
        """Sanitize a string for use as a directory/file name."""
        safe = "".join(ch if ch.isalnum() or ch in "-_." else "-" for ch in name)
        # Collapse multiple dashes and strip leading/trailing dashes
        while "--" in safe:
            safe = safe.replace("--", "-")
        return safe.strip("-")

    c = SimpleFINClient(access_url=os.getenv("SIMPLEFIN_ACCESS_URL"))
    console = Console()

    # Get list of accounts (with balance info but no transactions)
    accounts = c.get_accounts()
    console.print(f"Found {len(accounts)} accounts")

    # Create output directory
    output_path = pathlib.Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Fetch transactions for each account
    start_dt = datetime.date.today() - datetime.timedelta(days=lookback_days)
    today_str = datetime.date.today().isoformat()

    for account in accounts:
        account_id = account["id"]
        account_name = account["name"]
        org_domain = account.get("org", {}).get("domain", "unknown")

        # Fetch transactions for this account
        # get_transactions returns a list of transaction dicts
        transactions = c.get_transactions(account_id, start_dt)

        # Merge account metadata with transactions
        account_data = account.copy()
        account_data["transactions"] = transactions if isinstance(transactions, list) else []

        # Build directory structure: <institution>/<account-name>/
        inst_dir = output_path / sanitize_path(org_domain)
        acct_dir = inst_dir / sanitize_path(account_name)
        acct_dir.mkdir(parents=True, exist_ok=True)

        # Filename: <account-id>_<date>.json
        filename = f"{account_id}_{today_str}.json"
        filepath = acct_dir / filename

        with open(filepath, "w") as f:
            json.dump(account_data, f, indent=2, cls=DateTimeEncoder)

        txn_count = len(account_data.get("transactions", []))
        rel_path = filepath.relative_to(output_path)
        console.print(f"  {account_name}: {txn_count} transactions -> {rel_path}")

    console.print(f"\nWrote {len(accounts)} account files to {output_dir}")


if __name__ == "__main__":
    cli()
