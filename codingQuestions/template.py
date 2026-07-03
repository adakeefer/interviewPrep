from __future__ import annotations

import argparse


def problem() -> str:
    return "hello"


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Compute the H-Index of a list of citation counts.")
    parser.add_argument("citations", nargs="+", type=int)
    args = parser.parse_args(argv)
    print(args)
    print(problem())


if __name__ == "__main__":
    main()


# ---- tests: run with `pytest` (from repo root) or `pytest codingQuestions/template.py` ----


def test_1():
    assert problem() == "hello"
