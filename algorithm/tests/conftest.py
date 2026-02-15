"""Pytest configuration for test discovery and imports."""

import sys
from pathlib import Path

# Add src directory to Python path for imports
# __file__ is /algorithm/tests/conftest.py
# We need /algorithm/src
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))
