# Interview 2 - 7/15 2pmEST

# Bank Reconciliation Automation

## Background
A fundamental task in accounting is ensuring that every transaction recorded in a bank account is accurately reflected in the accounting system, referred to as the "general ledger" (GL).

Historically, this involved manually comparing a bank statement with entries in the GL, matching transactions based on date, amount, and description.
However, with advancements in bank APIs, this process can now be partially automated.

## Task Overview
Upon onboarding a new client, our system gains API access to their bank account and their existing accounting system.

You will be provided with two CSV files:

### bank_transactions.csv
- Downloaded directly from the bank API.
- Contains:
  - `datetime`: The transaction date.
  - `amount`: The transaction amount.
  - `description`: A description of the transaction.

Example:

| description | amount | datetime |
|-------------|--------|----------|
| "BESTBUY"   | 1000   | 1/3/2024 |

### gl_line_items.csv
- Exported from the accounting system.
- Contains:
  - `journal_entry_id`: Links split transactions that are part of the same entry.
  - `datetime`: The transaction date.
  - `amount`: The transaction amount.
  - `description`: A description of the GL entry.

Example:

| journal_entry_id       | datetime  | amount | description |
|------------------------|-----------|--------|-------------|
| '955f6fc9-...42583'    | 1/3/2024  | 200    | "monitor"   |
| '955f6fc9-...42583'    | 1/3/2024  | 800    | "laptop"    |

### Your task:
Write a production-ready Python function that compares the two datasets and returns a list of transactions present in the bank transactions file but missing in the GL.

## Considerations and Challenges
The comparison process involves several potential mismatches:

### Date Discrepancies:
- Bank transaction dates may not align perfectly with GL entry dates. For example, a bank transaction on 3/1/2024 might appear as 3/3/2024 in the GL.

### Split Transactions:
- A single bank transaction (e.g., $1,000 at Best Buy) might be split into multiple line items in the GL (e.g., $200 for monitor, $800 for laptop).

### Description Differences:
- Bank descriptions may differ or be missing in the GL. For instance, the bank might record "Uber" while the GL records "Taxi" or leaves the description empty.

### Combined Discrepancies:
- Any combination of the above may occur in a single transaction.



### Notes

Journal entry is a view of a transaction. might be broken down into multiple steps
sum of all journal entries' line items will be equal to a transaction

stub: get_similarity(str1, str2) -> float range 0.0->1.0

all dates for line item entry are exactly the same

positives match positives negatives match negatives
sum of all of these match bank transaction