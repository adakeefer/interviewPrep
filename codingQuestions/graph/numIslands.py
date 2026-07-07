'''
Given an m x n 2D binary grid grid which represents a map of '1's (land) and '0's (water), return the number of islands.

An island is surrounded by water and is formed by connecting adjacent lands horizontally or vertically. You may assume all four edges of the grid are all surrounded by water.

 

Example 1:

Input: grid = [
  ["1","1","1","1","0"],
  ["1","1","0","1","0"],
  ["1","1","0","0","0"],
  ["0","0","0","0","0"]
]
Output: 1
Example 2:

Input: grid = [
  ["1","1","0","0","0"],
  ["1","1","0","0","0"],
  ["0","0","1","0","0"],
  ["0","0","0","1","1"]
]
Output: 3




'''

from __future__ import annotations
from collections import deque

import argparse


def numIslands(grid: list[list[int]]) -> int:
    numIslands = 0

    search = deque()
    dirs = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    for i in len(grid):
        for j in len(grid[i]):
            if grid[i][j] == 1:
                search.append((i, j))
                while len(search) > 0:
                    i0, j0 = search.popleft()
                    for dir in dirs:
                        if i0 + dir[0] > 0 and i0 + dir[0]


    return 0


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Compute the H-Index of a list of citation counts.")
    parser.add_argument("citations", nargs="+", type=int)
    args = parser.parse_args(argv)



if __name__ == "__main__":
    main()


# ---- tests: run with `pytest` (from repo root) or `pytest codingQuestions/template.py` ----


def test_1():
    assert numIslands([
  ["1","1","1","1","0"],
  ["1","1","0","1","0"],
  ["1","1","0","0","0"],
  ["0","0","0","0","0"]
]) == 1

def test_2():
    assert numIslands([
  ["1","1","0","0","0"],
  ["1","1","0","0","0"],
  ["0","0","1","0","0"],
  ["0","0","0","1","1"]
]) == 3