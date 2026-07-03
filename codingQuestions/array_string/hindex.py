"""
H-Index (LeetCode 274)

Given an array of integers `citations` where citations[i] is the number of
citations a researcher received for their ith paper, return the researcher's
h-index: the largest h such that the researcher has published h papers that
have each been cited at least h times.
"""

from __future__ import annotations

import argparse


def h_index(citations: list[int]) -> int:
    return 0


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Compute the H-Index of a list of citation counts.")
    parser.add_argument("citations", nargs="+", type=int, help="space-separated citation counts, e.g. 3 0 6 1 5")
    args = parser.parse_args(argv)
    print(h_index(args.citations))


if __name__ == "__main__":
    main()


# ---- tests: run with `pytest` (from repo root) or `pytest codingQuestions/array_string/hindex.py` ----


def test_leetcode_example_1():
    assert h_index([3, 0, 6, 1, 5]) == 3


def test_leetcode_example_2():
    assert h_index([1, 3, 1]) == 1


def test_all_zero_citations():
    assert h_index([0, 0, 0]) == 0


def test_empty_input():
    assert h_index([]) == 0


def test_single_paper():
    assert h_index([100]) == 1
