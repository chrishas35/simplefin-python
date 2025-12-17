# SimpleFIN Python Library

## Installation

`pip install simplefin`

## Command line interface

### Setup

You will first need to get a setup token and convert it to an access URL.

1. Create a new application connection in you SimpleFIN Bridge account.
2. Copy the provided setup key to your clipboard.
3. Run `simplefin setup` and paste the setup key from above.
4. Securely store the provided Access URL as it is required for future calls.

See [#1](https://github.com/chrishas35/simplefin-python/issues/1) for discussion on securely storing this in future releases.

### Usage

Your Access URL will need to be stored in an environment variable called `SIMPLEFIN_ACCESS_URL` for future CLI calls.

Examples below leverage the SimpleFIN Bridge Demo Access URL of `https://demo:demo@beta-bridge.simplefin.org/simplefin`. Real world Account IDs will be in the format of `ACT-[guid]`.

#### Get accounts

`simplefin accounts [--format FORMAT]`

<!-- [[[cog
import cog
from simplefin import cli
from click.testing import CliRunner
runner = CliRunner()
result = runner.invoke(cli, ["accounts"])
cog.out(
    "```\n❯ simplefin accounts\n{}```".format(result.output)
)
]]] -->
```
❯ simplefin accounts
                        SimpleFIN Accounts                         
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━┓
┃ Institution    ┃ Account            ┃ Balance   ┃ Account ID    ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━┩
│ SimpleFIN Demo │ SimpleFIN Savings  │ 115525.50 │ Demo Savings  │
│ SimpleFIN Demo │ SimpleFIN Checking │ 26134.42  │ Demo Checking │
└────────────────┴────────────────────┴───────────┴───────────────┘
```
<!-- [[[end]]] -->

##### JSON output

<!-- [[[cog
import cog
from simplefin import cli
from click.testing import CliRunner
runner = CliRunner()
result = runner.invoke(cli, ["accounts", "--format", "json"])
cog.out(
    "```\n❯ simplefin accounts --format json\n{}```".format(result.output)
)
]]] -->
```
❯ simplefin accounts --format json
[
    {
        "org": {
            "domain": "beta-bridge.simplefin.org",
            "sfin-url": "https://beta-bridge.simplefin.org/simplefin",
            "name": "SimpleFIN Demo",
            "url": "https://beta-bridge.simplefin.org",
            "id": "simplefin.demoorg"
        },
        "id": "Demo Savings",
        "name": "SimpleFIN Savings",
        "currency": "USD",
        "balance": "115525.50",
        "available-balance": "115525.50",
        "balance-date": 1738368000,
        "transactions": [],
        "holdings": []
    },
    {
        "org": {
            "domain": "beta-bridge.simplefin.org",
            "sfin-url": "https://beta-bridge.simplefin.org/simplefin",
            "name": "SimpleFIN Demo",
            "url": "https://beta-bridge.simplefin.org",
            "id": "simplefin.demoorg"
        },
        "id": "Demo Checking",
        "name": "SimpleFIN Checking",
        "currency": "USD",
        "balance": "26134.42",
        "available-balance": "26134.42",
        "balance-date": 1738368000,
        "transactions": [],
        "holdings": []
    }
]
```
<!-- [[[end]]] -->

#### Get transactions for an account

`simplefin transactions ACCOUNT_ID [--format FORMAT] [--lookback-days INTEGER]`

<!-- [[[cog
import cog
from simplefin import cli
from click.testing import CliRunner
runner = CliRunner()
result = runner.invoke(cli, ["transactions", "Demo Savings", "--lookback-days", 1])
cog.out(
    "```\n❯ simplefin transactions \"Demo Savings\"\n{}```".format(result.output)
)
]]] -->
```
❯ simplefin transactions "Demo Savings"
         Transactions for Demo Savings         
┏━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┓
┃ Date        ┃ Payee               ┃ Amount  ┃
┡━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━┩
│ 01 Feb 2025 │ You                 │ 1960.00 │
│ 01 Feb 2025 │ John's Fishin Shack │ -05.50  │
│ 01 Feb 2025 │ Grocery store       │ -135.50 │
└─────────────┴─────────────────────┴─────────┘
```
<!-- [[[end]]] -->

##### JSON output

<!-- [[[cog
import cog
from simplefin import cli
from click.testing import CliRunner
runner = CliRunner()
result = runner.invoke(cli, ["transactions", "Demo Savings", "--format", "json", "--lookback-days", 1])
cog.out(
    "```\n❯ simplefin transactions \"Demo Savings\" --format json\n{}```".format(result.output)
)
]]] -->
```
❯ simplefin transactions "Demo Savings" --format json
{
    "errors": [],
    "accounts": [
        {
            "org": {
                "domain": "beta-bridge.simplefin.org",
                "sfin-url": "https://beta-bridge.simplefin.org/simplefin",
                "name": "SimpleFIN Demo",
                "url": "https://beta-bridge.simplefin.org",
                "id": "simplefin.demoorg"
            },
            "id": "Demo Savings",
            "name": "SimpleFIN Savings",
            "currency": "USD",
            "balance": "115525.50",
            "available-balance": "115525.50",
            "balance-date": 1738368000,
            "transactions": [
                {
                    "id": "1738382400",
                    "posted": 1738382400,
                    "amount": "1960.00",
                    "description": "Pay day!",
                    "payee": "You",
                    "memo": "PAY DAY - FROM YER JOB"
                },
                {
                    "id": "1738396800",
                    "posted": 1738396800,
                    "amount": "-05.50",
                    "description": "Fishing bait",
                    "payee": "John's Fishin Shack",
                    "memo": "JOHNS FISHIN SHACK BAIT"
                },
                {
                    "id": "1738425600",
                    "posted": 1738425600,
                    "amount": "-135.50",
                    "description": "Grocery store",
                    "payee": "Grocery store",
                    "memo": "LOCAL GROCER STORE #1133"
                }
            ],
            "holdings": [
                {
                    "id": "25bc4910-4cb4-437b-9924-ee98003651c5",
                    "created": 345427200,
                    "cost_basis": "55.00",
                    "currency": "USD",
                    "description": "Shares of Apple",
                    "market_value": "105884.8",
                    "purchase_price": "0.10",
                    "shares": "550.0",
                    "symbol": "AAPL"
                }
            ]
        }
    ]
}
```
<!-- [[[end]]] -->

#### Fetch all accounts to separate files

`simplefin fetch --output-dir DIRECTORY [--lookback-days INTEGER]`

Fetches all accounts with their transactions and saves each account to a separate JSON file. Files are organized hierarchically by institution and account name:

```
output-dir/
  institution-domain/
    account-name/
      account-id_YYYY-MM-DD.json
```

This is useful for integration with tools like [beangulp](https://github.com/beancount/beangulp) that expect one file per account.

```
❯ simplefin fetch --output-dir ./simplefin-data --lookback-days 30
Found 2 accounts
  SimpleFIN Savings: 3 transactions -> beta-bridge.simplefin.org/SimpleFIN-Savings/Demo-Savings_2025-01-15.json
  SimpleFIN Checking: 2 transactions -> beta-bridge.simplefin.org/SimpleFIN-Checking/Demo-Checking_2025-01-15.json

Wrote 2 account files to ./simplefin-data
```

Each JSON file contains the full account metadata plus transactions:

```json
{
  "org": {
    "domain": "beta-bridge.simplefin.org",
    "name": "SimpleFIN Demo"
  },
  "id": "Demo Savings",
  "name": "SimpleFIN Savings",
  "currency": "USD",
  "balance": "115525.50",
  "balance-date": 1738368000,
  "transactions": [
    {
      "id": "1738382400",
      "posted": "2025-02-01T12:00:00+00:00",
      "amount": "-50.00",
      "description": "Fishing bait",
      "payee": "John's Fishin Shack"
    }
  ]
}
```
