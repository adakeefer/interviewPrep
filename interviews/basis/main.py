import csv
import os


def load_bank_transactions() -> list[dict]:
    script_directory = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_directory, "bank_transactions.csv")
    with open(file_path, mode="r", encoding="utf-8") as f:
        bank_transactions = list(csv.DictReader(f))
    return bank_transactions


def load_general_ledger() -> list[dict]:
    script_directory = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_directory, "general_ledger_entries.csv")
    with open(file_path, mode="r", encoding="utf-8") as f:
        general_ledger_entries = list(csv.DictReader(f))
    return general_ledger_entries


def main() -> None:
    bank_transactions = load_bank_transactions()
    general_ledger_lines = load_general_ledger()

    # Write code here


if __name__ == "__main__":
    main()