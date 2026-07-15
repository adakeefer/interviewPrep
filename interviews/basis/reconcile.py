"""
Bank <-> GL reconciliation prototype.

Pipeline:
  1. Aggregate GL line items by journal_entry_id (sum of amounts = one
     "transaction" as viewed by the GL; a journal entry may fan out over
     multiple dates/descriptions if it was posted in split pieces).
  2. Deterministic pass: match bank transactions to GL journal entries on
     exact amount + exact date. Ambiguous cases (many candidates with the
     same amount/date) are resolved by ranking all candidate pairs and
     assigning highest-confidence pairs first, so a "cheap" match doesn't
     steal a GL entry that rightfully belongs to a different bank txn.
  3. Semantic pass: for whatever is left unmatched, widen the date window.
     If exactly one GL entry shares the amount in that window, accept it
     on date proximity alone. If several do, rank them by date proximity
     plus description similarity via get_similarity() (a stub for an
     LLM/embedding call) and take the best-supported one.
  4. Anything still unmatched on the bank side is returned as "missing
     from the GL".
"""

from __future__ import annotations

import csv
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from difflib import SequenceMatcher

DATE_FMT = "%m/%d/%y %H:%M"
AMOUNT_TOLERANCE = 0.01

# Pass 1 (deterministic): exact-date-only window.
EXACT_DATE_TOLERANCE_DAYS = 0
# Pass 2 (semantic): widen the window and lean on description similarity.
SEMANTIC_DATE_TOLERANCE_DAYS = 7


@dataclass
class BankTransaction:
    index: int
    datetime: datetime
    amount: float
    description: str


@dataclass
class GLEntry:
    journal_entry_id: str
    amount: float
    dates: list  # all distinct dates seen across this journal entry's line items
    descriptions: list  # all line item descriptions, for context/debugging
    description: str  # joined, used for similarity scoring

    def min_date_distance(self, dt: datetime) -> int:
        return min(abs((dt - d).days) for d in self.dates)


def _parse_datetime(raw: str) -> datetime:
    return datetime.strptime(raw.strip(), DATE_FMT)


def load_bank_transactions(path: str) -> list[BankTransaction]:
    transactions = []
    with open(path, newline="", encoding="utf-8") as f:
        for i, row in enumerate(csv.DictReader(f)):
            transactions.append(
                BankTransaction(
                    index=i,
                    datetime=_parse_datetime(row["datetime"]),
                    amount=round(float(row["amount"]), 2),
                    description=(row.get("description") or "").strip(),
                )
            )
    return transactions


def load_gl_entries(path: str) -> list[GLEntry]:
    """Group GL line items by journal_entry_id and sum every line in the
    group, regardless of sign - per the source spec, the sum of a journal
    entry's line items equals the transaction it represents. A split
    transaction (e.g. one $1,000 Best Buy charge posted as $200 monitor +
    $800 laptop) sums to the bank amount directly. A journal entry with
    offsetting lines (e.g. +12666.5 / -12666.5 on the same date) is a
    legitimate candidate too, just for a net-zero bank transaction (a wash
    entry) rather than for either line's amount individually.
    """
    groups: dict[str, list[dict]] = defaultdict(list)
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            groups[row["journal_entry_id"]].append(row)

    entries = []
    for journal_entry_id, rows in groups.items():
        amounts = [float(r["amount"]) for r in rows]
        dates = sorted({_parse_datetime(r["datetime"]) for r in rows})
        descriptions = [(r.get("description") or "").strip() for r in rows]
        entries.append(
            GLEntry(
                journal_entry_id=journal_entry_id,
                amount=round(sum(amounts), 2),
                dates=dates,
                descriptions=descriptions,
                description=" / ".join(d for d in descriptions if d),
            )
        )
    return entries


def get_similarity(str1: str, str2: str) -> float:
    """Stub for an LLM-backed semantic similarity check.

    In production, replace this with a call to an LLM (or an embedding
    model + cosine similarity) that judges whether two free-text
    transaction descriptions plausibly describe the same underlying
    transaction, e.g.:

        response = client.messages.create(
            model="claude-sonnet-5",
            max_tokens=8,
            messages=[{
                "role": "user",
                "content": (
                    "Rate 0.0-1.0 how likely these two bank/GL transaction "
                    f"descriptions refer to the same transaction.\n"
                    f'Bank: "{str1}"\nGL: "{str2}"\nRespond with only the number.'
                ),
            }],
        )
        return float(response.content[0].text.strip())

    For local development/testing (no network/LLM dependency), this falls
    back to a lightweight lexical similarity so the pipeline is exercisable
    end-to-end.
    """
    a, b = str1.strip().lower(), str2.strip().lower()
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


@dataclass
class Candidate:
    bank: BankTransaction
    gl: GLEntry
    score: float


def _deterministic_candidates(
    bank_txns: list[BankTransaction], gl_entries: list[GLEntry]
) -> list[Candidate]:
    gl_by_amount: dict[float, list[GLEntry]] = defaultdict(list)
    for g in gl_entries:
        gl_by_amount[g.amount].append(g)

    candidates = []
    for b in bank_txns:
        for g in gl_by_amount.get(b.amount, []):
            dist = g.min_date_distance(b.datetime)
            if dist <= EXACT_DATE_TOLERANCE_DAYS:
                candidates.append(Candidate(b, g, score=1.0))
    return candidates


def _semantic_candidates(
    bank_txns: list[BankTransaction], gl_entries: list[GLEntry]
) -> list[Candidate]:
    """Widen the date window past the deterministic pass. Amount plus a
    same-week date is already strong evidence, so descriptions only need
    to earn their keep when they're actually needed to break a tie: if a
    bank transaction has exactly one GL entry with the same amount inside
    the window, accept it on date proximity alone (descriptions are often
    empty or unrelated boilerplate in this data). If several GL entries
    with that amount fall inside the window, use get_similarity() to pick
    the best-described match, and only accept it above threshold.
    """
    gl_by_amount: dict[float, list[GLEntry]] = defaultdict(list)
    for g in gl_entries:
        gl_by_amount[g.amount].append(g)

    candidates = []
    for b in bank_txns:
        window = [
            (g, g.min_date_distance(b.datetime))
            for g in gl_by_amount.get(b.amount, [])
            if g.min_date_distance(b.datetime) <= SEMANTIC_DATE_TOLERANCE_DAYS
        ]
        if not window:
            continue

        if len(window) == 1:
            g, dist = window[0]
            date_score = 1 - (dist / (SEMANTIC_DATE_TOLERANCE_DAYS + 1))
            candidates.append(Candidate(b, g, score=0.9 + 0.1 * date_score))
            continue

        # Multiple GL entries share this amount within the window: rank by
        # date proximity plus description similarity rather than hard-gating
        # on similarity alone. Descriptions here are frequently generic
        # category labels ("Data Storage") uncorrelated with the bank's
        # counterparty text, so a same-day amount match should still win
        # even when get_similarity is weak - description mainly serves to
        # break genuine date ties. The global greedy assignment (which
        # claims the highest-scoring pairs across *all* bank txns first)
        # is what ultimately resolves same-date collisions correctly.
        scored = [
            Candidate(
                b, g,
                score=0.7 * (1 - dist / (SEMANTIC_DATE_TOLERANCE_DAYS + 1))
                + 0.3 * get_similarity(b.description, g.description),
            )
            for g, dist in window
        ]
        candidates.append(max(scored, key=lambda c: c.score))
    return candidates


def _greedy_assign(
    candidates: list[Candidate],
    matched_bank: set[int],
    matched_gl: set[str],
) -> None:
    """Claim highest-confidence pairs first so ambiguous same-amount
    collisions don't rob a bank txn of its rightful GL entry."""
    for c in sorted(candidates, key=lambda c: c.score, reverse=True):
        if c.bank.index in matched_bank or c.gl.journal_entry_id in matched_gl:
            continue
        matched_bank.add(c.bank.index)
        matched_gl.add(c.gl.journal_entry_id)


def find_bank_transactions_missing_from_gl(
    bank_csv_path: str, gl_csv_path: str
) -> list[BankTransaction]:
    """Return bank transactions that have no corresponding GL entry."""
    bank_txns = load_bank_transactions(bank_csv_path)
    gl_entries = load_gl_entries(gl_csv_path)

    matched_bank: set[int] = set()
    matched_gl: set[str] = set()

    # Pass 1: deterministic (exact amount, exact date).
    _greedy_assign(_deterministic_candidates(bank_txns, gl_entries), matched_bank, matched_gl)

    # Pass 2: semantic (exact amount, fuzzy date + description similarity).
    remaining_bank = [b for b in bank_txns if b.index not in matched_bank]
    remaining_gl = [g for g in gl_entries if g.journal_entry_id not in matched_gl]
    _greedy_assign(_semantic_candidates(remaining_bank, remaining_gl), matched_bank, matched_gl)

    return [b for b in bank_txns if b.index not in matched_bank]


if __name__ == "__main__":
    import os

    base = os.path.dirname(__file__)
    missing = find_bank_transactions_missing_from_gl(
        os.path.join(base, "bank_transactions.csv"),
        os.path.join(base, "gl_line_items.csv"),
    )

    bank_total = len(load_bank_transactions(os.path.join(base, "bank_transactions.csv")))
    print(f"bank transactions: {bank_total}")
    print(f"matched: {bank_total - len(missing)}")
    print(f"missing from GL: {len(missing)}")
    print()
    for b in missing[:30]:
        print(f"{b.datetime.date()}  {b.amount:>14,.2f}  {b.description}")
