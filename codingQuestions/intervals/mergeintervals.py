'''
Given an array of intervals where intervals[i] = [starti, endi], merge all overlapping intervals, and return an array of the non-overlapping intervals that cover all the intervals in the input.

 

Example 1:

Input: intervals = [[1,3],[2,6],[8,10],[15,18]]
Output: [[1,6],[8,10],[15,18]]
Explanation: Since intervals [1,3] and [2,6] overlap, merge them into [1,6].
Example 2:

Input: intervals = [[1,4],[4,5]]
Output: [[1,5]]
Explanation: Intervals [1,4] and [4,5] are considered overlapping.
Example 3:

Input: intervals = [[4,7],[1,4]]
Output: [[1,7]]
Explanation: Intervals [1,4] and [4,7] are considered overlapping.
 

Constraints:

1 <= intervals.length <= 104
intervals[i].length == 2
0 <= starti <= endi <= 104

cases:

[           ]
[ ],      [ ]

[  ][  ]
  [  ]

[ ]  [  ]   [    ] [ ]
 [ ]  [ ] [    ]
   [               ]
[ ]                  [     ] []
'''



from __future__ import annotations

import argparse


def merge(intervals):
    intervals = sorted(intervals, key=lambda x: x[0])
    output = []
    i = 0
    while i < len(intervals):
        left = intervals[i][0]
        right = intervals[i][1]
        while i + 1 < len(intervals) and right >= intervals[i + 1][0]:
            right = max(intervals[i + 1][1], right)
            i += 1
        output.append([left, right])
        i += 1

    return output


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Compute the H-Index of a list of citation counts.")
    parser.add_argument("citations", nargs="+", type=int)
    args = parser.parse_args(argv)


if __name__ == "__main__":
    main()


# ---- tests: run with `pytest` (from repo root) or `pytest codingQuestions/template.py` ----


def test_1():
    assert merge([[1,3],[2,6],[8,10],[15,18]]) == [[1,6],[8,10],[15,18]]

def test_2():
    assert merge([[1,4],[4,5]]) == [[1, 5]]