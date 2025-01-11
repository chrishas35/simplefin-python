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

    ❯ simplefin accounts
                            SimpleFIN Accounts
    ┏━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━┓
    ┃ Institution    ┃ Account            ┃ Balance   ┃ Account ID    ┃
    ┡━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━┩
    │ SimpleFIN Demo │ SimpleFIN Savings  │ 114125.50 │ Demo Savings  │
    │ SimpleFIN Demo │ SimpleFIN Checking │ 24302.22  │ Demo Checking │
    └────────────────┴────────────────────┴───────────┴───────────────┘

#### Get transactions for an account

`simplefin transactions ACCOUNT_ID [--format FORMAT] [--lookback-days INTEGER]`

    ❯ simplefin transactions "Demo Savings"
            Transactions for Demo Savings
    ┏━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┓
    ┃ Date        ┃ Payee               ┃ Amount ┃
    ┡━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━┩
    │ 10 Jan 2025 │ John's Fishin Shack │ -50.00 │
    │ 10 Jan 2025 │ Grocery store       │ -90.00 │
    │ 11 Jan 2025 │ John's Fishin Shack │ -55.50 │
    │ 11 Jan 2025 │ Grocery store       │ -85.50 │
    └─────────────┴─────────────────────┴────────┘

##### JSON output

We convert the posted and transacted_at, if provided, values into ISO strings.

    ❯ simplefin transactions "Demo Savings" --format json
    [
        {
            "id": "1736496000",
            "posted": "2025-01-10T08:00:00+00:00",
            "amount": "-50.00",
            "description": "Fishing bait",
            "payee": "John's Fishin Shack",
            "memo": "JOHNS FISHIN SHACK BAIT"
        },
        {
            "id": "1736524800",
            "posted": "2025-01-10T16:00:00+00:00",
            "amount": "-90.00",
            "description": "Grocery store",
            "payee": "Grocery store",
            "memo": "LOCAL GROCER STORE #1133"
        },
        {
            "id": "1736582400",
            "posted": "2025-01-11T08:00:00+00:00",
            "amount": "-55.50",
            "description": "Fishing bait",
            "payee": "John's Fishin Shack",
            "memo": "JOHNS FISHIN SHACK BAIT"
        },
        {
            "id": "1736611200",
            "posted": "2025-01-11T16:00:00+00:00",
            "amount": "-85.50",
            "description": "Grocery store",
            "payee": "Grocery store",
            "memo": "LOCAL GROCER STORE #1133"
        }
    ]
