"""Pytest configuration."""
import pytest
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture(scope="session")
def sample_pdf_path():
    """Path to sample PDF for testing."""
    return Path(__file__).parent / "fixtures" / "sample.pdf"


@pytest.fixture(scope="session")
def temp_output_dir(tmp_path_factory):
    """Temporary directory for test outputs."""
    return tmp_path_factory.mktemp("output")