"""
Module: Securities Lookup

Problem:
A ticker alone does not say which security was traded. "AMZN" in CAD is the
Amazon CDR (~24 CAD), "AMZN" in USD is the NASDAQ share (~210 USD). Grouping
or pricing by ticker alone mixes the two and silently gives wrong numbers.

Description:
Maps each (tckr, currency) pair written in the trades ledger to exactly one
security: the symbol yfinance prices it under, the currency that price is
quoted in, and its asset type. Nothing is downloaded here; this is a lookup.

Key Functions:
- create_securities_table: Creates the 'securities' lookup table
- add_security: Inserts one mapping
- get_security: Retrieves the mapping for one (tckr, currency) pair
- unmapped_securities: Lists ledger pairs that have no mapping yet

Dependencies:
- duckdb: Store and query data locally
- pydantic: Validate each mapping before it is stored

Example:
    >>> s = Security(tckr="AMZN", currency="CAD", yf_symbol="AMZN.TO",
    ...              quote_currency="CAD", asset_type="cdr", name="Amazon CDR")
    >>> add_security(conn, s)
"""

from typing import Literal, Optional
import pandas as pd
import duckdb as dd
from pydantic import BaseModel


class Security(BaseModel):
    tckr: str                                   
    currency: Literal["USD", "CAD"]             
    yf_symbol: str                              
    quote_currency: Literal["USD", "CAD"]
    asset_type: Literal["stock", "cdr", "etf", "crypto", "commodity"]
    name: Optional[str] = None


def create_securities_table(conn: dd.DuckDBPyConnection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS securities(
            tckr VARCHAR NOT NULL,
            currency VARCHAR NOT NULL CHECK (currency IN ('USD', 'CAD')),
            yf_symbol VARCHAR NOT NULL,
            quote_currency VARCHAR NOT NULL CHECK (quote_currency IN ('USD', 'CAD')),
            asset_type VARCHAR NOT NULL CHECK (asset_type IN ('stock', 'cdr', 'etf', 'crypto', 'commodity')),
            name VARCHAR,
            PRIMARY KEY (tckr, currency)
        )
        """)


def add_security(conn: dd.DuckDBPyConnection, s: Security) -> None:
    conn.execute(
        "INSERT INTO securities VALUES (?,?,?,?,?,?)",
        [s.tckr, s.currency, s.yf_symbol, s.quote_currency, s.asset_type, s.name]
    )


def get_security(conn: dd.DuckDBPyConnection, tckr: str, currency: str) -> pd.DataFrame:
    return conn.execute(
        "SELECT * FROM securities WHERE tckr = ? AND currency = ?",
        [tckr, currency]
    ).df()


def unmapped_securities(conn: dd.DuckDBPyConnection) -> pd.DataFrame:
    return conn.execute("""
        SELECT DISTINCT t.tckr, t.currency
        FROM trades t
        LEFT JOIN securities s USING (tckr, currency)
        WHERE s.tckr IS NULL
        ORDER BY t.tckr, t.currency
        """).df()
