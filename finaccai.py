"""Top-level wrapper for backward compatibility.

Running `python finaccai.py` will delegate to the package CLI in
`finaccai.cli.main()` so that both `python finaccai.py` and
`python -m finaccai` have the same behavior and the package provides
CLI logic.
"""
from finaccai.cli import main

if __name__ == "__main__":
    main()
