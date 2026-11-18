"""Source-checkout entry point; no pip install required."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from peoplecomfort.cli import main
if __name__ == "__main__":
    main()
