"""Test configuration for pytest."""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# Set test environment variables
os.environ["LOG_LEVEL"] = "DEBUG"
os.environ["TEMP_DIR"] = "test_temp"
os.environ["MAX_FILES"] = "5"  # Lower limit for testing
os.environ["CLEANUP_INTERVAL"] = "60"  # Shorter interval for testing
