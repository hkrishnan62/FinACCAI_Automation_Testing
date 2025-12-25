"""Package entrypoint to run the top-level `finaccai.py` script.

This keeps the repository layout unchanged while allowing:

    python -m finaccai --csv websites.csv

"""
import os
import runpy
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))
SCRIPT = os.path.join(ROOT, "finaccai.py")
if not os.path.exists(SCRIPT):
    print("Could not find finaccai.py at expected location.", file=sys.stderr)
    sys.exit(1)

# Execute the script as __main__ so it behaves like a script when invoked with -m
runpy.run_path(SCRIPT, run_name="__main__")
