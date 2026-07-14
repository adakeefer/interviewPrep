'''
Given the root of a binary tree, return the zigzag level order traversal of its nodes' values. (i.e., from left to right, then right to left for the next level and alternate between).

 

Example 1:


Input: root = [3,9,20,null,null,15,7]
Output: [[3],[20,9],[15,7]]
Example 2:

Input: root = [1]
Output: [[1]]
Example 3:

Input: root = []
Output: []
 

Constraints:

The number of nodes in the tree is in the range [0, 2000].
-100 <= Node.val <= 100


'''


from __future__ import annotations

import argparse

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def zigzag():
    ans = []
    return ans


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Compute the H-Index of a list of citation counts.")
    parser.add_argument("citations", nargs="+", type=int)
    args = parser.parse_args(argv)


if __name__ == "__main__":
    main()


# ---- tests: run with `pytest` (from repo root) or `pytest codingQuestions/template.py` ----


def test_1():
    assert zigzag() == "hello"
