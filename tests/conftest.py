import sys
from pathlib import Path

# Add project root to PYTHONPATH for tests
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
