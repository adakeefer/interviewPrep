"""Human-readable match report for the mini test dataset."""

import os

from reconcile import (
    load_bank_transactions,
    load_gl_entries,
    _deterministic_candidates,
    _semantic_candidates,
    _greedy_assign,
)

base = os.path.dirname(__file__)
bank_path = os.path.join(base, "test_data", "bank_transactions_mini.csv")
gl_path = os.path.join(base, "test_data", "gl_line_items_mini.csv")

bank_txns = load_bank_transactions(bank_path)
gl_entries = load_gl_entries(gl_path)

matched_bank = set()
matched_gl = set()
bank_to_gl = {}


def _claim(candidates):
    """Same ordering _greedy_assign uses, but also records which GL each
    bank txn actually landed on (for reporting)."""
    for c in sorted(candidates, key=lambda c: c.score, reverse=True):
        if c.bank.index in matched_bank or c.gl.journal_entry_id in matched_gl:
            continue
        matched_bank.add(c.bank.index)
        matched_gl.add(c.gl.journal_entry_id)
        bank_to_gl[c.bank.index] = c.gl


_claim(_deterministic_candidates(bank_txns, gl_entries))

remaining_bank = [b for b in bank_txns if b.index not in matched_bank]
remaining_gl = [g for g in gl_entries if g.journal_entry_id not in matched_gl]
_claim(_semantic_candidates(remaining_bank, remaining_gl))

print(f"{'DATE':<10} {'AMOUNT':>12}  {'BANK DESCRIPTION':<55} STATUS")
print("-" * 110)
for b in bank_txns:
    if b.index in matched_bank:
        g = bank_to_gl[b.index]
        status = f"matched -> GL[{g.journal_entry_id[:8]}] amount={g.amount} desc={g.description!r}"
    else:
        status = "UNMATCHED"
    print(f"{b.datetime.date()!s:<10} {b.amount:>12,.2f}  {b.description[:55]:<55} {status}")

print()
print(f"matched: {len(matched_bank)} / {len(bank_txns)}")
