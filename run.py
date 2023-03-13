import sys
import os
import runpy
from pathlib import Path

def main() -> None:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    modname = sys.argv[1]
    args = sys.argv[2:]
    sys.argv = [*sys.argv[0:1], *sys.argv[2:]]

    runpy._run_module_as_main(f"gptsearch.{modname}", alter_argv=False)

if __name__ == "__main__":
    main()