"""
H-Index (LeetCode 274)

Given an array of integers citations where citations[i] is the number of citations a researcher received for their ith paper, return the researcher's h-index.

According to the definition of h-index on Wikipedia: The h-index is defined as the maximum value of h such that the given researcher has published at least h papers that have each been cited at least h times.
 

Example 1:

Input: citations = [3,0,6,1,5]
Output: 3
Explanation: [3,0,6,1,5] means the researcher has 5 papers in total and each of them had received 3, 0, 6, 1, 5 citations respectively.
Since the researcher has 3 papers with at least 3 citations each and the remaining two with no more than 3 citations each, their h-index is 3.
Example 2:

Input: citations = [1,3,1]
Output: 1

min(curr, i)
(max of all the values), (current length of array), 
at every point: you know everything in front of you will be less than you.



inputs 7, 4, 3, 2, 4, 6, 0, 1, 3
7, 6, 4, 4, 3, 2, 

"""

from __future__ import annotations

import argparse


def h_index(citations: list[int]) -> int:
    citations = sorted(citations, reverse=True)
    i = 0
    h = 0
    while i < len(citations):
        h = max(h, min(citations[i], i + 1))
        i += 1

    return h


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
