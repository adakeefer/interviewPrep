This is a repo dedicated to locally recreating and rerunning both coding questions and system design prompts.

/codingQuestions contains all coding

/systemDesign is design.


Everything is in Python3 for symplicity.

When choosing a new tech stack for system design harnesses, please use existing technologies in the repo to keep things simple (no need for two open source implementations of a distributed queue).

# Coding question setup
source .venv/bin/activate.fish          # activate once per shell session
python3 codingQuestions/array_string/hindex.py 3 0 6 1 5   # run it: prints 3
pytest                              # run every question's tests from repo root
pytest codingQuestions/array_string/hindex.py   # run just this one



