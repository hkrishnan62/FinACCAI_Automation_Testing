"""Package entrypoint to run the package CLI: `finaccai.cli.main()`.

This enables `python -m finaccai --csv websites.csv` and delegates to
`finaccai.cli.main()` for a cleaner package layout.
"""
from .cli import main

if __name__ == "__main__":
    main()
