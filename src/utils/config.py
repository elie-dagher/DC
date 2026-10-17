"""
Module: Configuration

Problem:
All paths and keys are subject to change, which leads to changing the file path for several other files.
As algorithms adapt, creating a single path for criteria weighing is essential efficiency.

Description:
Single source of directories for paths, environment variables, and the MCDA criteria
defined in configs/criteria.yaml.

Key Functions:
- get_conn: Open the test database (default for all public code)
- get_real_conn: Open the real database (only private/ scripts call this)
- load_criteria: Read and parse configs/criteria.yaml

Dependencies:
- python-dotenv: Load .env
- pyyaml: Parse criteria.yaml

Example:
    >>> criteria = load_criteria()
    >>> criteria['screening']['altman_z_min']
    1.81
"""

import os

import duckdb as dd
import yaml
from dotenv import load_dotenv

load_dotenv()

# Paths
ROOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
DATA_DIR = os.path.join(ROOT_DIR, "data")
CONFIGS_DIR = os.path.join(ROOT_DIR, "configs")
# Built from __file__, so scripts find them no matter which folder they are run from.
# Real database: real clients and trades. Lives in private/ (gitignored). Only private/ scripts open it.
REAL_DB_PATH = os.path.join(ROOT_DIR, "private", "dagher.duckdb")
# Test database: demos, experiments, anything public code writes. Gitignored by *.duckdb.
TEST_DB_PATH = os.path.join(ROOT_DIR, "test.duckdb")
# API Keys
ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


def get_conn(read_only: bool = False) -> dd.DuckDBPyConnection:
    """Open the test database. Public code uses this, so it can never write to real data."""
    return dd.connect(TEST_DB_PATH, read_only=read_only)


def get_real_conn(read_only: bool = True) -> dd.DuckDBPyConnection:
    """Open the real database. Read-only unless the caller explicitly passes read_only=False."""
    return dd.connect(REAL_DB_PATH, read_only=read_only)


def load_criteria() -> dict:
    """Load the MCDA criteria (pillar weights + screening thresholds)."""
    with open(os.path.join(CONFIGS_DIR, "criteria.yaml"), "r") as f:
        return yaml.safe_load(f)
